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

## Iteration 1 complete (2026-07-01)
DONE this iteration (all gated test:pm 533 / roundtrip 27, verified LIVE via screenshots):
- Capture harness (clone `ribbon-shot-probe.js` + real Word `_capture_word_ribbon.ps1`).
- Table Design tab UI → Word parity (checkboxes / gallery / labeled borders) — `c498c6b`.
- Table overflow on add-column FIXED (re-fit to page) — `70dd581`.
- Borders CONFIRMED working live (apply + repaint, direct + ribbon path). No Border now
  writes val=nil so it actually removes the visible border (was leaving the style border) — `e96434e`.

NEXT ITERATIONS (priority order):
1. LAYOUT tab UI → Word parity (capture real Word Table Layout, rebuild groups: labeled
   buttons, Height/Width spinners, Select/Properties, Draw, Data). Same render-method pattern.
2. Table Styles GALLERY CATALOG — extract Word's ~105 built-in table styles (COM: apply each
   to a table + save + extract styles.xml) and mint them into the clone so the gallery is full
   + they apply. Big data task.
3. Border TOGGLE semantics (Word toggles a border off if already present) + Line Style/Weight/
   Pen Color affect the drawn border live.
4. Conditional-format RENDERING so Table Style Options (banding/header/first-col) show live.
5. Round-trip: import a real-Word styled-table .docx, confirm identical (visual + structure).
6. Full end-to-end sweep of every table control (live) + adversarial review; fix all bugs.

## Iteration 2 (2026-07-01)
DONE: Table LAYOUT tab UI → Word parity (`a31fd01`) — labeled large buttons for Table/Draw/
Rows&Columns/Merge/Data, AutoFit+Height/Width+Distribute Cell Size, 3x3 align grid + Text
Direction/Cell Margins, Word's exact labels (Insert Row Above etc.). Added `--shot-maximize`
so captures reflect the maximized window (labels condense only when narrow, like Word).
Verified maximized clone Layout tab mirrors real Word. test:pm 533.

KEY FINDING: the ribbon condenses (hides large labels) when the window is narrow (1440px);
at maximized (1920px) it shows labels like Word. So capture with --shot-maximize.

NEXT (updated priority):
1. ICONS — both table tabs use generic minus-in-box icons; Word has specific per-command icons
   (Select/Properties/Insert/Merge/Split/AutoFit/Align/Sort/Formula…). Map the ~40 tbl* cmds to
   Fluent icons (WC.icon / icons-fluent). HIGH visual impact ("random icon" complaint).
2. Table Styles GALLERY CATALOG (~105 built-in styles).
3. Border TOGGLE semantics + Line Style/Weight/Pen Color affect the drawn border.
4. Conditional-format RENDERING (banding/header live).
5. Round-trip a real-Word styled-table .docx.
6. Full sweep + adversarial review.
