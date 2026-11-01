import SwiftUI

struct AudioSettingsCommands: Commands {
    @Environment(\.openWindow) private var openWindow
    var body: some Commands {
        CommandGroup(replacing: .appSettings) {
            Button("Settings…") { openWindow(id: "audio-settings") }.keyboardShortcut(",")
        }
    }
}

struct AudioSettingsView: View {
    @ObservedObject var output: AudioOutputSettings
    @Environment(\.dismissWindow) private var dismissWindow
    @State private var deviceUID = ""
    @State private var sampleRate = 0.0
    @State private var error: String?
    private var device: OutputDevice? { output.device(for: deviceUID.isEmpty ? nil : deviceUID) }
    private var draft: OutputPreference { OutputPreference(deviceUID: deviceUID.isEmpty ? nil : deviceUID, sampleRate: sampleRate == 0 ? nil : sampleRate) }
    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Label("Audio output", systemImage: "speaker.wave.2").font(.system(size: 22, weight: .semibold))
            Grid(alignment: .leading, horizontalSpacing: 20, verticalSpacing: 20) {
                GridRow {
                    Text("Output").font(.system(size: 14, weight: .medium))
                    Picker("Output", selection: $deviceUID) {
                        Text("System Default").tag("")
                        ForEach(output.devices) { item in Text(item.name).tag(item.uid) }
                        if !deviceUID.isEmpty, device == nil { Text("Selected output unavailable").tag(deviceUID) }
                    }.labelsHidden().frame(maxWidth: .infinity).accessibilityLabel("Output")
                }
                GridRow {
                    Text("Sample rate").font(.system(size: 14, weight: .medium))
                    Picker("Sample rate", selection: $sampleRate) {
                        Text("Device default").tag(0.0)
                        ForEach(device?.sampleRates ?? [], id: \.self) { rate in Text(AudioOutputSettings.rateLabel(rate)).tag(rate) }
                        if sampleRate != 0, !(device?.sampleRates.contains(sampleRate) ?? false) {
                            Text("\(AudioOutputSettings.rateLabel(sampleRate)) — unavailable").tag(sampleRate)
                        }
                    }.labelsHidden().frame(maxWidth: .infinity).disabled(device == nil).accessibilityLabel("Sample rate")
                }
            }.padding(20).background(FlowTheme.surface, in: RoundedRectangle(cornerRadius: 12))
            VStack(alignment: .leading, spacing: 8) {
                Text(device.map { "Current: \($0.name) · \(AudioOutputSettings.rateLabel($0.rate))" } ?? output.status)
                Text("Changes affect playback. Exported audio keeps its original sample rate.")
                Text("Changing the device sample rate may affect other apps using this output.")
            }.font(.system(size: 12)).foregroundStyle(FlowTheme.secondary).fixedSize(horizontal: false, vertical: true)
            HStack {
                if output.isApplying { ProgressView().controlSize(.small); Text("Applying…").font(.system(size: 13)) }
                Spacer()
                Button("Cancel") { dismissWindow(id: "audio-settings") }.buttonStyle(FlowButtonStyle()).keyboardShortcut(.cancelAction)
                Button("Apply") {
                    Task { @MainActor in
                        do { try await output.apply(draft); dismissWindow(id: "audio-settings") }
                        catch { self.error = AppMessages.describe(error) }
                    }
                }.buttonStyle(FlowButtonStyle(primary: true)).keyboardShortcut(.defaultAction).disabled(device == nil)
            }
        }
        .padding(28).frame(width: 520).fixedSize(horizontal: false, vertical: true)
        .foregroundStyle(FlowTheme.text).background(FlowTheme.background)
        .tint(FlowTheme.action).preferredColorScheme(.dark).background(FlowWindowStyle())
        .disabled(output.isApplying)
        .onAppear { output.refresh(); deviceUID = output.preference.deviceUID ?? ""; sampleRate = output.preference.sampleRate ?? 0 }
        .onChange(of: deviceUID) { _, _ in
            if sampleRate != 0, !(device?.sampleRates.contains(sampleRate) ?? false) { sampleRate = 0 }
        }
        .alert("Unable to apply Settings", isPresented: Binding(get: { error != nil }, set: { if !$0 { error = nil } })) {
            Button("OK") { error = nil }
        } message: { Text(error ?? "") }
    }
}
