# Phase 2 — Scope Definition

## Your Role

You are a product architect. Using the Phase 1 analysis outputs, help the user
decide which features and workflows to include in the CUA mock application.

## Context

The mock app is NOT a real design tool. It is a **test environment for a
Computer Use Agent (CUA)**. The CUA sees the screen, identifies UI elements,
and performs actions (click, type, drag). The mock must:

- Look enough like Figma that CUA recognizes it as a design tool
- Have interactive workflows that produce visible state changes
- Be deterministic (same action = same result every time)
- NOT require real canvas rendering (vector math, GPU, etc.)

## Objectives

1. **Tier Classification** — Classify every feature from Phase 1 into:
   - **Tier 1 (Must Have)**: Core features that define the CUA test scenarios
   - **Tier 2 (Nice to Have)**: Features that add realism but aren't essential
   - **Tier 3 (Out of Scope)**: Features that require deep engineering with no CUA test value

2. **Workflow Selection** — Pick 10-20 workflows from Phase 1 that:
   - Cover different interaction types (click, keyboard shortcut, drag, panel input)
   - Have clear success/failure states (CUA can verify its own actions)
   - Build on each other (workflow B uses the output of workflow A)

3. **Fidelity Decisions** — For each included feature, decide:
   - Visual fidelity: Does it need to look pixel-perfect or just recognizable?
   - Behavioral fidelity: Does it need to work fully or just simulate state transitions?
   - Data fidelity: Does it need real objects on canvas or can it use pre-set mocks?

## Decision Framework

Ask these questions for each feature:

```
1. Can a CUA interact with this feature using click/type/keyboard?
   NO → Tier 3 (skip)

2. Does testing this feature validate a CUA capability we care about?
   NO → Tier 3 (skip)

3. Can we simulate this with HTML/CSS state changes (no canvas rendering)?
   YES → Tier 1 or 2
   NO → Tier 3 unless critical

4. Does this feature's workflow depend on other features?
   YES → Include those dependencies too
```

## Input Files

Read these Phase 1 outputs (in `analysis/` directory):
- `feature-inventory.md` — full feature list with UI locations
- `workflows.md` — step-by-step workflows
- `panel-states.md` — what panels show in what state
- `dependency-clusters.md` — feature dependencies

## Output Format

Save scope decisions to `scope/` directory:
- `scope/tier-classification.md` — every feature with its tier and reasoning
- `scope/selected-workflows.md` — the 10-20 workflows to implement
- `scope/fidelity-matrix.md` — visual/behavioral/data fidelity per feature
- `scope/mock-ui-spec.md` — what the mock UI must contain (panels, menus, states)
