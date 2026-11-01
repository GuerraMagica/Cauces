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
        WindowGroup("Cauces") {
            MainView(controller: controller)
                .onAppear { delegate.shutdown = { controller.shutdown() } }
        }
        .defaultSize(width: 1000, height: 656)
        .windowResizability(.contentMinSize)
        .commands {
            AudioSettingsCommands()
            CommandGroup(replacing: .newItem) {
                Button("Open audio…") { controller.choose() }
                    .keyboardShortcut("o").disabled(controller.state.busy)
            }
        }
        Window("Settings", id: "audio-settings") {
            AudioSettingsView(output: controller.preview.output)
        }.windowResizability(.contentSize).defaultPosition(.center)
    }
}

struct MainView: View {
    @ObservedObject var controller: JobController
    @State private var dropping = false
    var body: some View {
        VStack(spacing: 22) {
            if controller.state.hasResult {
                ReviewView(controller: controller)
            } else {
                importPanel
            }
            Text("© GuerraMagica Audio").font(.system(size: 12))
                .foregroundStyle(FlowTheme.secondary).frame(maxWidth: .infinity)
        }
        .padding(32).frame(minWidth: 820, minHeight: 576)
        .background(FlowTheme.background)
        .foregroundStyle(FlowTheme.text).tint(FlowTheme.action).preferredColorScheme(.dark)
        .background(FlowWindowStyle())
        .onDrop(of: [UTType.fileURL.identifier], isTargeted: $dropping) { providers in
            guard !controller.state.busy, let provider = providers.first else { return false }
            _ = provider.loadObject(ofClass: URL.self) { url, _ in
                guard let url else { return }; Task { @MainActor in controller.open(url) }
            }; return true
        }
        .onReceive(controller.preview.output.$notice) { message in
            if let message { controller.error = message; controller.preview.output.notice = nil }
        }
        .alert("Unable to complete the operation", isPresented: Binding(get: { controller.error != nil }, set: { if !$0 { controller.error = nil } })) {
            Button("OK") { controller.error = nil }
        } message: { Text(controller.error ?? "") }
    }
    private var importPanel: some View {
        VStack(spacing: 0) {
            Spacer(minLength: 16)
            FlowArtwork().padding(.horizontal, 28)
            Spacer().frame(height: 26)
            if controller.state.busy {
                Text(controller.state.active == .inspect ? "Opening audio" : "Separating voices")
                    .font(.system(size: 30, weight: .semibold))
                sourceName.padding(.top, 12)
                VStack(spacing: 12) {
                    if controller.state.active == .separate {
                        ProgressView(value: controller.progress).accessibilityLabel("Separation progress")
                        HStack {
                            Text(controller.stage)
                            Spacer()
                            Text("\(Int(controller.progress * 100))%").monospacedDigit()
                        }.font(.system(size: 13)).foregroundStyle(FlowTheme.secondary)
                    } else {
                        ProgressView().controlSize(.small).accessibilityLabel("Opening audio")
                    }
                }.frame(maxWidth: 420).padding(.top, 26)
                Button("Cancel", role: .cancel) { controller.cancel() }
                    .buttonStyle(FlowButtonStyle()).keyboardShortcut(.cancelAction).padding(.top, 24)
            } else if controller.state.hasSource {
                Text("Ready to separate").font(.system(size: 30, weight: .semibold))
                sourceName.padding(.top, 12)
                Text(controller.info).font(.system(size: 13)).foregroundStyle(FlowTheme.secondary).padding(.top, 8)
                HStack(spacing: 12) {
                    Button("Separate voices", systemImage: "waveform.path") { controller.separate() }
                        .buttonStyle(FlowButtonStyle(primary: true)).keyboardShortcut(.defaultAction)
                    Button("Change file…") { controller.choose() }.buttonStyle(FlowButtonStyle())
                }.padding(.top, 28)
            } else {
                Text("Give each voice its own course.").font(.system(size: 30, weight: .semibold))
                    .multilineTextAlignment(.center)
                Text("Drop a WAV file here to get started.").font(.system(size: 16))
                    .foregroundStyle(FlowTheme.secondary).padding(.top, 12)
                Button("Open audio…", systemImage: "plus") { controller.choose() }
                    .buttonStyle(FlowButtonStyle(primary: true)).keyboardShortcut(.defaultAction).padding(.top, 28)
                Text("Mono or identical dual mono · 8–48 kHz · Up to 30 min")
                    .font(.system(size: 12)).foregroundStyle(FlowTheme.secondary).padding(.top, 16)
            }
            Spacer(minLength: 20)
        }
        .padding(28).frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(FlowTheme.surface, in: RoundedRectangle(cornerRadius: 16))
        .overlay(RoundedRectangle(cornerRadius: 16).strokeBorder(dropping ? FlowTheme.action : FlowTheme.border, style: StrokeStyle(lineWidth: dropping ? 2 : 1, dash: dropping ? [6, 5] : [])))
    }
    private var sourceName: some View {
        Text(controller.source?.lastPathComponent ?? "Audio")
            .font(.system(size: 16, weight: .medium)).lineLimit(1).truncationMode(.middle)
            .help(controller.source?.lastPathComponent ?? "Audio").textSelection(.enabled)
    }
}

struct ReviewView: View {
    @ObservedObject var controller: JobController
    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            HStack(spacing: 12) {
                Image(systemName: "waveform").font(.system(size: 23)).foregroundStyle(FlowTheme.voice1)
                VStack(alignment: .leading, spacing: 6) {
                    Text(controller.source?.lastPathComponent ?? "Audio").font(.system(size: 15, weight: .semibold))
                        .lineLimit(1).truncationMode(.middle).help(controller.source?.lastPathComponent ?? "Audio")
                    Text(controller.info).font(.system(size: 12)).foregroundStyle(FlowTheme.secondary)
                }
                Spacer(minLength: 16)
                Button("Change file…") { controller.choose() }.buttonStyle(FlowButtonStyle()).disabled(controller.state.busy)
            }
            VStack(alignment: .leading, spacing: 22) {
                FlowArtwork().frame(maxWidth: .infinity).frame(height: 130)
                Text("Listen to each voice").font(.system(size: 26, weight: .semibold))
                Text("Switch between tracks at the same point in time.")
                    .font(.system(size: 14)).foregroundStyle(FlowTheme.secondary).padding(.top, -12)
                PreviewView(player: controller.preview, output: controller.preview.output) { controller.error = AppMessages.describe($0) }
                    .disabled(controller.state.busy)
            }
            .padding(28).frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
            .background(FlowTheme.surface, in: RoundedRectangle(cornerRadius: 16))
            .overlay(RoundedRectangle(cornerRadius: 16).strokeBorder(FlowTheme.border))
            HStack(spacing: 12) {
                if controller.state.active == .export {
                    ProgressView().controlSize(.small)
                    Text("Exporting audio…").font(.system(size: 13)).foregroundStyle(FlowTheme.secondary)
                } else if let directory = controller.exportDirectory {
                    Label("Audio exported", systemImage: "checkmark.circle.fill")
                        .font(.system(size: 13)).foregroundStyle(FlowTheme.success)
                    Button("Show folder") { NSWorkspace.shared.activateFileViewerSelecting([directory]) }
                        .buttonStyle(.link).font(.system(size: 13))
                } else {
                    Button("Separate again") { controller.separate() }.buttonStyle(FlowButtonStyle())
                }
                Spacer(minLength: 12)
                Button("Export audio…", systemImage: "square.and.arrow.up") { controller.export() }
                    .buttonStyle(FlowButtonStyle(primary: true)).disabled(!controller.state.canExport)
            }
        }
    }
}

struct PreviewView: View {
    @ObservedObject var player: PreviewPlayer
    @ObservedObject var output: AudioOutputSettings
    var onError: (Error) -> Void
    @State private var scrubbing = false
    @State private var scrubPosition = 0.0
    @State private var resume = false
    private let labels = ["Original", "Voice 1", "Voice 2", "Residual"]
    private let colors = [FlowTheme.text, FlowTheme.voice1, FlowTheme.voice2, FlowTheme.residual]
    var body: some View {
        VStack(spacing: 24) {
            HStack(spacing: 10) {
                ForEach(0..<4) { index in
                    Button { player.selected = index } label: {
                        HStack(spacing: 8) {
                            Image(systemName: player.selected == index ? "checkmark.circle.fill" : "circle")
                                .foregroundStyle(colors[index])
                            Text(labels[index]).font(.system(size: 14, weight: .semibold))
                        }.frame(maxWidth: .infinity).frame(height: 44)
                            .background(player.selected == index ? FlowTheme.raised : FlowTheme.surface, in: RoundedRectangle(cornerRadius: 10))
                            .overlay(RoundedRectangle(cornerRadius: 10).strokeBorder(player.selected == index ? colors[index] : FlowTheme.border))
                    }.buttonStyle(.plain)
                        .keyboardShortcut(KeyEquivalent(Character(String(index + 1))), modifiers: .command)
                        .help("Listen to \(labels[index]) (⌘\(index + 1))")
                        .accessibilityLabel(labels[index])
                        .accessibilityValue(player.selected == index ? "Selected" : "Not selected")
                        .accessibilityAddTraits(player.selected == index ? [.isSelected] : [])
                }
            }.accessibilityElement(children: .contain).accessibilityLabel("Listen to track")
            HStack(spacing: 16) {
                Button { do { try player.toggle() } catch { onError(error) } } label: {
                    Image(systemName: player.playing ? "pause.fill" : "play.fill").frame(width: 20)
                }.buttonStyle(FlowButtonStyle()).keyboardShortcut(" ", modifiers: [])
                    .help("Play or pause (Space)").accessibilityLabel(player.playing ? "Pause" : "Play")
                Slider(value: Binding(get: { scrubbing ? scrubPosition : player.position }, set: { value in
                    scrubPosition = value
                    if !scrubbing { do { try player.seek(to: value) } catch { onError(error) } }
                }), in: 0...max(0.001, player.duration)) { editing in
                    if editing { scrubPosition = player.position; resume = player.playing; player.pause(); scrubbing = true }
                    else {
                        do { try player.seek(to: scrubPosition); if resume { try player.play() } } catch { onError(error) }
                        scrubbing = false
                    }
                }.accessibilityLabel("Playback position")
                Text("\(JobController.time(scrubbing ? scrubPosition : player.position)) / \(JobController.time(player.duration))")
                    .font(.system(size: 12).monospacedDigit()).foregroundStyle(FlowTheme.secondary)
                    .frame(width: 166, alignment: .trailing)
            }
        }.disabled(output.isApplying)
    }
}
