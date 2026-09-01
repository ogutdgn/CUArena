# Step 4 — Priority justification (word-4tabs-v1)

Scope: HOME + INSERT + DESIGN + LAYOUT ribbon tabs + the contextual tabs/surfaces they summon.

Weights and boundaries are the **pipeline defaults** (playbook 04 R4.5), unmodified:
product-purpose **0.45** · web-usage **0.30** · UI-prominence **0.25**; boundaries
P0 ≥ 0.80 · P1 ≥ 0.68 · P2 ≥ 0.55 · P3 ≥ 0.38. No deviation → no `deviations` note.

Value is **usage only** (product-purpose reasoning + web corroboration + the designer's
prominence bet). Connections were used for **logistics** (closure) and never added to any
score. Layer counts: **P0 11 · P1 34 · P2 27 · P3 106 · P4 54** (189 scored sub-features +
5 boundary floored to P4, plus derived feature rows).

## Why the top layer is right (a human who knows Word can check this)

P0 is the irreducible core of "typing and formatting a document": **Paste** (the app's own
CEIP telemetry ranks it the #1 command of all), **Copy**, **Font** and **Font Size** (choosing
the typeface/size is the first act of formatting text), **Bold** (the single most-used
character format), plus the two core insert artifacts **Pictures** and **Tables** — with their
parent features (Clipboard, Font, Illustrations, Tables) derived to P0 from those children. Every
P0 node scores ≥ 0.80 on all three signals agreeing; none is there on prominence alone. This is
exactly the set a Word clone must ship first, and nothing surprising sneaked in.

The DESIGN/LAYOUT ground this run adds ranks sensibly against the same bar: **Margins P1** and
**Orientation / Breaks P2** are the everyday page-setup levers (Margins is a near-universal
page-setup choice; landscape/breaks are common in multi-page work), while the Design tab's theme
machinery (**Themes / Watermark / Page Borders P3**) is real but occasional polish — the tab most
users leave at its default. `feature:page-setup` derives to **P1** (best child Margins), so the
Layout tab's core enters full depth.

## Three things that stayed LOW — and why that is obviously right

- **`subfeature:hyphenation` (P4, 0.289)** — automatic hyphenation is off by default and rarely
  toggled by typical users; peripheral by product-purpose, rare by usage, buried on the Layout
  tab. A Word clone that shipped without it loses nothing for the core job.
- **`subfeature:set-as-default` (P4, 0.257)** — saving current formatting as the template default
  is a one-time power action, not a document-authoring capability. Peripheral + rare + buried.
- **`subfeature:equation-ink` (P4)** — hand-writing an equation with the pen is a niche input
  mode inside an already-niche capability (the Equation contextual tab); the web is silent on it
  and product-purpose reasoning calls it peripheral. Correctly outside the depth budget.

Cohesion (R3.5/R4.7): the **catalog** features (Editing, Pages, Illustrations, Links, Text,
Symbols, Page Background) never replicate whole even when a majority of their children rank high
(e.g. Editing = 2/3 high → **gems**, not whole — Find/Replace get depth, Select does not). Only
**capability** features go whole (Clipboard, Comments, Header & Footer, Object Size, Shape Styles,
Tables), so their whole-group children enter the depth set.

Closure pulled in **`subfeature:bookmark-insert`** (in-document hyperlinks jump to bookmarks) and
**`subfeature:icon-insert`** (the Graphics Format contextual tab exists only after an SVG/icon is
inserted) at "enough to work" depth — their P4 layer is unchanged; only their replication-set
membership is.
