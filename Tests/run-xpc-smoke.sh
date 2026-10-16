#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="${1:?Pass the built Ice.app path}"
PROBE_ROOT="$(mktemp -d /tmp/ice-xpc-smoke.XXXXXX)"
trap 'rm -rf "$PROBE_ROOT"' EXIT
PROBE="$PROBE_ROOT/IceXPCSmoke.app"
mkdir -p "$PROBE/Contents/MacOS" "$PROBE/Contents/XPCServices"
cp -R "$APP/Contents/XPCServices/MenuBarItemService.xpc" "$PROBE/Contents/XPCServices/"
cat > "$PROBE/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleIdentifier</key><string>com.andreireddy.Ice.XPCSmoke</string>
<key>CFBundleExecutable</key><string>IceXPCSmoke</string>
<key>CFBundlePackageType</key><string>APPL</string>
</dict></plist>
PLIST
swiftc -parse-as-library -target "$(uname -m)-apple-macos26.0" \
  "$ROOT/Tests/XPCSmoke.swift" "$ROOT/Shared/Utilities/CodeSigningInfo.swift" \
  "$ROOT/Shared/Utilities/Logging.swift" -o "$PROBE/Contents/MacOS/IceXPCSmoke"
codesign --force --deep --sign - --options 0 "$PROBE"
"$PROBE/Contents/MacOS/IceXPCSmoke"
