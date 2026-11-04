# Cauces — designer handoff / v1

Original Cauces artwork and design documentation are licensed **GPL-3.0-only**.
See [licence scope](../../LICENSE_SCOPE.md), [COPYRIGHT](../../COPYRIGHT) and
[contribution guidelines](../../CONTRIBUTING.md). The copyright licence does not
itself grant trademark or official-endorsement rights. Third-party material, if
introduced later, requires its own compatible licence and attribution.

**Status: Flow approved and integrated in Cauces 0.3.0.** The native app uses these colors/artwork and a generated macOS app icon. The SVG screens and HTML remain editable design references, not the running app.

Open `index.html` in a browser. It is self-contained: no account, external font or external network resource is needed. The interaction checks used a local loopback preview; direct file opening was not verified by the automation browser. Use the state buttons to inspect six screens, or click the primary action in the mock-up. This is a visual prototype: it does not open, play, process or export audio.

## What to open in a design tool

- `templates/*.svg`: neutral editable artboards. Replace the `slot-hero-art` group and restyle the named UI groups.
- `proposal/control-states.svg` and `templates/control-states.svg`: selection, hover, pressed, disabled and keyboard-focus references.
- `proposal/*.svg`: the proposed Flow design. All artwork and text remain editable; nothing is a flattened screenshot.
- `assets/brand/*.svg`: original vector artwork, a provisional mark and monochrome/light variants.
- `assets/icons/*.svg`: nine custom vector icons on a 24 × 24 grid. `currentColor` is black when viewed alone; recolor as needed.
- `previews/*.png`: visual references only. Screen previews are exported at 2×. Do not use a flattened screen image as the app interface.
- `tokens.json`: proposed colors, spacing, radii, type scale and artboard sizes.
- `copy.en.json`: English copy to preserve in the final design.
- `asset-manifest.json`: dimensions, intended use and provisional/approved status.
- `design-brief.md`: requirements, interaction states, constraints and handoff checklist.

Standard frame: **1000 × 700 pt**, including a 44 pt mock macOS title bar. Minimum check: **860 × 620 pt**. The title bar is only a design reference; the production app will keep native macOS window controls.

Cauces 0.4.0 also has a native **Settings** window (520 pt wide, content-sized height), using the same palette/system controls: Output, Sample rate, Apply and Cancel. The supplied SVG main-window artboards predate this window; include it when returning a complete redesign. Its source is `src/AudioSettingsView.swift` in the app repository.

## Return these files for integration

1. A source file from your preferred tool (Figma, Sketch, Illustrator or equivalent), plus editable SVG exports with named groups.
2. Every screen state, not just the empty screen: empty, ready, processing, review, exported, error.
3. Separate vector artwork, mark and icon files. Transparent PNG at 1×/2× only for artwork that genuinely requires raster output.
4. Color values, font names/weights, sizes, spacing and minimum window behavior. Explain any deviation from `tokens.json`.
5. Font/image licenses and any assets you introduced. System fonts are preferred; no proprietary font files are included here.

Keep application text editable. Do not bake labels, copyright or buttons into a hero image. If custom type is essential for a logo, include an outlined vector logo and identify the font separately.

Optional generation tools live in `tools/`. Rerunning `build_assets.py` regenerates the supplied designs and overwrites manual edits to those generated files; keep your custom design in a separate folder. `render-previews.cjs` uses an existing Node/sharp installation solely for optional PNG export. Neither tool nor dependency is part of the app.

The user approved using the supplied Flow mark as the 0.3.0 app icon. A replacement logo may still be supplied later; keep its slot replaceable.

© GuerraMagica Audio
