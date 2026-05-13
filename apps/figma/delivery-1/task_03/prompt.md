# Task 3 — Draw a yellow center circle and 8 colored petals arranged radially around it.

**Difficulty:** Easy  •  **Time horizon:** 14 min

## Thorough description

Inside a frame, draw 1 yellow center circle and arrange 8 elliptical petals around it in a radial pattern (one petal on each compass direction plus diagonals). Each petal is a different color.

**Sizing requirements:**
- The center is a true **circle** (width ≈ height).
- All 8 petals are the **same size** as each other.
- Each petal is **smaller than the center circle** (less total area).
- Each petal is **elongated** — its long axis is at least 1.5× its short axis (it cannot be circular like the center).
- Each petal is oriented with its **long axis pointing radially outward** from the center, and its inner end **touches the outside** of the center circle.

## Simplified prompt

> Draw a yellow center circle and 8 same-size colored petals arranged radially around it. Each petal is elongated outward with its inner tip touching the outside of the circle.

## Step-by-step

1. Click Frame tool, drag a frame. 2. Click Ellipse tool. 3. Drag the center circle (~200×200), pick yellow. 4. Drag a petal ellipse (~100×200, with long axis pointing outward from the center) so its inner end touches the circle, pick a color. 5. Right-click then Duplicate, rotate 45°, position so the inner end touches the circle again, pick a different color. 6. Repeat duplicate-rotate-recolor 6 more times until 8 same-size petals total.

## Verifier

The verifier script for this task lives next to this file as `verifier.py`.
In the framework it's imported as `tasks.task_03_glowing_orb` (see `../README.md` for run commands).
