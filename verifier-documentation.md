# Verifier Framework — Documentation

This document is the single source of truth for the CUA verifier framework.
Read this before writing any code.

---

## 1. Purpose

The Figma mock app is used as a controlled environment for testing CUA (Computer Use
Agent) models. Agents are given a task prompt and interact with the app. After the agent
finishes, the verifier reads the log the app produced and scores how well the task was
completed.

The verifier answers one question: **"Did the agent build the right thing?"**
It does not care how the agent did it — only what ended up on the canvas.

---

## 2. System Overview

```
tasks.csv                          log.json  (downloaded from test-app)
(task definitions)                 (raw + semantic + outcome streams)
        │                                      │
        ▼                                      ▼
tasks/<task_id>.py   ──────────►   run.py  (CLI runner)
(verifier script,                       │
 Claude Code writes)                    │ runs rubrics → checks → efficiency
                                        ▼
                               scores/<task_id>_<session_id>.json
```

---

## 3. Log Format

The test-app exports a single JSON file (`figma-mock-log-<sessionId>.json`) with three
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
| `semantic[]` | Efficiency rubric (turn count) |
| `outcome.summary.shapeCounts` | Fundamentals rubric (fast count lookup) |
| `outcome.document` | All geometry, fill, stroke, effect, text checks |

---

## 4. Scoring Model

### Rubrics

Each task defines a list of rubrics. Every rubric scores **0 .. 0.5**.
Tasks can have any number of rubrics — the more rubrics, the higher the possible total.

```
base_score = sum of all rubric scores
```

Partial credit applies within every rubric: each failing check reduces the rubric score
proportionally. A rubric with 3 checks where 2 pass scores `0.5 × 2/3 = 0.33`.

### Efficiency multiplier

After all rubrics run, the base score is multiplied by an efficiency factor based on
how many semantic events the agent used versus the per-task target.

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
- Per-task override: set `lambda_` on `EfficiencyRubric(target_turns=30, lambda_=0.1)`.
- Higher λ = steeper penalty for going over target turns.

---

## 5. Folder Structure

```
test-verifier/
│
├── verifier/                      ← framework (written once)
│   ├── types.py                   ← data classes: CheckResult, RubricResult,
│   │                                 EfficiencyResult, TaskResult, Task
│   ├── loader.py                  ← load + validate log JSON
│   ├── config.py                  ← reads config.yaml
│   ├── math_utils.py              ← find_layers_by_type, layer_center, geometry helpers
│   │
│   ├── checks/                    ← check primitives (leaf nodes)
│   │   ├── shape_checks.py
│   │   ├── geometry_checks.py
│   │   ├── fill_checks.py
│   │   ├── stroke_checks.py
│   │   ├── property_checks.py
│   │   ├── text_checks.py
│   │   ├── effect_checks.py
│   │   └── structure_checks.py
│   │
│   └── rubrics/                   ← rubric containers (node layer)
│       ├── fundamentals.py
│       ├── alignment.py
│       ├── color.py
│       ├── text.py
│       ├── property.py
│       ├── effect.py
│       ├── structure.py
│       └── efficiency.py
│
├── tasks/                         ← one file per task (Claude Code writes these)
│   └── house_task.py
│
├── task-docs/
│   └── tasks.csv                  ← 50 tasks with Scope field
│
├── logs/                          ← log JSON files downloaded from test-app
├── scores/                        ← verifier output JSON files
├── config.yaml                    ← global defaults (λ, tolerances)
├── run.py                         ← CLI runner
├── requirements.txt
└── CLAUDE.md                      ← instructions for writing new task verifiers
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
    name:      str              # "fundamentals", "alignment", ...
    score:     float            # 0 .. 0.5
    max_score: float            # 0.5
    checks:    list[CheckResult]

@dataclass
class EfficiencyResult:
    multiplier:    float   # 0.5 .. 1.0
    actual_turns:  int
    target_turns:  int
    lambda_used:   float
    message:       str

@dataclass
class TaskResult:
    task_id:               str
    log_path:              str
    rubrics:               list[RubricResult]
    base_score:            float   # sum of rubric scores
    efficiency:            EfficiencyResult
    final_score:           float   # base_score × multiplier

@dataclass
class Task:
    id:          str
    description: str
    rubrics:     list          # any combination of rubric objects
    efficiency:  object        # EfficiencyRubric instance
```

---

## 7. Check Primitives — Full Catalog

All checks live in `verifier/checks/`. Each check exposes a single method:
`run(log: dict) -> CheckResult`.

### shape_checks.py

| Class | Arguments | What it checks |
|---|---|---|
| `ShapeCount` | `layer_type, equals` | document has exactly N layers of type |
| `ShapeCountAtLeast` | `layer_type, minimum` | document has at least N layers of type |
| `PolygonSidesEquals` | `sides` | all polygon layers have exactly N sides |
| `StarPointsEquals` | `points` | all star layers have exactly N points |
| `StarInnerRatioEquals` | `ratio, tolerance=0.05` | all star layers have approximately this inner ratio (0..1) |

`layer_type` values: `rectangle` `ellipse` `polygon` `star` `line` `arrow`
`text` `vector` `image` `frame` `section` `group`

### geometry_checks.py

| Class | Arguments | What it checks |
|---|---|---|
| `LayersAligned` | `layer_type, axis, tolerance=5.0` | all layers of type share same coordinate on axis |
| `LayersSymmetricX` | `layer_type, tolerance=10.0` | layers symmetric around collective center X |
| `LayerSizeEquals` | `layer_type, width=None, height=None, tolerance=2.0` | layers have approx given dimensions |
| `LayerPosition` | `layer_type, x=None, y=None, tolerance=5.0` | layers are at approx given position |
| `LayerRotationEquals` | `layer_type, degrees, tolerance=2.0` | layers have approx given rotation |
| `DistanceBetween` | `type_a, type_b, expected_px, tolerance=5.0` | distance between nearest pair of layers |
| `LayerContains` | `outer_type, inner_type` | at least one inner_type layer is inside an outer_type layer |
| `LayersDistributed` | `layer_type, axis, tolerance=5.0` | layers are evenly spaced on axis |

`axis` options: `"x"` `"y"` `"center_x"` `"center_y"`

### fill_checks.py

| Class | Arguments | What it checks |
|---|---|---|
| `SolidColorEquals` | `layer_type, expected_rgb, fill_index=0, tolerance=0.05` | at least one layer has solid fill matching color |
| `AllSolidColorEquals` | `layer_type, expected_rgb, fill_index=0, tolerance=0.05` | every layer matches the color |
| `FillTypeIs` | `layer_type, kind` | at least one layer has fill of given kind |
| `FillCount` | `layer_type, equals` | all layers of type have exactly N fills |
| `ImageFillExists` | `layer_type` | at least one layer has an image fill |
| `FillOpacityEquals` | `layer_type, opacity, fill_index=0, tolerance=0.05` | fill-level opacity (not layer opacity) |

`expected_rgb` format: `{"r": 0..1, "g": 0..1, "b": 0..1}` — **not 0..255**
`kind` values: `"solid"` `"image"`

### stroke_checks.py

| Class | Arguments | What it checks |
|---|---|---|
| `StrokeExists` | `layer_type` | at least one layer has a stroke |
| `StrokeWeightEquals` | `layer_type, weight, tolerance=0.5` | stroke weight |
| `StrokeColorEquals` | `layer_type, expected_rgb, tolerance=0.05` | stroke paint color |
| `StrokeAlignmentIs` | `layer_type, alignment` | stroke alignment |
| `StrokeIsDashed` | `layer_type` | stroke has a dash pattern |

`alignment` values: `"inside"` `"center"` `"outside"`

### property_checks.py

| Class | Arguments | What it checks |
|---|---|---|
| `OpacityEquals` | `layer_type, opacity, tolerance=0.02` | layer opacity (0..1) |
| `VisibilityIs` | `layer_type, visible` | layer visible / hidden |
| `CornerRadiusEquals` | `layer_type, radius, tolerance=1.0` | corner radius (scalar) |
| `IsFlippedH` | `layer_type` | scaleX == -1 (horizontal flip) |
| `IsFlippedV` | `layer_type` | scaleY == -1 (vertical flip) |

### text_checks.py

| Class | Arguments | What it checks |
|---|---|---|
| `TextContent` | `expected` | any text layer has exactly this content |
| `TextContains` | `substring` | any text layer contains this substring |
| `FontSizeEquals` | `size, tolerance=1.0` | font size on any text layer |
| `FontWeightEquals` | `weight` | font weight on any text layer |
| `TextAlignEquals` | `align` | horizontal alignment on any text layer |

`align` values: `"left"` `"center"` `"right"` `"justify"`

### effect_checks.py

| Class | Arguments | What it checks |
|---|---|---|
| `DropShadowExists` | `layer_type` | at least one layer has a drop shadow effect |
| `LayerBlurExists` | `layer_type` | at least one layer has a layer blur effect |
| `BlurRadiusEquals` | `layer_type, radius, tolerance=1.0` | blur radius value |
| `EffectColorEquals` | `layer_type, effect_index, expected_rgb, tolerance=0.05` | drop shadow color |

### structure_checks.py

| Class | Arguments | What it checks |
|---|---|---|
| `LayerInsideFrame` | `layer_type` | at least one layer of type is a child of a frame |
| `ChildCount` | `parent_type, equals` | parent has exactly N children |
| `ChildCountAtLeast` | `parent_type, minimum` | parent has at least N children |
| `IsGrouped` | `layer_type` | at least one layer of type is inside a group |
| `ZOrderIsFirst` | `layer_type` | at least one layer is at the front (last in children array) |
| `ZOrderIsLast` | `layer_type` | at least one layer is at the back (first in children array) |
| `LayerTotalCount` | `equals` | total layer count across all pages |

---

## 8. Rubric Types

All rubrics live in `verifier/rubrics/`. Each scores **0 .. 0.5** with partial credit.

| Rubric class | Typical checks used |
|---|---|
| `FundamentalsRubric` | shape_checks |
| `AlignmentRubric` | geometry_checks |
| `ColorRubric` | fill_checks, stroke_checks |
| `TextRubric` | text_checks |
| `PropertyRubric` | property_checks |
| `EffectRubric` | effect_checks |
| `StructureRubric` | structure_checks |
| `EfficiencyRubric` | reads `semantic[]` — returns multiplier, not a rubric score |

`EfficiencyRubric` is special: it does not produce a `RubricResult`. It produces an
`EfficiencyResult` with a `multiplier` (0.5..1.0) that scales the final score.

---

## 9. Task Verifier Scripts

Each task gets one Python file in `tasks/`. Claude Code writes these.
The file must define a module-level `task` variable.

### Template

```python
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment import AlignmentRubric
from verifier.rubrics.efficiency import EfficiencyRubric
from verifier.checks.shape_checks import ShapeCount
from verifier.checks.geometry_checks import LayersAligned, LayersSymmetricX

task = Task(
    id="<task_id>",
    description="<one line>",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("polygon",   equals=1),
            ShapeCount("ellipse",   equals=2),
            ShapeCount("rectangle", equals=2),
        ]),
        AlignmentRubric([
            LayersAligned(layer_type="ellipse", axis="center_y", tolerance=8.0),
            LayersSymmetricX(layer_type="ellipse", tolerance=15.0),
        ]),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
    # efficiency=EfficiencyRubric(target_turns=30, lambda_=0.1),  # per-task override
)
```

### Rules for Claude Code

- Import ONLY from the modules listed in section 7.
- Do not write functions, classes, or logic — only the `task = Task(...)` definition.
- Do not invent check classes that are not in the catalog.
- Choose tolerances appropriate to the task description.
- Use `layer_type` values that match actual Figma primitive names.

---

## 10. CLI Runner (`run.py`)

```bash
# Run a verifier against a log file
python run.py --task house_task --log logs/house_sample.json

# Save result as JSON
python run.py --task house_task --log logs/house_sample.json --output scores/house_result.json
```

Output format:

```
Task : house_task
Log  : logs/house_sample.json
────────────────────────────────────────────────
  fundamentals      0.5000 / 0.5   (100%)
    ✓ polygon: expected 1, got 1
    ✓ ellipse: expected 2, got 2
    ✓ rectangle: expected 2, got 2
  alignment         0.2500 / 0.5   (50%)
    ✓ ellipse aligned on center_y: max diff 3.0px
    ✗ ellipse symmetric on X: max deviation 28.4px
────────────────────────────────────────────────
  base_score        0.7500 / 1.0
  efficiency        ×0.85  (42 turns, target 30, λ=0.05)
  FINAL             0.6375 / 1.0
```

Score JSON written to `scores/`:

```json
{
  "task_id": "house_task",
  "log_path": "logs/house_sample.json",
  "rubrics": [
    {
      "name": "fundamentals",
      "score": 0.5,
      "max_score": 0.5,
      "checks": [
        { "passed": true,  "score": 1.0, "max_score": 1.0, "message": "polygon: expected 1, got 1" },
        { "passed": true,  "score": 1.0, "max_score": 1.0, "message": "ellipse: expected 2, got 2" },
        { "passed": true,  "score": 1.0, "max_score": 1.0, "message": "rectangle: expected 2, got 2" }
      ]
    },
    {
      "name": "alignment",
      "score": 0.25,
      "max_score": 0.5,
      "checks": [
        { "passed": true,  "score": 1.0, "max_score": 1.0, "message": "ellipse aligned on center_y: max diff 3.0px" },
        { "passed": false, "score": 0.0, "max_score": 1.0, "message": "ellipse symmetric on X: max deviation 28.4px" }
      ]
    }
  ],
  "base_score": 0.75,
  "efficiency": {
    "multiplier": 0.85,
    "actual_turns": 42,
    "target_turns": 30,
    "lambda_used": 0.05,
    "message": "42 turns used, target 30, λ=0.05 → multiplier 0.85"
  },
  "final_score": 0.6375
}
```

---

## 11. config.yaml

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

## 12. Task Source (`task-docs/tasks.csv`)

50 tasks with fields: `Difficulty`, `Thorough Description`, `Simplified Prompt`,
`Time (minutes)`, `Step-by-step`, `Scope`.

`Scope` values:
- `in_scope` — 23 tasks. Features implemented in test-app. Verifier can be written now.
- `planned` — 5 tasks. Feature in test-app checklist but not yet built (gradients, image fill). Verifier will be writable once implemented.
- `out_of_scope` — 22 tasks. Feature not planned (boolean ops, auto-layout, components, variables, masks, inner shadow).

---

## 13. Setup

```bash
cd test-verifier
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

`requirements.txt`:
```
pyyaml>=6.0
```
