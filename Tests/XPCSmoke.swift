import Foundation
import XPC

// A minimal wire client exercises the actual bundled service, without
// requiring Accessibility access or loading Ice's UI.
enum SmokeMessage: Codable {
    case start
}

@main
struct XPCSmoke {
    static func main() throws {
        let queue = DispatchQueue(label: "Ice.XPCSmoke")
        let session = try XPCSession(xpcService: "com.jordanbaird.Ice.MenuBarItemService", options: .inactive) { _ in }
        if CodeSigningInfo.shouldEnforceSameTeamRequirement {
            session.setPeerRequirement(.isFromSameTeam())
        }
        session.setTargetQueue(queue)
        try session.activate()
        defer { session.cancel(reason: "Smoke test finished") }
        let reply = try session.sendSync(SmokeMessage.start)
        guard case .start = try reply.decode(as: SmokeMessage.self) else {
            fatalError("Unexpected helper reply")
        }
        print("PASS: bundled ad-hoc XPC helper handshake")
    }
}
