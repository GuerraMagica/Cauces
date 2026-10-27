import AVFoundation
import Combine
import Foundation

@MainActor final class PreviewPlayer: ObservableObject {
    @Published private(set) var playing = false
    @Published var position = 0.0
    @Published private(set) var duration = 0.0
    @Published var selected = 0 { didSet { updateVolumes() } }
    private let engine = AVAudioEngine()
    private var nodes: [AVAudioPlayerNode] = []
    private var files: [AVAudioFile] = []
    private var timer: Timer?
    private var startFrame: AVAudioFramePosition = 0

    var ready: Bool { files.count == 4 }
    func load(original: URL, stems: [URL]) throws {
        clear()
        let opened = try ([original] + stems).map { try AVAudioFile(forReading: $0) }
        guard opened.count == 4, let first = opened.first,
              opened.allSatisfy({ $0.length == first.length && $0.processingFormat.sampleRate == first.processingFormat.sampleRate && $0.processingFormat.channelCount == first.processingFormat.channelCount }) else {
            throw NSError(domain: "Preview", code: 1, userInfo: [NSLocalizedDescriptionKey: "Los stems no coinciden en duración, sample rate o canales."])
        }
        files = opened; duration = Double(first.length) / first.processingFormat.sampleRate
        for file in files {
            let node = AVAudioPlayerNode(); engine.attach(node)
            engine.connect(node, to: engine.mainMixerNode, format: file.processingFormat); nodes.append(node)
        }
        selected = 0; updateVolumes()
    }
    func toggle() throws { if playing { pause() } else { try play() } }
    func play() throws {
        guard ready, duration > 0 else { return }
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
    func clear() {
        pause(); engine.stop()
        nodes.forEach { engine.detach($0) }; nodes.removeAll(); files.removeAll(); position = 0; duration = 0
    }
}
