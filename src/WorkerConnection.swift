import Foundation
import Darwin

/// One persistent, restartable process. All public methods are called on the main thread.
final class WorkerConnection {
    let workspace: URL
    private let process = Process()
    private let input = Pipe()
    private let output = Pipe()
    private let diagnostics = Pipe()
    private let queue = DispatchQueue(label: "dialogue.worker.output")
    private var pending = Data()
    private var closed = false
    private var stagingFolders: [URL] = []
    var onEvent: (([String: Any]) -> Void)?
    var onExit: ((Int32) -> Void)?

    init(executable: URL, models: URL, temporaryRoot: URL = FileManager.default.temporaryDirectory) throws {
        workspace = temporaryRoot.appendingPathComponent("DialogueSeparator-\(UUID().uuidString)", isDirectory: true)
        try FileManager.default.createDirectory(at: workspace, withIntermediateDirectories: false, attributes: [.posixPermissions: 0o700])
        process.executableURL = executable
        process.arguments = ["--models", models.path, "--threads", "4"]
        process.standardInput = input; process.standardOutput = output; process.standardError = diagnostics
        output.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            guard !data.isEmpty, let self else { return }
            self.queue.async { [weak self] in self?.consume(data) }
        }
        diagnostics.fileHandleForReading.readabilityHandler = { handle in _ = handle.availableData }
        process.terminationHandler = { [weak self] proc in
            DispatchQueue.main.async { [weak self] in
                guard let self, !self.closed else { return }
                self.onExit?(proc.terminationStatus)
            }
        }
        do { try process.run() }
        catch { close(); throw error }
    }
    private func consume(_ data: Data) {
        pending.append(data)
        while let newline = pending.firstIndex(of: 10) {
            let line = pending.prefix(upTo: newline)
            pending.removeSubrange(...newline)
            guard let event = (try? JSONSerialization.jsonObject(with: line)) as? [String: Any] else { continue }
            DispatchQueue.main.async { [weak self] in
                guard let self, !self.closed else { return }; self.onEvent?(event)
            }
        }
    }
    func send(_ command: [String: Any]) throws {
        guard !closed, process.isRunning else { throw CocoaError(.executableNotLoadable) }
        var prepared = command
        var created: URL?
        if command["cmd"] as? String == "export", let destination = command["destination"] as? String {
            var pattern = Array((URL(fileURLWithPath: destination).appendingPathComponent(".export-XXXXXX").path).utf8CString)
            let success = pattern.withUnsafeMutableBufferPointer { mkdtemp($0.baseAddress!) != nil }
            guard success else { throw NSError(domain: NSPOSIXErrorDomain, code: Int(errno), userInfo: [NSLocalizedDescriptionKey: "No se puede crear la exportación; comprueba espacio y permisos."]) }
            let url = URL(fileURLWithPath: String(cString: pattern))
            created = url; stagingFolders.append(url); prepared["staging"] = url.path
        }
        do {
            var data = try JSONSerialization.data(withJSONObject: prepared); data.append(10)
            try input.fileHandleForWriting.write(contentsOf: data)
        } catch { if let created { try? FileManager.default.removeItem(at: created) }; throw error }
    }
    func close() {
        guard !closed else { return }; closed = true
        onEvent = nil; onExit = nil
        output.fileHandleForReading.readabilityHandler = nil
        diagnostics.fileHandleForReading.readabilityHandler = nil
        let oldProcess = process, oldWorkspace = workspace, oldStaging = stagingFolders
        if oldProcess.isRunning { Darwin.kill(oldProcess.processIdentifier, SIGKILL) }
        try? input.fileHandleForWriting.close()
        // Complete cleanup before returning: applicationWillTerminate does not
        // keep asynchronous GCD cleanup alive after the app exits. SIGKILL makes
        // this independent of a potentially long inference call.
        if oldProcess.processIdentifier > 0 { oldProcess.waitUntilExit() }
        try? FileManager.default.removeItem(at: oldWorkspace)
        for folder in oldStaging { try? FileManager.default.removeItem(at: folder) }
    }
    deinit { close() }
}
