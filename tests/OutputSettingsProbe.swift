import AppKit
import AVFoundation
import CoreAudio
import Foundation

@main struct OutputSettingsProbe {
    @MainActor static func main() {
        NSApplication.shared.setActivationPolicy(.prohibited)
        Task { @MainActor in await run(); NSApplication.shared.terminate(nil) }
        NSApplication.shared.run()
    }
    @MainActor static func run() async {
        setbuf(stdout, nil)
        let hardware = CoreAudioOutputHardware()
        do {
            let devices = try hardware.outputDevices()
            let defaultID = try hardware.defaultOutputID()
            print("OUTPUT_INVENTORY " + devices.map { "\($0.id):\($0.name):\($0.rate):\($0.sampleRates)" }.joined(separator: "; "))
            let targetIndex = CommandLine.arguments.firstIndex(of: "--device-id")
            let targetID = targetIndex.flatMap { CommandLine.arguments.count > $0+1 ? UInt32(CommandLine.arguments[$0+1]) : nil }
            guard let device = (targetID == nil ? devices.first(where: { $0.uid.hasPrefix("BuiltInSpeaker") }) ?? devices.first(where: { $0.id == defaultID }) : devices.first(where: { $0.id == targetID })) else { throw OutputSettingsError("No default output for the probe.") }
            if let index = CommandLine.arguments.firstIndex(of: "--restore-rate"), CommandLine.arguments.count > index+1,
               let rate = Double(CommandLine.arguments[index+1]), device.supports(rate) {
                try await hardware.setRate(rate, device: device.id)
                print("HARDWARE_RATE_RESTORED \(rate)"); return
            }
            print("RATE_BASELINE \(device.rate)")
            if CommandLine.arguments.contains("--clock-only") {
                guard let alternative = device.sampleRates.first(where: { [44100.0,48000.0].contains($0) && abs($0-device.rate) > 0.5 }) else { return }
                do {
                    try await hardware.setRate(alternative, device: device.id)
                    try await Task.sleep(nanoseconds: 700_000_000)
                    let held = try hardware.outputDevices().first { $0.id == device.id }!.rate
                    print("CLOCK_ONLY requested=\(alternative) actual=\(held)")
                    try await hardware.setRate(device.rate, device: device.id)
                } catch { try? await hardware.setRate(device.rate, device: device.id); throw error }
                return
            }
            guard CommandLine.arguments.contains("--exercise") else { return }
            let defaults = UserDefaults.standard
            let saved = defaults.data(forKey: "Cauces.AudioOutput.v1")
            defer { if let saved { defaults.set(saved, forKey: "Cauces.AudioOutput.v1") } else { defaults.removeObject(forKey: "Cauces.AudioOutput.v1") } }
            defaults.removeObject(forKey: "Cauces.AudioOutput.v1")
            let output = AudioOutputSettings(hardware: hardware, defaults: defaults)
            let player = PreviewPlayer(output: output)
            let fixture = Bundle.main.resourceURL!.appendingPathComponent("audit-input.wav")
            let file = try AVAudioFile(forReading: fixture)
            let originalDuration = Double(file.length)/file.processingFormat.sampleRate
            let alternative = device.sampleRates.first { [44100.0,48000.0].contains($0) && abs($0-device.rate) > 0.5 }
            do {
                try player.load(original: fixture, stems: [fixture,fixture,fixture])
                player.selected = 2
                if let alternative {
                    do { try await output.apply(OutputPreference(deviceUID: device.uid, sampleRate: alternative)) }
                    catch {
                        guard CommandLine.arguments.contains("--allow-rejection") else { throw error }
                        print("RATE_REJECTED_SAFELY \(alternative): \(error.localizedDescription)")
                        guard output.preference == OutputPreference() else { throw OutputSettingsError("Rejected rate was persisted.") }
                        try await output.apply(OutputPreference(deviceUID: device.uid, sampleRate: device.rate))
                    }
                    let actual = try hardware.outputDevices().first { $0.id == device.id }!.rate
                    let expected = output.preference.sampleRate ?? device.rate
                    guard abs(actual-expected) < 0.5 else { throw OutputSettingsError("Rate not applied: \(actual)") }
                    print("RATE_APPLIED \(actual)")
                    try await Task.sleep(nanoseconds: 500_000_000)
                    let held = try hardware.outputDevices().first { $0.id == device.id }!.rate
                    print("RATE_BEFORE_PLAY \(held)")
                    guard abs(held-expected) < 0.5 else { throw OutputSettingsError("Rate reverted before playback: \(held)") }
                } else { print("RATE_SWITCH_SKIPPED no alternative 44.1/48 kHz supported") }
                try player.seek(to: 2.0); try player.play()
                try await Task.sleep(nanoseconds: 500_000_000)
                guard player.playing else { throw OutputSettingsError("Playback stopped unexpectedly after 0.5 seconds: \(output.notice ?? "no notice")") }; player.pause()
                guard player.position > 2.2 && player.position < 2.8 else { throw OutputSettingsError("Unexpected playback position: \(player.position)") }
                try player.play()
                let cursor = player.position
                try await output.apply(OutputPreference(deviceUID: device.uid, sampleRate: device.rate))
                guard !player.playing && player.position >= cursor-0.01 && player.selected == 2 else { throw OutputSettingsError("Apply did not preserve transport state: \(player.position), \(player.selected), \(player.playing)") }
                guard abs(player.duration-originalDuration) < 1e-9 else { throw OutputSettingsError("Source duration changed.") }
                try player.play(); try await Task.sleep(nanoseconds: 200_000_000); player.pause()
                print("PLAYBACK_SETTINGS_PASS cursor=\(player.position) duration=\(player.duration) source_rate=\(file.processingFormat.sampleRate) selected=\(player.selected) paused_after_apply=true")
                player.clear()
            } catch {
                player.clear()
                try? await hardware.setRate(device.rate, device: device.id)
                throw error
            }
            try await hardware.setRate(device.rate, device: device.id)
            print("HARDWARE_RATE_RESTORED \(device.rate)")
        } catch { fputs("OUTPUT_SETTINGS_PROBE_FAIL \(error.localizedDescription)\n", stderr); exit(1) }
    }
}
