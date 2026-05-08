---
name: reinforce-verifier
description: Fully harden a task verifier in test-verifier/ — generate a 100-case stress battery, identify false positives, add new primitives + critical flags + harness handlers, run a round-3 novel-edge-case hunt, and iterate until ≤5 strict FPs. Produces qa_per_task/task_NN_extended.py, qa_per_task/task_NN_round3.py, qa_per_task/task_NN_findings.md. Use when the user wants to "QA", "harden", "stress-test", "reinforce", or "100-case-test" a task verifier.
---

# Reinforce a Task Verifier — Full Treatment

A playbook for taking a task verifier from "passes too easily" to "catches real failures." Derived from the 3-round hardening of `task_01_house_task_comprehensive` (FPs: ~35 → 6 → 0 strict).

**"Hardening" in this codebase means doing all of the following:**
1. Generate a `~100-case` stress battery (`qa_per_task/task_NN_extended.py`)
2. Identify FPs (cases scoring ≥ 0.95 that should fail)
3. Add new check primitives + mark them critical
4. Update the harness so the synthetic perfect log still scores 1.000
5. Generate a `~30-case` round-3 novel-deception battery (`qa_per_task/task_NN_round3.py`)
6. Iterate until **strict FPs ≤ 5**
7. Sync `delivery-1/` via `scripts/sync_delivery.sh`
8. Write `qa_per_task/task_NN_findings.md` with round-by-round results

Anything less is a partial pass.

## When to use

User says any of:
- "QA task NN" / "QA all tasks"
- "harden / reinforce / stress-test / 100-case test task NN"
- "find edge cases the verifier doesn't catch"
- "find false positives / true negatives that aren't caught"
- "make sure the verifier is bulletproof"

## Mental model

A verifier is a sum of weighted **rubrics**. Each rubric is a list of **checks**. A perfect log scores `1.0`; a broken log should score lower.

Two scoring mechanics worth memorizing:

- **Weight dilution** — a single failed check in a 4-check rubric only docks 25% × rubric_weight = 5% of total. Critical defects need stronger penalties.
- **Critical-fail halving** — `Rubric(checks, weight, critical=[indices])`. If any critical check fails, the rubric score is halved AFTER computing the pass-rate. A single critical fail drops the rubric ~10–15% of total. Use it for prompt-explicit requirements.

False positive types you'll hunt:
- **Weight-dilution FPs**: a real defect only docks 5%, total stays ≥ 0.95.
- **Trivial-pass FPs**: a check has a self-trivial bug (e.g., `LayerBoundsInside(rectangle, rectangle)` passes when body fits inside body via ID equality skip).
- **Role-confusion FPs**: door grew bigger than body, structural checks now pass on the wrong instance.
- **Tolerance-edge FPs**: 4° rotation passes a 5° tolerance.
- **Visibility-trick FPs**: shape exists structurally but is invisible (alpha=0, opacity=0, visible=False).
- **Z-order FPs**: roof rendered behind body; checks don't enforce stacking.
- **Multi-frame FPs**: shapes split across frames; "inside a frame" passes for each individually.

## The full loop

```
0. Read prompt + current verifier
1. Generate 100-case battery (qa_per_task/task_NN_extended.py)
   - 10 categories × 10 cases each
2. Run; flag any case scoring ≥ 0.95 that should fail (= "strict FP")
3. Categorize FPs by failure mode
4. For each mode:
   a. Design or extend a primitive
   b. Add to task_NN with critical flag
   c. Update qa_verifiers.py harness if perfect log breaks
5. Re-run battery; iterate until strict FPs ≤ 5
6. Generate round-3 battery (qa_per_task/task_NN_round3.py)
   - 30 NOVEL cases the round-1 battery didn't cover
   - Categories K (subtle deception), L (visibility), M (geometry tricks), N (structural), O (wrong types)
7. Find new FPs; add fixes; re-iterate
8. Sync delivery-1; write findings doc
```

## Step 0 — Read the prompt and current verifier

```
test-verifier/tasks/task_NN_*.py        ← the verifier
delivery-1/task_NN/prompt.md            ← the prompt (what the agent must build)
```

Identify the prompt's **mandatory properties** (counts, sizes, colors, alignments, geometry). Each maps to ≥1 critical check.

## Step 1 — Build the 100-case stress battery

File: `qa_per_task/task_NN_extended.py`. Pattern (≈100 lines):

```python
"""100 edge cases for task NN — runs all and prints a sorted score table."""
from __future__ import annotations
import sys, math
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
)
from tasks import task_NN_xxx as t
T = t.task

def evt(...): ...
def L(t, x, y, w, h, fill, **extra): return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)
def perfect_design(): return [...]   # the canonical good design
def H(layers=None, evts=None, frame_w=..., frame_h=..., in_frame=True):
    """Wrap layers in a frame + default events."""
    ...

CASES = []
def add(label, log): CASES.append((label, log))

# A. Counts (10 cases): extra/missing of each type
def case_a1(): ...; add("A1: 3 of X (extra)", case_a1())
...

# Run all
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
for i, (label, log) in enumerate(CASES, 1):
    score, b = score_task(T, log)
    breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
    eff = b["efficiency"]
    flag = " ⚠ FP" if score >= 0.95 else ""
    print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
```

### Required category coverage (10 cases per category, 10 categories = 100 total)

| Category | What to test |
|----------|-------------|
| **A** Counts | extra of each type, missing of each type, doubled, halved, off-by-1 |
| **B** Colors / fills | image fill, gradient fill, stroke-only, empty fills, near-identical colors, alpha=0, fillOpacity=0.1, layer.opacity=0, fill.visible=False, stacked-fills (first solid, rest gradient/image) |
| **C** Sizing | each layer too big / too small / extreme aspect, just-inside-tol, just-outside-tol |
| **D** Position | wrong corner, off-frame, off-center, edge cases, shifted globally |
| **E** Per-shape variants | wrong polygon sides, wrong star points, rotated 45°/90°/180°/4° (under-tol), flipped, scaleX=-1 |
| **F** Subcomponent variants | squashed, different size, overlapping, stacked vertically vs horizontally, edge-touching |
| **G** Frame variants | frame rotated, frame too big/small, nested frames, multiple frames, frame with stroke / image fill, frame translated |
| **H** Tools / events | extra tool changes, deletions, undo/redo, missing events, duplicate events, wrong tool used |
| **I** Hierarchy | shapes in group inside frame, shapes in section, shapes split across frames, shapes on page (no frame), 3-deep nesting, shapes on page 2 |
| **J** Bizarre | mirrored (scaleX=-1), rotated 180°, 1×1 degenerate, negative coords, all shapes overlapping pile, all shapes = full frame, text spelling out the design name |

This battery surfaces ~80% of FPs. The remaining hide in round 3.

## Step 2 — Run, flag FPs

```bash
cd test-verifier
PYTHONPATH=. python3 qa_per_task/task_NN_extended.py | grep "1.000"
PYTHONPATH=. python3 qa_per_task/task_NN_extended.py | grep " ⚠ FP"
```

Categorize the FPs:
- **Legitimate 1.000s** (cases where 1.000 is correct: A control "perfect" case, B "all distinct" case, intentional acceptable variants like "extras present but design intact").
- **Strict FPs** (cases that should clearly fail but score 1.000).
- **Borderline** (0.92–0.95: extras tolerated; usually OK).

Aim: strict FPs after round 1 ≤ 5.

## Step 3 — Design fixes (primitive patterns)

Match each FP to a pattern. Mirror the dataclass style in `verifier/checks/*.py`.

### Pattern 1: All<X> (every layer must satisfy)

Replace "≥1 layer satisfies" with "every layer satisfies" when prompt says ALL.

```python
@dataclass
class AllFillTypeIs:
    layer_type: str
    kind: str
    fill_index: int = 0

    def run(self, log):
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers: return CheckResult(passed=False, ...)
        failures = [...]
        return CheckResult(passed=not failures, ...)
```

Existing in repo: `AllFillTypeIs`, `AllLayerWidthFraction`, `AllLayerBoundsInside`.

### Pattern 2: <X>AtLeast / <X>AtMost (threshold)

Replace exact-equals with a range when extras are tolerable. Use AtMost when something should NOT exceed a value.

Existing: `FillOpacityAtLeast` (catches transparent fills), `FillCountAtMost` (catches stacked fills), `LayerSizeAtLeast` (catches degenerate 1×1), `CornerRadiusFractionAtMost` (catches rect-as-circle).

### Pattern 3: Largest / Smallest (role disambiguation)

When a check on `type_a` could be satisfied by a non-canonical instance (e.g., the door instead of the body — both rectangles). Anchor on the largest/smallest instance.

```python
@dataclass
class LayerAboveLargestLayer:
    top_type: str
    bottom_type: str
    tolerance: float = 10.0

    def run(self, log):
        bottoms = find_layers_by_type(...)
        anchor = max(bottoms, key=lambda l: l["w"] * l["h"])
        # check against anchor specifically, not "any bottom"
```

Existing: `LayerAboveLargestLayer`, `LayerAreaRatioAtLeast`, `SmallerLayerInsideLarger`, `SmallerLayerCenteredOnLargerEdge`.

### Pattern 4: axis= parameter (orthogonal relaxation)

When a check fuses two axes that should be independent.

Existing: `LayerCenteredOnLayer(axis="x" | "y" | "both")`.

### Pattern 5: Composite check

When the failure mode is multi-faceted (e.g., "visible" = fill alpha + fill visible + fill opacity + layer opacity + layer visible).

Existing: `LayerVisible` (catches B19/L2/L3/L4 in one shot).

### Pattern 6: Z-order primitives

Existing: `LayerInFrontOf(type_a, type_b)` (no overlap req), `LayerOnTopOf(type_a, type_b, require_overlap=True/False)`.

### Pattern 7: NoLayer<X> (negative property)

Existing: `NoLayerFlipped(layer_type)` (catches scaleX=-1 / scaleY=-1).

## Step 4 — Wire into the task verifier

Add the new checks, mark prompt-explicit ones critical:

```python
AlignmentRubric([
    ...                                                                              # 0..N
    SmallerLayerInsideLarger(layer_type="rectangle", tolerance=4.0),                 # ★
    LayerCenteredOnLayer(type_a="polygon", type_b="rectangle",
                         tolerance=20.0, axis="x"),                                  # ★
    AllLayerBoundsInside(inner_type="ellipse", outer_type="rectangle",
                         tolerance=4.0),                                             # ★
], weight=0.2, critical=[index_of_each_starred_check]),
```

Conventions:
- Comment-prefix `★` on critical checks. Their indices go in `critical=[...]`.
- A failed critical check halves the rubric → ~10% drop in total score.
- Aim for **30–60% of checks per rubric being critical**. Higher when the prompt is strict; lower when the rubric has many "soft" checks.

If the rubric factory doesn't accept `critical=`, all 9 factories should now (`fundamentals`, `alignment`, `color`, `effect`, `event`, `page`, `property`, `structure`, `text`). Add it if missing, mirroring `alignment.py`.

## Step 5 — Update qa_verifiers.py harness

The harness synthesizes a perfect log per task. Adding a new check may break the perfect log. Run after each change:

```bash
PYTHONPATH=. python3 qa_verifiers.py | grep "task_NN\|Summary"
# Want: 1.000 perfect, 0.000 empty, 50 OK
```

If perfect log fails on the new check, add a handler in `mutate_for_geometry`. Watch for **ordering conflicts** with existing handlers — the harness has explicit "Pass 1..9" stages.

Position-dependent checks (`LayerCenteredOnLayer`, `SmallerLayerInsideLarger`, `LayerEdgesAligned`, `LayersStacked`, `LayerAspectRatioGreaterThan`) belong in the **final pass** so they re-run after all sizing has settled.

Conditional scaling: when one type is a container for another (e.g., `AllLayerBoundsInside(ellipse, rectangle)`), scale the container's `h` proportionally so inners fit. See the `AllLayerWidthFraction` handler:

```python
needs_circular = any(LayerIsCircular for same type)
is_container = any(AllLayerBoundsInside.outer_type == this_type)
needs_h_scale = needs_circular or is_container
```

`SmallerLayerInsideLarger` final-pass handler branches on `LayersConcentric`:
```python
needs_concentric = any(LayersConcentric for same type)
if needs_concentric: center-align both axes
else: bottom-align + x-center (door-on-body convention)
```

## Step 6 — Round-3: novel-deception battery

Once round 1 is below 5 strict FPs, hunt for **new FPs the round-1 battery didn't cover**. File: `qa_per_task/task_NN_round3.py`. ~30 cases. Categories:

- **K Subtle deceptions**: tolerance-edge cases (rotation 4° under 5° tol), corner-radius extremes, z-order swaps
- **L Visibility tricks**: alpha=0 in color, opacity=0 on layer, visible=False on fill, image fill with no visible content
- **M Geometry tricks**: shapes piled at one point, body = full frame, occlusion
- **N Structural tricks**: shapes split across frames, in components, in groups
- **O Wrong types**: substitution (star instead of polygon, rectangle instead of ellipse)

Each round-3 case usually exposes a check that's missing entirely (not just weakly enforced).

## Step 7 — Iterate

Re-run both batteries. Targets:
- **Strict FPs total ≤ 5** (across both batteries combined).
- **Borderline (0.92–0.95)** acceptable if "extras present but design intact."
- **Catastrophic** (empty, wrong types) ≤ 0.5.

If stuck:
- Two FPs share a structural pattern → look for a primitive pattern above.
- Can't be caught without role-disambiguation → use Largest/Smallest patterns or document as a known limitation.
- Tolerance edge → tighten tolerance.

## Step 8 — Sync + findings

```bash
cd /Users/rashidalblwi/figma-mock
scripts/sync_delivery.sh                                                # delivery-1 mirror
PYTHONPATH=. python3 qa_verifiers.py | tail -2                          # 50 OK
PYTHONPATH=. python3 -m qa_per_task._runner NN | tail -10               # 0 bug(s)
```

Write `qa_per_task/task_NN_findings.md`:
```markdown
# Task NN — verifier hardening summary

## Results
| Round | Cases | Strict FPs |
|-------|-------|------------|
| 1 (initial 100-case) | ... | ... → ... |
| 3 (novel 30-case) | ... | ... → ... |

## New primitives added
| Primitive | File | Catches |
|-----------|------|---------|

## Critical-flag changes
- ...

## Harness handlers added/changed
- ...

## Known limitations
- ...
```

## Anti-patterns

- **Don't** add a critical check that the harness perfect log can't satisfy. Either fix the harness or weaken the check.
- **Don't** modify the prompt or test data — only the verifier.
- **Don't** loosen tolerances to make legit logs pass — tighten harness handling instead.
- **Don't** delete existing checks; extend them or add new ones.
- **Don't** mark every check critical — that just inverts the dilution problem (anything fails → score halves).
- **Don't** stop at round 1. The "obvious" 96-case battery only catches ~80% of FPs; round 3 finds the deceptions.
- **Don't** skip the findings doc. Future-you will need it.

## Existing primitives (use these before inventing new ones)

- **Fill**: `AllFillTypeIs`, `FillTypeIs`, `FillCountAtMost`, `FillOpacityAtLeast`, `DistinctSolidColors`, `LayersAllSameColor`, `SolidColorEquals`, `AllSolidColorEquals`, `LayersHaveColorOrder`, `CentermostLayerHasColor`, `LayerHasNoFill`, `SameColorAcrossTypes`, `ImageFillExists`
- **Geometry**: `LayersAligned`, `LayersSymmetricX`, `LayersSameDimensions`, `LayerSizeEquals`, `LayerSizeAtLeast`, `LayerPosition`, `LayerRotationEquals`, `DistanceBetween`, `LayerContains`, `LayerEdgesAligned`, `LayersAllShareEdge`, `LayersDistributed`, `LayersConcentric`, `LayersStacked`, `LayersOverlap`, `LayerBoundsInside`, `AllLayerBoundsInside`, `SmallerLayerInsideLarger`, `LayerAreaRatioAtLeast`, `SmallerLayerCenteredOnLargerEdge`, `LayerAboveLargestLayer`, `FrameSizeEquals`, `LayerIsCircular`, `LayerIsSquare`, `LayersHaveAspectMix`, `LayerAspectRatioGreaterThan`, `RadialDistribution`, `RadialDistributionExcludeCentral`, `LayersEvenlyRotated`, `LayersInGrid`, `OffsetGridLayout`, `LayerCenteredInFrame`, `LayerCenteredOnLayer`, `LayerOnTopOf`, `LayerInFrontOf`, `LayerNextTo`, `LayerWidthFraction`, `AllLayerWidthFraction`, `LayersHaveRotations`, `LayersAlternatingColors`, `LayersFlankLayer`, `LinesOnDiagonal`
- **Structure**: `LayerInsideFrame`, `ChildCountAtLeast`
- **Property**: `OpacityEquals`, `VisibilityIs`, `CornerRadiusEquals`, `CornerRadiusAtLeast`, `CornerRadiusFractionAtMost`, `IsFlippedH`, `IsFlippedV`, `NoLayerFlipped`, `LayerVisible`, `ConstraintHorizontalEquals`, `ConstraintVerticalEquals`
- **Stroke**: `StrokeExists`, `StrokeWeightEquals`, `StrokeColorEquals`, `StrokeAlignmentIs`, `StrokeIsDashed`, `DistinctStrokeColors`
- **Effect**: `DropShadowExists`, `DropShadowOffsetEquals`, `DropShadowBlurEquals`, `DropShadowSpreadEquals`, `EffectColorEquals`, `EffectCount`, `LayerBlurExists`, `BlurRadiusEquals`
- **Text**: `TextContent`, `TextContains`, `FontSizeEquals`, `FontWeightEquals`, `TextAlignEquals`, `VerticalAlignEquals`, `LineHeightEquals`, `LetterSpacingEquals`
- **Shape**: `ShapeCount`, `ShapeCountAtLeast`, `PolygonSidesEquals`, `StarPointsEquals`
- **Page**: `PageBackgroundColorEquals`, `PageCount`, `LayerOnPage`
- **Event**: `ToolUsed`, `EventTypeCount`, `EventTypeCountAtLeast`, `EventTypeUsed`, `AlignToolUsed`

## Worked example: task_01 hardening trace

```
Round 1 (96-case battery): ~25 strict FPs at 1.000
  + AllFillTypeIs (B13–B20)
  + AllLayerWidthFraction (C25–C30)
  + LayerCenteredOnLayer.axis=x (D39, D40)
  + LayerRotationEquals (J87, G61)
  + LayerSizeAtLeast (J94)
  + AllLayerBoundsInside (D38, J95)
  → 6 strict FPs

Round 2 (close remaining gaps): 6 strict FPs
  + FillOpacityAtLeast (B19)
  + LayerAreaRatioAtLeast (C23)
  + SmallerLayerCenteredOnLargerEdge (D31, D35)
  + LayerAboveLargestLayer (E41)
  + AllLayerBoundsInside(ellipse, rectangle) (F57)
  → 0 strict FPs

Round 3 (31 NOVEL cases): 13 strict FPs at 1.000
  + tighten rotation tolerance (K3, K5)
  + CornerRadiusFractionAtMost (K6, K7)
  + LayerInFrontOf (K8, K9, K10)
  + LayerVisible (L2, L3, L4)
  + StructureRubric.critical=[...] (N2, N3)
  → 1 borderline (M3 at 0.95, accepted)
```

Final: 0 strict FPs, 38 checks total (32 critical), 5 weighted rubrics summing to 1.0.

## File outputs (mandatory)

After hardening task NN, these MUST exist:
- `test-verifier/qa_per_task/task_NN_extended.py` — the 100-case battery
- `test-verifier/qa_per_task/task_NN_round3.py` — the 30-case novel-deception battery
- `test-verifier/qa_per_task/task_NN_findings.md` — the round-by-round findings
- `test-verifier/tasks/task_NN_*.py` — updated with critical flags + new checks
- `delivery-1/task_NN/verifier.py` — synced via `scripts/sync_delivery.sh`

If any are missing, the task is not hardened.
