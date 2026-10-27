import Foundation

@main struct WorkerConnectionTests {
    static func main() throws {
        let root = URL(fileURLWithPath: CommandLine.arguments[1])
        let models = URL(fileURLWithPath: CommandLine.arguments[2])
        let fixtures = URL(fileURLWithPath: CommandLine.arguments[3])
        let binary = root.appendingPathComponent("build/arm64/dialogue-worker")
        let temporary = root.appendingPathComponent("build/transport-tests-\(UUID().uuidString)")
        try FileManager.default.createDirectory(at: temporary, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: temporary) }
        var events: [[String: Any]] = []
        func wait(_ predicate: () -> Bool) {
            let deadline = Date().addingTimeInterval(15)
            while !predicate() && Date() < deadline { RunLoop.current.run(until: Date().addingTimeInterval(0.02)) }
            precondition(predicate(), "Timed out waiting for real worker")
        }
        let worker = try WorkerConnection(executable: binary, models: models, temporaryRoot: temporary)
        worker.onEvent = { events.append($0) }
        wait { events.contains { $0["type"] as? String == "ready" } }
        try worker.send(["cmd":"separate","source":fixtures.appendingPathComponent("chunk8_exact.wav").path,"workspace":worker.workspace.path,"id":1])
        wait { events.contains { ($0["stage"] as? String) == "Separando voces" } }
        worker.close()
        wait { !FileManager.default.fileExists(atPath: worker.workspace.path) }
        events.removeAll()
        let retry = try WorkerConnection(executable: binary, models: models, temporaryRoot: temporary)
        retry.onEvent = { events.append($0) }
        try retry.send(["cmd":"separate","source":fixtures.appendingPathComponent("signed_zero.wav").path,"workspace":retry.workspace.path,"id":2])
        wait { events.contains { $0["type"] as? String == "result" } }
        let readOnly = temporary.appendingPathComponent("read-only")
        try FileManager.default.createDirectory(at: readOnly, withIntermediateDirectories: false, attributes: [.posixPermissions: 0o500])
        do {
            try retry.send(["cmd":"export","destination":readOnly.path,"id":3])
            preconditionFailure("Accepted a destination without write permission")
        } catch {}
        try FileManager.default.setAttributes([.posixPermissions: 0o700], ofItemAtPath: readOnly.path)
        let destination = temporary.appendingPathComponent("export-cancel")
        try FileManager.default.createDirectory(at: destination, withIntermediateDirectories: false)
        // Extend a test-owned preview sparsely so the real copy/hash stays in
        // progress long enough to exercise cancellation, without a mock worker.
        let result = events.first { $0["type"] as? String == "result" }!
        let firstStem = (result["stems"] as! [String])[0]
        let testOutput = try FileHandle(forWritingTo: URL(fileURLWithPath: firstStem))
        try testOutput.truncate(atOffset: 256 * 1024 * 1024); try testOutput.close()
        try retry.send(["cmd":"export","destination":destination.path,"id":3])
        // The client owns the staging directory before sending a command, so even
        // an immediate process kill cannot race ahead of cleanup registration.
        let staging = try FileManager.default.contentsOfDirectory(at: destination, includingPropertiesForKeys: nil).filter { $0.lastPathComponent.hasPrefix(".export-") }
        precondition(staging.count == 1, "Export staging was not registered before command dispatch")
        retry.close()
        precondition(!FileManager.default.fileExists(atPath: retry.workspace.path), "Shutdown returned before cleanup completed")
        precondition(staging.allSatisfy { !FileManager.default.fileExists(atPath: $0.path) }, "App termination could leave export temporaries")
        wait { !FileManager.default.fileExists(atPath: retry.workspace.path) }
        wait { staging.allSatisfy { !FileManager.default.fileExists(atPath: $0.path) } }
        print("Real worker cancellation, cleanup and retry passed")
    }
}
