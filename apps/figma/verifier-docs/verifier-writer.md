# verifier — Claude Code Instructions

When asked to write a verifier for a task, read the task's row from
`task-docs/tasks.csv` (Simplified Prompt + Thorough Description columns),
then write `tasks/<task_id>.py` using ONLY the primitives listed below.

---

## Rules

- Import ONLY from the modules listed in this file.
- Define only a single `task = Task(...)` variable — no functions, no classes, no other logic.
- Do not invent check classes not in this catalog.
- Only use tasks with `Scope = in_scope`. Skip `planned` and `out_of_scope`.
- Choose tolerances appropriate to the task (tighter for pixel-precise tasks, looser for freehand).

---

## Template

```python
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.text         import TextRubric
from verifier.rubrics.property     import PropertyRubric
from verifier.rubrics.effect       import EffectRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.page         import PageRubric
from verifier.rubrics.event        import EventRubric

from verifier.checks.shape_checks     import ShapeCount, ShapeCountAtLeast, PolygonSidesEquals, StarPointsEquals, StarInnerRatioEquals
from verifier.checks.geometry_checks  import LayersAligned, LayersSymmetricX, LayerSizeEquals, LayerPosition, LayerRotationEquals, DistanceBetween, LayerContains, LayersDistributed, LayersSameDimensions, LayerEdgesAligned
from verifier.checks.fill_checks      import SolidColorEquals, AllSolidColorEquals, FillTypeIs, FillCount, ImageFillExists, FillOpacityEquals
from verifier.checks.stroke_checks    import StrokeExists, StrokeWeightEquals, StrokeColorEquals, StrokeAlignmentIs, StrokeIsDashed
from verifier.checks.property_checks  import OpacityEquals, VisibilityIs, CornerRadiusEquals, IsFlippedH, IsFlippedV
from verifier.checks.text_checks      import TextContent, TextContains, FontSizeEquals, FontWeightEquals, TextAlignEquals
from verifier.checks.effect_checks    import DropShadowExists, LayerBlurExists, BlurRadiusEquals, EffectColorEquals
from verifier.checks.structure_checks import LayerInsideFrame, ChildCount, ChildCountAtLeast, IsGrouped, ZOrderIsFirst, ZOrderIsLast, LayerTotalCount
from verifier.checks.page_checks      import PageCount, PageCountAtLeast, LayerOnPage, ActivePageIs
from verifier.checks.event_checks     import EventTypeUsed, EventTypeCount, EventTypeCountAtLeast, AlignToolUsed, UndoUsed, ToolUsed

task = Task(
    id="<task_id>",
    description="<one line>",
    rubrics=[
        FundamentalsRubric([...]),
        AlignmentRubric([...]),
        # add other rubrics as needed
    ],
    efficiency=EfficiencyRubric(target_turns=<N>),
    # efficiency=EfficiencyRubric(target_turns=<N>, lambda_=0.1),  # per-task override
)
```

---

## Check Catalog

### shape_checks
| Class | Args | Checks |
|---|---|---|
| `ShapeCount` | `layer_type, equals` | exactly N layers of type |
| `ShapeCountAtLeast` | `layer_type, minimum` | at least N layers of type |
| `PolygonSidesEquals` | `sides` | all polygons have N sides |
| `StarPointsEquals` | `points` | all stars have N points |
| `StarInnerRatioEquals` | `ratio, tolerance=0.05` | all stars have ≈ inner ratio (0..1) |

### geometry_checks
| Class | Args | Checks |
|---|---|---|
| `LayersAligned` | `layer_type, axis, tolerance=5.0` | same coordinate on axis |
| `LayersSymmetricX` | `layer_type, tolerance=10.0` | symmetric around center X |
| `LayerSizeEquals` | `layer_type, width=None, height=None, tolerance=2.0` | dimensions |
| `LayerPosition` | `layer_type, x=None, y=None, tolerance=5.0` | position |
| `LayerRotationEquals` | `layer_type, degrees, tolerance=2.0` | rotation |
| `DistanceBetween` | `type_a, type_b, expected_px, tolerance=5.0` | distance between layers |
| `LayerContains` | `outer_type, inner_type` | inner is direct child of outer |
| `LayersDistributed` | `layer_type, axis, tolerance=5.0` | evenly spaced |
| `LayersSameDimensions` | `layer_type, tolerance=2.0` | all layers of type have equal w and h |
| `LayerEdgesAligned` | `type_a, edge_a, type_b, edge_b, tolerance=5.0` | edge of type_a ≈ edge of type_b |

axis values: `"x"` `"y"` `"center_x"` `"center_y"`

### fill_checks
| Class | Args | Checks |
|---|---|---|
| `SolidColorEquals` | `layer_type, expected_rgb, fill_index=0, tolerance=0.05` | ≥1 layer has this color |
| `AllSolidColorEquals` | `layer_type, expected_rgb, fill_index=0, tolerance=0.05` | all layers have this color |
| `FillTypeIs` | `layer_type, kind, fill_index=0` | ≥1 layer has fill of kind |
| `FillCount` | `layer_type, equals` | all layers have N fills |
| `ImageFillExists` | `layer_type` | ≥1 layer has image fill |
| `FillOpacityEquals` | `layer_type, opacity, fill_index=0, tolerance=0.05` | fill-level opacity |

`expected_rgb`: `{"r": 0..1, "g": 0..1, "b": 0..1}` — NOT 0..255
`kind`: `"solid"` or `"image"`

### stroke_checks
| Class | Args | Checks |
|---|---|---|
| `StrokeExists` | `layer_type` | ≥1 layer has a stroke |
| `StrokeWeightEquals` | `layer_type, weight, tolerance=0.5` | stroke weight |
| `StrokeColorEquals` | `layer_type, expected_rgb, tolerance=0.05` | stroke color |
| `StrokeAlignmentIs` | `layer_type, alignment` | stroke alignment |
| `StrokeIsDashed` | `layer_type` | stroke has dash pattern |

`alignment`: `"inside"` `"center"` `"outside"`

### property_checks
| Class | Args | Checks |
|---|---|---|
| `OpacityEquals` | `layer_type, opacity, tolerance=0.02` | layer opacity (0..1) |
| `VisibilityIs` | `layer_type, visible` | visible/hidden |
| `CornerRadiusEquals` | `layer_type, radius, tolerance=1.0` | corner radius |
| `IsFlippedH` | `layer_type` | scaleX == -1 |
| `IsFlippedV` | `layer_type` | scaleY == -1 |

### text_checks
| Class | Args | Checks |
|---|---|---|
| `TextContent` | `expected` | exact text match |
| `TextContains` | `substring` | text contains substring |
| `FontSizeEquals` | `size, tolerance=1.0` | font size |
| `FontWeightEquals` | `weight` | font weight (e.g. 400, 700) |
| `TextAlignEquals` | `align` | hAlign value |

`align`: `"left"` `"center"` `"right"` `"justify"`

### effect_checks
| Class | Args | Checks |
|---|---|---|
| `DropShadowExists` | `layer_type` | ≥1 layer has drop shadow |
| `LayerBlurExists` | `layer_type` | ≥1 layer has layer blur |
| `BlurRadiusEquals` | `layer_type, radius, tolerance=1.0` | blur radius |
| `EffectColorEquals` | `layer_type, effect_index, expected_rgb, tolerance=0.05` | shadow color |

### structure_checks
| Class | Args | Checks |
|---|---|---|
| `LayerInsideFrame` | `layer_type` | ≥1 layer is child of a frame |
| `ChildCount` | `parent_type, equals` | parent has exactly N children |
| `ChildCountAtLeast` | `parent_type, minimum` | parent has ≥ N children |
| `IsGrouped` | `layer_type` | ≥1 layer is inside a group |
| `ZOrderIsFirst` | `layer_type` | ≥1 layer is at front |
| `ZOrderIsLast` | `layer_type` | ≥1 layer is at back |
| `LayerTotalCount` | `equals` | total layers across all pages |

### page_checks
| Class | Args | Checks |
|---|---|---|
| `PageCount` | `equals` | document has exactly N pages |
| `PageCountAtLeast` | `minimum` | document has ≥ N pages |
| `LayerOnPage` | `layer_type, page_index` | layer of type exists on page at index (0-based) |
| `ActivePageIs` | `page_name` | active page at session end has this name |

### event_checks  ← reads semantic stream, not outcome
| Class | Args | Checks |
|---|---|---|
| `EventTypeUsed` | `event_name` | semantic event was emitted ≥1 time |
| `EventTypeCount` | `event_name, equals` | emitted exactly N times |
| `EventTypeCountAtLeast` | `event_name, minimum` | emitted ≥ N times |
| `AlignToolUsed` | — | `align_layers` event was used |
| `UndoUsed` | — | `undo` event was used |
| `ToolUsed` | `tool_id` | `tool_change` to given tool id occurred |

Common `event_name` values: `create_rectangle` `create_ellipse` `create_polygon` `create_frame`
`move_layer` `resize_layer` `rotate_layer` `align_layers` `group_selection` `ungroup`
`set_fill_color` `set_corner_radius` `set_layer_opacity` `rename_layer` `undo` `redo`

---

## layer_type values
`rectangle` `ellipse` `polygon` `star` `line` `arrow` `text` `vector`
`image` `frame` `section` `group` `slice`

---

## Running
```bash
cd verifier
.venv/bin/python run.py --task house_task --log logs/house_sample.json
```
Score is automatically saved to `scores/<task_id>_<timestamp>.json` on every run.

## Setup
```bash
cd verifier
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```
