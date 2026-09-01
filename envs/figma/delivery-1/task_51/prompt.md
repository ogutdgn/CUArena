# Task 51 [READ] — Count the blue rectangles in the scene and click the matching number label.

**Difficulty:** Easy  •  **Time horizon:** 8 min  •  **Operation:** Read

## Thorough description

A scene contains a mix of colored shapes scattered across the canvas: blue rectangles, red rectangles, yellow rectangles, red circles, and pink stars. Some shapes overlap the blue rectangles, so the agent may need to click on a blue shape to confirm it is a rectangle rather than another shape type hidden underneath. Along the bottom of the frame is a row of 8 number labels (1–8). The agent must count how many blue rectangles are in the scene, then click the number label corresponding to that count.

## Simplified prompt

> Count the blue rectangles in the scene. Click the number label that matches your count.

## Step-by-step

1. Visually scan the scene for blue rectangles (ignore red/yellow rectangles, red circles, and pink stars). 2. Some shapes overlap blue rectangles — click on them if needed to verify shape type. 3. Count the blue rectangles. 4. Click the corresponding number label at the bottom of the frame.

## Starting state

A 1200×800 frame contains:
- 4 blue rectangles
- 2 red rectangles, 3 red circles, 3 pink stars, 2 yellow rectangles (distractors)
- 2 distractor shapes partially overlap blue rectangles
- A horizontal row of 8 number labels (1–8) along the bottom
- Correct answer: **4**

## Verifier

The verifier script for this task lives next to this file as `verifier.py`.
