import SwiftUI
import AppKit
import UniformTypeIdentifiers

final class AppDelegate: NSObject, NSApplicationDelegate {
    var shutdown: (() -> Void)?
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { true }
    func applicationWillTerminate(_ notification: Notification) { shutdown?() }
}

@main struct DialogueSeparatorApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var delegate
    @StateObject private var controller = JobController()
    var body: some Scene {
        WindowGroup("Separador de diálogo") {
            MainView(controller: controller)
                .onAppear { delegate.shutdown = { controller.shutdown() } }
        }
        .defaultSize(width: 860, height: 620)
        .windowResizability(.contentMinSize)
        .commands {
            CommandGroup(replacing: .newItem) { Button("Abrir WAV…") { controller.choose() }.keyboardShortcut("o").disabled(controller.state.busy) }
        }
    }
}

struct MainView: View {
    @ObservedObject var controller: JobController
    @State private var dropping = false
    var body: some View {
        VStack(alignment: .leading, spacing: 22) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Separador de diálogo").font(.largeTitle.bold())
                    Text("Dos voces · Residual · Procesamiento local").foregroundStyle(.secondary)
                }
                Spacer()
                Text("BETA PERSONAL · CPU").font(.caption.weight(.semibold)).padding(.horizontal, 10).padding(.vertical, 7)
                    .background(.quaternary, in: Capsule())
            }
            VStack(spacing: 12) {
                Image(systemName: controller.source == nil ? "waveform.badge.plus" : "waveform")
                    .font(.system(size: 30)).foregroundStyle(.tint)
                Text(controller.source?.lastPathComponent ?? "Arrastra un WAV o selecciona un archivo")
                    .font(.headline).lineLimit(2).textSelection(.enabled)
                Text(controller.info).font(.callout).foregroundStyle(.secondary).multilineTextAlignment(.center)
                Button(controller.source == nil ? "Abrir WAV…" : "Cambiar archivo…") { controller.choose() }
                    .disabled(controller.state.busy)
                if controller.source == nil { Text("Hasta 30 minutos. Los originales se conservan.").font(.caption).foregroundStyle(.secondary) }
            }
            .frame(maxWidth: .infinity).padding(24)
            .background(dropping ? Color.accentColor.opacity(0.12) : Color.primary.opacity(0.035), in: RoundedRectangle(cornerRadius: 14))
            .overlay(RoundedRectangle(cornerRadius: 14).strokeBorder(dropping ? Color.accentColor : Color.primary.opacity(0.12), style: StrokeStyle(lineWidth: 1, dash: [6, 5])))
            .onDrop(of: [UTType.fileURL.identifier], isTargeted: $dropping) { providers in
                guard !controller.state.busy, let provider = providers.first else { return false }
                _ = provider.loadObject(ofClass: URL.self) { url, _ in
                    guard let url else { return }; Task { @MainActor in controller.open(url) }
                }; return true
            }
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Text(controller.stage).font(.headline)
                    Spacer()
                    Text(controller.elapsed).font(.caption.monospacedDigit()).foregroundStyle(.secondary)
                }
                if controller.state.active == .separate { ProgressView(value: controller.progress).accessibilityLabel("Progreso de separación") }
                HStack {
                    Button("Separar voces", systemImage: "waveform.path") { controller.separate() }
                        .buttonStyle(.borderedProminent).disabled(!controller.state.canSeparate)
                    if controller.state.active == .separate || controller.state.active == .inspect {
                        Button("Cancelar", role: .cancel) { controller.cancel() }
                    }
                    if controller.state.active == .export { ProgressView().controlSize(.small); Text("Exportando…").foregroundStyle(.secondary) }
                    Spacer()
                    Button("Exportar tres stems…", systemImage: "square.and.arrow.up") { controller.export() }
                        .disabled(!controller.state.canExport)
                }
            }
            Divider()
            PreviewView(player: controller.preview) { controller.error = $0.localizedDescription }
                .disabled(!controller.preview.ready || controller.state.busy)
            HStack(alignment: .top) {
                Text("Float32 · Sin normalización automática · El residual puede contener diálogo")
                    .font(.caption).foregroundStyle(.secondary)
                Spacer()
                if let directory = controller.exportDirectory {
                    Button("Mostrar exportación") { NSWorkspace.shared.activateFileViewerSelecting([directory]) }.font(.caption)
                }
            }
        }
        .padding(28).frame(minWidth: 760, minHeight: 600)
        .alert("No se ha podido completar", isPresented: Binding(get: { controller.error != nil }, set: { if !$0 { controller.error = nil } })) {
            Button("Entendido") { controller.error = nil }
        } message: { Text(controller.error ?? "") }
    }
}

struct PreviewView: View {
    @ObservedObject var player: PreviewPlayer
    var onError: (Error) -> Void
    @State private var scrubbing = false
    @State private var scrubPosition = 0.0
    @State private var resume = false
    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text("Comparar en el mismo punto").font(.headline)
                Spacer()
                Picker("Escuchar", selection: $player.selected) {
                    Text("Original").tag(0); Text("Voz 1").tag(1); Text("Voz 2").tag(2); Text("Residual").tag(3)
                }.pickerStyle(.segmented).frame(maxWidth: 480)
            }
            HStack(spacing: 14) {
                Button { do { try player.toggle() } catch { onError(error) } } label: {
                    Image(systemName: player.playing ? "pause.fill" : "play.fill").frame(width: 22)
                }.accessibilityLabel(player.playing ? "Pausar" : "Reproducir")
                Slider(value: Binding(get: { scrubbing ? scrubPosition : player.position }, set: { scrubPosition = $0 }), in: 0...max(0.001, player.duration)) { editing in
                    if editing { scrubPosition = player.position; resume = player.playing; player.pause(); scrubbing = true }
                    else {
                        do { try player.seek(to: scrubPosition); if resume { try player.play() } } catch { onError(error) }
                        scrubbing = false
                    }
                }.accessibilityLabel("Posición de reproducción")
                Text("\(JobController.time(scrubbing ? scrubPosition : player.position)) / \(JobController.time(player.duration))")
                    .font(.caption.monospacedDigit()).frame(width: 180, alignment: .trailing)
            }
        }
    }
}
