// Test-only executable: not shipped in Cauces. Exercises real controller + packaged worker.
import AppKit
import Darwin
import Foundation

@main struct SandboxProbe {
 @MainActor static func main() throws {
  func trace(_ text: String) { try? FileHandle.standardError.write(contentsOf: Data((text+"\n").utf8)) }
  trace("start")
  _ = NSApplication.shared
  let fm = FileManager.default, resources = Bundle.main.resourceURL!
  let temporary = fm.temporaryDirectory
  let source = resources.appendingPathComponent("audit-input.wav")
  let output = try PrivateDirectory(parent: temporary, prefix: "Cauces-audit-")
  var address = sockaddr_in(); address.sin_len = UInt8(MemoryLayout<sockaddr_in>.size); address.sin_family = sa_family_t(AF_INET); address.sin_port = UInt16(9).bigEndian; address.sin_addr.s_addr = inet_addr("127.0.0.1")
  let socketFD = socket(AF_INET, SOCK_STREAM, 0)
  let result = withUnsafePointer(to: &address) { $0.withMemoryRebound(to: sockaddr.self, capacity: 1) { Darwin.connect(socketFD, $0, socklen_t(MemoryLayout<sockaddr_in>.size)) } }
  let networkErrno = errno; Darwin.close(socketFD)
  guard result == -1, networkErrno == EPERM else { fatalError("Network not denied: \(result) errno \(networkErrno)") }
  trace("network result=\(result) errno=\(networkErrno)")
  let child = Process(); child.executableURL = Bundle.main.executableURL!.deletingLastPathComponent().appendingPathComponent("network-control"); child.standardOutput = FileHandle.standardError; try child.run(); child.waitUntilExit(); guard child.terminationStatus == 0 else { throw NSError(domain: "ChildNetwork", code: Int(child.terminationStatus)) }
  trace("child network denied")
  let controller = JobController()
  func wait(_ predicate: () -> Bool) {
   let deadline = Date().addingTimeInterval(180)
   while !predicate() && Date() < deadline { RunLoop.current.run(until: Date().addingTimeInterval(0.02)) }
   precondition(predicate(), "Timed out")
  }
  controller.open(source);wait { !controller.state.busy }
  trace("inspect: \(controller.error ?? "ok")")
  precondition(controller.state.canSeparate, controller.error ?? "inspect failed")
#if arch(x86_64)
  precondition(controller.engineArchitecture == "x86_64")
#else
  precondition(controller.engineArchitecture == "arm64")
#endif
  trace("worker architecture: \(controller.engineArchitecture ?? "unknown")")
  controller.separate();wait { !controller.state.busy }
  trace("separate: \(controller.error ?? "ok")")
  precondition(controller.state.canExport, controller.error ?? "separation failed")
  try controller.preview.toggle();controller.preview.pause()
  controller.export(to: output.url);wait { !controller.state.busy }
  precondition(controller.exportDirectory != nil, controller.error ?? "export failed")
  let paths = try fm.contentsOfDirectory(at: controller.exportDirectory!, includingPropertiesForKeys: nil)
  precondition(paths.count == 3)
  controller.separate();controller.cancel();precondition(!controller.state.busy)
  controller.shutdown()
  let pending = JobController()
  let before = Set(try fm.contentsOfDirectory(atPath: temporary.path).filter { $0.hasPrefix("Cauces-input-") })
  pending.open(source); pending.shutdown()
  let after = Set(try fm.contentsOfDirectory(atPath: temporary.path).filter { $0.hasPrefix("Cauces-input-") })
  precondition(before == after, "shutdown left pending input copy")
  print("CAUCES_SANDBOX_PASS network=EPERM inspect=true separation=true playback=true export=3 cancellation=true shutdown=true")
 }
}
