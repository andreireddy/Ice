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
