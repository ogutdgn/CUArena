# 025 — Theme font colors (group 2 of the parity fix pass)

**Source:** deep T0/T1 fidelity identification (`parity/results/DEEP_T0_T1_REPORT.md` §4a, adversarially verified).
`fd-fontcolor-theme` — the clone's run font-color was **sRGB-only**: a Theme-Colors pick baked the resolved hex and
dropped the theme link, so it exported `<w:color w:val="E97132"/>` where Word writes
`<w:color w:val="E97132" w:themeColor="accent2"/>` (and never recolored on a theme change).

Branch: `parity-pipeline` (no feature branch). FIX phase.

## FR-025-1 — carry the theme binding on the color mark + export + import + the picker
- **Color mark** (`extensions/color/color.js`): add `themeColor` / `themeTint` / `themeShade` attrs to the
  `textStyle` mark (model metadata; renderDOM uses `data-*` so in-app copy/paste preserves them). `setColor(color,
  options)` writes them unconditionally (null when absent, so switching to a plain color CLEARS a stale link);
  `unsetColor` clears them too.
- **Export:** `decodeRPrFromMarks` (styles.js, the body run path) threads the keys onto `runProperties.color` so the
  existing **v3 `w:color` translator** (which already declares `w:themeColor`/`themeTint`/`themeShade` handlers) emits
  them. `translateMark` (exporter.js, the hyperlink/run path) writes them too (defense-in-depth).
- **Import:** `encodeMarksFromRPr` (styles.js) reads the decoded `themeColor`/`themeTint`/`themeShade` off the color
  object so a Theme-Colors run **round-trips** instead of degrading to flat sRGB.
- **Picker** (NO-FORK, `util.js` + `commands.js`): the 10 base Theme-Colors swatches carry their OOXML slot
  (`THEME_SLOTS`: background1/text1/background2/text2/accent1..accent6) through `onPick` → `applyColor` →
  `setColor({themeColor})`; `lastFontColorMeta` re-applies the link from the main-face Font Color button.

### Acceptance
`python parity/engines/run.py --only fd-fontcolor-theme` = **0/0** (Word-COM `ObjectThemeColor=accent2` ground truth).
`test:pm` regression `025 theme font color exports <w:color w:themeColor>` (positive + negative: a plain color must
NOT gain a themeColor). Gates: test:pm + test:roundtrip green. Fork edits → NOTICE.

## v1 limitations (logged, no regression)
- **Tint/shade swatches** stay resolved sRGB (the `w:themeTint`/`w:themeShade` byte computation is deferred). This is
  today's behavior — only the **base** theme colors gain the link in v1.
- Standard/custom colors are unchanged (sRGB, no theme link — correct).

## Out of scope
The remaining group-3/4 gaps (double-strike/hidden/kerning, bullet-font/align, special-replace, margins).
