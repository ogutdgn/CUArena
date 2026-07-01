# 029 — Define New Bullet: font + alignment (group 3b)

**Source:** deep T0/T1 fidelity identification (`DEEP_T0_T1_REPORT.md` §4a, adversarially verified). Two CONFIRMED
real gaps in the Define-New-Bullet dialog:
- `fd-bullet-font` — the clone had no font picker AND `applyListDefinition` unconditionally **stripped `w:rFonts`**,
  so a Symbol/Wingdings bullet was unreachable.
- `fd-bullet-align` (narrowed by review) — the clone DOES emit `w:lvlJc=left` (Word's default), but there was no
  control for a non-default **Centered/Right** alignment.

Branch: `parity-pipeline`. FIX phase.

## FR-029 — author the bullet font + alignment (additive)
- `core/commands/applyListDefinition.js` (fork edit): per overridden level, `if (lvl.align) setChild('w:lvlJc',
  lvl.align)`; `if (lvl.font)` keep/set `w:rFonts` (ascii/hAnsi/cs = font) in the level's `w:rPr`, `else` strip it as
  before (literal Unicode glyph). ADDITIVE — callers not passing `font`/`align` are unchanged.
- `defineNewBulletDialog` (`commands.js`, NO-FORK): a Font `<select>` (''/Symbol/Wingdings/… ; '' = normal text) + an
  Alignment `<select>` (Left/Centered/Right); OK passes `{ fmt:'bullet', text, align, font? }`.

### Acceptance — test:pm numbering.xml (NOT run.py 0/0)
These land in numbering.xml; the COM `ApplyBulletDefault` ground truth is a **single-level artifact** (the same
COM≠ribbon issue that keeps the `bullets`/`numbering` tasks off 0/0), so a `run.py --only` measurement can't reach
0/0. Verified instead by `test:pm` `029 Define New Bullet font + alignment` — walks the exported numbering.xml and
asserts the bullet level 0 carries `<w:rFonts w:ascii="Wingdings">` + `<w:lvlJc w:val="center">`. Gates: test:pm
515/515 (incl. the existing `[2] EXPORT: bullet/numbered list` unaffected), test:roundtrip 27/0.

## 🏁 With this, ALL 10 verified real gaps from the deep T0/T1 identification are fixed.
