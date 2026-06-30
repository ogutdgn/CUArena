# 026 — Missing Font-dialog effects: Double strikethrough / Hidden / Kerning (group 3a)

**Source:** deep T0/T1 fidelity identification (`DEEP_T0_T1_REPORT.md` §4a). Three CONFIRMED real gaps — Word's Font
dialog has these effects but the clone had **no author path**: the fork ships the `w:dstrike`/`w:vanish`/`w:kern` v3
translators, but the `textStyle` mark never declared the attrs (so `setMark` dropped them) and the dialog had no controls.

Branch: `parity-pipeline`. FIX phase.

## FR-026 — author + export + import + dialog the three effects (the 015 NO-FORK-extension pattern)
- **Owned extension** (`src/renderer/extensions/advanced-font-effects.ts`, NO fork edit): declare `dstrike`/`vanish`/
  `kern` textStyle attrs (booleans + a half-point integer threshold), with best-effort renderDOM (double line-through /
  dimmed / metadata).
- **Export + import** (fork edits, additive, NOTICE'd — `styles.js`): `decodeRPrFromMarks` forwards the three to
  `runProperties` so the existing v3 translators emit `<w:dstrike/>`/`<w:vanish/>`/`<w:kern w:val=N/>`;
  `encodeMarksFromRPr` reads them back (round-trip).
- **Dialog + bridge** (NO-FORK): `advFxAttrs`/`getAdvancedFontEffects` (bridge) gain `doubleStrike`/`hidden`/`kerningPt`
  (points → half-points); the Font dialog gets a **Double strikethrough** + **Hidden** checkbox (Effects grid) and a
  **Kerning for fonts ≥ N pt** control (Advanced tab), prefilled + applied in the one OK setMark.

### Acceptance
`run.py --only fd-double-strike` / `fd-hidden` / `fd-kerning` = **0/0** (Word-COM `Font.DoubleStrikeThrough` /
`Font.Hidden` / `Font.Kerning=8` ground truth). `test:pm` regression `026 double-strike/hidden/kerning`. Gates green.

## Remaining group-3 (3b, separate): `fd-bullet-font`, `fd-bullet-align` (Define-New-Bullet font/alignment).
