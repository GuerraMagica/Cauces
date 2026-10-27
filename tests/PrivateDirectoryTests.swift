import Foundation
@main struct PrivateDirectoryTests {
 static func main() throws {
  let fm = FileManager.default
  let root = fm.temporaryDirectory.appendingPathComponent("cauces-owned-test-\(UUID().uuidString)")
  try fm.createDirectory(at: root, withIntermediateDirectories: false)
  defer { try? fm.removeItem(at: root) }
  var owned: PrivateDirectory? = try PrivateDirectory(parent: root, prefix: "owned-")
  let path = owned!.url
  try fm.moveItem(at: path, to: root.appendingPathComponent("retired"))
  try fm.createDirectory(at: path, withIntermediateDirectories: false)
  let marker = path.appendingPathComponent("keep")
  try Data("synthetic".utf8).write(to: marker)
  owned = nil
  precondition(fm.fileExists(atPath: marker.path), "cleanup deleted replacement data")
  let input = root.appendingPathComponent("input.wav")
  try Data([0,1,2,3]).write(to: input)
  let export = try PrivateDirectory(parent: root, prefix: ".export-")
  try export.copy(source: input, name: "voice.wav")
  let final = try export.publish(name: "result")
  let copied = try Data(contentsOf: final.appendingPathComponent("voice.wav"))
  precondition(copied == Data([0,1,2,3]))
  do { _ = try PrivateDirectory(parent: root, prefix: "../invalid"); preconditionFailure("accepted traversal") } catch {}
  let collision = try PrivateDirectory(parent: root, prefix: ".export-")
  do { _ = try collision.publish(name: "result"); preconditionFailure("overwrote export") } catch {}
  let cancelled = try PrivateDirectory(parent: root, prefix: "cancel-")
  cancelled.cancel()
  do { try cancelled.copy(source: input, name: "copy.wav"); preconditionFailure("copy ignored cancellation") } catch {}
  print("Swift private cleanup, verified copy, traversal and collision protection passed")
 }
}
