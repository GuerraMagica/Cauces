import Foundation

@main struct JobStateTests {
    static func main() throws {
        var state = JobState()
        precondition(!state.canSeparate && !state.canExport)
        let inspect = try state.begin(.inspect)
        do { _ = try state.begin(.separate); preconditionFailure("second job accepted") } catch {}
        precondition(!state.finish(id: inspect + 1, success: true), "stale event changed current job")
        precondition(state.finish(id: inspect, success: true))
        precondition(state.canSeparate && !state.canExport)
        let work = try state.begin(.separate)
        state.cancel()
        precondition(!state.finish(id: work, success: true), "cancelled event accepted")
        precondition(state.canSeparate && !state.canExport)
        let retry = try state.begin(.separate)
        precondition(state.finish(id: retry, success: true) && state.canExport)
        let export = try state.begin(.export)
        precondition(state.finish(id: export, success: false) && state.canExport, "export failure lost preview")
        _ = try state.begin(.export)
        state.failCurrent()
        precondition(state.canExport, "local destination failure lost a valid result")
        _ = try state.begin(.inspect)
        precondition(!state.canExport, "new source kept stale stems")
        print("Job state contracts passed")
    }
}
