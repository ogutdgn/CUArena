# Verifier Framework — Documentation

Single source of truth for the CUA verifier framework. Read this before writing
any code or task verifier script.

---

## 1. Purpose

The Figma mock app is a controlled environment for testing CUA (Computer Use
Agent) models. Agents are given a task prompt and interact with the app. After
the agent finishes, the verifier reads the log the app produced and scores how
well the task was completed.

The verifier answers one question: **"Did the agent build the right thing?"**
It does not care how the agent did it — only what ended up on the canvas.

---

## 2. Pipeline

```
tasks.csv                          log.json  (downloaded from test-app)
(task definitions)                 (raw + semantic + outcome streams)
        │                                      │
        ▼                                      ▼
tasks/<task_id>.py   ──────────►   run.py  (CLI runner)
(Claude Code writes)                    │
                                        │  runs rubrics → checks → efficiency
                                        ▼
                               scores/<task_id>_<timestamp>.json
                               (or delivery-1/<task_NN>/output/<ts>/)
```

---

## 3. Log Format

The test-app exports a JSON file (`figma-mock-log-<sessionId>.json`) with three
streams. The verifier reads all three.

```json
{
  "schemaVersion": 1,
  "sessionId": "session_abc123",
  "exportedAt": 1746100000000,
  "raw":      [...],
  "semantic": [...],
  "outcome":  {
    "sessionId": "session_abc123",
    "activePageId": "page_1",
    "summary": {
      "semanticEventCount": 25,
      "shapeCounts": { "rectangle": 2, "ellipse": 2, "polygon": 1 }
    },
    "document": { ... }
  }
}
```

| Stream | Used for |
|---|---|
| `raw` | Not used by verifier directly — forensics only |
| `semantic[]` | Efficiency rubric (turn count) and event_checks |
| `outcome.summary.shapeCounts` | Fast count lookup |
| `outcome.document` | All geometry, fill, stroke, effect, text checks |

Full schema: `project-documents/app-docs/logging-documentation.md`.

---

## 4. Scoring Model

### Rubrics

A task defines a list of rubrics. Each rubric has a `weight` (default `0.5`)
that becomes its `max_score`. Within a rubric, partial credit applies: if 2 of
3 checks pass, the rubric scores `weight × 2/3`.

```
base_score = sum of rubric scores
```

By convention, tasks size their weights so the sum is `1.0`. The framework
doesn't enforce that — it's a per-task choice.

### Efficiency multiplier

After all rubrics run, the base score is multiplied by an efficiency factor
based on how many semantic events the agent used vs. the per-task target.

```
multiplier = 0.5 + 0.5 × e^(−λ × max(0, actual_turns − target_turns))
```

| Turns used | Multiplier (λ=0.05) |
|---|---|
| ≤ target | 1.00 (full score) |
| 1.5× target | ~0.85 |
| 2× target | ~0.75 |
| 3× target | ~0.63 |
| ∞ | 0.50 (floor — always keeps ≥50% of base) |

```
final_score = base_score × multiplier
```

### λ (lambda)

- Default: `0.05` in `config.yaml` — applies to all tasks unless overridden.
- Per-task override: `EfficiencyRubric(target_turns=30, lambda_=0.1)`.
- Higher λ = steeper penalty for going over target turns.

---

## 5. Folder Structure

```
test-verifier/
│
├── verifier/                      ← framework
│   ├── types.py                   ← CheckResult, RubricResult, EfficiencyResult,
│   │                                 TaskResult, Task
│   ├── loader.py                  ← load + validate log JSON
│   ├── config.py                  ← reads config.yaml
│   ├── math_utils.py              ← geometry helpers
│   │
│   ├── checks/                    ← check primitives (leaf nodes)
│   │   ├── shape_checks.py
│   │   ├── geometry_checks.py
│   │   ├── fill_checks.py
│   │   ├── stroke_checks.py
│   │   ├── property_checks.py
│   │   ├── text_checks.py
│   │   ├── effect_checks.py
│   │   ├── structure_checks.py
│   │   ├── page_checks.py
│   │   └── event_checks.py
│   │
│   └── rubrics/                   ← rubric containers
│       ├── _base.py               ← Rubric class (the only real rubric type)
│       ├── fundamentals.py        ← FundamentalsRubric factory
│       ├── alignment.py           ← AlignmentRubric factory
│       ├── color.py
│       ├── effect.py
│       ├── event.py
│       ├── page.py
│       ├── property.py
│       ├── structure.py
│       ├── text.py
│       └── efficiency.py          ← EfficiencyRubric (special — produces multiplier)
│
├── tasks/                         ← one file per task (Claude Code writes these)
│   └── task_NN_<slug>.py
│
├── task-docs/
│   └── tasks.csv                  ← 50 tasks with Scope field
│
├── logs/                          ← log JSON files downloaded from test-app
├── scores/                        ← verifier output JSON files (fallback)
├── config.yaml                    ← global defaults (λ, tolerances)
├── run.py                         ← CLI runner
├── qa_verifiers.py                ← QA harness (perfect/empty synthesis)
└── requirements.txt
```

---

## 6. Data Types (`verifier/types.py`)

```python
@dataclass
class CheckResult:
    passed:    bool    # True / False
    score:     float   # 1.0 if passed, 0.0 if not
    max_score: float   # always 1.0
    message:   str     # "ellipse: expected 2, got 3"

@dataclass
class RubricResult:
    name:      str            # "fundamentals", "alignment", ...
    score:     float          # 0 .. weight
    max_score: float          # weight
    checks:    list[CheckResult]

@dataclass
class EfficiencyResult:
    multiplier:   float       # 0.5 .. 1.0
    actual_turns: int
    target_turns: int
    lambda_used:  float
    message:      str

@dataclass
class TaskResult:
    task_id:     str
    log_path:    str
    rubrics:     list[RubricResult]
    base_score:  float        # sum of rubric scores
    efficiency:  EfficiencyResult
    final_score: float        # base_score × multiplier

@dataclass
class Task:
    id:          str
    description: str
    rubrics:     list         # list of rubric objects (from rubric factories)
    efficiency:  Any          # EfficiencyRubric instance
    scope:       str = "in_scope"   # "in_scope" | "planned" | "out_of_scope"
```

---

## 7. Rubric System

### Generic `Rubric`

All non-efficiency rubrics are instances of one class (`verifier/rubrics/_base.py`):

```python
@dataclass
class Rubric:
    name:   str
    checks: list
    weight: float = 0.5    # max_score for this rubric

    def run(self, log: dict) -> RubricResult: ...
```

### Named factories

For ergonomics, each rubric has a factory function that fills in `name`:

| Factory | Name | Typical checks |
|---|---|---|
| `FundamentalsRubric(checks, weight=0.5)` | `fundamentals` | shape_checks |
| `AlignmentRubric(checks, weight=0.5)` | `alignment` | geometry_checks |
| `ColorRubric(checks, weight=0.5)` | `color` | fill_checks, stroke_checks |
| `TextRubric(checks, weight=0.5)` | `text` | text_checks |
| `PropertyRubric(checks, weight=0.5)` | `property` | property_checks |
| `EffectRubric(checks, weight=0.5)` | `effect` | effect_checks |
| `StructureRubric(checks, weight=0.5)` | `structure` | structure_checks |
| `PageRubric(checks, weight=0.5)` | `page` | page_checks |
| `EventRubric(checks, weight=0.5)` | `event` | event_checks |

### `EfficiencyRubric` (special)

Does not produce a `RubricResult`. Produces an `EfficiencyResult` with a
multiplier (0.5..1.0) that scales the final score.

```python
EfficiencyRubric(target_turns=30)               # uses config.yaml λ
EfficiencyRubric(target_turns=30, lambda_=0.1)  # per-task λ override
```

---

## 8. Check Primitives — Full Catalog

All checks live in `verifier/checks/`. Each exposes `run(log: dict) -> CheckResult`.

### `shape_checks.py`

| Class | Args | Checks |
|---|---|---|
| `ShapeCount` | `layer_type, equals` | exactly N layers of type |
| `ShapeCountAtLeast` | `layer_type, minimum` | at least N layers of type |
| `PolygonSidesEquals` | `sides` | all polygons have N sides |
| `StarPointsEquals` | `points` | all stars have N points |
| `StarInnerRatioEquals` | `ratio, tolerance=0.05` | all stars have ≈ inner ratio (0..1) |

### `geometry_checks.py`

| Class | Args | Checks |
|---|---|---|
| `LayersAligned` | `layer_type, axis, tolerance=5.0` | layers share coord on axis |
| `LayersSymmetricX` | `layer_type, tolerance=10.0` | symmetric around center X |
| `LayerSizeEquals` | `layer_type, width=None, height=None, tolerance=2.0` | dimensions |
| `LayerPosition` | `layer_type, x=None, y=None, tolerance=5.0` | position |
| `LayerRotationEquals` | `layer_type, degrees, tolerance=2.0` | rotation |
| `DistanceBetween` | `type_a, type_b, expected_px, tolerance=5.0` | distance between layers |
| `LayerContains` | `outer_type, inner_type` | inner is direct child of outer |
| `LayersSameDimensions` | `layer_type, tolerance=2.0` | all layers of type have equal w,h |
| `LayerEdgesAligned` | `type_a, edge_a, type_b, edge_b, tolerance=5.0` | edge of A ≈ edge of B |
| `LayersDistributed` | `layer_type, axis, tolerance=5.0` | evenly spaced on axis |
| `LayersConcentric` | `layer_type, tolerance=5.0` | layers share same center point |
| `LayersStacked` | `layer_type, axis, gap_px=0.0, tolerance=4.0` | stacked w/ given gap |
| `LayersOverlap` | `type_a, type_b` | overlapping bounding boxes |
| `LayerBoundsInside` | `inner_type, outer_type, tolerance=2.0` | inner bbox fits inside outer bbox |
| `FrameSizeEquals` | `width, height, tolerance=5.0` | a frame matches (w, h) |
| `LayerIsCircular` | `layer_type, tolerance=2.0` | w ≈ h (circular shape) |
| `LayerIsSquare` | `layer_type, tolerance=2.0` | w ≈ h (square shape) |
| `LayersHaveAspectMix` | `layer_type, horizontal_count=0, vertical_count=0, ratio=1.5` | mix of wide and tall |
| `LayerAspectRatioGreaterThan` | `layer_type, ratio, axis='horizontal'` | aspect ratio above threshold |
| `RadialDistribution` | `layer_type, n, tolerance_deg=10.0` | n layers at equal angular steps |
| `RadialDistributionExcludeCentral` | `layer_type, n, tolerance_deg=12.0` | radial pattern around a central layer |
| `LayersEvenlyRotated` | `layer_type, n, step_deg, tolerance_deg=5.0` | rotations evenly stepped |
| `LayersHaveRotations` | `layer_type, expected, count_per=1, tolerance_deg=5.0` | covers expected rotations |
| `LayersInGrid` | `layer_type, rows, cols, tolerance=8.0` | rows × cols regular grid |
| `OffsetGridLayout` | `layer_type, rows, cols, tolerance=12.0` | offset / honeycomb grid |
| `LayerCenteredInFrame` | `layer_type, tolerance=8.0` | layer centered within parent frame |
| `LayerCenteredOnLayer` | `type_a, type_b, tolerance=5.0` | A's center ≈ B's center |
| `LayerOnTopOf` | `type_a, type_b` | A is later in z-order than B |
| `LayerNextTo` | `type_a, type_b, side, tolerance=8.0` | A is on the given side of B |
| `LayerWidthFraction` | `inner_type, parent_type, min_frac, max_frac` | inner width as fraction of parent |
| `LayersAlternatingColors` | `layer_type, n_colors, sort_axis='x', tolerance=0.05` | sorted layers cycle N colors |
| `LinesOnDiagonal` | `rect_type='rectangle', line_type='line', tolerance=12.0` | two diagonals across a rect |

`axis` values: `"x"` `"y"` `"center_x"` `"center_y"`
`edge` values: `"top"` `"bottom"` `"left"` `"right"` `"center_x"` `"center_y"`
`side` values (for `LayerNextTo`): `"left"` `"right"` `"top"` `"bottom"`

### `fill_checks.py`

| Class | Args | Checks |
|---|---|---|
| `SolidColorEquals` | `layer_type, expected_rgb, fill_index=0, tolerance=0.05` | ≥1 layer has this color |
| `AllSolidColorEquals` | `layer_type, expected_rgb, fill_index=0, tolerance=0.05` | all layers have this color |
| `FillTypeIs` | `layer_type, kind, fill_index=0` | ≥1 layer has fill of kind |
| `FillCount` | `layer_type, equals` | all layers have N fills |
| `ImageFillExists` | `layer_type` | ≥1 layer has image fill |
| `FillOpacityEquals` | `layer_type, opacity, fill_index=0, tolerance=0.05` | fill-level opacity |
| `LayersHaveColorOrder` | `layer_type, expected_rgbs, sort_axis='y', tolerance=0.15` | sorted layers match colors in order; `sort_axis` ∈ {x, y, size} |
| `CentermostLayerHasColor` | `layer_type, expected_rgb, tolerance=0.15` | the layer nearest the centroid has this color |
| `LayerHasNoFill` | `layer_type` | ≥1 layer has no visible fills |
| `SameColorAcrossTypes` | `types, tolerance=0.05` | first layer of each type shares the same color |
| `DistinctSolidColors` | `minimum, tolerance=0.05` | document has ≥ N distinct solid fills |
| `LayersAllSameColor` | `layer_type, fill_index=0, tolerance=0.05` | every layer of type shares one solid fill color |

`expected_rgb`: `{"r": 0..1, "g": 0..1, "b": 0..1}` — **not** 0..255.
`kind`: `"solid"` or `"image"`.

### `stroke_checks.py`

| Class | Args | Checks |
|---|---|---|
| `StrokeExists` | `layer_type` | ≥1 layer has a stroke |
| `StrokeWeightEquals` | `layer_type, weight, tolerance=0.5` | stroke weight |
| `StrokeColorEquals` | `layer_type, expected_rgb, tolerance=0.05` | stroke color |
| `StrokeAlignmentIs` | `layer_type, alignment` | stroke alignment |
| `DistinctStrokeColors` | `minimum, tolerance=0.05` | ≥ N distinct stroke colors in document |
| `StrokeIsDashed` | `layer_type` | stroke has dash pattern |

`alignment` values: `"inside"` `"center"` `"outside"`.

### `property_checks.py`

| Class | Args | Checks |
|---|---|---|
| `OpacityEquals` | `layer_type, opacity, tolerance=0.02` | layer opacity (0..1) |
| `VisibilityIs` | `layer_type, visible` | visible / hidden |
| `CornerRadiusEquals` | `layer_type, radius, tolerance=1.0` | corner radius |
| `CornerRadiusAtLeast` | `layer_type, min_value` | corner radius ≥ min_value |
| `IsFlippedH` | `layer_type` | scaleX == -1 |
| `IsFlippedV` | `layer_type` | scaleY == -1 |
| `ConstraintHorizontalEquals` | `layer_type, value` | `constraints.horizontal` ∈ {left, right, center, stretch, scale} |
| `ConstraintVerticalEquals` | `layer_type, value` | `constraints.vertical` ∈ {top, bottom, center, stretch, scale, top_bottom} |

### `text_checks.py`

| Class | Args | Checks |
|---|---|---|
| `TextContent` | `expected` | exact text match |
| `TextContains` | `substring` | text contains substring |
| `FontSizeEquals` | `size, tolerance=1.0` | font size |
| `FontWeightEquals` | `weight` | font weight (e.g. 400, 700) |
| `TextAlignEquals` | `align` | hAlign value |
| `VerticalAlignEquals` | `align` | vAlign value (top/middle/bottom) |
| `LineHeightEquals` | `value, tolerance=1.0` | `lineHeight.value` |
| `LetterSpacingEquals` | `value, tolerance=0.5` | `letterSpacing.value` |

`align` values: `"left"` `"center"` `"right"` `"justify"`.

### `effect_checks.py`

| Class | Args | Checks |
|---|---|---|
| `DropShadowExists` | `layer_type` | ≥1 layer has drop shadow |
| `LayerBlurExists` | `layer_type` | ≥1 layer has layer blur |
| `BlurRadiusEquals` | `layer_type, radius, tolerance=1.0` | blur radius |
| `EffectColorEquals` | `layer_type, effect_index, expected_rgb, tolerance=0.05` | effect color |
| `DropShadowOffsetEquals` | `layer_type, x, y, effect_index=0, tolerance=1.0` | drop shadow offset (x, y) |
| `DropShadowBlurEquals` | `layer_type, blur, effect_index=0, tolerance=1.0` | drop shadow blur |
| `DropShadowSpreadEquals` | `layer_type, spread, effect_index=0, tolerance=1.0` | drop shadow spread |
| `EffectCount` | `layer_type, equals` | all layers of type have N effects |

### `structure_checks.py`

| Class | Args | Checks |
|---|---|---|
| `LayerInsideFrame` | `layer_type` | ≥1 layer is direct child of a frame |
| `ChildCount` | `parent_type, equals` | parent has exactly N children |
| `ChildCountAtLeast` | `parent_type, minimum` | parent has ≥ N children |
| `IsGrouped` | `layer_type` | ≥1 layer is inside a group |
| `ZOrderIsFirst` | `layer_type` | ≥1 layer is at front |
| `ZOrderIsLast` | `layer_type` | ≥1 layer is at back |
| `LayerTotalCount` | `equals` | total layers across all pages |

### `page_checks.py`

| Class | Args | Checks |
|---|---|---|
| `PageCount` | `equals` | document has exactly N pages |
| `PageCountAtLeast` | `minimum` | document has ≥ N pages |
| `LayerOnPage` | `layer_type, page_index` | layer of type exists on page (0-based) |
| `PageBackgroundColorEquals` | `expected_rgb, page_index=0, tolerance=0.05` | page background color |
| `ActivePageIs` | `page_name` | active page at session end has this name |

### `event_checks.py` — reads `semantic[]`, not `outcome`

| Class | Args | Checks |
|---|---|---|
| `EventTypeUsed` | `event_name` | semantic event was emitted ≥1 time |
| `EventTypeCount` | `event_name, equals` | emitted exactly N times |
| `EventTypeCountAtLeast` | `event_name, minimum` | emitted ≥ N times |
| `AlignToolUsed` | — | `align_layers` event was used |
| `UndoUsed` | — | `undo` event was used |
| `ToolUsed` | `tool_id` | `tool_change` to given tool id occurred |

Common `event_name` values: `create_rectangle` `create_ellipse` `create_polygon`
`create_frame` `move_layer` `resize_layer` `rotate_layer` `align_layers`
`group_selection` `ungroup` `set_fill_color` `set_corner_radius`
`set_layer_opacity` `rename_layer` `undo` `redo`.

### `layer_type` values

`rectangle` `ellipse` `polygon` `star` `line` `arrow` `text` `vector`
`image` `frame` `section` `group` `slice`

---

## 9. How Verifiers Are Built

### Composition tree (a single task at runtime)

```
Task                                    ← tasks/task_NN_<slug>.py
├── id           : "task_07_mountain_range"
├── description  : "3 polygons forming mountains, …"
├── scope        : "in_scope"
├── efficiency   : EfficiencyRubric(target_turns=20)   ── reads log.semantic[]
└── rubrics      : list[Rubric]                        ── verifier/rubrics/_base.py
       │
       ├── Rubric(name="fundamentals", weight=0.25, checks=[…])
       │     │                                         ── factory: FundamentalsRubric()
       │     └── checks                                ── primitives from verifier/checks/
       │           ├── ShapeCount("polygon", equals=3) ── reads log.outcome.document
       │           └── ShapeCount("rectangle", equals=1)
       │
       ├── Rubric(name="alignment", weight=0.25, checks=[…])
       │     └── LayersStacked("polygon", axis="x", gap_px=0)
       │
       ├── Rubric(name="color", weight=0.25, checks=[…])
       │     ├── FillTypeIs("polygon", kind="solid")
       │     └── DistinctSolidColors(minimum=3)
       │
       └── Rubric(name="event", weight=0.25, checks=[…])
             ├── ToolUsed("polygon")                   ── reads log.semantic[]
             └── EventTypeCount("create_polygon", equals=3)

run.py loops:    rubric_results = [r.run(log) for r in task.rubrics]
                 efficiency     = task.efficiency.run(log)
                 base_score     = sum(r.score for r in rubric_results)
                 final_score    = base_score × efficiency.multiplier
```

Each `Check.run(log)` returns `CheckResult(passed, score, max_score, message)`.
Each `Rubric.run(log)` aggregates check results into a `RubricResult` with
partial credit: `score = weight × (passed / total)`.

### Library architecture (the framework)

```
verifier/
├── types.py          ── dataclasses: Check/Rubric/Efficiency/Task results
├── loader.py         ── reads + validates the log JSON
├── config.py         ── reads config.yaml (default λ, default tolerances)
├── math_utils.py     ── shared geometry helpers (find_layers_by_type, centers, bboxes)
│
├── checks/           ── leaf primitives — one class per question to ask the log
│   │                    each: dataclass with fields (args), .run(log) -> CheckResult
│   ├── shape_checks.py        ShapeCount, PolygonSidesEquals, …
│   ├── geometry_checks.py     LayersAligned, LayersConcentric, RadialDistribution, …
│   ├── fill_checks.py         SolidColorEquals, DistinctSolidColors, …
│   ├── stroke_checks.py       StrokeExists, DistinctStrokeColors, …
│   ├── property_checks.py     OpacityEquals, CornerRadiusEquals, …
│   ├── text_checks.py         TextContent, FontSizeEquals, …
│   ├── effect_checks.py       DropShadowExists, BlurRadiusEquals, …
│   ├── structure_checks.py    LayerInsideFrame, ChildCount, …
│   ├── page_checks.py         PageCount, ActivePageIs, …
│   └── event_checks.py        EventTypeUsed, ToolUsed, AlignToolUsed   ← reads semantic[]
│
└── rubrics/          ── containers — one factory per scoring dimension
    ├── _base.py              Rubric class (the only real rubric type)
    ├── fundamentals.py       FundamentalsRubric()  → Rubric(name="fundamentals", …)
    ├── alignment.py          AlignmentRubric()
    ├── color.py              ColorRubric()
    ├── text.py               TextRubric()
    ├── property.py           PropertyRubric()
    ├── effect.py             EffectRubric()
    ├── structure.py          StructureRubric()
    ├── page.py               PageRubric()
    ├── event.py              EventRubric()
    └── efficiency.py         EfficiencyRubric()    ← special: produces a multiplier
```

### Flow: write a NEW task verifier

```
┌─ 1. Read row in task-docs/tasks.csv
│       • Simplified Prompt + Thorough Description
│       • Confirm Scope = in_scope (skip otherwise)
│
├─ 2. Decide which dimensions matter
│       fundamentals? alignment? color? property? structure? event?
│       → 3–5 rubrics is typical
│
├─ 3. For each chosen rubric, pick checks from §8
│       • Match each rubric requirement to one or more check primitives
│       • Don't invent new ones — if missing, extend the library first (below)
│
├─ 4. Set tolerances + weights
│       • tighter tolerances for pixel-precise tasks, looser for freehand
│       • weights typically sum to 1.0  (e.g. 4 rubrics × 0.25)
│
├─ 5. Estimate target_turns for EfficiencyRubric
│       • Baseline: count of "create_*" + "set_*" events a careful agent needs
│
├─ 6. Save as tasks/task_NN_<slug>.py
│       • Single  task = Task(...)  variable, no other top-level code
│
└─ 7. Verify
        • PYTHONPATH=. python qa_verifiers.py     → row should be OK
        • python run.py --task NN                 → synthetic perfect log
        • python run.py --task NN --log <real>    → real session log
```

### Flow: edit an EXISTING task verifier

```
┌─ 1. Open tasks/task_NN_<slug>.py
├─ 2. Adjust checks / weights / tolerances / target_turns in place
├─ 3. Re-run qa_verifiers.py — flag if it now scores STRICT/LENIENT
└─ 4. Re-run run.py against any saved real logs to confirm parity
```

### Flow: extend the LIBRARY

**Add a new check primitive:**
```
1. Pick the right module      verifier/checks/<group>_checks.py
2. Add a @dataclass with run(log) -> CheckResult
3. Add a row to §8 catalog (this doc)
4. (Optional) extend qa_verifiers.collect_expected() if the check
   constrains shape counts or event counts (so the synthesized
   perfect log includes what the new check expects)
5. Use it in any task verifier
```

**Add a new rubric category** (rare — most needs fit existing 9):
```
1. Add verifier/rubrics/<name>.py:
       from verifier.rubrics._base import Rubric
       def <Name>Rubric(checks, weight=0.5):
           return Rubric(name="<name>", checks=checks, weight=weight)
2. Add a row to §7 "Named factories" table
```

**Change the scoring formula:**
- Per-rubric partial credit lives in `verifier/rubrics/_base.py:Rubric.run`.
- Efficiency multiplier lives in `verifier/rubrics/efficiency.py`.

---

## 10. Writing a Task Verifier

When asked to write a verifier for a task, read the task's row from
`task-docs/tasks.csv` (Simplified Prompt + Thorough Description), then write
`tasks/<task_id>.py` using ONLY the primitives in §8.

### Rules

- Import ONLY from the modules listed in §7 and §8.
- Define only a single `task = Task(...)` variable. No functions, no classes,
  no other top-level logic.
- Do not invent check classes not in the catalog.
- Skip tasks with `Scope = planned` or `Scope = out_of_scope`.
- Choose tolerances appropriate to the task (tighter for pixel-precise, looser
  for freehand).
- Size weights so they sum to your task's intended max (typically 1.0).

### Template

```python
from verifier.types import Task

from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.text         import TextRubric
from verifier.rubrics.property     import PropertyRubric
from verifier.rubrics.effect       import EffectRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.page         import PageRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric

from verifier.checks.shape_checks     import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks  import LayersAligned, LayersSymmetricX
from verifier.checks.fill_checks      import SolidColorEquals, FillTypeIs
from verifier.checks.stroke_checks    import StrokeExists
from verifier.checks.property_checks  import OpacityEquals, CornerRadiusEquals
from verifier.checks.text_checks      import TextContent
from verifier.checks.effect_checks    import DropShadowExists
from verifier.checks.structure_checks import LayerInsideFrame, ChildCountAtLeast
from verifier.checks.page_checks      import PageCount
from verifier.checks.event_checks     import EventTypeUsed, ToolUsed

task = Task(
    id="<task_id>",
    description="<one-line description>",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=2),
            ShapeCount("ellipse",   equals=1),
        ], weight=0.25),

        AlignmentRubric([
            LayersAligned("rectangle", axis="center_y"),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("ellipse"),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
```

---

## 11. CLI Runner (`run.py`)

```bash
python run.py --task task_01 --log logs/house_sample.json
python run.py --task 01      --log logs/house_sample.json   # numeric prefix
python run.py --task task_01_house_task_comprehensive --log logs/...  # full
```

Without `--log`, the runner uses a synthetic perfect log built by `qa_verifiers.py`.

Output is human-readable, plus full JSON. Saved to:
- `delivery-1/task_NN/output/<timestamp>/` if that folder exists, with
  `result.json`, `log.json`, `reward.txt`.
- Else `scores/<task_id>_<timestamp>.json`.

Sample output:

```
Task : task_01_house_task_comprehensive
Log  : logs/house_sample.json
────────────────────────────────────────────────
  fundamentals      0.2000 / 0.2   (100%)
    ✓ rectangle: expected 2, got 2
    ...
  alignment         0.1000 / 0.2   (50%)
    ✓ ellipse aligned on center_y: max diff 3.0px
    ✗ ellipse symmetric on X: max deviation 28.4px
────────────────────────────────────────────────
  base_score        0.7500 / 1.0
  efficiency        ×0.85  (42 turns, target 30, λ=0.05)
  FINAL             0.6375 / 1.0
```

---

## 12. QA Harness (`qa_verifiers.py`)

For each `tasks/*.py`, synthesizes a perfect log and an empty log, runs the
verifier, and flags:

- `CRASH` — verifier raised an exception
- `TOO STRICT` — perfect log scored < 0.7
- `TOO LENIENT` — empty log scored > 0.3
- `OK`

Run after editing checks, rubrics, or task files:

```bash
PYTHONPATH=. python qa_verifiers.py
```

---

## 13. `config.yaml`

```yaml
efficiency:
  lambda: 0.05   # steepness of turn penalty. higher = harsher.

alignment:
  default_tolerance_px: 5.0

property:
  default_opacity_tolerance: 0.02
  default_radius_tolerance: 1.0
```

---

## 14. Task Source (`task-docs/tasks.csv`)

50 tasks with fields: `Difficulty`, `Thorough Description`, `Simplified Prompt`,
`Time (minutes)`, `Step-by-step`, `Scope`.

`Scope` values:
- `in_scope` — feature implemented in test-app. Verifier can be written.
- `planned` — feature in test-app checklist but not yet built. Wait until shipped.
- `out_of_scope` — feature not planned (boolean ops, auto-layout, components,
  variables, masks, inner shadow).

The `scope` field on `Task` should mirror the row's `Scope` (default `in_scope`).

---

## 15. Setup

```bash
cd test-verifier
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

`requirements.txt`:
```
pyyaml>=6.0
```

---

## 16. Check Knowledge Tree

A second view of the catalog from §8: same 87 checks, but grouped by the
**primitive concept** a verifier author thinks about rather than by the file
they live in. Use this when picking checks for a task ("I need an alignment
primitive — go to branch 3") or when deciding what new primitive to author
("Visual/Effects has gaps for shadow offset/blur — write those next").

### How to read a leaf

Every leaf cites the source as `<file>:<class>` so an editor can jump to it.
A `[GAP]` leaf is a primitive concept the test-app supports (a feature that
ships, a field that exists in `outcome.document`, or an event that emits) but
no check class implements yet.

### The 11 branches

#### 1. Existence & Counts
*Does the right number of the right thing exist?*

- `shape_checks.py:ShapeCount` — exactly N layers of a type
- `shape_checks.py:ShapeCountAtLeast` — at least N layers of a type
- `shape_checks.py:PolygonSidesEquals` — all polygons have N sides
- `shape_checks.py:StarPointsEquals` — all stars have N points
- `shape_checks.py:StarInnerRatioEquals` — star inner ratio
- `structure_checks.py:ChildCount` — parent has exactly N children
- `structure_checks.py:ChildCountAtLeast` — parent has ≥ N children
- `structure_checks.py:LayerTotalCount` — total layers across pages
- `structure_checks.py:LayerInsideFrame` — ≥1 layer of type is inside a frame
- `page_checks.py:PageCount` — document has exactly N pages
- `page_checks.py:PageCountAtLeast` — document has ≥ N pages
- `fill_checks.py:LayerHasNoFill` — ≥1 layer has no visible fills

#### 2. Shape & Geometry — Single layer
*Where is one thing, how big is it, how is it rotated?*

- `geometry_checks.py:LayerSizeEquals` — width/height equals
- `geometry_checks.py:LayerPosition` — position equals
- `geometry_checks.py:LayerRotationEquals` — rotation in degrees
- `geometry_checks.py:LayerIsCircular` — w ≈ h (intent: round)
- `geometry_checks.py:LayerIsSquare` — w ≈ h (intent: square)
- `geometry_checks.py:LayerAspectRatioGreaterThan` — aspect ratio threshold
- `geometry_checks.py:FrameSizeEquals` — a frame's dimensions
- `[GAP] ArcStartAngleEquals` — `ellipse.arcStartAngle` field, no check
- `[GAP] ArcEndAngleEquals` — `ellipse.arcEndAngle` field, no check
- `[GAP] EllipseInnerRadiusEquals` — `ellipse.innerRadius` field, no check

#### 3. Layout — Multi-layer arrangement
*Are several things arranged together correctly?*

- `geometry_checks.py:LayersAligned` — same coord on axis
- `geometry_checks.py:LayersSymmetricX` — symmetric around center X
- `geometry_checks.py:LayersDistributed` — evenly spaced on axis
- `geometry_checks.py:LayersConcentric` — share center point
- `geometry_checks.py:LayersStacked` — stacked along axis with gap
- `geometry_checks.py:LayersInGrid` — rows × cols regular grid
- `geometry_checks.py:OffsetGridLayout` — offset / honeycomb grid
- `geometry_checks.py:RadialDistribution` — n layers at equal angles
- `geometry_checks.py:RadialDistributionExcludeCentral` — radial around a center layer
- `geometry_checks.py:LayersEvenlyRotated` — rotations evenly stepped
- `geometry_checks.py:LayersHaveRotations` — covers expected rotations
- `geometry_checks.py:LayersHaveAspectMix` — mix of horizontal + vertical
- `geometry_checks.py:LayersAlternatingColors` — sorted layers cycle N colors
- `geometry_checks.py:LayerEdgesAligned` — edge-of-A ≈ edge-of-B
- `geometry_checks.py:LayerCenteredInFrame` — child centered in parent
- `geometry_checks.py:LayerCenteredOnLayer` — A's center ≈ B's center
- `geometry_checks.py:LayersSameDimensions` — uniform w & h
- `geometry_checks.py:LinesOnDiagonal` — two lines form an X across a rect

#### 4. Spatial Relations — Two-layer
*How do two specific layers relate?*

- `geometry_checks.py:DistanceBetween` — min pair distance ≈ N px
- `geometry_checks.py:LayersOverlap` — bbox intersection
- `geometry_checks.py:LayerBoundsInside` — inner bbox fits in outer
- `geometry_checks.py:LayerOnTopOf` — z-order: A above B
- `geometry_checks.py:LayerNextTo` — A on a given side of B
- `geometry_checks.py:LayerContains` — direct child containment
- `geometry_checks.py:LayerWidthFraction` — inner width as % of parent

#### 5. Visual — Fill
*What's painted on it?*

- `fill_checks.py:SolidColorEquals` — ≥1 layer has this fill color
- `fill_checks.py:AllSolidColorEquals` — every layer of type matches
- `fill_checks.py:FillTypeIs` — kind is solid / image / …
- `fill_checks.py:FillCount` — exactly N fills per layer
- `fill_checks.py:FillOpacityEquals` — fills[i].opacity
- `fill_checks.py:ImageFillExists` — ≥1 layer has image fill
- `fill_checks.py:DistinctSolidColors` — ≥ N distinct fills in document
- `fill_checks.py:SameColorAcrossTypes` — first layer of each type shares color
- `fill_checks.py:LayersHaveColorOrder` — sorted layers match color sequence (sort by x/y/size)
- `fill_checks.py:CentermostLayerHasColor` — centroid layer has this color
- `fill_checks.py:LayersAllSameColor` — every layer of type shares one solid color
- `[GAP] GradientFillExists` — `paint.kind == "gradient"` (gradient fills are PLANNED in feature-checklist #6 — add when shipped)
- `[GAP] GradientStopColorEquals` — stops[i].color (PLANNED)
- `[GAP] GradientAngleEquals` — gradient angle (PLANNED)
- `[GAP] ImageFitEquals` — `imageFill.fit` (cover / contain / fill / tile)
- `[GAP] ImageRotationEquals` — `imageFill.rotation`

#### 6. Visual — Stroke
*What's outlined and how?*

- `stroke_checks.py:StrokeExists` — ≥1 layer has any stroke
- `stroke_checks.py:StrokeWeightEquals` — stroke weight in px
- `stroke_checks.py:StrokeColorEquals` — stroke paint color
- `stroke_checks.py:StrokeAlignmentIs` — inside / center / outside
- `stroke_checks.py:StrokeIsDashed` — dash pattern present (boolean)
- `stroke_checks.py:DistinctStrokeColors` — ≥ N distinct stroke colors
- `[GAP] DashRatioEquals` — `dash.dash` value within tolerance
- `[GAP] DashGapEquals` — `dash.gap` value within tolerance

#### 7. Visual — Effects
*Shadows and blurs.*

- `effect_checks.py:DropShadowExists` — ≥1 layer has drop shadow
- `effect_checks.py:EffectColorEquals` — shadow color (effect_index)
- `effect_checks.py:LayerBlurExists` — ≥1 layer has layer blur
- `effect_checks.py:BlurRadiusEquals` — blur radius
- `effect_checks.py:DropShadowOffsetEquals` — drop_shadow.x / drop_shadow.y
- `effect_checks.py:DropShadowBlurEquals` — drop_shadow.blur (distinct from layer-blur radius)
- `effect_checks.py:DropShadowSpreadEquals` — drop_shadow.spread
- `effect_checks.py:EffectCount` — number of effects on a layer
- `[GAP] FrameOverflowScrollingIs` — `frame.overflowScrolling` (none/h/v/both)

#### 8. Layer Properties
*Per-layer scalar properties.*

- `property_checks.py:OpacityEquals` — layer-level opacity
- `property_checks.py:VisibilityIs` — visible / hidden
- `property_checks.py:CornerRadiusEquals` — radius (scalar)
- `property_checks.py:CornerRadiusAtLeast` — radius ≥ N
- `property_checks.py:IsFlippedH` — scaleX == -1
- `property_checks.py:IsFlippedV` — scaleY == -1
- `property_checks.py:ConstraintHorizontalEquals` — `constraints.horizontal`
- `property_checks.py:ConstraintVerticalEquals` — `constraints.vertical`
- `[GAP] CornerRadiusTuple` — per-corner [tl, tr, br, bl] (the schema supports a 4-tuple but only scalar checks exist)
- `[GAP] TextResizingModeEquals` — `text.resizingMode` (auto_width/auto_height/fixed)

#### 9. Text & Typography
*What does the text say and how does it look?*

- `text_checks.py:TextContent` — exact match
- `text_checks.py:TextContains` — substring
- `text_checks.py:FontSizeEquals` — fontSize ≈ N
- `text_checks.py:FontWeightEquals` — fontWeight equals
- `text_checks.py:TextAlignEquals` — hAlign value
- `text_checks.py:VerticalAlignEquals` — vAlign value (top/middle/bottom)
- `text_checks.py:LineHeightEquals` — `text.lineHeight.value`
- `text_checks.py:LetterSpacingEquals` — `text.letterSpacing.value`
- `[GAP] TextHasMultipleRuns` — `text.runs[].length > 1` (mixed styling)
- `[GAP] TextRunFontWeightEquals` — `runs[i].fontWeight`

#### 10. Structure & Hierarchy
*Where does a layer sit in the tree?*

- `structure_checks.py:IsGrouped` — ≥1 layer of type inside a group
- `structure_checks.py:ZOrderIsFirst` — layer is at the front
- `structure_checks.py:ZOrderIsLast` — layer is at the back
- `page_checks.py:LayerOnPage` — ≥1 layer of type exists on page N
- `page_checks.py:ActivePageIs` — active page name at session end
- `page_checks.py:PageBackgroundColorEquals` — page background color
- `[GAP] LayerZOrderBefore` — A is earlier in z-order than B (between, not extremes)
- `[GAP] LayerDepthEquals` — layer is N levels deep in hierarchy
- `[GAP] VectorIsClosed` — `vector.network.closed`
- `[GAP] VectorVertexCount` — `vector.network.vertices.length` equals N

#### 11. Behavior — Semantic Events
*What did the agent DO during the session (vs. what's on canvas)?*

- `event_checks.py:EventTypeUsed` — event was emitted ≥1 time
- `event_checks.py:EventTypeCount` — emitted exactly N times
- `event_checks.py:EventTypeCountAtLeast` — emitted ≥ N times
- `event_checks.py:ToolUsed` — tool_change to a given tool id
- `event_checks.py:AlignToolUsed` — align_layers event was used
- `event_checks.py:UndoUsed` — undo event was used
- `[GAP] DistributeToolUsed` — distribute_layers (existing app event, no shortcut check)
- `[GAP] PrototypeConnectionExists` — `create_prototype_connection` event (PLANNED — feature #34)
- `[GAP] PageNavigationOccurred` — `switch_page` event (multi-page is PLANNED)

### Coverage gaps — prioritized

Two tiers based on whether the underlying feature ships in test-app today:

**Tier 1 — Feature SHIPPED, check missing** (✅ = built, ⬜ = open):

| Branch | Gap | Status | Reads from |
|---|---|---|---|
| 2 Geometry | `ArcStartAngleEquals` / `ArcEndAngleEquals` / `EllipseInnerRadiusEquals` | ⬜ | `ellipse.arcStartAngle/arcEndAngle/innerRadius` |
| 5 Fill | `ImageFitEquals` / `ImageRotationEquals` | ⬜ | `imageFill.fit` / `imageFill.rotation` |
| 5 Fill | `LayersAllSameColor` | ✅ | every layer of type shares one color |
| 6 Stroke | `DashRatioEquals` / `DashGapEquals` | ⬜ | `stroke.dash.dash` / `stroke.dash.gap` |
| 7 Effects | `DropShadowOffsetEquals` / `DropShadowBlurEquals` / `DropShadowSpreadEquals` / `EffectCount` | ✅ | `effect.drop_shadow.x/y/blur/spread`, count |
| 7 Effects | `FrameOverflowScrollingIs` | ⬜ | `frame.overflowScrolling` |
| 8 Properties | `CornerRadiusTuple` | ⬜ | `cornerRadius` (4-tuple form) |
| 8 Properties | `ConstraintHorizontalEquals` / `ConstraintVerticalEquals` | ✅ | `constraints.horizontal/vertical` |
| 8 Properties | `TextResizingModeEquals` | ⬜ | `text.resizingMode` |
| 9 Text | `TextHasMultipleRuns` / `TextRunFontWeightEquals` | ⬜ | `text.runs[]` |
| 9 Text | `LetterSpacingEquals` / `LineHeightEquals` / `VerticalAlignEquals` | ✅ | `text.letterSpacing/lineHeight/vAlign` |
| 10 Structure | `LayerZOrderBefore` / `LayerDepthEquals` | ⬜ | parent's `children[]` index |
| 11 Events | `DistributeToolUsed` | ⬜ | `distribute_layers` event |

**Tier 2 — Feature PLANNED in test-app, write check when shipped:**

| Branch | Gap | Waits on feature |
|---|---|---|
| 5 Fill | `GradientFillExists` / `GradientStopColorEquals` / `GradientAngleEquals` | feature-checklist #6 (gradient fills) |
| 10 Structure | `VectorIsClosed` / `VectorVertexCount` | feature-checklist #17–18 (vector vertex editing) |
| 11 Events | `PrototypeConnectionExists` / `PageNavigationOccurred` | features #30 (multi-page), #34 (prototype) |

### Branch ↔ Rubric mapping

Which rubric (`verifier/rubrics/<name>.py`) typically holds checks from each branch:

| Branch | Primary rubric | Secondary |
|---|---|---|
| 1 Existence & Counts | `FundamentalsRubric` | `StructureRubric`, `PageRubric` |
| 2 Shape & Geometry — Single | `AlignmentRubric` | — |
| 3 Layout — Multi-layer | `AlignmentRubric` | — |
| 4 Spatial Relations | `AlignmentRubric` | `StructureRubric` |
| 5 Visual — Fill | `ColorRubric` | — |
| 6 Visual — Stroke | `ColorRubric` | — |
| 7 Visual — Effects | `EffectRubric` | — |
| 8 Layer Properties | `PropertyRubric` | — |
| 9 Text & Typography | `TextRubric` | — |
| 10 Structure & Hierarchy | `StructureRubric` | `PageRubric` |
| 11 Behavior — Events | `EventRubric` | — |

### Adding a new primitive

See §9 "How Verifiers Are Built — Flow: extend the LIBRARY" for the
five-step author flow. After adding, append the new leaf under the relevant
branch above and remove its `[GAP]` row from the prioritized table.
