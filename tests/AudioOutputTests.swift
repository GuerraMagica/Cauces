import Foundation

@MainActor final class FakeOutputHardware: AudioOutputHardware {
    var devices = [OutputDevice(id: 10, uid: "speakers", name: "Speakers", rate: 48000, ranges: [44100...48000], canSetRate: true),
                   OutputDevice(id: 20, uid: "interface", name: "Interface", rate: 48000, ranges: [48000...96000], canSetRate: true)]
    var defaultID: UInt32 = 10
    var rejectRate: Double?
    var queryFails = false
    var callback: (() -> Void)?
    func outputDevices() throws -> [OutputDevice] {
        if queryFails { throw OutputSettingsError("Query failed.") }; return devices
    }
    func defaultOutputID() throws -> UInt32 { defaultID }
    func setRate(_ rate: Double, device: UInt32) async throws {
        if rate == rejectRate { throw OutputSettingsError("Hardware refused the sample rate.") }
        guard let i = devices.firstIndex(where: { $0.id == device }) else { throw OutputSettingsError("Disconnected.") }
        devices[i].rate = rate
    }
    func observe(device: UInt32?, change: @escaping () -> Void) { callback = change }
}

@main struct AudioOutputTests {
    @MainActor static func main() async throws {
        let suite = "Cauces.OutputTests.\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: suite)!
        defer { defaults.removePersistentDomain(forName: suite) }
        let hw = FakeOutputHardware()
        let settings = AudioOutputSettings(hardware: hw, defaults: defaults)
        func checkDevice(_ id: UInt32, _ settings: AudioOutputSettings) throws {
            let actual = try settings.playbackDevice(); precondition(actual == id)
        }
        try checkDevice(10, settings)
        let chosen = OutputPreference(deviceUID: "interface", sampleRate: 96000)
        try await settings.apply(chosen)
        precondition(settings.preference == chosen && hw.devices[1].rate == 96000)
        let reopened = AudioOutputSettings(hardware: hw, defaults: defaults)
        precondition(reopened.preference == chosen); try checkDevice(20, reopened)
        for bad in [Double.nan, Double.infinity, -1, 0, 44100] {
            do { try await settings.apply(OutputPreference(deviceUID: "interface", sampleRate: bad)); fatalError("Invalid rate accepted") }
            catch { precondition(settings.preference == chosen && hw.devices[1].rate == 96000) }
        }
        do { try await settings.apply(OutputPreference(deviceUID: "missing", sampleRate: nil)); fatalError("Missing output accepted") }
        catch { precondition(settings.preference == chosen) }
        hw.rejectRate = 48000
        do { try await settings.apply(OutputPreference(deviceUID: "interface", sampleRate: 48000)); fatalError("Refusal accepted") }
        catch { precondition(settings.preference == chosen && hw.devices[1].rate == 96000) }
        hw.rejectRate = nil
        settings.configureRoute = { id in if id == 10 { throw OutputSettingsError("Route failed.") } }
        do { try await settings.apply(OutputPreference(deviceUID: "speakers", sampleRate: 44100)); fatalError("Route failure accepted") }
        catch { precondition(settings.preference == chosen && hw.devices[0].rate == 48000) }
        var interruptions = 0
        settings.onHardwareChange = { _ in interruptions += 1 }
        hw.devices[1].rate = 48000; settings.refresh()
        precondition(interruptions == 1)
        do { _ = try settings.playbackDevice(); fatalError("External rate change ignored") } catch {}
        hw.devices.removeLast(); settings.refresh()
        precondition(interruptions == 2)
        do { _ = try settings.playbackDevice(); fatalError("Silently fell back to speakers") } catch {}
        settings.configureRoute = nil
        try await settings.apply(OutputPreference(deviceUID: nil, sampleRate: nil))
        try checkDevice(10, settings)
        hw.devices.append(OutputDevice(id: 30, uid: "other", name: "Other", rate: 48000, ranges: [48000...48000], canSetRate: false))
        settings.refresh(); precondition(interruptions == 2)
        hw.defaultID = 30; settings.refresh(); precondition(interruptions == 3)
        try checkDevice(30, settings)
        do { try await settings.apply(OutputPreference(deviceUID: "other", sampleRate: 96000)); fatalError("Read-only rate accepted") } catch {}
        precondition(settings.devices.first(where: { $0.id == 10 })!.sampleRates.contains(44100))
        hw.queryFails = true
        do { _ = try settings.playbackDevice(); fatalError("A stale cached output was used after hardware query failure") } catch {}
        precondition(settings.devices.isEmpty)
        hw.queryFails = false; settings.refresh(); try checkDevice(30, settings)
        var blockedDuringApply = false
        settings.onWillChange = {
            do { _ = try settings.playbackDevice() } catch { blockedDuringApply = true }
        }
        try await settings.apply(OutputPreference(deviceUID: nil, sampleRate: nil))
        precondition(blockedDuringApply, "Playback was allowed during Apply")
        let previousPreference = settings.preference
        var routeCalls = 0
        settings.configureRoute = { id in
            if id == 10 { routeCalls += 1; if routeCalls == 2 { hw.devices[0].rate = 48000 } }
        }
        do { try await settings.apply(OutputPreference(deviceUID: "speakers", sampleRate: 44100)); fatalError("A reverted clock was persisted") }
        catch { precondition(settings.preference == previousPreference && hw.devices[0].rate == 48000) }
        settings.configureRoute = nil
        var callsBeforeFailure = 0
        settings.configureRoute = { id in
            if id == 10 { callsBeforeFailure += 1; if callsBeforeFailure == 2 { throw OutputSettingsError("Second route failed.") } }
        }
        do { try await settings.apply(OutputPreference(deviceUID: "speakers", sampleRate: 44100)); fatalError("Second route failure was ignored") }
        catch { precondition(settings.preference == previousPreference && hw.devices[0].rate == 48000 && callsBeforeFailure == 2) }
        let followHardware = FakeOutputHardware()
        let follow = AudioOutputSettings(hardware: followHardware, defaults: defaults)
        var followInterruptions = 0
        follow.onHardwareChange = { _ in followInterruptions += 1 }
        follow.configureRoute = { _ in followHardware.devices[0].rate = 44100 }
        try await follow.apply(OutputPreference())
        precondition(followHardware.devices[0].rate == 44100 && follow.preference.sampleRate == nil && followInterruptions == 0)
        print("Output settings: UID/default routing, persistence, invalid rates, rollback, external changes and disconnect passed")
    }
}
