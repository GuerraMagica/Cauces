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
    private var stagingFolders: [PrivateDirectory] = []
    private var exports: [Int: PrivateDirectory] = [:]
    private let ownedWorkspace: PrivateDirectory
    var onEvent: (([String: Any]) -> Void)?
    var onExit: ((Int32) -> Void)?

    init(executable: URL, models: URL, temporaryRoot: URL = FileManager.default.temporaryDirectory) throws {
        ownedWorkspace = try PrivateDirectory(parent: temporaryRoot, prefix: "Cauces-")
        workspace = ownedWorkspace.url
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
        guard pending.count + data.count <= 1048576 else {
            pending.removeAll()
            DispatchQueue.main.async { [weak self] in self?.onExit?(-1); self?.close() }
            return
        }
        pending.append(data)
        while let newline = pending.firstIndex(of: 10) {
            let line = pending.prefix(upTo: newline)
            pending.removeSubrange(...newline)
            guard let event = (try? JSONSerialization.jsonObject(with: line)) as? [String: Any] else { continue }
            DispatchQueue.main.async { [weak self] in
                guard let self, !self.closed else { return }; if let id = event["id"] as? Int, ["exported", "error"].contains(event["type"] as? String ?? ""), let completed = self.exports.removeValue(forKey: id) {
                    self.stagingFolders.removeAll { $0 === completed }
                }
                self.onEvent?(event)
            }
        }
    }
    func send(_ command: [String: Any]) throws {
        guard !closed, process.isRunning else { throw CocoaError(.executableNotLoadable) }
        var prepared = command
        var created: PrivateDirectory?
        if command["cmd"] as? String == "export", let destination = command["destination"] as? String {
            let directory = try PrivateDirectory(parent: URL(fileURLWithPath: destination), prefix: ".export-")
            created = directory; stagingFolders.append(directory); if let id = command["id"] as? Int { exports[id] = directory }; prepared["staging"] = directory.url.path
        }
        do {
            var data = try JSONSerialization.data(withJSONObject: prepared); data.append(10)
            try input.fileHandleForWriting.write(contentsOf: data)
        } catch { if let created { stagingFolders.removeAll { $0 === created }; exports = exports.filter { $0.value !== created } }; throw error }
    }
    func close() {
        guard !closed else { return }; closed = true
        onEvent = nil; onExit = nil
        output.fileHandleForReading.readabilityHandler = nil
        diagnostics.fileHandleForReading.readabilityHandler = nil
        let oldProcess = process
        if oldProcess.isRunning { Darwin.kill(oldProcess.processIdentifier, SIGKILL) }
        try? input.fileHandleForWriting.close()
        // Complete cleanup before returning: applicationWillTerminate does not
        // keep asynchronous GCD cleanup alive after the app exits. SIGKILL makes
        // this independent of a potentially long inference call.
        if oldProcess.processIdentifier > 0 { oldProcess.waitUntilExit() }
        exports.removeAll(); stagingFolders.removeAll()
        ownedWorkspace.cleanup()
    }
    deinit { close() }
}
