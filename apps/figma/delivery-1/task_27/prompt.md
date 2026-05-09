# Task 27 — Neumorphic pressed-button rectangle.

**Difficulty:** Easy  •  **Time horizon:** 12 min

## Thorough description

Draw a single 200×200 light-gray rounded rectangle and apply two opposing drop shadows — one offset toward the top-left (highlight) and one offset toward the bottom-right (shadow) — to create the soft pressed look of a neumorphic button. Both shadows should share the same blur and similar alpha, with offsets pointing in opposite directions across the rectangle.

## Simplified prompt

> Draw a 200×200 light-gray rounded rectangle with two paired (opposing) drop shadows so it looks like a neumorphic button.

## Step-by-step

1. Click Rectangle tool. 2. Drag a 200×200 rectangle. 3. Set the fill to light gray (around #E1E5EE). 4. Scrub corner radius to 20. 5. Open the Effects panel and add a drop shadow with offset roughly (-8, -8), blur 16. 6. Add a second drop shadow with offset roughly (8, 8), blur 16. 7. Confirm the rectangle stays upright (0° rotation, not flipped).

## Verifier

The verifier script for this task lives next to this file as `verifier.py`.
In the framework it's imported as `tasks.task_27_neumorphic_button` (see `../README.md` for run commands).
