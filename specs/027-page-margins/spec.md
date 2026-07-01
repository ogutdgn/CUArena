# 027 — Independent page margins (group 4a)

**Source:** deep T0/T1 fidelity identification (`DEEP_T0_T1_REPORT.md` §4a). `fd-margin-uniform` — Word's Page
Setup → Margins sets **Top/Bottom/Left/Right independently**; the clone's Custom Margins dialog had a **single
uniform "Margin (inches)" field** applied to all four sides. The bridge `dePageMargins` already supports distinct
sides (proven by `fd-margin-top`/`fd-margin-left` = 0/0) — **only the dialog UI was the gap**. NO-FORK.

## FR-027 — Custom Margins dialog: 4 independent inputs
- `customMarginsDialog` (`src/renderer/public/js/commands.js`): replace the one uniform input with Top/Bottom/Left/
  Right number inputs (a 2×2 grid), passing the distinct values straight to `WC.PM.dePageMargins({top,bottom,left,right})`.
  The uniform `--page-margin` CSS var is set to the smallest side (best-effort visual; `dePageMargins` → body sectPr
  `w:pgMar` is the faithful export + paged relayout).
- Expose `WC.Dialogs.customMargins` (was flyout-only) — consistent with the other `WC.Dialogs.*`, and directly testable.

### Acceptance
`test:pm` regression `027 Custom Margins dialog sets independent Top/Bottom/Left/Right` — opens the dialog, asserts
≥4 number inputs, sets distinct T/B/L/R, and asserts the export carries distinct `<w:pgMar w:top/bottom/left/right>`
(1.25/0.75/1.5/0.5 in → 1800/1080/2160/720 twips). Gates: test:pm 513/513, test:roundtrip 27/0. (No `run.py` task —
this is a dialog-completeness/flow gap; the per-side OOXML is already 0/0 via `fd-margin-top`/`fd-margin-left`.)

## v1 note
Gutter + header/footer-from-edge fields are not added (out of scope); the 4 core sides match Word's common case.

## Remaining group 4: `fd-special-replace` (^p/^t/^l in the Replace box → parse a Slice; touches the fork replace cmd).
