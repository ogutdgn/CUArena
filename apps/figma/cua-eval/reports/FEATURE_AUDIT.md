# Delivery-1 Task → Figma Feature Dependencies

Audit of every feature the **50 delivery-1 tasks** assume the figma-mock environment supports. Built by reading each `delivery-1/task_NN/prompt.md` and recording both **explicit tool/operation references** (e.g. "use Tidy up") and **implicit feature requirements** (e.g. "centered together" → needs an align/center primitive).

Granularity bias is intentional: a feature is called out even if a determined model could *theoretically* reproduce the result by eyeballing pixels (e.g. centering via raw drag). What matters is whether the **environment surface** exposes the feature, since that's what determines whether a CUA agent can use the natural / expected path.

Two indexes below: **feature → tasks** (what the env needs to support, with usage counts), and **task → features** (per-task dependency manifest).

---

## Feature → tasks (env requirements)

### 1. Shape-creation tools (toolbar)

| Feature | Tasks requiring it | Count |
|---|---|---|
| **Rectangle tool** (drag-to-create) | 01, 02, 04, 05, 09, 10, 12, 13 (lines via this?), 14 (?), 16, 17, 19, 20 (?), 21, 22, 23, 24, 25, 26, 27, 28, 30, 36, 37, 38, 40, 41, 46, 50 | 27 |
| **Ellipse tool** (drag-to-create) | 01, 03, 14, 15, 18, 19, 20, 29, 31, 32, 33, 39, 40, 41, 42, 43, 44, 47 | 18 |
| **Polygon tool** (drag-to-create) | 01, 11, 16, 17, 31, 32, 33, 35, 43, 48 | 10 |
| **Polygon — configurable side count** (scrub sides to 3, 6) | 11 (3), 17 (3 via "triangle"), 35 (6), 48 (6) | 4 |
| **Star tool** (drag-to-create) | 45, 47, 50 | 3 |
| **Star — configurable point count** (scrub points: 5, 8) | 45 (8), 47 (8), 50 (5) | 3 |
| **Line tool** | 06, 13, 25 (?), 28, 34, 37, 41, 46 (?), 48 | 7-9 |
| **Pen tool** (anchor-by-anchor path) | 07, 08, 19, 37, 39, 42, 49 | 7 |
| **Pen tool — bezier handles** (click-and-drag at anchor for curve) | 08, 49, (implied for 39 arcs and 42 bell) | 4+ |
| **Pen tool — close path** (click first anchor to close) | 07, 37 (implied), 42 (implied) | 2-3 |
| **Frame tool** | 01, 02, 03, 04, 07, 08, 09, 20, 23, 24, 29, 30, 31, 32, 34, 35, 39, 48 | 18 |
| **Frame preset (named device)** — specifically MacBook Air 1280×832 | 01 | 1 |
| **Frame at custom exact dimensions** (drag with target px) | 07 (1000×400), 08 (1000×300), 20 (800×600), 30 (600×600), 39 (200×200), 27 (200×200 rectangle) | 6 |

### 2. Fill / paint

| Feature | Tasks requiring it | Count |
|---|---|---|
| **Solid color fill** (any color) | 01, 02, 03, 04, 05, 06 (stroke), 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 50 | 47 |
| **Distinct color picker / palette** (multiple distinct hues per task) | 01, 02, 03, 04, 09, 11, 14, 17, 19 (gray), 20, 21, 22, 26, 27, 30, 31, 32, 33, 36, 38, 40, 42, 43, 44, 45, 47, 48, 50 | 28 |
| **Specific named colors** (sunset palette, brand colors, rainbow, navy, sand, gold, gold #d9a521, neumorphic #E1E5EE) | 02, 04, 09, 14, 17, 20, 22, 26, 27, 31, 33, 38, 40, 42, 43, 45, 47, 48 | 18 |
| **No fill / transparent** | 35 (only stroke), 38 (body), 41 (magnifier ring), 48 (hexagons stroke only) | 4 |
| **Fill opacity** (≥ 0.5 implied by verifier; not directly set) | all | — |

### 3. Stroke

| Feature | Tasks requiring it | Count |
|---|---|---|
| **Stroke present (any weight)** | 06, 08, 14, 19, 35, 38, 39, 41, 42, 44, 48, 49 | 12 |
| **Custom stroke weight** — specific px values | 08 (4px), 14 (4px), 19 (14px), 35 (1px), 38 (gray, weight unspecified), 39 (6px), 41 (2px), 42 (2px badge), 44 (2px), 49 (12px) | 9 |
| **Stroke color** (separate from fill) | 06 (gold), 14 (black), 19, 35 (black), 38 (gray), 39 (navy), 41 (default), 42 (white), 44 (white), 48 (white), 49 | 11 |
| **Stroke cap style — round caps** | 08, 19 | 2 |
| **Stroke dash style — dashed** | 49 | 1 |

### 4. Corner radius

| Feature | Tasks requiring it | Count |
|---|---|---|
| **Corner radius (scrub or value)** | 16, 19, 22, 24, 27, 38, 40, 41 | 8 |
| **Specific radius values** — 8, 12, 16, 20, 24, 999 (pill) | 16 (16), 19 (12), 22 (999), 24 (~16), 27 (20), 38 (8), 40 (999), 41 (24) | 8 |

### 5. Effects (right panel)

| Feature | Tasks requiring it | Count |
|---|---|---|
| **Drop shadow** (single) | 27 | 1 |
| **Multiple drop shadows on one layer** (with opposing offsets) | 27 | 1 |
| **Shadow offset (x, y)** | 27 | 1 |
| **Shadow blur radius** | 27 | 1 |

### 6. Transforms

| Feature | Tasks requiring it | Count |
|---|---|---|
| **Drag-to-position** (any move) | all | — |
| **Width / height scrub or numeric resize** | 10, 11, 14, 18, 27 (specific 200×200), 36, 46 (vary height per bar) | 7+ |
| **Rotation — scrub angle** | 03 (45°), 06 (45°,90°,135°,180°,225°,270°,315°), 17 (180°), 31 (90°), 32 (90°,180°,270°), 34 (90°,180°,270°), 37 (3°), 43 (90°,180°,270°), 48 (90°,180°,270°) | 9 |
| **Rotation 0° default preserved** (no accidental flip) | 27 explicitly checks | implicit for all |
| **No flipping** | implicit verifier check | — |

### 7. Selection

| Feature | Tasks requiring it | Count |
|---|---|---|
| **Single-click select** | all | — |
| **Marquee select (drag empty)** | 02, 05, 09, 10, 11, 12, 14, 17, 18, 21, 22, 24, 25, 26, 29, 36, 45, 47, 50 | 19 |

### 8. Duplication

| Feature | Tasks requiring it | Count |
|---|---|---|
| **Right-click → Duplicate** | 01, 03, 04, 06, 09, 10, 11, 12, 13, 14, 15, 17, 18, 21, 22, 25, 26, 29, 30, 31, 32, 34, 35, 36, 37, 39, 43, 46, 48 | 29 |
| **Duplicate-then-drag** (as a placement workflow) | most of above | — |

### 9. Alignment helpers (toolbar / right panel)

| Feature | Tasks requiring it | Count |
|---|---|---|
| **Align horizontal centers** | 02, 05, 10, 11, 14, 17, 18, 21, 24, 36, 45, 47, 50 | 13 |
| **Align vertical centers** | 05, 10, 14, 18, 24, 36, 45, 47, 50 | 9 |
| **Align top** | 12, 22, 25, 26 | 4 |
| **Align bottom** | 46 | 1 |
| **Distribute horizontal spacing** | 12, 25 | 2 |

### 10. Layout helpers

| Feature | Tasks requiring it | Count |
|---|---|---|
| **Tidy up** (auto-grid) | 09, 29 | 2 |

### 11. Z-order / layering

| Feature | Tasks requiring it | Count |
|---|---|---|
| **Layer stack by creation order** (later-drawn renders on top) | 03, 10, 11, 14, 16, 17, 18, 19, 33, 36, 37, 39, 40, 41, 42, 43, 44, 45, 47, 50 | 20 |

### 12. Structure / hierarchy

| Feature | Tasks requiring it | Count |
|---|---|---|
| **Shapes inside frame** (parent-child) | 01, 02, 03, 04, 07, 08, 09, 20, 23, 24, 29, 30, 31, 32, 34, 35, 39, 48 | 18 |
| **Frame contains ≥5 children** | 01 | 1 |

### 13. Keyboard / mode

| Feature | Tasks requiring it | Count |
|---|---|---|
| **Escape to exit pen tool** | 07, 08, 19, 37, 39, 42, 49 | 7 |
| **Keyboard input** (text typing) | none | 0 |

### 14. Specific assumed UI elements / panels

| Feature | Tasks requiring it | Count |
|---|---|---|
| **Right panel: fill picker** | most (47) | — |
| **Right panel: stroke picker** | 12 |
| **Right panel: corner radius input/scrub** | 8 |
| **Right panel: Effects → Add drop shadow** | 27 | 1 |
| **Right panel: frame preset list** (named devices like MacBook Air) | 01 | 1 |
| **Right panel: stroke dash style selector** | 49 | 1 |
| **Right panel: stroke caps (round) toggle** | 08, 19 | 2 |
| **Toolbar: align cluster** (4–5 align buttons) | 13+ | — |
| **Toolbar: distribute cluster** | 12, 25 | 2 |
| **Toolbar: Tidy up button** (or context menu) | 09, 29 | 2 |
| **Context menu on right-click** (Duplicate option) | 29+ tasks | — |

---

## Task → features (per-task dependency manifest)

> Notation: each task lists the discrete features it relies on. "RECT" = rectangle tool, "ELL" = ellipse, "POLY" = polygon, "POLY-3"/"POLY-6" = with side count, "STAR-N" = star tool with point count, "LINE", "PEN", "PEN-BEZ" = pen with bezier handles, "FRAME", "FRAME-PRESET" = named device preset, "FILL", "STROKE-Wpx", "RADIUS-N", "ROT-θ", "ALIGN-H/V/T/B", "DIST-H", "TIDY", "DUP", "MARQ", "DUP-ROT" = duplicate + rotate workflow, "SHADOW".

| # | Task | Features |
|---|---|---|
| 01 | Two-story house | FRAME, FRAME-PRESET (MacBook Air 1280×832), RECT, ELL, POLY-3, FILL (4+ colors), DUP, layer-in-frame structure |
| 02 | Sunset stripe band | FRAME, RECT, FILL (5 specific sunset colors), MARQ, ALIGN-H |
| 03 | Radial flower with petals | FRAME, ELL, FILL (≥9 distinct colors), DUP, ROT (45° intervals), implicit radial positioning |
| 04 | Color hexagon ring | FRAME, RECT, FILL (rainbow palette), DUP, implicit hexagon positioning (radial 60° intervals) |
| 05 | Plus-sign emblem | RECT, FILL (1 color, 2 layers), MARQ, ALIGN-H, ALIGN-V |
| 06 | Asterisk burst | LINE, STROKE color (gold #d9a521), DUP, ROT (45°,90°,...,315°), implicit shared-center endpoint anchoring |
| 07 | Layered mountain range | FRAME (1000×400), PEN (multi-anchor closed path), Escape to exit pen, FILL (2 gray shades), DUP-ish (2 paths) |
| 08 | Layered water waves | FRAME (1000×300), PEN-BEZ (bezier handles), STROKE-4px, STROKE color (2 blues), STROKE-CAP-ROUND, DUP |
| 09 | 12-color swatch grid | FRAME, RECT, FILL (12 distinct colors), DUP, MARQ, **TIDY UP** |
| 10 | Concentric squares | RECT, FILL (alternating 2 colors), DUP, width/height scrub, MARQ, ALIGN-H, ALIGN-V |
| 11 | Nested triangles | POLY-3, FILL (alternating 2), DUP, scrub size, MARQ, ALIGN-H |
| 12 | Card row | RECT, FILL (per-layer), DUP, MARQ, ALIGN-T, DIST-H |
| 13 | Cross-hatch hashtag | LINE, DUP, perpendicular line placement |
| 14 | Concentric ring target | ELL, FILL (red/white alternation), STROKE-4px black, DUP, scrub size, MARQ, ALIGN-H, ALIGN-V |
| 15 | Cloud silhouette | ELL, FILL (white), DUP, scrub size |
| 16 | Speech bubble | RECT, RADIUS-16, FILL (light gray), POLY-3, same-fill |
| 17 | Hourglass | POLY-3, ROT-180°, DUP, ROT-0°, RECT (caps), MARQ, ALIGN-H |
| 18 | Eye icon | ELL, FILL (white, color, black), DUP, scrub size, MARQ, ALIGN-H, ALIGN-V |
| 19 | Padlock | RECT, RADIUS-12, FILL (dark gray), PEN (U-shape), STROKE-14px, STROKE-CAP-ROUND, ELL (keyhole), FILL black |
| 20 | Overlapping circles on navy | FRAME (800×600), FRAME FILL (dark navy), ELL, FILL (magenta, cyan), overlap positioning |
| 21 | Vertical card stack | RECT, FILL (3 distinct), DUP, MARQ, ALIGN-H |
| 22 | Pastel pill row | RECT, RADIUS-999, FILL (4 pastels), DUP, MARQ, ALIGN-T |
| 23 | Left sidebar | FRAME, RECT, FILL (dark gray), proportional width (~17%) |
| 24 | Centered modal in frame | FRAME, RECT, RADIUS-~16, FILL (white), MARQ (incl. parent frame), ALIGN-H, ALIGN-V |
| 25 | Identical card row | RECT, FILL (1 color), DUP, MARQ, ALIGN-T, DIST-H |
| 26 | Brand color squares | RECT, FILL (5 brand colors), DUP, MARQ, ALIGN-T |
| 27 | Neumorphic pressed button | RECT, scrub to 200×200, FILL (#E1E5EE), RADIUS-20, **SHADOW** (-8,-8, blur 16), **SECOND SHADOW** (8,8, blur 16), no rotation/flip |
| 28 | Photo placeholder with X | RECT, FILL (light gray), LINE (corner-to-corner ×2) |
| 29 | Polka-dot 2×2 grid | FRAME, FRAME FILL (off-white), ELL, FILL, DUP, MARQ, **TIDY UP** |
| 30 | Alternating stripes | FRAME (600×600), RECT, FILL (2 alternating), DUP |
| 31 | Sun | FRAME, ELL, FILL (yellow), POLY-3 (rays), DUP, ROT-90°,180°,270° |
| 32 | Pinwheel | FRAME, POLY-3, FILL (2 alternating), DUP, ROT-90°,180°,270°, ELL (pivot) |
| 33 | Pie chart | ELL (teal), POLY-3 (wedges), DUP, ROT to angle, FILL (2 wedge colors), z-order |
| 34 | Snowflake | FRAME (navy fill), LINE (white), DUP, ROT-90°,180°,270° |
| 35 | Honeycomb 2×2 | FRAME, POLY-6, FILL (yellow), STROKE-1px black, DUP |
| 36 | Vintage frame | RECT (outer + inner), FILL (2), DUP, scrub size, MARQ, ALIGN-H, ALIGN-V |
| 37 | Tilted sticky note | RECT, FILL (yellow), ROT-3°, PEN (corner fold triangle), FILL (darker yellow), LINE (note lines), DUP |
| 38 | Battery indicator | RECT, RADIUS-8, no fill, STROKE (gray), RECT (terminal), RECT (3 inner bars), FILL (green/yellow/red) |
| 39 | Wifi icon | FRAME (200×200), PEN-BEZ (arc), STROKE-6px navy, DUP, scrub size, ELL (filled navy dot) |
| 40 | iOS toggle | RECT, RADIUS-999, FILL (green), ELL, FILL (white), edge-anchored positioning |
| 41 | Search bar | RECT, RADIUS-24, ELL no-fill STROKE-2px (magnifier ring), LINE (handle), ELL (dots) |
| 42 | Bell + badge | PEN (bell silhouette), FILL (yellow-gold), ELL (clapper), ELL (red badge), STROKE-2px white |
| 43 | Compass rose | ELL (sand), POLY-3 (4 cardinal triangles), FILL (red + 3 gray), DUP, ROT-90°,180°,270°, ELL (gold center) |
| 44 | Avatar + status badge | ELL (large), FILL, ELL (smaller), FILL (green), STROKE-2px white |
| 45 | Star + circle emblem | STAR-8, FILL (deep blue), ELL, FILL (yellow), MARQ, ALIGN-H, ALIGN-V |
| 46 | Histogram bars | RECT, DUP, scrub height per bar, MARQ, ALIGN-B |
| 47 | Sunburst stamp | STAR-8, FILL (warm orange), ELL, FILL (cream), MARQ, ALIGN-H, ALIGN-V |
| 48 | Spiderweb | FRAME (navy fill), LINE (white), DUP, ROT-90°,180°,270°, POLY-6 no-fill STROKE-white, DUP, scrub size |
| 49 | S-curve ribbon | PEN-BEZ (multi-anchor curve), Escape, STROKE-12px, **STROKE-DASHED** |
| 50 | Square + 5-point star | RECT, FILL (dark), STAR-5, FILL (bright), MARQ, ALIGN-H, ALIGN-V |

---

## Headline observations

1. **Drawing primitives are the universal floor.** Rectangle (27 tasks), Ellipse (18), Polygon (10), Star (3), Line (7–9), Pen (7), Frame (18) — every single task uses at least one creation tool.

2. **Alignment helpers are load-bearing.** 13 tasks need `Align horizontal centers`, 9 need `Align vertical centers`. Without these, ~1/3 of tasks become much harder for a CUA agent (the model has to pixel-match by hand, which is what task 04 / 06 already fail at).

3. **Duplicate + rotate is the workhorse pattern for radial / repeated layouts.** 29 tasks use `Duplicate`. 9 use rotation. Tasks that rely on `Duplicate → scrub rotation` (03, 06, 31, 32, 34, 43, 48) need both features wired *plus* a numeric rotation scrub (not just a rotate handle).

4. **Tidy up** is a hard requirement for 2 tasks (09, 29). Without it, the model has to place a 4×3 grid (task 09) or 2×2 grid (task 29) by hand — exactly the type of geometric arrangement Sonnet 4.5 is currently failing at on radial layouts.

5. **One task is shadow-dependent.** Task 27 is the only neumorphic effect; it needs **multiple drop shadows on a single layer** with controllable offset and blur. If the mock only supports a single shadow, this task is unachievable.

6. **Specific values matter.** Several tasks specify exact pixel values (frame sizes, corner radii, stroke weights) and exact colors (#d9a521 gold for task 06, #E1E5EE for task 27). The mock needs:
   - Frame size presets: MacBook Air (task 01)
   - Custom frame sizes: 200×200, 600×600, 800×600, 1000×300, 1000×400 (tasks 27, 30, 20, 08, 07)
   - Corner radius scrub including 999 (for pills)
   - Stroke weights: 1, 2, 4, 6, 12, 14 px
   - Stroke caps: round
   - Stroke style: dashed
   - Color picker that can hit specific hex values

7. **Pen-tool sophistication varies.** Some tasks need only anchor-by-anchor straight paths (07 mountains). Others need bezier handles (08 waves, 49 ribbon) and closing paths (07, 19 maybe, 42 maybe). The pen-tool surface area is broad and easy to ship partial.

8. **Star tool with adjustable points** is needed for only 3 tasks (45, 47 with 8 points; 50 with 5 points). Could be cut from scope without losing much breadth.

9. **Zero typing required.** No task in the corpus asks the model to type text — the keyboard handicap from our environment doesn't gate any tasks (assuming the feature audit is exhaustive).

10. **Layout-by-implication is the hidden dependency.** Many tasks say "centered together" or "arranged radially" without naming an align tool. Verifiers do tolerate raw drag positioning (with px tolerances), but in practice CUA agents perform much better when the natural path is a discoverable button (the failure modes on tasks 03/04/06 are exactly: the model couldn't visually achieve uniform radial spacing without a `Distribute around point` primitive, which the mock doesn't seem to have).

## Suggested mock-coverage targets

To unblock all 50 tasks at the **feature** level (separate from whether Sonnet/Opus can actually drive them):

- ✓ already-shipped (per prior conversation): Rectangle, Ellipse, Polygon with side scrub, Line, Pen, Frame, Star with point scrub, fill, stroke, corner radius, alignment, distribute, align (per the feature → check table in `apps/figma/CLAUDE.md`)
- ⚠ **Tidy up** — needed for tasks 09, 29
- ⚠ **Effects → Drop shadow** with offset/blur, supporting multiple shadows per layer — needed for task 27
- ⚠ **Frame presets** list including MacBook Air 1280×832 — needed for task 01
- ⚠ **Stroke dash style** selector — needed for task 49
- ⚠ **Stroke cap style** (round) — needed for tasks 08, 19
