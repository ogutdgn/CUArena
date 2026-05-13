# Task 52 [READ] — Find and click the gift box among the colored shapes.

**Difficulty:** Easy  •  **Time horizon:** 6 min  •  **Operation:** Read

## Thorough description

A scene contains several plain colored shapes scattered across the canvas and one gift box. The gift box is the only composite object — it is made of a colored rectangle (the box body) with two crossing ribbon strips and an oval bow on top. The other shapes are simple solid-colored rectangles of various sizes and colors. The agent must find the gift box and click on it.

## Simplified prompt

> Find the gift box in the scene and click on it.

## Step-by-step

1. Scan the scene for a shape that looks like a wrapped present (a rectangle with crossing ribbons and a bow on top). 2. Click on it.

## Starting state

A 1200×800 frame contains:
- 1 gift box (an orange rectangle with yellow cross-ribbons and a yellow oval bow) — not centered or highlighted
- 10 plain colored rectangles of various sizes scattered across the canvas as distractors

## Verifier

The verifier script for this task lives next to this file as `verifier.py`.
