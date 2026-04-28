**Execution Map (review first, then I implement step-by-step with separate commits)**

**Status (2026-04-28):** Wave 1 (Frames) DONE. Wave 2 (Logging) partial — raw+semantic streams now auto-persist to sessionStorage; outcome stream still pending. Waves 3–6 pending. Wave 5 / Step 7 partial — `K` scale and send-to-back/front done; multi-page logging consistency pending.

**Priority Wave 1: Frames** — DONE

1. **Frame foundation + "frame workspace" behavior** — DONE
Covers: `#7 #8 #9 #10 #13 #15 #20`
How:
- Make frame focus-context authoritative for selection/hit-test/create flows.
- Double-click frame enters frame workspace; `Esc` exits one level.
- Creation tools place new shapes inside focused frame (not always page root).
- Frame resize updates children using constraints (left/right/center/stretch/scale).
Main files:
- [coordinates.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/engine/coordinates.ts)
- [selectors.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/engine/selectors.ts)
- [move.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/tools/move.ts)
- [creationBbox.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/tools/creationBbox.ts)
- [line.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/tools/line.ts)
- [pen.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/tools/pen.ts)
- [pencil.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/tools/pencil.ts)
- [ops.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/engine/ops.ts)

2. **Frame nesting integrity: drag/drop + copy/paste + grouping with frames** — DONE (except `#14`)
Covers: `#11 #12 #14` (+ part of `#29`)
How:
- Drag-drop shape into frame on canvas reparents node.
- Layers panel drag supports cross-parent reparent (not same-parent only).
- Copy/duplicate/paste preserve full nested subtree 1:1 for frames.
Main files:
- [move.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/tools/move.ts)
- [hierarchyCommands.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/engine/hierarchyCommands.ts)
- [commands.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/engine/commands.ts)
- [LayersTree.tsx](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/ui/panels/LayersTree.tsx)

**Priority Wave 2: Logging** — Partial

3. **Dual logging system (input stream + app outcome stream)** — Partial: raw+semantic streams persist to sessionStorage on a 250ms throttle (`logger/persist.ts`); outcome stream from op layer still pending.
Covers: `#33`
How:
- Keep current raw input logger as-is (every input + timestamp).
- Add `outcome` logger stream from op/transaction layer: node created/moved/resized/reparented, page/tool/mode/selection changes, before/after deltas.
- Correlate outcome entries with semantic/raw IDs for replay/debug.
- Export all three streams together (`raw`, `semantic`, `outcome`).
Main files:
- [raw.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/logger/raw.ts)
- [semantic.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/logger/semantic.ts)
- [buffer.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/logger/buffer.ts)
- [dispatch.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/engine/dispatch.ts)
- [export.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/logger/export.ts)
- [events.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/types/events.ts)

**Priority Wave 3: Robustness / Unsupported Buttons** — Pending

4. **Universal unsupported-action behavior + rename + scroll hardening**
Covers: `#1 #2 #3 #4 #26`
How:
- Replace silent no-op clicks with consistent toast: `Currently "{feature}" unsupported`.
- Keep semantic logging for unsupported clicks.
- Fix rename UX paths (layers/pages/context/menu/modal) so names always editable.
- Harden right-panel and fill panel scrolling behavior.
Main files:
- [noopClick.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/ui/chrome/noopClick.ts)
- [Toasts.tsx](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/ui/overlays/Toasts.tsx)
- [RightPanel.tsx](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/ui/chrome/RightPanel.tsx)
- [global.css](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/theme/global.css)
- [LayersTree.tsx](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/ui/panels/LayersTree.tsx)
- [LeftPanel.tsx](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/ui/chrome/LeftPanel.tsx)

---

**Wave 4: Fill/Color System** — Pending

5. **Color/Fill parity expansion**
Covers: `#5 #6 #16 #21 #22 #23 #24`
How:
- Full color definition inputs (`hex`, `rgb`, `hsv/wheel`).
- Fill types: solid + linear/radial gradient + image fill.
- Fill previews in rows; persistent recent-color history.
- Right-side palette/library mock for reusable colors.
Main files:
- [FillSection.tsx](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/ui/panels/FillSection.tsx)
- [ColorPicker.tsx](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/ui/overlays/ColorPicker.tsx)
- [propertyCommands.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/engine/propertyCommands.ts)
- [scene.ts](/Users/cumhuraygar/Desktop/avenStudio/CUA/figma-mock/test-app/src/types/scene.ts)

**Wave 5: Vector/Shape/Transform Finishing** — Partial

6. **Vector + shape-edit parity** — Pending
Covers: `#17 #18 #19 #27 #28 #31 #32`
How:
- Improve vertex workflows and post-create vector editing.
- Shape-to-vector / flatten-to-vector command path.
- Ensure Shift-proportional circle behavior is strict.
- Arrow behavior fully editable/functional end-to-end.

7. **Scale/layer/page parity cleanup** — Partial: `#25` and `#29` done; `#30` (multi-page logging consistency) pending.
Covers: `#25 #29 #30`
How:
- `K` scale correctness for nested content (recursive). — Done
- Validate send-to-back/front across nesting contexts. — Done
- Verify multi-page behavior + logging consistency. — Pending

---

**Assumptions I'll use unless you change them**
1. `#18` means converting primitive shapes (like ellipse) to editable vectors and manipulating vertices/curves.
2. `#24` ("Libraries & colors") will be implemented as local mock libraries/palettes, not remote/team libraries.
3. `#14` ("Grouping frames & sessions") means grouping behavior inside/around frame contexts plus correct logging sessions.
