import AVFoundation
import AudioToolbox
import Combine
import Foundation

@MainActor final class PreviewPlayer: ObservableObject {
    @Published private(set) var playing = false
    @Published var position = 0.0
    @Published private(set) var duration = 0.0
    @Published var selected = 0 { didSet { updateVolumes() } }
    let output: AudioOutputSettings
    private var engine = AVAudioEngine()
    private var graphDevice: UInt32?
    private var graphGeneration = 0
    private var configurationObserver: NSObjectProtocol?
    private var nodes: [AVAudioPlayerNode] = []
    private var files: [AVAudioFile] = []
    private var timer: Timer?
    private var startFrame: AVAudioFramePosition = 0

    init(output: AudioOutputSettings? = nil) {
        self.output = output ?? AudioOutputSettings()
        self.output.onWillChange = { [weak self] in self?.pause(); self?.engine.stop() }
        self.output.configureRoute = { [weak self] device in try self?.buildGraph(device: device) }
        self.output.onHardwareChange = { [weak self] message in
            guard let self else { return }
            let wasPlaying = self.playing
            self.pause(); self.engine.stop(); self.graphDevice = nil
            if wasPlaying { self.output.notice = message }
        }
    }
    var ready: Bool { files.count == 4 }
    private func buildGraph(device: UInt32) throws {
        pause(); graphGeneration += 1
        if let observer = configurationObserver { NotificationCenter.default.removeObserver(observer) }
        configurationObserver = nil
        let changingDevice = graphDevice != device
        engine.stop(); nodes.forEach { engine.detach($0) }; nodes.removeAll()
        if changingDevice { engine = AVAudioEngine() }
        else { engine.disconnectNodeOutput(engine.mainMixerNode) }
        graphDevice = nil
        guard let unit = engine.outputNode.audioUnit else { throw OutputSettingsError("The audio output unit is unavailable.") }
        if changingDevice {
            var id = device
            let status = AudioUnitSetProperty(unit, kAudioOutputUnitProperty_CurrentDevice, kAudioUnitScope_Global, 0, &id, UInt32(MemoryLayout<UInt32>.size))
            guard status == noErr else { throw OutputSettingsError("Unable to select the audio output (Core Audio error \(status)).") }
        }
        var actualID: UInt32 = 0, idSize = UInt32(MemoryLayout<UInt32>.size)
        guard AudioUnitGetProperty(unit, kAudioOutputUnitProperty_CurrentDevice, kAudioUnitScope_Global, 0, &actualID, &idSize) == noErr, actualID == device else {
            throw OutputSettingsError("The audio engine did not select the requested output. Choose it again in Settings.")
        }
        let hardwareFormat = engine.outputNode.outputFormat(forBus: 0)
        guard hardwareFormat.sampleRate > 0, hardwareFormat.channelCount > 0 else { throw OutputSettingsError("The selected output has no available playback channels.") }
        for file in files {
            let node = AVAudioPlayerNode(); engine.attach(node)
            engine.connect(node, to: engine.mainMixerNode, format: file.processingFormat); nodes.append(node)
        }
        if !files.isEmpty { engine.connect(engine.mainMixerNode, to: engine.outputNode, format: hardwareFormat) }
        updateVolumes(); graphDevice = device
        let generation = graphGeneration
        configurationObserver = NotificationCenter.default.addObserver(forName: .AVAudioEngineConfigurationChange, object: engine, queue: .main) { [weak self] _ in
            MainActor.assumeIsolated {
                guard let self, self.graphGeneration == generation, !self.output.isApplying else { return }
                let wasPlaying = self.playing
                self.pause(); self.engine.stop(); self.graphDevice = nil; self.output.refresh()
                if wasPlaying { self.output.notice = "The playback engine configuration changed. Playback paused. Check Settings before resuming." }
            }
        }
    }
    func load(original: URL, stems: [URL]) throws {
        clear()
        let opened = try ([original] + stems).map { try AVAudioFile(forReading: $0) }
        guard opened.count == 4, let first = opened.first,
              opened.allSatisfy({ $0.length == first.length && $0.processingFormat.sampleRate == first.processingFormat.sampleRate && $0.processingFormat.channelCount == first.processingFormat.channelCount }) else {
            throw NSError(domain: "Preview", code: 1, userInfo: [NSLocalizedDescriptionKey: "The audio files do not match in duration, sample rate or channel count."])
        }
        files = opened; duration = Double(first.length) / first.processingFormat.sampleRate
        selected = 0; updateVolumes()
    }
    func toggle() throws { if playing { pause() } else { try play() } }
    func play() throws {
        guard ready, duration > 0 else { return }
        let device = try output.playbackDevice()
        if graphDevice != device || nodes.count != files.count { try buildGraph(device: device) }
        if position >= duration { position = 0 }
        let rate = files[0].processingFormat.sampleRate
        startFrame = min(files[0].length - 1, max(0, AVAudioFramePosition((position * rate).rounded())))
        let count = AVAudioFrameCount(files[0].length - startFrame)
        for (node, file) in zip(nodes, files) {
            node.stop(); node.scheduleSegment(file, startingFrame: startFrame, frameCount: count, at: nil)
        }
        try engine.start()
        let at = AVAudioTime(hostTime: mach_absolute_time() + AVAudioTime.hostTime(forSeconds: 0.05))
        nodes.forEach { $0.play(at: at) }; playing = true
        timer?.invalidate()
        timer = Timer.scheduledTimer(withTimeInterval: 0.04, repeats: true) { [weak self] _ in
            Task { @MainActor [weak self] in self?.tick() }
        }
    }
    private func tick() {
        guard playing, let node = nodes.first, let time = node.lastRenderTime,
              let player = node.playerTime(forNodeTime: time) else { return }
        position = min(duration, max(0, Double(startFrame + player.sampleTime) / player.sampleRate))
        if position >= duration - 0.001 { pause(); position = duration }
    }
    func pause() { tickWithoutPause(); nodes.forEach { $0.stop() }; playing = false; timer?.invalidate(); timer = nil }
    private func tickWithoutPause() {
        guard playing, let node = nodes.first, let time = node.lastRenderTime,
              let player = node.playerTime(forNodeTime: time) else { return }
        position = min(duration, max(0, Double(startFrame + player.sampleTime) / player.sampleRate))
    }
    func seek(to seconds: Double) throws {
        let resume = playing; pause(); position = min(duration, max(0, seconds))
        if resume { try play() }
    }
    private func updateVolumes() {
        for (index, node) in nodes.enumerated() { node.volume = index == selected ? 1 : 0 }
    }
    deinit {
        if let observer = configurationObserver { NotificationCenter.default.removeObserver(observer) }
        timer?.invalidate()
    }
    func clear() {
        pause(); engine.stop(); graphDevice = nil; graphGeneration += 1
        if let observer = configurationObserver { NotificationCenter.default.removeObserver(observer); configurationObserver = nil }
        nodes.forEach { engine.detach($0) }; nodes.removeAll(); files.removeAll(); position = 0; duration = 0
    }
}
