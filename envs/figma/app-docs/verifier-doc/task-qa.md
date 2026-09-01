# delivery-1 Task QA — Achievability Audit

**Audit date:** 2026-05-07
**Scope:** All 50 tasks in `apps/figma/delivery-1/`
**Question:** For each task, is a perfect 1.0 score reachable? If not, why?

This audit was done by reading every `verifier.py` file and cross-checking each check against the actual mock implementation (event names emitted, layer defaults, panel capabilities). Findings cite mock and verifier files by `path:line` so they can be re-verified.

---

## Scoring model recap

```
final_score = base_score × multiplier
base_score  = sum of WeightedRubric scores (each scaled to its max_score; total = 1.0)
multiplier  = 0.5 + 0.5 × exp(-λ × max(0, actual_turns - target_turns))    λ default 0.05
```

`actual_turns ≤ target_turns` ⇒ multiplier 1.0. Below target gives no extra credit. Multiplier floor 0.5. So 1.0 requires (a) every check satisfiable with mock primitives, (b) `actual_turns ≤ target_turns` plausibly reachable.

---

## Cross-cutting mock realities

These affect more than one task. Each is the **mock as-is** behavior, not a verifier bug — but verifiers that don't account for them become unreachable.

1. **Pen tool emits `create_vector_with_pen`, pencil emits `create_vector_with_pencil`** — `apps/figma/mock/src/tools/pen.ts:496`, `apps/figma/mock/src/tools/pencil.ts:142`. There is no plain `create_vector` event. Verifiers asking for `create_vector` permanently score 0 on that check (`apps/figma/verifier/checks/event_checks.py:6` does exact name match).

2. **Line tool hard-codes `rotation: 0`** — `apps/figma/mock/src/tools/line.ts:43`. Lines drawn at any visual angle still have `rotation === 0` because direction is encoded in `p1`/`p2`. Any check that reads `layer.rotation` for line layers (`LayersEvenlyRotated`, `LayersHaveRotations` — both use `l.get("rotation", 0)` per `geometry_checks.py:657, 937`) sees all-zeros for natural drawing. Workaround: draw stacked lines at one position then rotate each via the panel (`set_property → rotate_layer` event from `propertyCommands.ts:79`).

3. **`LayersConcentric` reads bounding-box center** (`geometry_checks.py:361`). For "radial lines from a center point" drawn naturally (each line goes outward from origin to a peripheral point), every line's bbox center is at the line midpoint — different per angle. So natural radial-line layouts fail `LayersConcentric`. To pass, lines must be drawn so their bboxes share a center (e.g., diameters that cross center, or stacked at one location).

4. **Auto-revert-to-move tax** — every shape creation triggers an extra `tool_change` event with `trigger: "auto_revert_after_create"` (e.g. `apps/figma/mock/src/tools/creationBbox.ts:148`, `pencil.ts:158`, `line.ts:200`). So drawing N shapes = `1 + 2N` tool/create events at minimum, before any property edits. Several `🟡 Tight` verdicts below trace to this tax pushing optimal counts above `target_turns`.

5. **Duplicate doesn't emit `create_*`** — `commands.ts:177` emits `name: "duplicate"`. So `EventTypeCount("create_X", equals=N)` cannot be satisfied via duplicate; user must draw each instance fresh.

6. **`EventTypeCount(create_X, equals=N)` is monotonic** — once N+1 creates are logged, deletion does not decrement. ~35 tasks use this pattern, so any over-shoot during exploration permanently caps the Event rubric.

7. **Default fills by layer type:**
   - rectangle, ellipse, polygon (gray `polygon.ts:14`), star, frame: ship with **one solid fill by default** → `FillTypeIs(<type>, "solid")` passes for free if any such layer exists.
   - vector (pen/pencil): ships with **empty `fills: []`** → `FillTypeIs("vector", "solid")` requires explicit `add_fill` + `set_fill_color` per vector (tasks 42, 49 use this).
   - `LayerHasNoFill(<type>)` for rectangle/ellipse/polygon requires explicit `remove_fill` (tasks 38, 41, 48 use this).

8. **Polygon default `sides = 3`** (`polygon.ts:13`). Tasks needing 6-sided hexagons (35, 48) require N×set-sides property edits via the panel.

9. **Stars and polygons gain `rotation` when rotated via panel** (`propertyCommands.ts:79` — `set_property → rotate_layer`). Unlike lines, polygon/star rotation is honored by `LayersEvenlyRotated` / `LayersHaveRotations`. So tasks 17, 27, 32 are fine.

10. **`tidy_up` semantic event exists** (`alignmentCommands.ts:417`) but the AlignmentRow.tsx button is `disabled visualOnly` (`apps/figma/mock/src/ui/panels/AlignmentRow.tsx:44`). No verifier in delivery-1 actually checks for `tidy_up`, so this is only relevant if a prompt insists on it (e.g. task 9 prompt mentions "Tidy up" but verifier ignores it).

11. **Set of all `create_*` semantic events the mock can emit:** `create_rectangle`, `create_ellipse`, `create_polygon`, `create_star`, `create_line`, `create_arrow`, `create_frame`, `create_section`, `create_slice`, `create_text`, `create_vector_with_pen`, `create_vector_with_pencil`, `create_page`, `create_prototype_connection`. Anything else asked by name is unreachable.

---

## Summary table

| Task | Title (from prompt) | Verdict | Achievable cap | Key blockers / risks |
|---|---|---|---|---|
| 01 | Two-story house | ✅ Clean | 1.0 | target=30 fits 5 creates + colors + structure with margin |
| 02 | Sunset stripe band | 🟡 Tight | 1.0 | 5 rects + LayersHaveColorOrder; target=24 with auto-revert tax tight |
| 03 | Radial flower | ✅ Clean | 1.0 | 9 creates radial + colors; target=30 OK |
| 04 | Color hexagon ring | 🟡 Tight | 1.0 | 6 creates radial + colors; target=24 |
| 05 | Plus-sign emblem | ✅ Clean | 1.0 | 2 rects only; target=15 ample |
| 06 | Asterisk burst (8 lines @ 45°) | ⚠️ Partial | 0.67 natural / 1.0 only via stacked-rotate workaround | line rotation hardcoded 0 (§2) **and** radial layout fails LayersConcentric (§3); workaround at target=24 is achievable but contrived |
| 07 | Layered gray mountain range | ⚠️ Partial | 0.835 | `EventTypeCountAtLeast("create_vector", 2)` — mock emits `create_vector_with_pen` (§1). Hard cap, no workaround. |
| 08 | Layered water waves | ✅ Clean | 1.0 | uses correct `create_vector_with_pen`; DistinctStrokeColors needs explicit stroke color set on each vector |
| 09 | 12 colored squares 4×3 grid | 🟡 Tight | 1.0 | 12 creates + 12 fills + grid arrange; target=36 leaves ~12 events for arrangement (auto-revert tax = 24+ events from drawing alone) |
| 10 | 4 nested concentric squares | ✅ Clean | 1.0 | target=18 fits 4 draw + 4 fill + center-align |
| 11 | 3 concentric polygons | ✅ Clean | 1.0 | target=18 |
| 12 | 4 cards in row | ✅ Clean | 1.0 | target=18 |
| 13 | Hashtag # (4 lines) | ⚠️ Partial | 0.67 natural / 1.0 with rotate workaround at target=14 | line rotation hardcoded 0 (§2) — `LayersHaveRotations(line, [0,90], count_per=2)` cannot match naturally-drawn vertical lines (all 4 have rotation=0). Workaround: draw 4 horizontal lines, rotate 2 by 90° via panel. Target=14 leaves ~6 events of slack. |
| 14 | Concentric ring target | ✅ Clean | 1.0 | 4 ellipses concentric+circular+stacked; target=20 |
| 15 | Cloud silhouette | 🟡 Tight | 1.0 | target=14, 4 ellipses + same fill (already default if all white set once) |
| 16 | Speech bubble | ✅ Clean | 1.0 | rect+polygon, same color, corner-radius set on rect |
| 17 | Hourglass | ✅ Clean | 1.0 | polygon rotation works via panel (§9); 2 rotates needed at target=20 |
| 18 | Eye icon (3 nested ellipses) | ✅ Clean | 1.0 | concentric+circular+inside; target=15 tight but doable |
| 19 | Padlock | ✅ Clean | 1.0 | rect+vector+ellipse; target=30 ample |
| 20 | Glow blob backdrop | ✅ Clean | 1.0 | frame + 2 ellipses + `PageBackgroundColorEquals` (mock supports `set_page_background` via PageSection panel) |
| 21 | Vertical icon column | ✅ Clean | 1.0 | 3 stacked rects with gap=8; LayersStacked tolerance ample |
| 22 | Tag pill row | ✅ Clean | 1.0 | 4 same-size + corner ≥ 24 + 4 colors |
| 23 | Sidebar layout | ✅ Clean | 1.0 | frame + 1 sidebar rect width fraction; target=18 |
| 24 | Centered modal rect | ✅ Clean | 1.0 | frame + 1 rounded rect centered via align; target=20 |
| 25 | Identical button row | ✅ Clean | 1.0 | 3 same-size rects; target=15 — duplicate cannot emit create event so each must be drawn |
| 26 | Brand color row (5 squares) | ✅ Clean | 1.0 | 5 same-size + 5 distinct colors; target=20 |
| 27 | Layered diamond (3 rotated squares) | ✅ Clean | 1.0 | 3 rotates via panel + concentric; target=24 |
| 28 | Photo placeholder + diagonal lines | ✅ Clean | 1.0 | LinesOnDiagonal uses endpoints not rotation — line tool ✅ |
| 29 | Polka-dot 2×2 grid | 🟡 Tight | 1.0 | 4 ellipses must be circular AND in grid AND same dim; target=20 tight |
| 30 | Vertical stripe wallpaper | 🟡 Tight | 1.0 | 6 rects in frame + alternating colors + stacked; target=20 tight |
| 31 | Sun rays (1 ellipse + 8 polygons) | 🟡 Tight | 1.0 | 8 polygon creates + 1 ellipse + frame + LayersSameDimensions(polygon); auto-revert tax: 8×2+1 ≈ 18 events from draws alone, target=30 leaves ~12 events |
| 32 | 4-blade pinwheel | 🟡 Tight | 1.0 | polygon rotation works (§9) but 4 rotates + radial placement + 4 colors at target=25 tight |
| 33 | 4-section pie chart | ✅ Clean | 1.0 | very loose — only counts + circular + fills checked; target=40 generous |
| 34 | 6-fold snowflake | ✅ Clean | 1.0 | only counts checked, no rotation/concentric on lines; target=35 ample |
| 35 | Honeycomb 3×2 hexagons | 🟡 Tight | 1.0 | polygon defaults to 3 sides — 6 set-sides property edits required + OffsetGridLayout placement; target=30 |
| 36 | Vintage frame (2 nested rects) | ✅ Clean | 1.0 | concentric + bounds-inside; target=15 |
| 37 | Sticky note | ✅ Clean | 1.0 | rect + vector + ≥3 lines, vector inside rect bounds; target=24 |
| 38 | Battery indicator | ✅ Clean | 1.0 | 5 rects + at-least-one-no-fill; needs 1 explicit `remove_fill` |
| 39 | Wifi icon | ✅ Clean | 1.0 | 3 vectors + 1 ellipse; uses correct `create_vector_with_pen`; target=30 |
| 40 | iOS toggle switch | ✅ Clean | 1.0 | rect + ellipse + corner-radius ≥ 24 + ellipse-bounds-inside-rect; target=18 |
| 41 | Search bar | ✅ Clean | 1.0 | rect + ≥3 ellipse + ≥1 line; needs `LayerHasNoFill(ellipse)` — at least one ellipse with explicit `remove_fill`; target=40 ample |
| 42 | Bell with badge | ✅ Clean | 1.0 | uses `create_vector_with_pen` + needs `add_fill` + color on vector to satisfy `FillTypeIs("vector","solid")`; target=36 |
| 43 | Compass rose | ✅ Clean | 1.0 | 2 ellipses + 4 polygons; target=36 |
| 44 | Avatar with badge | 🟡 Tight | 1.0 | 2 ellipses both circular + on-top + overlap; target=14 tight |
| 45 | 8-point star + circle | ✅ Clean | 1.0 | star defaults to 5 points — 1 set-points edit needed; target=20 |
| 46 | 8 histogram bars | 🟡 Tight | 1.0 | 8 rect creates → 1 + 2×8 = 17 baseline events from draws + colors + alignment; target=24 leaves ~7 events |
| 47 | Sunburst stamp (16-pt star + circle) | ✅ Clean | 1.0 | star points=16 + innerRatio=0.7 — 2 property edits; target=24 |
| 48 | Spiderweb | 🟡 Tight | 1.0 | 6 lines + 3 hexagons (3×set-sides + 3×remove_fill) + frame + colors; target=36 |
| 49 | Tied ribbon | ✅ Clean | 1.0 | 1 vector + add_fill + color; target=24 |
| 50 | Star inside square | ✅ Clean | 1.0 | 1 rect + 1 5-point star (default); target=15 |

**Aggregate:** 47 ✅/🟡 → 1.0 reachable in principle (32 ✅, 15 🟡), 3 ⚠️ → hard-capped below 1.0 (tasks 6, 7, 13). Mean achievable cap (taking ⚠️ caps and assuming 🟡 tight tasks lose a small efficiency multiplier 0.95): ~0.97.

---

## Per-task analysis

Notation: `R(weight)[checks]` = WeightedRubric. ⌀ = no relevant blocker.

### Task 01 — Two-story house

- Fundamentals(0.2): rect=2, ellipse=2, polygon=1
- Alignment(0.2): ellipse aligned/same-dim/symmetric, polygon-bottom touches rect-top, rect-inside-rect, ellipse-overlaps-rect, frame size 1280×832
- Color(0.2): rect/polygon/ellipse solid + ≥4 distinct colors
- Structure(0.2): all primitives inside frame, frame has ≥5 children
- Event(0.2): rect/ellipse/polygon tools + create counts (2/2/1)
- Efficiency: target=30

All checks reachable. Default fills are solid so `FillTypeIs` passes free; only need to set 4 distinct colors. `FrameSizeEquals(1280,832,tol=10)` needs the frame drawn with frame-tool's "1280×832" preset OR resized to that. Optimal: 1 frame + 5 shape draws (5 tool changes + 5 creates + 5 auto-reverts = 16) + 4 fill changes + 4 distinct colors + alignment (manual) ≈ 25–28 events. Margin of ~2 events at target=30. **Verdict: ✅** (close to 🟡).

### Task 02 — Sunset stripe band

- Fund(0.25): rect=5
- Align(0.25): same-dim, center_x aligned, stacked y gap=0, aspect>2 horizontal, inside frame
- Color(0.25): solid + 5 distinct + `LayersHaveColorOrder` (purple→pink→orange→yellow→pale-yellow sorted by y)
- Event(0.25): rect tool + create=5
- Efficiency: target=24

Optimal: frame + 5 rect draws (1 + 2×5 = 11 tool/create events) + 5 fill colors + 5 stacking adjustments ≈ 22–25. Color-order check has tolerance 0.20 so colors don't need to be exact, just distinguishable. `LayerInsideFrame` requires drawing rects inside the frame (resolveCreationParentId handles this). **Verdict: 🟡** — at-target.

### Task 03 — Radial flower

- Fund(0.25): ellipse=9
- Align(0.25): `RadialDistributionExcludeCentral(ellipse, n=8, tol_deg=15)` — central ellipse excluded, 8 petals at evenly-spaced angles around centroid
- Color(0.25): solid + ≥8 distinct + centermost-yellow `(1.0,0.9,0.2)` tol 0.20
- Event(0.25): ellipse tool + create=9
- Efficiency: target=30

Default ellipse fills solid. Need 9 colors, one center yellow. 9 creates + tool + 9 fills ≈ 19 events + radial placement ≈ 25–28. **Verdict: ✅**.

### Task 04 — Color hexagon ring

- Fund(0.25): rect=6
- Align(0.25): same-dim, RadialDistribution(rect, n=6, tol=10°), LayerIsSquare
- Color(0.25): solid + ≥6 distinct
- Event(0.25): rect + create=6
- Efficiency: target=24

Squares same-size + arranged radially. 6 creates (13) + 6 fills + 6 placements ≈ 25. **Verdict: 🟡**.

### Task 05 — Plus-sign emblem

- Fund/Align/Color/Event each 0.25 — 2 rects, both red, perpendicular (one horizontal-aspect, one vertical-aspect, both center-aligned)
- Efficiency: target=15

`LayersHaveAspectMix(horizontal_count=1, vertical_count=1, ratio=2.0)` — need one 2:1 wide rect and one 2:1 tall rect. 2 rects + same red fill + center align ≈ 10–12 events. **Verdict: ✅**.

### Task 06 — Asterisk burst (8 lines @ 45°)

- Fund(0.34): line=8
- Align(0.33): `LayersConcentric(line, tol=10)` + `LayersEvenlyRotated(line, n=8, step=45°, tol=8)`
- Event(0.33): line tool + create_line=8
- Efficiency: target=24

**Two blockers from cross-cutting §2 + §3:**
1. Line `rotation` is always 0 → `LayersEvenlyRotated` fails for any naturally-drawn line set.
2. Lines drawn radially have different bbox centers → `LayersConcentric` fails.

Workaround: draw all 8 lines stacked at the same starting position, then panel-rotate each by 0/45/.../315°. Bbox centers stay coincident → `LayersConcentric` passes; rotations differ by 45° → `LayersEvenlyRotated` passes. Cost: 1 tool_change + 8 line creates (with auto-revert taxes = 17 events) + 8 set_property rotates + 1 select-all = ~26 events at target=24 → mild multiplier hit (~0.95).

Natural-play cap: Alignment fully fails → 0.34 + 0 + 0.33 = **0.67**. Workaround cap: 1.0 × ~0.95 ≈ 0.95. **Verdict: ⚠️ Partial** (natural). Salvageable to ✅ only with the contrived stacked-rotate workflow.

### Task 07 — Layered gray mountain range

- Fund(0.34): vector ≥ 2
- Color(0.33): vector solid + ≥2 distinct
- Event(0.33): pen tool + `EventTypeCountAtLeast("create_vector", 2)` ❌
- Efficiency: target=30

The `"create_vector"` event name does not exist in the mock (§1). The check is permanently 0, capping Event at 0.165 (only `ToolUsed("pen")` passes). Vector defaults to empty fills so each vector also needs `add_fill` + `set_fill_color`.

**Hard cap: 0.34 + 0.33 + 0.165 = 0.835**. **Verdict: ⚠️ Partial**. Fix: change to `EventTypeCountAtLeast("create_vector_with_pen", 2)` (and arguably accept `create_vector_with_pencil` too).

### Task 08 — Layered water waves

- Fund(0.34): vector ≥ 2
- Color(0.33): `DistinctStrokeColors(min=2, tol=0.05)`
- Event(0.33): pen tool + `EventTypeCountAtLeast("create_vector_with_pen", 1)` ✅ (correct name)
- Efficiency: target=40

Pen-vector default stroke = white solid. To satisfy DistinctStrokeColors need to set different stroke color on each vector → 2 stroke property edits. Generous target. **Verdict: ✅**.

### Task 09 — 12 colored squares 4×3 grid

- Fund(0.25): rect=12
- Align(0.25): same-dim + LayersInGrid(rows=3, cols=4, tol=10)
- Color(0.25): solid + ≥12 distinct (tol 0.05 — keep tones perceptually apart)
- Event(0.25): rect tool + create=12
- Efficiency: target=36

Auto-revert tax dominates: 12 rect draws = 1 + 2×12 = 25 baseline events. Add 12 fill colors and grid placement → ~45 events. Multiplier penalty at target=36: `0.5 + 0.5 × exp(-0.05 × (45−36))` ≈ 0.82. So even a perfect base score lands ~0.82 final. **Verdict: 🟡** (target is not realistic for a careful human; suggest target ≥ 50).

Note: prompt says "use Tidy up" but `tidy_up` button is disabled and verifier doesn't check for it — irrelevant to score.

### Task 10 — 4 nested concentric squares

- Fund/Align(LayersConcentric, BoundsInside)/Color/Event 0.25 each
- Efficiency: target=18

4 rects + tool changes (9) + 4 fills + 4 center-aligns ≈ 17. **Verdict: ✅** (close to 🟡).

### Task 11 — 3 concentric triangles

- Fund: polygon=3 (default 3-sided, no panel edit needed)
- Align: concentric + bounds-inside
- Color/Event standard
- Efficiency: target=18

3 polygon creates (7) + 3 fills + 3 center-aligns ≈ 13. **Verdict: ✅**.

### Task 12 — 4 cards in row

- Fund: rect=4
- Align: same-dim + center_y aligned
- Color: solid (default)
- Event: rect + create=4
- Efficiency: target=18

4 creates (9) + 1 align-center-y + position adjustments ≈ 14. **Verdict: ✅**.

### Task 13 — Hashtag #

- Fund(0.34): line=4
- Align(0.33): `LayersHaveRotations(line, expected=[0,90], count_per=2, tol=8°)`
- Event(0.33): line tool + create=4
- Efficiency: target=14

Same line-rotation blocker as task 6 (§2). Natural-drawn vertical lines have rotation=0, not 90 → check fails → Alignment 0. Cap natural: 0.34 + 0 + 0.33 = **0.67**. Workaround: draw 4 horizontal lines, rotate 2 by 90° via panel. Cost: 1 + 2×4 = 9 baseline + 2 rotates = 11. Target=14 leaves ~3 events of slack — workable but tight. **Verdict: ⚠️ Partial** (natural) / ✅ with workaround.

### Task 14 — Concentric ring target

- Fund: ellipse=4
- Align: concentric + bounds-inside + circular (each ellipse must have w≈h)
- Color: solid (default)
- Event: ellipse + create=4
- Efficiency: target=20

`LayerIsCircular` only requires *one* ellipse to be circular (`for l in layers: if w≈h: return pass`). Easy. Concentric needs all 4 to share center. 4 creates (9) + manual align ≈ 14. **Verdict: ✅**.

### Task 15 — Cloud silhouette

- Fund: ellipse=4
- Align: aligned center_y (tol=20) + overlap (between any pair)
- Color: AllSolidColorEquals(ellipse, white, tol=0.1) — every ellipse white
- Event: ellipse + create=4
- Efficiency: target=14

4 creates (9) + 4 fill→white (or set once and all default to white if user sets first then dups — but dup doesn't emit create). 9 + 4 = 13. **Verdict: 🟡**.

### Task 16 — Speech bubble

- Fund: rect=1, polygon=1
- Align: rect-polygon overlap + rect cornerRadius ≥ 8
- Color: both solid + same color across types
- Event: rect+polygon tools + create=1 each
- Efficiency: target=18

2 creates (5) + 1 corner-radius + 2 fill-same-color ≈ 9. **Verdict: ✅**.

### Task 17 — Hourglass

- Fund: polygon=2, rect=2
- Align: polygon center_x aligned + rect center_x aligned + `LayersHaveRotations(polygon, [0,180], count_per=1)` — one polygon at 0°, one at 180°
- Color/Event standard
- Efficiency: target=20

Polygon rotation IS honored (§9) — just rotate one triangle 180° via panel. 4 creates (9) + 1 rotate + 2 align-center_x ≈ 13. **Verdict: ✅**.

### Task 18 — Eye icon

- Fund: ellipse=3
- Align: concentric + bounds-inside + circular (one)
- Color: solid (default)
- Event: ellipse + create=3
- Efficiency: target=15

3 creates (7) + concentric placement + 3 fills ≈ 13. **Verdict: ✅**.

### Task 19 — Padlock

- Fund: ≥1 rect, ≥1 vector, ≥1 ellipse
- Align: ellipse-bounds-inside-rect + vector-overlaps-rect + circular ellipse
- Color: solid rect (default)
- Event: rect/pen/ellipse + uses correct `create_vector_with_pen`
- Efficiency: target=30

Pen vector with empty fills is fine here — only `FillTypeIs("rectangle","solid")` is checked, and that's free. **Verdict: ✅**.

### Task 20 — Glow blob backdrop

- Fund: ≥1 frame, ellipse=2
- Align: overlap + circular
- Color: ellipse+frame solid + ≥2 distinct + `PageBackgroundColorEquals({0.05,0.05,0.2}, tol=0.4)`
- Event: frame+ellipse + create_ellipse=2
- Efficiency: target=22

Page bg is editable via PageSection panel which emits `set_page_background` (`PageSection.tsx:32`). 1 frame + 2 ellipses (5) + 1 page bg + 2 fills + alignment ≈ 16. **Verdict: ✅**.

### Task 21 — Vertical icon column

- Fund: rect=3
- Align: same-dim + center_x + stacked y gap=8 (tol=8)
- Color: solid + ≥3 distinct
- Event: rect + create=3
- Efficiency: target=18

3 creates (7) + 3 fills + position with 8px gap ≈ 14. **Verdict: ✅**.

### Task 22 — Tag pill row

- Fund: rect=4
- Align: same-dim + center_y + cornerRadius ≥ 24
- Color: solid + ≥4 distinct
- Event: rect + create=4
- Efficiency: target=20

4 creates (9) + 4 fills + 1 corner-radius (applied once via select-all) + align ≈ 16. **Verdict: ✅**.

### Task 23 — Sidebar layout

- Fund: ≥1 frame + rect=1
- Align: rect aspect>2 vertical + width fraction 0.08–0.30 of parent frame
- Color: solid (default)
- Event: frame+rect + create_rectangle=1
- Efficiency: target=18

Very lenient. 1 frame + 1 rect (drag long-vertical inside frame) + fill ≈ 8. **Verdict: ✅**.

### Task 24 — Centered modal rect

- Fund: ≥1 frame + rect=1
- Align: rect centered in frame (tol=12) + cornerRadius ≥ 8
- Color: solid (default)
- Event: rect tool + create=1
- Efficiency: target=20

1 frame + 1 rect inside frame + 1 corner-radius + 2 align clicks (center horiz/vert) ≈ 10. **Verdict: ✅**.

### Task 25 — Identical button row

- Fund: rect=3
- Align: same-dim (tol=2) + center_y (tol=3)
- Color: solid (default)
- Event: rect + create=3
- Efficiency: target=15

3 creates (7) + 3 same-size set + 1 align ≈ 12. Note: duplicate cannot help with create-count. **Verdict: ✅**.

### Task 26 — Brand color row

- Fund: rect=5
- Align: same-dim + center_y
- Color: solid + ≥5 distinct
- Event: rect + create=5
- Efficiency: target=20

5 creates (11) + 5 fills + align ≈ 18. **Verdict: ✅** (close to 🟡).

### Task 27 — Layered diamond

- Fund: rect=3
- Align: same-dim + concentric + `LayersEvenlyRotated(rect, n=3, step=30°, tol=8)`
- Color: solid + ≥3 distinct
- Event: rect + create=3
- Efficiency: target=24

Rectangle rotation honored via panel. 3 creates (7) + 3 fills + 3 rotates (0/30/60) + concentric align ≈ 16. **Verdict: ✅**.

### Task 28 — Photo placeholder + diagonal X

- Fund: rect=1, line=2
- Align: `LinesOnDiagonal(rect, line, tol=12)` — uses line endpoints, not rotation
- Color: rect solid (default)
- Event: rect+line + create=1/2
- Efficiency: target=15

Bypasses the line-rotation issue entirely (endpoint-based check). 1 rect + 2 lines (corner-to-corner drags) ≈ 8. **Verdict: ✅**.

### Task 29 — Polka-dot 2×2 grid

- Fund: ellipse=4 + ≥1 frame
- Align: same-dim + LayersInGrid(2,2) + circular
- Color: solid (default)
- Event: ellipse + create=4
- Efficiency: target=20

1 frame + 4 circle draws (9) + grid arrange ≈ 16. Tight because circles must be both same-size AND in grid AND each circular. **Verdict: 🟡**.

### Task 30 — Vertical stripe wallpaper

- Fund: rect=6 + ≥1 frame
- Align: same-dim + center_y + stacked x gap=0 + aspect>2 vertical + `LayersAlternatingColors(2)`
- Color: solid (default)
- Event: rect + create=6
- Efficiency: target=20

1 frame + 6 rect draws (13) + 2 alternating fills (set 6 times) + alignment ≈ 22. **Verdict: 🟡**.

### Task 31 — Sun rays

- Fund: ellipse=1, polygon=8, ≥1 frame
- Align: polygon same-dim + ellipse circular
- Color: solid for both (default)
- Event: ellipse+polygon + create_ellipse=1, create_polygon=8
- Efficiency: target=30

No rotation/distribution check on polygons! Just same-dim + count. So 8 triangles arranged radially-ish, no need for them to be rotated 45° each. 1 frame + 1 ellipse + 8 polygon draws (1 + 2 + 17 = 20) + arrangement ≈ 24–28. **Verdict: 🟡**.

### Task 32 — 4-blade pinwheel

- Fund: polygon=4, ellipse=1, ≥1 frame
- Align: polygon same-dim + RadialDistribution(n=4, tol=15°) + `LayersEvenlyRotated(polygon, n=4, step=90°, tol=8)` + ellipse circular
- Color: polygon solid (default)
- Event: polygon + create_polygon=4, create_ellipse=1
- Efficiency: target=25

Polygon rotation honored. 1 frame + 5 creates (1 + 2×5 = 11) + 4 rotates (0/90/180/270) + radial placement + ellipse fill ≈ 22. **Verdict: 🟡**.

### Task 33 — 4-section pie chart

- Fund: ellipse=1, polygon=3
- Align: ellipse circular only
- Color: both solid (default)
- Event: ellipse+polygon + create=1/3
- Efficiency: target=40

Very loose. **Verdict: ✅** (no risk).

### Task 34 — 6-fold snowflake

- Fund: ≥1 frame + ≥6 lines
- Color: frame solid (default)
- Event: line + create_line ≥ 6
- Efficiency: target=35

No rotation/distribution check on lines. Only counts. 1 frame + 6 lines ≈ 14 events. **Verdict: ✅** (very loose).

### Task 35 — Honeycomb

- Fund: polygon=6 + `PolygonSidesEquals(sides=6)`
- Align: same-dim + `OffsetGridLayout(rows=2, cols=3, tol=15)`
- Color: solid (default)
- Event: polygon + create=6
- Efficiency: target=30

Polygons default to 3 sides (§8). PolygonSidesEquals checks ALL polygons → user must change sides on each. Either change first then duplicate (but dup doesn't emit create — must draw 6) or 6 separate set_property edits. 6 polygon creates (13) + 6 sides edits (or 1 if user changes default first; need to verify — I believe it's per-instance) + 6 fills + grid placement ≈ 25–28. **Verdict: 🟡**.

### Task 36 — Vintage frame

- Fund: rect=2
- Align: concentric + bounds-inside
- Color: solid (default)
- Event: rect + create=2
- Efficiency: target=15

2 rects + concentric align ≈ 8. **Verdict: ✅**.

### Task 37 — Sticky note

- Fund: rect=1, ≥1 vector, ≥3 lines
- Align: vector-bounds-inside-rect (tol=4)
- Color: rect solid (default)
- Event: rect+pen+line + create_rect=1, create_line ≥ 3 (no `create_vector_with_pen` count check)
- Efficiency: target=24

1 rect + 1 vector + 3 lines ≈ 13 events + alignment ≈ 18. **Verdict: ✅**.

### Task 38 — Battery indicator

- Fund: rect=5
- Align: `LayerHasNoFill(rectangle)` — at least one rect with no visible fill
- Color: rect solid (passes — at least one rect has solid fill among the 5)
- Event: rect + create=5
- Efficiency: target=24

Need ≥1 rect with explicit `remove_fill`. 5 creates (11) + 1 remove_fill + 4 fills + alignment ≈ 21. **Verdict: ✅** (close to 🟡).

### Task 39 — Wifi icon

- Fund: ≥3 vector + ellipse=1
- Color: ellipse solid (default; no fill check on vectors!)
- Event: pen+ellipse + `create_vector_with_pen` ≥ 1, create_ellipse=1
- Efficiency: target=30

Vectors don't need fills checked. 3 vectors + 1 ellipse ≈ 12 events. **Verdict: ✅**.

### Task 40 — iOS toggle switch

- Fund: rect=1, ellipse=1
- Align: ellipse-inside-rect + cornerRadius ≥ 24
- Color: both solid (default)
- Event: rect+ellipse + create=1/1
- Efficiency: target=18

2 creates (5) + 1 corner-radius + 2 fills + position ellipse on right ≈ 11. **Verdict: ✅**.

### Task 41 — Search bar

- Fund: rect=1, ≥3 ellipse, ≥1 line
- Align: `LayerHasNoFill(ellipse)` + circular
- Color: rect solid (default)
- Event: rect+ellipse+line + counts
- Efficiency: target=40

Need ≥1 ellipse with explicit `remove_fill`. 1 rect + 3 ellipses + 1 line ≈ 13 events + remove_fill + 3 alignments ≈ 18. Generous target. **Verdict: ✅**.

### Task 42 — Bell with badge

- Fund: ≥1 vector, ≥2 ellipse
- Align: ellipse circular
- Color: vector solid + ellipse solid
- Event: pen+ellipse + `create_vector_with_pen` ≥ 1, create_ellipse ≥ 2
- Efficiency: target=36

`FillTypeIs("vector","solid")` requires explicit add_fill on the vector (default is `[]`). 1 vector + add_fill + color + 2 ellipses + 2 fills + alignment ≈ 15. **Verdict: ✅**.

### Task 43 — Compass rose

- Fund: ellipse=2, polygon=4
- Align: polygon same-dim + ellipse circular
- Color: both solid (default)
- Event: ellipse+polygon + create_ellipse=2, create_polygon=4
- Efficiency: target=36

6 creates (13) + 6 fills + alignment ≈ 22. **Verdict: ✅**.

### Task 44 — Avatar with badge

- Fund: ellipse=2
- Align: overlap + LayerOnTopOf + circular
- Color: solid (default)
- Event: ellipse + create=2
- Efficiency: target=14

2 creates (5) + 2 fills + position badge bottom-right ≈ 10. **Verdict: 🟡** (target tight but works).

### Task 45 — Geometric emblem

- Fund: star=1 + `StarPointsEquals(8)` + ellipse=1
- Align: ellipse-bounds-inside-star + ellipse-centered-on-star + circular
- Color: both solid (default)
- Event: star+ellipse + create=1/1
- Efficiency: target=20

Star defaults to 5 points (assumed; star.ts) — need 1 set-points to 8. 2 creates (5) + 1 set-points + 2 fills + center align ≈ 11. **Verdict: ✅**.

### Task 46 — Histogram bars

- Fund: rect=8
- Color: solid (default)
- Event: rect + create=8
- Efficiency: target=24

Auto-revert tax: 8 creates = 1 + 2×8 = 17 baseline events. Plus 8 height adjustments (resize) and possibly fill changes ≈ 27. Slight multiplier hit at target=24. **Verdict: 🟡**.

### Task 47 — Sunburst stamp badge

- Fund: star=1 + StarPointsEquals(16) + StarInnerRatioEquals(0.7, tol=0.05) + ellipse=1
- Align: centered-on + circular
- Color: both solid (default)
- Event: star+ellipse + create=1/1
- Efficiency: target=24

1 star + set-points to 16 + set-innerRatio to 0.7 + 1 ellipse + 2 fills + center align ≈ 12. **Verdict: ✅**.

### Task 48 — Spiderweb

- Fund: ≥1 frame, ≥6 lines, polygon=3 + PolygonSidesEquals(6)
- Align: `LayerHasNoFill(polygon)` — at least one hexagon outline-only
- Color: frame solid (default)
- Event: line+polygon + create_line ≥ 6, create_polygon=3
- Efficiency: target=36

3 polygons must all have sides=6 (PolygonSidesEquals checks all). At least one must have no visible fill. 1 frame + 6 lines + 3 polygons + 3 set-sides + 1+ remove_fill + arrangement ≈ 28–32. **Verdict: 🟡**.

### Task 49 — Tied ribbon

- Fund: ≥1 vector
- Color: `FillTypeIs("vector","solid")` — needs add_fill
- Event: pen + create_vector_with_pen ≥ 1
- Efficiency: target=24

1 vector + add_fill + color ≈ 8. **Verdict: ✅**.

### Task 50 — Star inside square

- Fund: rect=1, star=1, StarPointsEquals(5) (default!)
- Align: star-bounds-inside-rect + star-centered-on-rect
- Color: both solid (default)
- Event: rect+star + create=1/1
- Efficiency: target=15

5 points is the star default — no edit needed. 2 creates (5) + 2 fills + center align ≈ 9. **Verdict: ✅**.

---

## What's wrong vs. what's calibrated tight

**Real verifier bugs (need code fixes):**
- Task 7: `EventTypeCountAtLeast("create_vector", 2)` → change to `"create_vector_with_pen"`. One-line fix; restores 1.0 ceiling.

**Mock gaps that cap natural play:**
- Task 6 and 13 both rely on line-layer `rotation` reflecting visual angle. The mock encodes line angle in `p1`/`p2` only and hardcodes `rotation: 0` (`line.ts:43`). Either (a) update the line tool to set `rotation` based on drag direction, or (b) replace `LayersEvenlyRotated`/`LayersHaveRotations` on lines with an endpoint-based check (analogue of `LinesOnDiagonal`).
- Task 6 also has the `LayersConcentric` issue: radial lines from a center point have different bbox centers. The intent is probably "all lines share a common endpoint" — would need a new `LayersShareEndpoint` check, or a different geometric definition.

**Target_turns calibration questions** (tasks where the optimal estimate is at or near target, leaving no room for selection clicks, mistakes, or color picker interactions):
- Task 9 (target=36, optimal ≈ 45 with auto-revert tax) — **likely under-calibrated**; consider 50.
- Tasks 2, 4, 15, 25, 29, 30, 31, 32, 35, 44, 46, 48 — sit at-target or 1–3 events over. Multiplier likely 0.93–0.99 even on optimal play. Marginal.
- Auto-revert tax (§4) is the biggest single contributor to over-target counts. Tasks where the prompt centers on "draw N shapes" need targets sized as `1 + 2N + (per-shape property edits)`, not `N + small slack`.

**Calibration is generous** for: tasks 33 (40), 34 (35), 41 (40), 42 (36), 43 (36) — at least 10 events of headroom. Possibly over-budgeted.

---

## Methodology & limitations

- Read all 50 `verifier.py` files end-to-end and listed every check used.
- Cross-referenced check-class signatures in `apps/figma/verifier/checks/{event,fill,geometry,property,shape,structure,page,stroke,text,effect}_checks.py`.
- Built the full set of mock-emitted semantic event names by grepping `name: "<event>"` in `apps/figma/mock/src/**` (creation events from `tools/`, mutations from `engine/`).
- Spot-checked specific implementations: `tools/line.ts` (rotation handling), `tools/polygon.ts` (default sides), `tools/pen.ts` and `tools/pencil.ts` (vector event names), `engine/propertyCommands.ts` (property mutation events), `engine/alignmentCommands.ts` (tidy_up/align/distribute).
- **Did NOT exhaustively verify:** star tool defaults (assumed 5 points / inner ratio close to expected), the existence of "set polygon sides" and "set star points/innerRatio" panel inputs (assumed yes given the rest of the app expects them), every `set_property` event field `path` value. If any of those assumptions are wrong, tasks 35, 45, 47, 48 would shift down.
- **Did NOT execute** any task end-to-end with the mock running — all judgments are static. A live run would be needed to confirm exact `actual_turns` for borderline 🟡 tasks.
- All file:line refs are valid as of audit date 2026-05-07 (branch `fix/figma-mock-audit-fixes`, head `41fd1c8`).
