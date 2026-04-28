# Feature Checklist


**Customer-provided list of features to implement:**

1. [ ] Can not change names
2. [ ] Cannot click most buttons (share, export etc)
3. [ ] Color Fill scroll
4. [ ] Right bar scroll
5. [ ] Define color (hexcode, wheel)
6. [ ] Solid, linear, gradiaent on fill
7. [x] Shape to frame array
8. [x] Frame workspace (double click)
9. [x] Frame acts like separate env
10. [x] Frame/shape in frame logic (nesting)
11. [x] Frame copying is not 1-1 (because no nesting)
12. [x] Drag drop shape into frame to make it a part of it.
13. [x] Frames frames frames....
14. [ ] Grouping frames & sessions
15. [x] Frame commands & making shapes
16. [ ] Fill with image
17. [ ] vector system - vertex
18. [ ] Vector Shapes - Circle into 3M circle
19. [ ] Shift shape-circle keeps proprotionality.
20. [x] Frame resizing
21. [ ] Color style - pallete on right side
22. [ ] History of colors - hex, rgb, css
23. [ ] Color preview on fills
24. [ ] Libraries & colors
25. [x] Press K button on box to scale correctly
26. [ ] Robust buttons logic for all features on the screen (pop up 'currently {feature_name} unsupported' error message if not yet implemented)
27. [ ] Edit voxes after completion
28. [ ] Flattening objects to vectors
29. [x] Send to back, sort to front.
30. [ ] Files have multiple pages
31. [ ] Shift standard circle to make
32. [ ] Arrows work functionally
33. [ ] Logging - I want to be able to verify the work of a CUA model, so I need to have two logging systems, one logging EVERY action input from the user & the timestamps of those actions, and the second system logging all outcomes on the canvas & app. (multi-state amanagement, shapes moved from x to z, etc etc)
34. [ ] Prototype Feature
35. [ ] Right-sidebar state/visual parity
36. [ ] text-range


---

**Main priorities:**

1. Making frames work
2. Logging
3. Robustness on all buttons, error messages showing what is not supported or not.

---

**feature-explanation**

- Prototype Feature
  Add Design / Prototype tab toggle in the right sidebar (`Shift E`).
  In Prototype mode: hotspot-to-frame connections, trigger + action + animation per connection, flow starting points on top-level frames, basic preview/play.
  Reference: `helper/figma_docs/articles/Figma Design/guide-to-prototyping-in-figma`, `prototype-triggers`, `prototype-actions`, `prototype-animations`, `create-and-manage-prototype-flows`.

- Right-sidebar state/visual parity
  Align the right sidebar's section visibility, fields, and buttons across every state — no selection (page section), single layer per type, multi-select, frame context, vector edit mode, text edit mode, Design vs Prototype tab — against actual Figma, and tighten the visual look to match.
  Reference: `helper/analysis/panel-states.md`.

- text-range
  Introduce explicit edit-state model for caret/range.
  Make `runs` a real editable target (not passive storage).
  Support range-aware typography updates and mixed-value reflection.
