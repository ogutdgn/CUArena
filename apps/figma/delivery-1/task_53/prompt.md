# Task 53 [DELETE] — Delete all red shapes from the frame.

**Difficulty:** Easy  •  **Time horizon:** 8 min  •  **Operation:** Delete (batch by attribute)

## Thorough description

A scene contains 10 shapes of various types (rectangles, ellipses, polygons) scattered across the canvas. 5 are red and 5 are blue. The agent must delete all 5 red shapes and leave all 5 blue shapes intact.

## Simplified prompt

> Delete all red shapes in the scene. Leave the blue shapes alone.

## Step-by-step

1. Identify all red shapes. 2. Click the first red shape to select it. 3. Press Delete or right-click → Delete. 4. Repeat for each remaining red shape.

## Starting state

A 1200×800 frame contains 10 scattered shapes:
- 5 red shapes (#FF0000) — mix of rectangles, ellipses, and polygons
- 5 blue shapes (#0000FF) — mix of rectangles, ellipses, and polygons

## Verifier

The verifier script for this task lives next to this file as `verifier.py`.
