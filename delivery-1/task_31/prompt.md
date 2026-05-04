# Task 31 — Draw a sun: yellow circle + 8 triangle rays rotated radially around it.

**Difficulty:** Medium  •  **Time horizon:** 15 min

## Thorough description

Inside a frame, draw a 100px yellow center circle and 8 thin triangle rays around it, each rotated 45° from the last (so 12 o'clock, 1:30, 3:00, 4:30, 6:00, 7:30, 9:00, 10:30 directions).

## Simplified prompt

> Draw a sun: yellow circle + 8 triangle rays rotated radially around it.

## Step-by-step

1. Click Frame tool. 2. Click Ellipse tool, drag the center circle, pick yellow. 3. Click Polygon tool, drag a thin triangle pointing up. 4. Right-click then Duplicate, scrub rotation +45°. 5. Repeat the duplicate-rotate pattern 6 more times for 8 rays total.

## Verifier

The verifier script for this task lives next to this file as `verifier.py`.
In the framework it's imported as `tasks.task_31_sun_rays` (see `../README.md` for run commands).
