import AppKit
import Combine
import Foundation
import UniformTypeIdentifiers

@MainActor final class JobController: ObservableObject {
    @Published private(set) var state = JobState()
    @Published private(set) var source: URL?
    @Published private(set) var info = "WAV · PCM16, PCM24 o float32 · Mono o dual mono · 8–48 kHz"
    @Published private(set) var stage = "Abre un archivo para comenzar"
    @Published private(set) var progress = 0.0
    @Published private(set) var elapsed = ""
    @Published var error: String?
    @Published private(set) var exportDirectory: URL?
    let preview = PreviewPlayer()
    private var connection: WorkerConnection?

    func choose() {
        guard !state.busy else { return }
        let panel = NSOpenPanel(); panel.allowedContentTypes = [.wav]; panel.allowsMultipleSelection = false
        panel.canChooseDirectories = false; panel.message = "Selecciona un WAV de hasta 30 minutos"
        if panel.runModal() == .OK, let url = panel.url { open(url) }
    }
    func open(_ url: URL) {
        guard !state.busy else { return }
        do {
            let id = try state.begin(.inspect); source = url; preview.clear(); exportDirectory = nil; elapsed = ""; error = nil
            stage = "Leyendo cabecera WAV"; progress = 0
            try send(["cmd": "inspect", "source": url.path, "id": id])
        } catch { fail(error) }
    }
    private func send(_ command: [String: Any]) throws {
        if connection == nil {
            guard let executable = Bundle.main.executableURL, let resources = Bundle.main.resourceURL else { throw CocoaError(.executableNotLoadable) }
            let worker = executable.deletingLastPathComponent().appendingPathComponent("dialogue-worker")
            let client = try WorkerConnection(executable: worker, models: resources.appendingPathComponent("Models", isDirectory: true))
            client.onEvent = { [weak self] event in self?.receive(event) }
            client.onExit = { [weak self] status in
                guard let self else { return }; self.connection?.close(); self.connection = nil
                self.state.cancel(); self.preview.clear(); self.stage = "El motor se ha cerrado"
                self.error = "El motor se cerró inesperadamente (\(status)). Puedes volver a separar. Comprueba espacio disponible y que la app esté completa."
            }
            connection = client
        }
        try connection!.send(command)
    }
    func separate() {
        guard state.canSeparate, let source else { return }
        do {
            let id = try state.begin(.separate); preview.clear(); exportDirectory = nil; elapsed = ""; error = nil; progress = 0; stage = "Preparando separación"
            // send creates a connection if this is a retry after cancellation.
            if connection == nil { try send(["cmd": "inspect", "source": source.path, "id": -1]) }
            try send(["cmd": "separate", "source": source.path, "workspace": connection!.workspace.path, "id": id])
        } catch { fail(error) }
    }
    func cancel() {
        guard state.active == .separate || state.active == .inspect else { return }
        state.cancel(); preview.clear(); connection?.close(); connection = nil
        stage = "Trabajo cancelado"; progress = 0; elapsed = ""
    }
    func export() {
        guard state.canExport else { return }
        let panel = NSOpenPanel(); panel.canChooseDirectories = true; panel.canChooseFiles = false
        panel.canCreateDirectories = true; panel.message = "Se creará una carpeta con los tres stems float32. No se sobrescribirá una exportación existente."
        guard panel.runModal() == .OK, let destination = panel.url else { return }
        do {
            let id = try state.begin(.export); stage = "Verificando y exportando los tres stems"; error = nil
            try send(["cmd": "export", "destination": destination.path, "id": id])
        } catch { fail(error) }
    }
    private func receive(_ event: [String: Any]) {
        guard let type = event["type"] as? String, type != "ready", let id = event["id"] as? Int, id == state.generation else { return }
        switch type {
        case "progress": progress = event["value"] as? Double ?? progress; stage = event["stage"] as? String ?? stage
        case "info":
            guard state.finish(id: id, success: true) else { return }
            let rate = event["rate"] as? Int ?? 0, channels = event["channels"] as? Int ?? 0
            let bits = event["bits"] as? Int ?? 0, seconds = event["duration"] as? Double ?? 0
            info = "\(rate) Hz · \(bits) bit · \(channels == 1 ? "Mono" : "2 canales; se comprobará dual mono") · \(Self.time(seconds))"
            if event["time_reference"] != nil { info += " · BWF" }; stage = "Listo para separar"
        case "result":
            guard state.finish(id: id, success: true), let source, let paths = event["stems"] as? [String] else { return }
            do {
                try preview.load(original: source, stems: paths.map { URL(fileURLWithPath: $0) })
                progress = 1; stage = "Dos voces y residual listos"
                if let seconds = event["process_seconds"] as? Double { elapsed = String(format: "Separación: %.1f s", seconds) }
            } catch { fail(error) }
        case "exported":
            guard state.finish(id: id, success: true), let path = event["directory"] as? String else { return }
            exportDirectory = URL(fileURLWithPath: path); stage = "Tres stems exportados y verificados"
        case "error":
            _ = state.finish(id: id, success: false); stage = "No se ha completado el trabajo"
            error = event["message"] as? String ?? "El motor devolvió un error sin diagnóstico."
        default: break
        }
    }
    private func fail(_ problem: Error) { state.failCurrent(); error = problem.localizedDescription; stage = "No se ha completado el trabajo" }
    func shutdown() { preview.clear(); connection?.close(); connection = nil }
    static func time(_ value: Double) -> String {
        let total = max(0, Int(value * 1000)); return String(format: "%02d:%02d.%03d", total/60000, total/1000%60, total%1000)
    }
}
