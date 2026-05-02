**Execution Map**

The status section at the top is a per-session log of what shipped (newest entry on top). The lower section lists only **pending** work — items are deleted from the lower section as soon as they ship; their record lives in the session log instead.

---

**Session log**

- **2026-05-02**
  - Prototype connection arrow bugfix: drag-to-connect now uses recursive world-space layer bounds, recognizes frame targets beyond the previous top-level/one-level assumptions, and tracks pointer movement/up at window capture level so releasing over a target frame reliably creates the connection instead of losing the drag.
  - Prototype connector usability: selected frames now show persistent `+` handles on all four sides in Prototype mode, and dragging from any `+` connects to the destination frame object rather than requiring a second `+` target. Connections remain directed, so `A -> B` and `B -> A` are distinct.
  - Prototype selection parity: selected frames keep corner-only resize handles in Prototype mode, and reverse-pair arrows are visually offset onto opposite lanes so both directions remain visible.
  - Prototype interaction editor: drag-created connections now immediately open the existing interaction modal with the default On tap / Navigate to / destination frame / Instant setup.
  - Prototype interaction types: interaction modal now stores/edits animation type, labels the default trigger as On click, and preview runtime supports the functional trigger/action subset (`on_tap`, hover/press/down/up/drag-style gestures, after-delay, key/gamepad, navigate/change/open/swap/back/close-overlay).
  - Prototype interaction UI: trigger/action/destination/animation controls now use compact dropdown rows instead of long always-visible lists; `After delay` reveals a delay field and persists `delayMs` for preview playback.
  - Prototype preview start order: preview fallback frame order is now deterministic (`Frame 1`, `Frame 2`, ... by numeric name, then top-left position), so a file with Frame 1 and Frame 2 starts on Frame 1 when no explicit flow overrides it.
  - Verification: Vite dev server serves the updated `ConnectionArrows.tsx` module successfully at `http://127.0.0.1:5173`; full browser automation was blocked by the local Node REPL runtime requiring Node `>=22.22.0` while this machine exposes `22.13.1`.

- **2026-04-28**
  - Frames shipped: frame workspace double-click + scope-as-context, creation tools place inside focused frame, nesting via canvas drag (50% overlap auto-nest/unnest, live reparent), layers panel cross-parent reparent + drop-into-frame, copy/paste/duplicate preserve full nested subtree, frame resize reflows children via constraints.
  - Logger refactor: raw + semantic streams now auto-persist to `sessionStorage` on a 250ms throttle (`logger/persist.ts`). Backtick dev panel removed. Outcome stream still pending.
  - Scale tool (`K`) shipped with proportional stroke / radius / font scaling on commit; recursive children scaling confirmed working. Send-to-back / send-to-front already shipped via `reorderZ` keymap + context menu.
  - Layout fix: `min-height: 0` on panel flex containers stopped CSS-Grid `1fr` row from pushing toolbar/sidebar off-screen on selection.
  - Pen fixes: anchor-drag Immer-freeze crash fixed (index-based segment replacement); pen tool now exits vector edit mode on activation so VectorEditOverlay no longer intercepts pointer events.
  - Selection: `select-all` scoped to current hierarchy level; frame-context exits one level at a time.
  - feature-checklist priority slices added at top of the file: Prototype Feature, Right-sidebar state/visual parity, text-range.
  - feature-checklist ticks: `#7 #8 #9 #10 #11 #12 #13 #15 #20 #25 #29`.

---

**Wave 1: Logging**

1. **Outcome logger stream (third stream alongside raw + semantic)**
Covers: `#33`
How:
- Add `outcome` logger stream from op/transaction layer: node created/moved/resized/reparented, page/tool/mode/selection changes, before/after deltas.
- Correlate outcome entries with semantic/raw IDs for replay/debug.
- Export all three streams together (`raw`, `semantic`, `outcome`).
Main files:
- [raw.ts](figma-mock/test-app/src/logger/raw.ts)
- [semantic.ts](figma-mock/test-app/src/logger/semantic.ts)
- [buffer.ts](figma-mock/test-app/src/logger/buffer.ts)
- [dispatch.ts](figma-mock/test-app/src/engine/dispatch.ts)
- [export.ts](figma-mock/test-app/src/logger/export.ts)
- [events.ts](figma-mock/test-app/src/types/events.ts)

**Wave 2: Robustness / Unsupported Buttons**

1. **Universal unsupported-action behavior + rename + scroll hardening**
Covers: `#1 #2 #3 #4 #26`
How:
- Replace silent no-op clicks with consistent toast: `Currently "{feature}" unsupported`.
- Keep semantic logging for unsupported clicks.
- Fix rename UX paths (layers/pages/context/menu/modal) so names always editable.
- Harden right-panel and fill panel scrolling behavior.
Main files:
- [noopClick.ts](figma-mock/test-app/src/ui/chrome/noopClick.ts)
- [Toasts.tsx](figma-mock/test-app/src/ui/overlays/Toasts.tsx)
- [RightPanel.tsx](figma-mock/test-app/src/ui/chrome/RightPanel.tsx)
- [global.css](figma-mock/test-app/src/theme/global.css)
- [LayersTree.tsx](figma-mock/test-app/src/ui/panels/LayersTree.tsx)
- [LeftPanel.tsx](figma-mock/test-app/src/ui/chrome/LeftPanel.tsx)

---

**Wave 3: Fill/Color System**

1. **Color/Fill parity expansion**
Covers: `#5 #6 #16 #21 #22 #23 #24`
How:
- Full color definition inputs (`hex`, `rgb`, `hsv/wheel`).
- Fill types: solid + linear/radial gradient + image fill.
- Fill previews in rows; persistent recent-color history.
- Right-side palette/library mock for reusable colors.
Main files:
- [FillSection.tsx](figma-mock/test-app/src/ui/panels/FillSection.tsx)
- [ColorPicker.tsx](figma-mock/test-app/src/ui/overlays/ColorPicker.tsx)
- [propertyCommands.ts](figma-mock/test-app/src/engine/propertyCommands.ts)
- [scene.ts](figma-mock/test-app/src/types/scene.ts)

**Wave 4: Vector/Shape/Transform Finishing**

1. **Vector + shape-edit parity**
Covers: `#17 #18 #19 #27 #28 #31 #32`
How:
- Improve vertex workflows and post-create vector editing.
- Shape-to-vector / flatten-to-vector command path.
- Ensure Shift-proportional circle behavior is strict.
- Arrow behavior fully editable/functional end-to-end.

2. **Multi-page logging consistency**
Covers: `#30`
How:
- Verify multi-page behavior + logging consistency.

**Leftover (frames)**

1. **Grouping frames & sessions**
Covers: `#14`
How:
- Define what grouping behavior should look like inside / around frame contexts (vs. existing `groupSelection`).
- Ensure logging "sessions" framing for grouped operations is consistent.

---

**Assumptions I'll use unless you change them**
1. `#18` means converting primitive shapes (like ellipse) to editable vectors and manipulating vertices/curves.
2. `#24` ("Libraries & colors") will be implemented as local mock libraries/palettes, not remote/team libraries.
3. `#14` ("Grouping frames & sessions") means grouping behavior inside/around frame contexts plus correct logging sessions.
