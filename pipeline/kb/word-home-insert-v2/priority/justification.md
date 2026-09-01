# Priority justification (Step 4 proof)

**Weights:** product-purpose 0.45 · web-usage 0.30 · UI-prominence 0.25 (recorded in
`priority.json`). **Boundaries:** P0 ≥ 0.80, P1 ≥ 0.68, P2 ≥ 0.55, P3 ≥ 0.38, else P4.
Only sub-features are scored; feature rows are derived (layer = best child, ratio → scope).
Value = usage only; connections are logistics (closure), never scored.

## Why the top layer is the top layer

P0 = **Paste, Copy, Font Size, Font, Bold, Insert Pictures, Table** (+ their parent features
Clipboard, Font, Illustrations, Tables). Word is a word processor whose core job is *creating
and formatting text documents*. These seven are the irreducible moves of that job: you cannot
compose a document without moving content (Paste — measured indispensable, and Microsoft's own
telemetry ranks it the #1 command of all; Copy #3), you cannot format text without choosing its
typeface, size and primary emphasis (Font, Font Size, Bold — Bold is the #5 command overall and
the only formatting command in the telemetry top-5), and the two most common structural
artifacts a document gains are images and tables (Insert Pictures, Table). Every one is
indispensable by product-reasoning **and** top-tier by web usage **and** large-and-first on the
ribbon face — all three signals agree (0 strong disagreements across the whole ranking).

## Three things that stayed LOW — and why that's obviously right

- **`subfeature:editor` (P4)** — the cloud proofing pane is a quality aid delivered by an
  external service; the core job (writing a formatted document) is complete without it. Boundary.
- **`subfeature:icon-insert` (P4)** — stock icon graphics stream from the Office CDN; pure
  decoration a niche of documents ever use. Product-reasoning: peripheral; web: rare.
- **`subfeature:table-insert-cells` (P4)** — inserting individual cells with a shift is a rare
  table op, correctly far below the everyday Insert Rows / Insert Columns / Delete (all P1).

## Closure (logistics, not value)

`subfeature:bookmark-insert` ranks P4 on its own usage, but is pulled into the replication set
by `subfeature:insert-link` via a measured `requires` edge (in-document hyperlinks target
bookmarks) — it gets "enough to work" depth, labelled `pulled-in-by`. No connection density
entered any value score.
