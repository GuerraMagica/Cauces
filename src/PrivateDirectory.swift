import Foundation

/// Pins directory descriptors and rejects detected identity replacements.
/// Does not provide atomic isolation from a concurrent writer of the same user.
// Copy/publish run on one worker queue; cleanup runs only after its DispatchGroup
// completes. cancel is the sole concurrent operation and uses a C++ atomic flag.
final class PrivateDirectory: @unchecked Sendable {
    private var handle: OpaquePointer?
    let url: URL
    init(parent: URL, prefix: String) throws {
        var message = [CChar](repeating: 0, count: 512)
        guard let value = cauces_directory_create(parent.path, prefix, &message, message.count) else {
            throw Self.failure(message)
        }
        handle = value; url = URL(fileURLWithPath: String(cString: cauces_directory_path(value)))
    }
    func copy(source: URL, name: String) throws {
        var message = [CChar](repeating: 0, count: 512)
        guard cauces_directory_copy(handle, source.path, name, &message, message.count) == 0 else { throw Self.failure(message) }
    }
    func publish(name: String) throws -> URL {
        var message = [CChar](repeating: 0, count: 512)
        guard cauces_directory_publish(handle, name, &message, message.count) == 0 else { throw Self.failure(message) }
        return url.deletingLastPathComponent().appendingPathComponent(name)
    }
    func cancel() { cauces_directory_cancel(handle) }
    func cleanup() { if let value = handle { cauces_directory_destroy(value); handle = nil } }
    deinit { cleanup() }
    private static func failure(_ message: [CChar]) -> Error {
        NSError(domain: "Cauces.Files", code: 1, userInfo: [NSLocalizedDescriptionKey: String(cString: message)])
    }
}
