# Step 4 — Priority: why the layers fall where they do

**A priority is arithmetic, not a vibe.** Every node's layer comes from a recorded weighted sum
of three signals — connectivity (0.30), usage (0.40), audience (0.30) — cut at recorded
boundaries (`layers.json`). All inputs are auditable: `priority/signals/connectivity.json`
(deterministic degree centrality over the affects/uses graph), `priority/signals/audience.json`
(lookup from each node's `audience_breadth`), `priority/signals/usage.json` (web-researched,
every entry carrying a claim + source URL). Boundary nodes (the Home-tab groups we deliberately
never pressed — Voice, Editor, Adobe Acrobat, Add-ins) are floored to P4, because depth is
excluded for them by policy and they must not claim a budget we won't spend.

## Why the top layer (P0) is P0
**P0 = Bold, Font Size, Font.** These are the three nodes that are simultaneously (a) used by
*everyone* (audience 1.0), and (b) the most-used commands in Microsoft's own CEIP telemetry —
Bold is the #5 most-executed command in Word and the only text-format command in the top five;
"Change Font Size" is #11; choosing a typeface is the foundational everyday formatting action.
They score highest because two independent signals (real usage + universal audience) both max
out. A human who knows Word will agree: if you had to name the three things every Word user does
constantly, "make it bold, change the size, change the font" is exactly that set.

## Why P1–P2 next
**P1** adds the rest of the daily-driver formatting and editing: Italic, Underline, Copy, Paste,
Cut, Align Left/Center, Font Color, Find — plus the Font and Clipboard *feature* nodes. All are
everyone-audience with high/very-high usage. **P2** captures the structural workhorses and the
consolidation hubs: the Paragraph and Styles features, Bullets/Numbering, Quick Styles, Line
Spacing, and the **Font dialog / Paragraph dialog** — the latter two rank here on *connectivity*
(degree 14 and 12: every character/paragraph control consolidates into them), even though their
own usage is modest. That is the connectivity signal doing its job: the dialogs are structurally
central to everything that renders text.

## Why the bottom (P4) is P4
P4 is niche-or-specialized (Sort, Subscript/Superscript, Text Effects, Office Clipboard,
Multilevel List, Change Case, Show/Hide ¶, Styles pane) plus every boundary/add-in node
(Dictate, Editor, Create a PDF, Add-ins). These have low/rare usage, narrow audience, and little
structural centrality — and the add-in/AI ones are policy boundaries. Breadth was their budget.

## Sanity check
The ranking passes the common-sense test for a word processor: the things every user touches
constantly (bold, font, paste, alignment, find, headings) outrank installation-specific or niche
tools (sort, subscript, the add-in store). Nothing obviously-central is buried and nothing niche
is inflated. Layer counts: P0=3, P1=11, P2=10, P3=10, P4=20.
