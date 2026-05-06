# Task 14 — Make a dartboard target with 4 concentric red and white circles, centered, each with a 4px black stroke.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Draw 4 concentric circles with decreasing diameters (e.g., 240, 180, 120, 60 px), all sharing the same center. Alternate red and white from outermost to center: red, white, red, white. Add a 4px black stroke to each.

## Simplified prompt

> Make a dartboard target with 4 concentric red and white circles, centered, each with a 4px black stroke.

## Step-by-step

1. Click Ellipse tool. 2. Drag the largest circle, pick red. 3. Add 4px black stroke. 4. Right-click then Duplicate, scrub to 180px square, pick white. 5. Duplicate, scrub to 120px, pick red. 6. Duplicate, scrub to 60px, pick white. 7. Marquee all. 8. Click Align horizontal centers, then Align vertical centers.

## Verifier

The verifier script for this task lives next to this file as `verifier.py`.
In the framework it's imported as `tasks.task_14_concentric_target` (see `../README.md` for run commands).
