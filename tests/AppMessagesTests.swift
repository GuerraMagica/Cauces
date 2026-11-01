import Foundation

@main struct AppMessagesTests {
 static func main() {
  let foreign = NSError(domain: NSCocoaErrorDomain, code: CocoaError.fileReadNoPermission.rawValue, userInfo: [NSLocalizedDescriptionKey:"No se puede leer el archivo."])
  let permission = AppMessages.describe(foreign)
  precondition(permission.lowercased().contains("permission") && !permission.contains("No se puede"))
  let unknown = NSError(domain:"ExampleAudio",code:42,userInfo:[NSLocalizedDescriptionKey:"未知のエラー"])
  let fallback = AppMessages.describe(unknown)
  precondition(fallback.contains("ExampleAudio") && fallback.contains("42") && !fallback.contains("未知"))
  let owned = NSError(domain:"Cauces.Files",code:1,userInfo:[NSLocalizedDescriptionKey:"The source changed during copying."])
  precondition(AppMessages.describe(owned)=="The source changed during copying.")
  precondition(AppMessages.describe(JobError.noSource).contains("WAV"))
  print("English diagnostic fallback and own-message preservation passed")
 }
}
