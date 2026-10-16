<div align="center">
    <img src="Ice/Assets.xcassets/AppIcon.appiconset/icon_256x256.png" width=200 height=200>
    <h1>Ice</h1>
</div>

## macOS Tahoe community build

This fork packages the upstream `macos-26` work plus fixes for recent Tahoe
releases. Download **Ice.zip** from [this fork's releases](https://github.com/andreireddy/Ice/releases).
The release app supports Apple Silicon and Intel; macOS 14 is the minimum.
Runtime verification is performed on macOS 26.5.2. macOS 27 is not verified.

1. Quit any running copy of Ice, unzip the download, and move `Ice.app` into `Applications`.
2. This community build is ad-hoc signed and is **not Apple-notarized**. If macOS blocks it,
   open System Settings → Privacy & Security → Open Anyway, then confirm opening Ice.
3. Grant Ice Accessibility access. Grant Screen Recording to enable item images, layout,
   search and appearance features. If macOS requests it, quit and reopen Ice after granting access.
4. Verify showing/hiding items, clicking an Ice Bar item, dragging an item between layout
   sections, and search. On multiple displays, also check each display's icon size.

Updates for this build are downloaded manually from this fork's releases via the About pane.
The upstream update checker is disabled for community builds.

### Build and verify

With Xcode 26 or later, build the `Ice` scheme in `Ice.xcodeproj`.
The `Build macOS app` workflow builds both architectures, signs the app ad-hoc,
runs regression and bundled-XPC tests, and uploads an installable ZIP.

Without Xcode, run `zsh Scripts/build-without-xcode.sh` (macOS 26 SDK required).
This builds for the host architecture and writes `build/Ice.app`. It compiles all
executable code from source, and reuses only the compiled asset catalog from the
upstream beta archive, pinned by SHA-256. CLT build support and signature inspection
are adapted from [Steven Chen's upstream PR #985](https://github.com/jordanbaird/Ice/pull/985).

Run `python3 Tests/run-regressions.py` and
`bash Tests/run-xpc-smoke.sh build/Ice.app` to check transparent captures,
concurrent permission waits/cancellation, and the embedded helper handshake.

Known limitations: multi-display runtime checks need physical displays; the
upstream report [#946](https://github.com/jordanbaird/Ice/issues/946) about items
moving into the always-hidden section is not yet reproduced or claimed fixed.
The upstream transparent-menu-bar appearance limitation also remains: enable
“Show menu bar background” in System Settings → Menu Bar if the custom appearance
produces a brightness mismatch.

## Upstream project

Ice is a powerful menu bar management tool. While its primary function is hiding and showing menu bar items, it aims to cover a wide variety of additional features to make it one of the most versatile menu bar tools available.

![Banner](https://github.com/user-attachments/assets/4423085c-4e4b-4f3d-ad0f-90a217c03470)

[![Download](https://img.shields.io/badge/download-latest-brightgreen?style=flat-square)](https://github.com/jordanbaird/Ice/releases/latest)
![Platform](https://img.shields.io/badge/platform-macOS-blue?style=flat-square)
![Requirements](https://img.shields.io/badge/requirements-macOS%2014%2B-fa4e49?style=flat-square)
[![Sponsor](https://img.shields.io/badge/Sponsor%20%E2%9D%A4%EF%B8%8F-8A2BE2?style=flat-square)](https://github.com/sponsors/jordanbaird)
[![Website](https://img.shields.io/badge/Website-015FBA?style=flat-square)](https://icemenubar.app)
[![License](https://img.shields.io/github/license/jordanbaird/Ice?style=flat-square)](LICENSE)

> [!NOTE]
> Ice is currently in active development. Some features have not yet been implemented. Download the latest release [here](https://github.com/jordanbaird/Ice/releases/latest) and see the roadmap below for upcoming features.

<a href="https://www.buymeacoffee.com/jordanbaird" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;">
</a>

## Install

### Manual Installation

Download the "Ice.zip" file from the [latest release](https://github.com/jordanbaird/Ice/releases/latest) and move the unzipped app into your `Applications` folder.

### Homebrew

Install Ice using the following command:

```sh
brew install --cask jordanbaird-ice
```

## Features/Roadmap

### Menu bar item management

- [x] Hide menu bar items
- [x] "Always-hidden" menu bar section
- [x] Show hidden menu bar items when hovering over the menu bar
- [x] Show hidden menu bar items when an empty area in the menu bar is clicked
- [x] Show hidden menu bar items by scrolling or swiping in the menu bar
- [x] Automatically rehide menu bar items
- [x] Hide application menus when they overlap with shown menu bar items
- [x] Drag and drop interface to arrange individual menu bar items
- [x] Display hidden menu bar items in a separate bar (e.g. for MacBooks with the notch)
- [x] Search menu bar items
- [x] Menu bar item spacing (BETA)
- [ ] Profiles for menu bar layout
- [ ] Individual spacer items
- [ ] Menu bar item groups
- [ ] Show menu bar items when trigger conditions are met

### Menu bar appearance

- [x] Menu bar tint (solid and gradient)
- [x] Menu bar shadow
- [x] Menu bar border
- [x] Custom menu bar shapes (rounded and/or split)
- [ ] Remove background behind menu bar
- [ ] Rounded screen corners
- [ ] Different settings for light/dark mode

### Hotkeys

- [x] Toggle individual menu bar sections
- [x] Show the search panel
- [x] Enable/disable the Ice Bar
- [x] Show/hide section divider icons
- [x] Toggle application menus
- [ ] Enable/disable auto rehide
- [ ] Temporarily show individual menu bar items

### Other

- [x] Launch at login
- [x] Automatic updates
- [ ] Menu bar widgets

## Why does Ice only support macOS 14 and later?

Ice uses a number of system APIs that are available starting in macOS 14. As such, there are no plans to support earlier versions of macOS.

## Gallery

#### Show hidden menu bar items below the menu bar

![Ice Bar](https://github.com/user-attachments/assets/f1429589-6186-4e1b-8aef-592219d49b9b)

#### Drag-and-drop interface to arrange menu bar items

![Menu Bar Layout](https://github.com/user-attachments/assets/095442ba-f2d0-4bb4-9632-91e26ef8d45b)

#### Customize the menu bar's appearance

![Menu Bar Appearance](https://github.com/user-attachments/assets/8c22c185-c3d2-49bb-971e-e1fc17df04b3)

#### Menu bar item search

![Menu Bar Item Search](https://github.com/user-attachments/assets/d1a7df3a-4989-4077-a0b1-8e7d5a1ba5b8)

#### Custom menu bar item spacing

![Menu Bar Item Spacing](https://github.com/user-attachments/assets/b196aa7e-184a-4d4c-b040-502f4aae40a6)

## License

Ice is available under the [GPL-3.0 license](LICENSE).
