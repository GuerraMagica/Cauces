# Cauces / Flow — UI design proposal

Date: 2026-10-28. Native macOS desktop app. This is the app's main screen, not a website.

## Intent

Make a focused dialogue separation tool feel clear, professional and quiet. The user opens one WAV, separates two voices plus a residual, compares the results and exports audio. Give each state one obvious next action. Preserve the existing local processing, data integrity and security behavior.

## Requested changes

- All app-owned UI text in English: controls, progress, messages, alerts, accessibility labels and file-panel messages. The proposed copy is in `copy.en.json`. Translating backend diagnostics must also be included when implementing; translating only `App.swift` is insufficient.
- Remove the entire large in-content header from screenshot 02: duplicate Cauces title, the explanatory subtitle and the personal beta/CPU badge. Keep Cauces in the native window title.
- Replace the incorrect export label with **Export audio…**. Describe the result as three WAV files: Voice 1, Voice 2 and Residual. Do not use the word "stems" in product copy.
- Remove the technical footer in screenshot 04. Do not reintroduce those statements elsewhere on the main screen under another badge.
- Add exactly **© GuerraMagica Audio** as a quiet footer, with no invented year or additional ownership claim.
- Produce a neutral editable kit for an external designer and a separate Cauces concept proposal.

## Approaches considered

**Minimal cleanup:** retain the current macOS panel layout, translate text and remove the specified rows. Low implementation cost, but leaves the initial screen with several inactive controls and little visual identity.

**Flow (recommended proposal):** progressive disclosure, a single import action initially, and a restrained channel motif. Show the player and export actions when results exist. Reuse the current processing and transport behaviors. The user approved this direction for the 0.3.0 native implementation and requested its mark as the app icon.

## Visual concept

Cauces means channels or riverbeds. A shared incoming route separates into two readable paths. Mint and sand distinguish the two voices; the residual is a quieter neutral route. Fine parallel contours suggest the structure of channels, without landscape photography, rainbows, prisms, water textures or visual effects that compete with audio work.

A charcoal surface, system type, sparse outlines and moderate contrast suit a sound-editing workspace. Color supports labels; it never replaces them. The exploratory mark/icon remain separate assets because the user may provide a final logo later.

## State and layout specification

- **Empty:** no duplicate header, no disabled player or export area. Center a replaceable artwork slot, "Drop a WAV file here", Open audio… and one short compatibility line (mono/identical dual mono, sample-rate range and duration).
- **Ready:** show the file name and useful source metadata; make Separate voices the primary action. Allow changing the source. The displayed filename/metadata in the mock-up are synthetic placeholders.
- **Processing:** show the current stage, progress and Cancel. The 52% example is a static design sample, not a performance result. Keep model/CPU/provider details out of this screen.
- **Review:** compact source row, four labeled selectors, synchronized playback/seek and one primary Export audio… action. No invented waveform visualization, meters, quality scores, track editor or new audio processing.
- **Exported:** preserve review controls and add a short confirmation plus Show folder.
- **Error:** give a direct diagnosis and an appropriate recovery action. Native alerts may be used for transient errors; the full error artboard demonstrates content placement, not a required custom modal system.

The minimum artboard demonstrates the import screen at 860 × 620 pt. In production, review/processing must also be checked at that size, with longer filenames and accessibility text sizes. SVG previews are not proof of native SwiftUI layout at every size.

## Interaction and accessibility

Use native SwiftUI buttons and transport controls. Preserve keyboard navigation, Command-O, named play/pause controls, progress semantics and seek accessibility. Use stable Voice 1/Voice 2/Residual names. Keep selection, focus and disabled states distinct without relying on color alone. A visible checkmark identifies the selected voice; control-state sheets provide the intended visual states. Respect Reduce Motion; animation is optional and never needed to understand progress.

Use the system font. Recreate layout with native controls; do not use a WebView or a full-window PNG as the shipped interface. Keep decorative artwork separate from UI text and hit targets. This browser prototype exists only for design review.

## Integration scope after approval

1. Add a small style/asset layer, then apply the approved layout in SwiftUI.
2. Translate app-owned strings across Swift and C++ progress/diagnostics; update tests that intentionally check translated messages. Use English bundle localization metadata where appropriate. System-owned dialog/menu text follows macOS localization behavior and must be verified on both target systems.
3. Remove the specified header/footer, correct export terminology and add the signature.
4. Verify open/drop, all processing states, cancel/retry, playback/seek, export/collision handling, long filenames and keyboard use. Build both architectures and verify the signed sandboxed package. Audio mathematics, model files and their fingerprints are outside this design change.
5. Deliver a new local version for review. Git commits/pushes and distribution follow the user's publication instructions; this design draft is not published automatically.

## Acceptance before integration

The user approves a visual direction and may replace the provisional logo. Until then, this kit is a design deliverable only: `src/`, model assets and the installed/distributed Cauces 0.2 app remain unchanged.

## Designer return checklist

Return editable named layers; all six states; minimum-size behavior; colors/type/spacing; separate logo/artwork/icons; exact English text; focus/hover/pressed/disabled states for changed controls; any font or image licenses. Preserve the distinction between two estimated voices and a residual.
