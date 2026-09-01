# UI Fixes — Non-Functional Elements Checklist

Goal: Remove or hide all UI elements with no functionality.
> **Note:** State-conditional items are marked `[STATE]` — handle carefully.

---

## 1. LEFT RAIL — `LeftRail.tsx`

- [x] `left-rail.layers` — Layers button
- [x] `left-rail.assets` — Assets button
- [x] `left-rail.find-replace` — Find button
- [x] `left-rail.notifications` — Notifications button

**Action taken:** Removed `<LeftRail />` from DOM entirely. Removed import. Updated grid layout from 4 to 3 columns in `App.tsx`.

---

## 2. LEFT PANEL — `LeftPanel.tsx`

- [x] `file-menu.open` — Removed (entire FileNameRow removed)
- [x] `left-nav.tab.assets` — Removed (entire TabsRow removed)
- [x] `page-context.{id}.duplicate` — Removed from page context menu
- [x] `page-context.{id}.copy-link` — Removed from page context menu
- [ ] `page-context.{id}.delete` — Working correctly (disabled only when 1 page remains) — skip

**Action taken:** Removed FileNameRow and TabsRow entirely. Pages: collapse toggle (shows active page name when collapsed) + working search filter. Layers: collapse toggle.

---

## 3. TOOLBAR — `Toolbar.tsx`

### Always visible, noop:
- [x] `toolbar.comment-tools-dropdown.open` — Removed (entire comment ToolGroup)
- [x] `toolbar.actions-menu.open` — Removed (Sparkles button)
- [x] `toolbar.expand` — Removed (More/ChevronUp button)

### Always disabled:
- [x] `toolbar.shape-tools.image` — Removed from shape items dropdown
- [x] `toolbar.comment-tools-dropdown.comment` — Removed with comment group
- [x] `toolbar.comment-tools-dropdown.annotation` — Removed with comment group
- [x] `toolbar.comment-tools-dropdown.measurement` — Removed with comment group

### visualOnly, never active:
- [x] `toolbar.mode-switcher.draw` — Removed from ModeSwitcher
- [x] `toolbar.mode-switcher.dev` — Removed from ModeSwitcher

**Action taken:** Removed comment tools ToolGroup, Sparkles, More button, image/video shape item, Draw/Dev mode segments. ModeSwitcher now shows only the active Design segment. Cleaned noopClick import and visualOnly prop from Segment.

---

## 4. RIGHT PANEL HEADER — `RightPanel.tsx`

- [x] `right-panel.avatar.self` — Removed (multiplayer avatar button)
- [x] `right-panel.share` — Removed (disabled share button)

### Zoom menu — always disabled:
- [x] `zoom-view-options.pixel-preview` — Removed
- [x] `zoom-view-options.pixel-grid` — Removed
- [x] `zoom-view-options.snap-to-pixel` — Removed
- [x] `zoom-view-options.layout-guides` — Removed
- [x] `zoom-view-options.multiplayer-cursors` — Removed
- [x] `zoom-view-options.outlines.show` — Removed

**Action taken:** Removed avatar + share from header. Removed 6 disabled zoom view items + separator. Cleaned Share2 import, ChromeIconButton component, and disabled branch from ZoomMenuItem.

---

## 5. DESIGN TAB SUB-HEADER — `RightPanel.tsx`
> `[STATE: visible only when hasSelection === true]`

- [x] `sub-header.mask` — Removed
- [x] `sub-header.create-component` — Removed
- [x] `sub-header.boolean.open` — Removed
- [x] `sub-header.more` — Removed

**Action taken:** Removed entire SubHeader + SubHeaderButton component. noopClick import cleaned up.

---

## 6. ACTION BAR — `ActionBar.tsx` (file deleted)

- [x] `action-bar.create-component` — File deleted entirely; ActionBar component never imported anywhere
- [x] `action-bar.use-as-mask` — Same
- [x] `action-bar.boolean` — Same
- [x] `action-bar.suggest-auto-layout` — Same

**Action taken:** ActionBar.tsx was already orphaned (no caller); deleted the file. Group (`Cmd+G`) still works via keyboard shortcut and context menu.

---

## 7. CONTEXT MENU — `ContextMenu.tsx`
> `[STATE: visible when right-click context menu is open]`

- [x] `ctx.copy-as.css` — Removed (with the Copy as CSS/SVG/PNG group + separator)
- [x] `ctx.copy-as.svg` — Removed
- [x] `ctx.copy-as.png` — Removed
- [x] `ctx.use-as-mask` — Removed (with the Use as mask / Create component / Flatten group + separator)
- [x] `ctx.create-component` — Removed
- [x] `ctx.flatten` — Removed

---

## 8. PANEL SECTIONS

- [x] `appearance.blend-mode` — Removed from AppearanceSection in figma/ui session
- [x] `layout.use-auto-layout` — Removed by previous chat (LayoutSection refactor)
- [x] `typography.type-settings` — Three-dot button removed from `TypographySection.tsx`. Trailing flex spacer also dropped; `noopClick` import cleaned up (unused after removal).
- [x] `export.add` — ExportSection no longer imported anywhere (dead file; UI surface effectively gone)
- [x] `fill.add` — Now functional (wired to addSolidFill, no longer noopClick)
- [x] `stroke.add` — StrokeSection no longer carries this `data-id` (Section uses onAdd directly)
- [x] `effects.add` — Now functional (adds Drop Shadow + opens detail popover)

### Effects dropdown items — `EffectsSection.tsx`
> `[STATE: visible when effects add dropdown is open]`

- [x] `effects.add.inner-shadow` — Removed by previous chat (EffectsSection overhaul)
- [x] `effects.add.background-blur` — Removed
- [x] `effects.add.noise` — Removed
- [x] `effects.add.texture` — Removed
- [x] `effects.add.glass` — Removed

---

## 9. COLOR PICKER — `ColorPicker.tsx`
> `[STATE: visible when color picker is open]`

- [x] `color-picker.tab.linear` — Removed by previous chat (ColorPicker overhaul; tabs replaced with Custom + X header)
- [x] `color-picker.tab.radial` — Removed
- [x] `color-picker.tab.angular` — Removed
- [x] `color-picker.tab.diamond` — Removed
- [x] `color-picker.tab.image` — Removed

---

## 10. PROTOTYPE PANEL — `PrototypePanel.tsx`
> `[STATE: visible in Prototype tab when frame/item is selected]`

- [x] "Interaction settings" button (SlidersHorizontal icon) — on frame selection (FramePanel)
- [x] "Interaction settings" button (SlidersHorizontal icon) — on item selection (ItemPanel)

**Action taken:** Removed both noop SlidersHorizontal buttons from the Interactions section header in `FramePanel` and `ItemPanel`. The wrapping `<div>` collapsed back to a single `Plus` button. Removed `SlidersHorizontal` from `lucide-react` import (no longer used anywhere in `PrototypePanel.tsx`).

---

## Progress

**Done:** 58 / 59 (1 explicitly skipped — `page-context.{id}.delete` working correctly).

Checklist closed — every actionable noop UI element listed in this file has been removed.
