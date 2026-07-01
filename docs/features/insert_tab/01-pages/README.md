# Insert > Pages — group feasibility index

Per-button build/keep/remove feasibility for the **Insert > Pages** ribbon group.
Each button has its own doc with the full template (real-Word behavior, current clone
state, engine verdict, required structures, open questions, decision).

All three controls trace to **real `WC.PM` bridge writes** (no toast/no-op). The fork
already has every node type and converter handler they need — this group is the most
complete in the Insert tab.

| Button | Verdict | Size | Required structure (one line) |
|--------|---------|------|-------------------------------|
| [Cover Page](./cover-page.md) | ✅ Already works (shallow) | S–M | reuse `documentPartObject` node + `translate-document-part-obj.js` handler; richer designs ride the Shapes (`wps:sp`) engine — NO-FORK |
| [Blank Page](./blank-page.md) | ✅ Already works | S | reuse `paragraph` + `paragraphProperties.pageBreakBefore` + `pageBreakBefore-translator.js` — NO-FORK (deliberate +1-page model) |
| [Page Break](./page-break.md) | ✅ Already works | S | reuse `paragraph.pageBreakBefore` (live) ↔ `w:br w:type="page"` via `br-translator.js` — NO-FORK |

## Group takeaways
- **No fork edits needed** for any of the three — every node (`documentPartObject`,
  `paragraph.pageBreakBefore`, `hardBreak[lineBreakType:'page']`) and every converter
  handler already exists.
- **Cover Page** is the only one worth a build decision: it works and round-trips, but
  the inserted SDT is a 3-paragraph placeholder vs Word's rich, shape-laden gallery
  building blocks. Enhancing it is additive (more node JSON + the existing Shapes
  engine), not a new subsystem.
- **Blank Page / Page Break** carry deliberate, documented model deviations
  (a single `pageBreakBefore` paragraph rather than inline `w:br` runs) for caret
  visibility in the paged engine. The open questions are about *fidelity choices*, not
  feasibility.
