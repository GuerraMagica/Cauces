import Foundation
@main struct LocalFilePolicyTests {
 static func main() throws {
  let root = FileManager.default.temporaryDirectory
  try LocalFilePolicy.requireLocal(root)
  for path in ["/Users/example/Library/CloudStorage/provider/session.wav", "/Users/example/Library/Mobile Documents/session.wav", "/Users/example/Dropbox/session.wav", "/Users/example/MEGA/session.wav", "/Users/example/local/file.icloud"] {
   do { try LocalFilePolicy.requireLocal(URL(fileURLWithPath: path)); preconditionFailure("accepted cloud path: \(path)") } catch {}
  }
  let link = root.appendingPathComponent("cauces-policy-\(UUID().uuidString)")
  try FileManager.default.createSymbolicLink(atPath: link.path, withDestinationPath: "/Users/example/Library/CloudStorage/provider")
  defer { try? FileManager.default.removeItem(at: link) }
  do { try LocalFilePolicy.requireLocal(link); preconditionFailure("accepted unresolved cloud link") } catch {}
  print("Local volume accepted; known cloud roots, placeholders and missing/symlink paths rejected")
 }
}
