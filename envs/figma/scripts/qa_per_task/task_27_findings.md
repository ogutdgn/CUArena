# Task 27 — verifier hardening summary

Spec: 200×200 light-gray rounded rectangle with two paired drop shadows.

## Results

| Round | Cases | Strict FPs |
|-------|-------|------------|
| 1 (initial 100-case battery) | 100 | ~37 → ~12 (mostly borderline-acceptable) |
| 3 (novel 30-case battery) | 27 | 2 (K9 camouflage, M3 4-tuple cornerRadius — both legitimate) |

## New primitives added

| Primitive | File | Catches |
|-----------|------|---------|
| `DropShadowCountAtLeast` | `verifier/checks/effect_checks.py` | F54 (mixed effects), F56 (alpha=0 shadows), F57 (visible=False shadows), K3, K4 |
| `PairedDropShadowsOpposite` | `verifier/checks/effect_checks.py` | F58 (same-side shadows), F59 (zero-offset shadows), K1, K2, K8 |

## Critical-flag changes

Added to `task_27_neumorphic_button.py`:

- **AlignmentRubric** — added critical checks:
  - `CornerRadiusFractionAtMost(max_frac=0.45)` (catches E45 cornerRadius=100 = full circle / pill)
  - `LayerRotationEquals(rectangle, degrees=0, tolerance=2.0)` (catches E46–E48 rotations)
  - `LayerRotationEquals(frame, degrees=0, tolerance=2.0)` (catches G61 frame rotated)
  - `NoLayerFlipped(rectangle)` (catches E49, E50)
  - `AllLayerBoundsInside(rectangle, frame, tolerance=4.0)` (catches D32, D36, D39, D40)

- **ColorRubric** — added critical checks:
  - `FillCountAtMost(rectangle, max_count=1)` (catches B20 stacked fills)
  - `FillOpacityAtLeast(rectangle, min_opacity=0.5)` (catches B19, L3)
  - `LayerVisible(rectangle)` (catches B18, J96, J97, L1, L2, L4, L5)

- **EffectRubric** — added critical checks:
  - `DropShadowCountAtLeast(rectangle, minimum=2)` (catches F54, F56, F57, K3, K4)
  - `PairedDropShadowsOpposite(rectangle, min_offset=2.0)` (catches F58, F59, K1, K2, K8)

- **StructureRubric** (new) — added critical check:
  - `LayerInsideFrame(rectangle)` (catches G68, J92, J93)

## Harness handlers added/changed

`qa_verifiers.py` (mutate_for_geometry):
- `EffectCount` handler: now generates drop shadows with non-zero offsets (-6,-6) / (6,6) and alpha=0.4 (was zero-offset alpha=0.2). Required for the new `PairedDropShadowsOpposite` and `DropShadowCountAtLeast` primitives to pass on perfect log.
- New `DropShadowCountAtLeast` handler: ensures ≥minimum visible drop shadows with alternating opposing offsets.
- New `PairedDropShadowsOpposite` handler: ensures ≥2 visible shadows with opposite-direction offsets.

## Known limitations

- **K9 (white-on-white camouflage)**: button RGB matches frame fill. Hard to catch — prompt doesn't specify contrast against frame.
- **M3 (cornerRadius as 4-tuple)**: legitimate per type system; the 4-tuple form is functionally equivalent to scalar.
- **Borderline 1.000s**: extras-present designs (A6, A8, H75, H80) score 1.0. The verifier accepts decorations as long as the core button is correct.
