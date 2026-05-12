# Task 51 [READ] — Count the jeans in the scene and click the number label that matches.

**Difficulty:** Easy  •  **Time horizon:** 8 min  •  **Operation:** Read

## Thorough description

A scene contains a cluttered group of clothing items (shirts, jeans, hats, jackets, dresses) scattered across the canvas. Along the bottom of the frame is a row of 8 number labels (1, 2, 3, 4, 5, 6, 7, 8). The agent must count how many items in the scene are jeans, then click the number label corresponding to that count.

## Simplified prompt

> Count the jeans in the scene. Click the number label that matches your count.

## Step-by-step

1. Visually scan the scene for jeans (denim pants/trousers). 2. Count them. 3. Click the corresponding number label at the bottom of the frame.

## Starting state

A 1200x800 frame contains:
- ~12 clothing items scattered across the upper portion (shirts, hats, jackets, dresses, and **4 jeans**)
- A horizontal row of 8 number labels (1-8) along the bottom of the frame, evenly spaced
- Correct answer: **4**

Each clothing item is a named layer (e.g. "jeans_01", "shirt_03"). Each number label is a named layer (e.g. "label_1", "label_2", ..., "label_8") containing a circle background and a number.

## Verifier

The verifier script for this task lives next to this file as `verifier.py`.
In the framework it's imported as `tasks.task_51_read_count_jeans` (see `../README.md` for run commands).
