# Tables → Real-Word Parity Loop

Goal (user directive): the clone's **Table** feature — behavior, functionality, ribbon UI,
UI flows, ribbon buttons, ribbon design — must be **the same as real MS Word**, and a real-Word
`.docx` round-trips into the clone unchanged. Verify in the **live UI**, not just exported XML.

## Ground-truth capture toolkit (both confirmed working)
- **Real Word ribbon** → `parity/oracle/_capture_word_ribbon.ps1 -Tab '<name>' -Out <png>`
  (visible Word via COM, UIA clicks the contextual tab, PrintWindow → PNG). PID-safe.
- **Clone ribbon** → `scripts/ribbon-shot-probe.js` via `electron . --shot=<png> --shot-evalfile=... --shot-delay`
  (inserts a table, activates the tab, dumps controls + screenshot).
- Behaviour ground truth: `parity/oracle/*` COM + ExecuteMso.
- Read both PNGs to eyeball; diff structure via the DOM dump.

## Phases (each: build → clone-vs-Word screenshot diff → /code-review → gates)
1. **Table Design tab UI parity** — labeled 2-col checkbox Table Style Options; inline Table
   Styles gallery + More + Shading; Borders group = Border Styles / Line Style / Line Weight /
   Pen Color (labeled) / Borders / Border Painter + launcher; real icons + labels throughout.
2. **Table Layout tab UI parity** — Table / Draw / Rows&Columns / Merge / Cell Size / Alignment /
   Data with Word's labeled buttons, spinners (Height/Width), and layout.
3. **Functional correctness (live)** — every control applies to the selection and REPAINTS:
   borders visible on the cell, Table Style Options render banding/header, shading, alignment.
4. **Table layout** — new table fits the page; adding columns redistributes within the margins
   (Word's AutoFit-to-window default); no page overflow.
5. **Round-trip fidelity** — a real-Word `.docx` (styled table, banding, borders) imports to the
   clone visually + structurally identical.
6. **Full sweep** — drive every table control end-to-end live; fix every bug; /code-review.

## Status
- P0 DONE: capture toolkit built + baseline captured. Clone Table Design tab = unlabeled icons,
  no gallery (confirmed against real Word). Starting P1.

## Progress log
- **P1 Table Design UI → Word parity DONE** (`c498c6b`): labeled 2-col checkbox Table Style
  Options, inline Table Styles gallery + Shading, Borders group (Border Styles/Line Style/
  Line Weight/Pen Color/Borders/Border Painter) all labeled. Verified clone-vs-Word screenshots.
- **Table overflow on add-column FIXED** (`70dd581`): re-fit to page text width when columns
  overflow (was 24360 twips on a 9360 page → now 9360). Verified live (13 equal cols in-page).
- REMAINING: (a) Table Styles GALLERY CATALOG — clone has only 2 table styles vs Word's ~105
  (extract the built-in catalog from Word + mint into styles.xml); (b) LAYOUT tab UI parity
  (same per-group render pattern); (c) BORDERS apply-live to the selected cell + REPAINT (user:
  "don't change anything in selected cell") — investigate the paged repaint/dispatch; (d)
  conditional-format RENDERING so Table Style Options show banding/header; (e) tblW=pct→auto
  refinement on the overflow fix; (f) round-trip a real-Word styled-table docx; (g) full
  end-to-end sweep of every control + adversarial review.
