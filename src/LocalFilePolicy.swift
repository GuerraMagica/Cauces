import Foundation
import Darwin

/// Reject recognized cloud providers before reading file content. Other apps' sync
/// configuration is outside Cauces: users must choose a genuinely unsynced folder.
enum LocalFilePolicy {
    static func requireLocal(_ url: URL) throws {
        guard url.isFileURL else { throw denied() }
        func cloudPath(_ candidate: URL) -> Bool {
            let components = candidate.standardizedFileURL.pathComponents.map { $0.lowercased() }
            return components.contains { ["cloudstorage", "mobile documents", "dropbox", "mega", "megasync"].contains($0) || $0.hasPrefix("onedrive") || $0.hasPrefix("googledrive") || $0.hasSuffix(".icloud") }
        }
        guard !cloudPath(url) else { throw denied() }
        let resolved = url.resolvingSymlinksInPath()
        guard !cloudPath(resolved) else { throw denied() }
        var st = stat()
        guard lstat(resolved.path, &st) == 0, (st.st_mode & S_IFMT) != S_IFLNK,
              (st.st_flags & UInt32(SF_DATALESS)) == 0 else { throw denied() }
        let values = try resolved.resourceValues(forKeys: [.volumeIsLocalKey, .isUbiquitousItemKey])
        guard values.volumeIsLocal == true, values.isUbiquitousItem != true else { throw denied() }
    }
    private static func denied() -> Error {
        NSError(domain: "Cauces.LocalOnly", code: 1, userInfo: [NSLocalizedDescriptionKey: "Elige un archivo o carpeta de un disco local sin sincronización. Cauces rechaza ubicaciones de nube o red reconocidas y archivos pendientes de descarga."])
    }
}
