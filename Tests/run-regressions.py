#!/usr/bin/env python3
"""Compile the actual color-averaging implementation without Xcode/UI dependencies."""
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parent.parent
source = (root / 'Ice/Utilities/Extensions.swift').read_text()
# Keep the production implementation verbatim, including its options type.
color = source[source.index('extension CGImage {'):source.index('    // MARK: Transparency Trimming')] + '}\n'
clamp = source[source.index('extension Comparable {'):source.index('// MARK: - DistributedNotificationCenter')]
# Ifrit's bitmap-info convenience initializer is the only external dependency.
support = '''import CoreGraphics
extension CGBitmapInfo {
    init(alpha: CGImageAlphaInfo, byteOrder: CGBitmapInfo) {
        self.init(rawValue: alpha.rawValue | byteOrder.rawValue)
    }
}
'''
cases = '''
func image(alpha: CGFloat) -> CGImage {
    let context = CGContext(data: nil, width: 2, height: 2, bitsPerComponent: 8,
        bytesPerRow: 8, space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    context.setFillColor(red: 1, green: 0, blue: 0, alpha: alpha)
    context.fill(CGRect(x: 0, y: 0, width: 2, height: 2))
    return context.makeImage()!
}
precondition(image(alpha: 0).averageColor() == nil, "Transparent capture must return nil")
precondition(image(alpha: 0.2).averageColor() == nil, "All pixels below threshold must return nil")
for option: CGImage.ColorAveragingOption in [[], .ignoreAlpha] {
    let color = image(alpha: 1).averageColor(option: option)!
    precondition(color.components!.allSatisfy { $0.isFinite }, "Color must be finite")
    precondition(abs(color.components![0] - 1) < 0.01, "Opaque red must stay red")
    precondition(color.components![1] < 0.01 && color.components![2] < 0.01)
}
print("PASS: transparent, below-threshold and opaque color captures")
'''
with tempfile.TemporaryDirectory(prefix='ice-regressions-') as temp:
    swift = pathlib.Path(temp) / 'main.swift'
    swift.write_text(support + color + clamp + cases)
    binary = pathlib.Path(temp) / 'regressions'
    subprocess.run(['swiftc', str(swift), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)

# Exercise concurrent permission waiters and SwiftUI-style task cancellation.
permission = (root / 'Ice/Permissions/Permission.swift').read_text()
permission = permission[:permission.index('// MARK: - AccessibilityPermission')]
permission_cases = r"""
@main struct PermissionRegression {
    @MainActor static func main() async throws {
        var granted = false
        let permission = Permission(title: "Test", details: [], isRequired: true,
            settingsURL: nil, check: { granted }, request: {})
        let first = Task { await permission.waitForPermission() }
        let second = Task { await permission.waitForPermission() }
        try await Task.sleep(for: .milliseconds(100))
        granted = true
        await first.value
        await second.value
        await permission.waitForPermission() // Already granted: returns immediately.
        permission.stopCheck()

        let denied = Permission(title: "Test", details: [], isRequired: true,
            settingsURL: nil, check: { false }, request: {})
        let cancelled = Task { await denied.waitForPermission() }
        try await Task.sleep(for: .milliseconds(100))
        cancelled.cancel()
        await cancelled.value
        denied.stopCheck()
        print("PASS: concurrent permission waiters, already granted and cancellation")
    }
}
"""
with tempfile.TemporaryDirectory(prefix='ice-permissions-') as temp:
    swift = pathlib.Path(temp) / 'PermissionRegression.swift'
    swift.write_text(permission + permission_cases)
    binary = pathlib.Path(temp) / 'regressions'
    subprocess.run(['swiftc', '-parse-as-library', str(swift), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True, timeout=15)

# Run the production display-selection function against simulated OS responses.
# This covers the nil-identifier failure and secondary-display capture selection.
bridging = (root / 'Shared/Bridging/Bridging.swift').read_text()
start = bridging.index('    static func getActiveMenuBarDisplayID()')
end = bridging.index('\n    }', start) + len('\n    }')
display_function = bridging[start:end]
display_support = r'''
import Foundation
import CoreGraphics
var activeDisplays: [CGDirectDisplayID] = [1, 2]
var privateIdentifier: CFString?
var menuWindows: [WindowInfo] = []
var mainDisplay: CGDirectDisplayID = 1
let secondaryUUID = CFUUIDCreateFromString(nil, "01234567-89AB-CDEF-0123-456789ABCDEF" as CFString)!
let primaryUUID = CFUUIDCreateFromString(nil, "11234567-89AB-CDEF-0123-456789ABCDEF" as CFString)!
func CGSCopyActiveMenuBarDisplayIdentifier(_ connection: Int) -> Unmanaged<CFString>? {
    privateIdentifier.map { Unmanaged.passRetained($0) }
}
func CGMainDisplayID() -> CGDirectDisplayID { mainDisplay }
func CGDisplayBounds(_ id: CGDirectDisplayID) -> CGRect {
    CGRect(x: id == 1 ? 0 : 1000, y: 0, width: 1000, height: 800)
}
struct WindowInfo {
    var isWindowServerWindow = true
    var layer = Int(kCGMainMenuWindowLevel)
    let bounds: CGRect
    enum Option { case onScreen }
    static func createMenuBarWindows(option: Option) -> [WindowInfo] { menuWindows }
}
enum Bridging {
    static func getActiveDisplayList() -> [CGDirectDisplayID] { activeDisplays }
    static func getMainConnection() -> Int { 0 }
    static func getDisplayUUID(for id: CGDirectDisplayID) -> CFUUID? { id == 1 ? primaryUUID : secondaryUUID }
'''
display_cases = r'''
privateIdentifier = CFUUIDCreateString(nil, secondaryUUID)
precondition(Bridging.getActiveMenuBarDisplayID() == 2, "Use the OS identifier when valid")
privateIdentifier = nil
menuWindows = [WindowInfo(bounds: CGRect(x: 1000, y: 0, width: 1000, height: 24))]
precondition(Bridging.getActiveMenuBarDisplayID() == 2, "Recover secondary display from menu bar geometry")
menuWindows = []
precondition(Bridging.getActiveMenuBarDisplayID() == 1, "Fall back to main active display")
activeDisplays = [2]
precondition(Bridging.getActiveMenuBarDisplayID() == 2, "Do not select an inactive main display")
activeDisplays = []
precondition(Bridging.getActiveMenuBarDisplayID() == nil, "No active display is not a capture target")
print("PASS: private display identifier, secondary geometry, main fallback and headless state")
'''
with tempfile.TemporaryDirectory(prefix='ice-displays-') as temp:
    swift = pathlib.Path(temp) / 'main.swift'
    swift.write_text(display_support + display_function + '\n}\n' + display_cases)
    binary = pathlib.Path(temp) / 'regressions'
    subprocess.run(['swiftc', str(swift), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
