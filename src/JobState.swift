import Foundation

enum JobCommand { case inspect, separate, export }
struct JobState {
    private(set) var generation = 0
    private(set) var active: JobCommand?
    private(set) var hasSource = false
    private(set) var hasResult = false
    var busy: Bool { active != nil }
    var canSeparate: Bool { hasSource && !busy }
    var canExport: Bool { hasResult && !busy }
    mutating func begin(_ command: JobCommand) throws -> Int {
        guard !busy else { throw JobError.busy }
        if command == .separate && !hasSource { throw JobError.noSource }
        if command == .export && !hasResult { throw JobError.noResult }
        generation += 1; active = command
        if command == .inspect { hasSource = false; hasResult = false }
        if command == .separate { hasResult = false }
        return generation
    }
    @discardableResult mutating func finish(id: Int, success: Bool) -> Bool {
        guard id == generation, let command = active else { return false }
        if command == .inspect { hasSource = success }
        if command == .separate { hasResult = success }
        active = nil
        return true
    }
    mutating func cancel() { generation += 1; active = nil; hasResult = false }
    mutating func failCurrent() {
        if active != nil { _ = finish(id: generation, success: false); generation += 1 }
        else { cancel() }
    }
}
enum JobError: LocalizedError {
    case busy, noSource, noResult
    var errorDescription: String? {
        switch self {
        case .busy: return "Espera a que termine el trabajo actual."
        case .noSource: return "Abre primero un WAV compatible."
        case .noResult: return "Separa primero el audio."
        }
    }
}
