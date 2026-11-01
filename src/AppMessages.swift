import Foundation
import Darwin

/// App-owned diagnostics stay English even if the operating system uses another language.
enum AppMessages {
    static func describe(_ error: Error) -> String {
        if let own = error as? JobError { return own.errorDescription ?? "The operation could not be completed." }
        let detail = error as NSError
        if ["Cauces.Files", "Cauces.LocalOnly", "Cauces.Output", "Preview"].contains(detail.domain),
           let message = detail.userInfo[NSLocalizedDescriptionKey] as? String { return message }
        if detail.domain == NSCocoaErrorDomain {
            switch detail.code {
            case CocoaError.fileReadNoPermission.rawValue, CocoaError.fileWriteNoPermission.rawValue:
                return "File permission denied. Choose an accessible local file or folder."
            case CocoaError.fileNoSuchFile.rawValue, CocoaError.fileReadNoSuchFile.rawValue:
                return "The file or folder is no longer available. Choose it again."
            case CocoaError.fileWriteOutOfSpace.rawValue:
                return "There is not enough disk space. Free some space and try again."
            case CocoaError.executableNotLoadable.rawValue:
                return "The audio engine could not start. Check that the complete Cauces app has been copied."
            default: break
            }
        }
        if detail.domain == NSPOSIXErrorDomain {
            switch detail.code {
            case Int(EACCES), Int(EPERM): return "File permission denied. Choose an accessible local file or folder."
            case Int(ENOENT): return "The file or folder is no longer available. Choose it again."
            case Int(ENOSPC): return "There is not enough disk space. Free some space and try again."
            default: break
            }
        }
        return "The operation could not be completed (\(detail.domain), error \(detail.code)). Check the audio format, file permissions, available disk space and audio output device."
    }
}
