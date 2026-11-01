import CoreAudio
import Combine
import Foundation

struct OutputSettingsError: LocalizedError, CustomNSError {
    static var errorDomain: String { "Cauces.Output" }
    var errorCode: Int { 1 }
    var errorUserInfo: [String: Any] { [NSLocalizedDescriptionKey: message] }
    let message: String
    init(_ message: String) { self.message = message }
    var errorDescription: String? { message }
}

struct OutputPreference: Codable, Equatable {
    var deviceUID: String? = nil
    var sampleRate: Double? = nil // nil follows the device without changing its clock.
}

struct OutputDevice: Identifiable {
    let id: UInt32
    let uid: String
    let name: String
    var rate: Double
    let ranges: [ClosedRange<Double>]
    let canSetRate: Bool
    func supports(_ rate: Double) -> Bool {
        rate.isFinite && rate > 0 && ranges.contains { $0.contains(rate) }
    }
    var sampleRates: [Double] {
        let common: [Double] = [8000, 16000, 22050, 24000, 32000, 44100, 48000, 64000, 88200, 96000, 176400, 192000, 352800, 384000]
        let candidates = common + [rate] + ranges.flatMap { [$0.lowerBound, $0.upperBound] }
        return Set(candidates.filter { supports($0) && (canSetRate || abs($0-rate) < 0.5) }).sorted()
    }
}

@MainActor protocol AudioOutputHardware: AnyObject {
    func outputDevices() throws -> [OutputDevice]
    func defaultOutputID() throws -> UInt32
    func setRate(_ rate: Double, device: UInt32) async throws
    func observe(device: UInt32?, change: @escaping () -> Void)
}

@MainActor final class AudioOutputSettings: ObservableObject {
    @Published private(set) var devices: [OutputDevice] = []
    @Published private(set) var preference: OutputPreference
    @Published private(set) var defaultID: UInt32 = 0
    @Published private(set) var status = ""
    @Published private(set) var isApplying = false
    @Published var notice: String?
    var onWillChange: (() -> Void)?
    var configureRoute: ((UInt32) throws -> Void)?
    var onHardwareChange: ((String) -> Void)?
    private let hardware: AudioOutputHardware
    private let defaults: UserDefaults
    private let preferenceKey = "Cauces.AudioOutput.v1"
    private var watchedID: UInt32?
    private var observing = false
    private var observedDevice: (id: UInt32, rate: Double)?

    init(hardware: AudioOutputHardware? = nil, defaults: UserDefaults = .standard) {
        self.hardware = hardware ?? CoreAudioOutputHardware(); self.defaults = defaults
        preference = defaults.data(forKey: preferenceKey).flatMap { try? JSONDecoder().decode(OutputPreference.self, from: $0) } ?? OutputPreference()
        refresh()
    }
    var currentDevice: OutputDevice? { resolve(preference, in: devices) }
    func device(for uid: String?) -> OutputDevice? { resolve(OutputPreference(deviceUID: uid), in: devices) }
    private func resolve(_ value: OutputPreference, in inventory: [OutputDevice]) -> OutputDevice? {
        if let uid = value.deviceUID { return inventory.first { $0.uid == uid } }
        return inventory.first { $0.id == defaultID }
    }
    func refresh() {
        do {
            devices = try hardware.outputDevices(); defaultID = try hardware.defaultOutputID()
            let device = currentDevice
            status = device.map { "Current: \($0.name) · \(Self.rateLabel($0.rate))" } ?? "The selected output is unavailable. Connect it or choose another output."
            if !isApplying {
                if let previous = observedDevice, device?.id != previous.id || abs((device?.rate ?? 0) - previous.rate) > 0.5 {
                    onHardwareChange?(device == nil ? "The selected audio output was disconnected. Playback paused. Choose an available output in Settings." : "The audio output configuration changed. Playback paused. Check Settings before resuming.")
                }
                observedDevice = device.map { ($0.id, $0.rate) }
            }
            if !observing || watchedID != device?.id {
                observing = true; watchedID = device?.id
                hardware.observe(device: watchedID) { [weak self] in self?.refresh() }
            }
        } catch {
            devices = []; defaultID = 0
            status = error.localizedDescription
            if !isApplying, observedDevice != nil {
                observedDevice = nil
                onHardwareChange?("The audio output could not be queried. Playback paused. Check Settings.")
            }
        }
    }
    private func validate(_ value: OutputPreference) throws -> OutputDevice {
        guard let device = resolve(value, in: devices) else { throw OutputSettingsError("The selected output is unavailable. Connect it or choose another output.") }
        if let rate = value.sampleRate {
            guard device.supports(rate) else { throw OutputSettingsError("This sample rate is not supported by the selected output.") }
            guard device.canSetRate || abs(device.rate-rate) < 0.5 else { throw OutputSettingsError("This output controls its sample rate externally. Use its control panel or choose Device default.") }
        }
        return device
    }
    func playbackDevice() throws -> UInt32 {
        guard !isApplying else { throw OutputSettingsError("Wait for the output change to finish.") }
        refresh()
        let device = try validate(preference)
        if let desired = preference.sampleRate, abs(desired-device.rate) > 0.5 {
            throw OutputSettingsError("The output sample rate changed. Open Settings and apply your selected sample rate before playing.")
        }
        return device.id
    }
    func apply(_ value: OutputPreference) async throws {
        guard !isApplying else { throw OutputSettingsError("Wait for the output change to finish.") }
        refresh()
        let device = try validate(value)
        let previousDevice = currentDevice
        isApplying = true
        onWillChange?()
        var attemptedRateChange = false
        defer { isApplying = false; refresh() }
        do {
            try configureRoute?(device.id)
            if let desired = value.sampleRate, abs(device.rate-desired) > 0.5 {
                attemptedRateChange = true
                try await hardware.setRate(desired, device: device.id)
                try await waitForRate(desired, device: device.id)
            }
            try configureRoute?(device.id)
            if let desired = value.sampleRate { try await waitForRate(desired, device: device.id) }
            guard let finalDevice = try hardware.outputDevices().first(where: { $0.id == device.id }) else {
                throw OutputSettingsError("The output was disconnected while applying Settings.")
            }
            if value.deviceUID == nil, try hardware.defaultOutputID() != device.id {
                throw OutputSettingsError("The system output changed while applying Settings. Choose the output again.")
            }
            preference = value
            defaults.set(try JSONEncoder().encode(value), forKey: preferenceKey)
            notice = nil
            // Suppress the expected refresh notification from our own Apply.
            observedDevice = (device.id, finalDevice.rate)
        } catch {
            var rollbackProblems: [String] = []
            if attemptedRateChange {
                do { try await hardware.setRate(device.rate, device: device.id); try await waitForRate(device.rate, device: device.id) }
                catch { rollbackProblems.append("The previous hardware sample rate could not be restored: \(error.localizedDescription)") }
            }
            if let previousDevice {
                do { try configureRoute?(previousDevice.id) }
                catch { rollbackProblems.append("The previous output route could not be restored: \(error.localizedDescription)") }
            }
            throw OutputSettingsError(([error.localizedDescription] + rollbackProblems).joined(separator: "\n"))
        }
    }
    private func waitForRate(_ rate: Double, device: UInt32) async throws {
        var stableReadings = 0
        for _ in 0..<100 {
            guard let actual = try hardware.outputDevices().first(where: { $0.id == device }) else {
                throw OutputSettingsError("The output was disconnected while applying Settings.")
            }
            stableReadings = abs(actual.rate-rate) < 0.5 ? stableReadings + 1 : 0
            if stableReadings >= 15 { return } // Confirm a stable clock, not a provisional HAL value.
            try await Task.sleep(nanoseconds: 20_000_000)
        }
        throw OutputSettingsError("The output did not retain the requested sample rate. Another app, driver or clock may control it. Check its control panel or choose Device default.")
    }
    static func rateLabel(_ rate: Double) -> String { String(format: "%.0f Hz", rate) }
}

/// HAL access stays separate from preference/transaction logic for deterministic failure tests.
@MainActor final class CoreAudioOutputHardware: AudioOutputHardware {
    private var listeners: [(AudioObjectID, AudioObjectPropertyAddress, AudioObjectPropertyListenerBlock)] = []
    private func address(_ selector: AudioObjectPropertySelector, scope: AudioObjectPropertyScope = kAudioObjectPropertyScopeGlobal) -> AudioObjectPropertyAddress {
        AudioObjectPropertyAddress(mSelector: selector, mScope: scope, mElement: kAudioObjectPropertyElementMain)
    }
    private func check(_ status: OSStatus, _ action: String) throws {
        guard status == noErr else { throw OutputSettingsError("\(action) (Core Audio error \(status)).") }
    }
    private func value<T>(_ object: AudioObjectID, _ selector: AudioObjectPropertySelector, initial: T) throws -> T {
        var result = initial, a = address(selector), size = UInt32(MemoryLayout<T>.size)
        try withUnsafeMutablePointer(to: &result) { pointer in
            try check(AudioObjectGetPropertyData(object, &a, 0, nil, &size, pointer), "Unable to read the audio output")
        }
        return result
    }
    private func string(_ object: AudioObjectID, _ selector: AudioObjectPropertySelector) throws -> String {
        var result: Unmanaged<CFString>?, a = address(selector), size = UInt32(MemoryLayout<CFString?>.size)
        try check(AudioObjectGetPropertyData(object, &a, 0, nil, &size, &result), "Unable to read the audio output name")
        guard let result else { throw OutputSettingsError("The audio output returned an empty identifier.") }
        return result.takeRetainedValue() as String
    }
    private func array<T>(_ object: AudioObjectID, _ selector: AudioObjectPropertySelector, type: T.Type) throws -> [T] {
        var a = address(selector), size: UInt32 = 0
        try check(AudioObjectGetPropertyDataSize(object, &a, 0, nil, &size), "Unable to query audio devices")
        guard size <= 1_048_576, Int(size) % MemoryLayout<T>.stride == 0 else { throw OutputSettingsError("The audio device returned an invalid property size.") }
        let count = Int(size) / MemoryLayout<T>.stride
        if count == 0 { return [] }
        let buffer = UnsafeMutablePointer<T>.allocate(capacity: count); defer { buffer.deallocate() }
        try check(AudioObjectGetPropertyData(object, &a, 0, nil, &size, buffer), "Unable to read audio devices")
        return Array(UnsafeBufferPointer(start: buffer, count: min(count, Int(size)/MemoryLayout<T>.stride)))
    }
    private func outputChannels(_ id: AudioObjectID) throws -> UInt32 {
        var a = address(kAudioDevicePropertyStreamConfiguration, scope: kAudioDevicePropertyScopeOutput), size: UInt32 = 0
        try check(AudioObjectGetPropertyDataSize(id, &a, 0, nil, &size), "Unable to inspect the output channels")
        guard size >= MemoryLayout<AudioBufferList>.size, size < 1_048_576 else { return 0 }
        let data = UnsafeMutableRawPointer.allocate(byteCount: Int(size), alignment: MemoryLayout<AudioBufferList>.alignment)
        defer { data.deallocate() }
        try check(AudioObjectGetPropertyData(id, &a, 0, nil, &size, data), "Unable to inspect the output channels")
        let list = UnsafeMutableAudioBufferListPointer(data.assumingMemoryBound(to: AudioBufferList.self))
        return list.reduce(0) { $0 + $1.mNumberChannels }
    }
    func outputDevices() throws -> [OutputDevice] {
        let ids = try array(AudioObjectID(kAudioObjectSystemObject), kAudioHardwarePropertyDevices, type: AudioObjectID.self)
        return ids.compactMap { id in
            // A device may disappear between enumeration and property reads.
            do {
                guard try outputChannels(id) > 0, try value(id, kAudioDevicePropertyDeviceIsAlive, initial: UInt32(0)) != 0 else { return nil }
                let uid = try string(id, kAudioDevicePropertyDeviceUID)
                let name = try string(id, kAudioObjectPropertyName)
                let rate = try value(id, kAudioDevicePropertyNominalSampleRate, initial: Double(0))
                guard rate.isFinite, rate > 0 else { return nil }
                let raw = try array(id, kAudioDevicePropertyAvailableNominalSampleRates, type: AudioValueRange.self)
                let ranges = raw.compactMap { r -> ClosedRange<Double>? in
                    guard r.mMinimum.isFinite, r.mMaximum.isFinite, r.mMinimum > 0, r.mMaximum >= r.mMinimum else { return nil }
                    return r.mMinimum...r.mMaximum
                }
                var a = address(kAudioDevicePropertyNominalSampleRate), writable = DarwinBoolean(false)
                let status = AudioObjectIsPropertySettable(id, &a, &writable)
                return OutputDevice(id: id, uid: uid, name: name, rate: rate, ranges: ranges.isEmpty ? [rate...rate] : ranges, canSetRate: status == noErr && writable.boolValue)
            } catch { return nil }
        }.sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
    }
    func defaultOutputID() throws -> UInt32 {
        try value(AudioObjectID(kAudioObjectSystemObject), kAudioHardwarePropertyDefaultOutputDevice, initial: UInt32(0))
    }
    func setRate(_ rate: Double, device: UInt32) async throws {
        let current = try value(device, kAudioDevicePropertyNominalSampleRate, initial: Double(0))
        if abs(current-rate) < 0.5 { return }
        var a = address(kAudioDevicePropertyNominalSampleRate), requested = rate
        var acknowledged = false
        let listener: AudioObjectPropertyListenerBlock = { _, _ in
            MainActor.assumeIsolated { acknowledged = true }
        }
        try check(AudioObjectAddPropertyListenerBlock(device, &a, .main, listener), "Unable to observe the output clock change")
        defer { AudioObjectRemovePropertyListenerBlock(device, &a, .main, listener) }
        try check(AudioObjectSetPropertyData(device, &a, 0, nil, UInt32(MemoryLayout<Double>.size), &requested), "Unable to set the output sample rate")
        for _ in 0..<100 {
            if acknowledged {
                let actual = try value(device, kAudioDevicePropertyNominalSampleRate, initial: Double(0))
                if abs(actual-rate) < 0.5 { return }
            }
            try await Task.sleep(nanoseconds: 20_000_000)
        }
        throw OutputSettingsError("The audio driver did not confirm the requested sample rate. Check its clock or control panel.")
    }
    func observe(device: UInt32?, change: @escaping () -> Void) {
        removeListeners()
        var properties: [(AudioObjectID, AudioObjectPropertySelector)] = [(AudioObjectID(kAudioObjectSystemObject), kAudioHardwarePropertyDevices), (AudioObjectID(kAudioObjectSystemObject), kAudioHardwarePropertyDefaultOutputDevice)]
        if let device { properties += [(device, kAudioDevicePropertyNominalSampleRate), (device, kAudioDevicePropertyDeviceIsAlive)] }
        for (id, selector) in properties {
            var a = address(selector)
            let block: AudioObjectPropertyListenerBlock = { _, _ in Task { @MainActor in change() } }
            if AudioObjectAddPropertyListenerBlock(id, &a, .main, block) == noErr { listeners.append((id, a, block)) }
        }
    }
    private func removeListeners() {
        for (id, address, block) in listeners { var a = address; AudioObjectRemovePropertyListenerBlock(id, &a, .main, block) }
        listeners.removeAll()
    }
    deinit {
        for (id, address, block) in listeners { var a = address; AudioObjectRemovePropertyListenerBlock(id, &a, .main, block) }
    }
}
