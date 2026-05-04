# Task 17 — Build an hourglass: 2 triangles point-to-point + 2 horizontal cap rectangles.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Build an hourglass: 2 triangles meeting point-to-point at the center (one pointing down, one pointing up below it), plus 2 horizontal rectangles as caps at the top and bottom. All shapes share a center x.

## Simplified prompt

> Build an hourglass: 2 triangles point-to-point + 2 horizontal cap rectangles.

## Step-by-step

1. Click Polygon tool. 2. Drag the upper triangle, scrub rotation to 180° (point down). 3. Right-click then Duplicate, scrub rotation to 0° (point up), drag below the first. 4. Click Rectangle tool. 5. Drag the top cap rectangle. 6. Drag the bottom cap rectangle. 7. Marquee all. 8. Click Align horizontal centers.

## Verifier

The verifier script for this task lives next to this file as `verifier.py`.
In the framework it's imported as `tasks.task_17_play_button` (see `../README.md` for run commands).
