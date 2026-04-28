# Panel Scroll Behavior

**Purpose:** Cross-region notes on how the left navigation panel, right properties panel, color picker, and other floating overlays scroll when their contents exceed available height.

---

## Left navigation panel

**Layout** (top → bottom):
1. File-name dropdown / main menu (sticky top).
2. Minimize-UI icon (sticky top corner).
3. Tabs (File / Assets) (sticky top, below dropdown).
4. **Scrollable area:**
   - File tab: pages selector + layers tree + collapse-layers icon.
   - Assets tab: libraries list, search, asset grid.
5. Find/Replace takeover (replaces scrollable area when active).

**Scroll behavior:**
- Scrollable area accepts wheel / touchpad / scrollbar drag / `Page Up` / `Page Down`.
- During panel-row drag (reparent), auto-scrolls when cursor near top/bottom edges (~20px threshold).
- Pages selector and layers tree share one scroll container; pages selector pinned to top of scroll area.
- Layers tree expand/collapse: scroll position preserved across expand operations (best-effort).

---

## Right properties panel

**Layout** (top → bottom):
1. Header row (zoom %, view-options, Share, Present, avatar stack) — sticky.
2. Tabs (Design / Prototype) — sticky.
3. Sub-header (Mask / Component / Boolean / `…`) — sticky when selection is non-empty.
4. **Scrollable section list** — varies by selection (see `state-matrix.md`):
   - Page bg / Local styles / Local variables / Export page (no selection).
   - Layout / Position / Appearance / Typography / Fill / Stroke / Effects / Component / Export (selection-driven).

**Scroll behavior:**
- Scrollable section list scrolls independently of header / tabs / sub-header.
- Section headers (Layout, Position, etc.) are NOT individually sticky in default Figma (they scroll with content).
- Resize bar on left edge of panel → drag to change panel width (not a scroll affordance).

---

## Color picker (floating overlay)

- Picker has a fixed width and may exceed window height (large gradient stop list, document colors row, library colors).
- Picker scrolls vertically inside its bounds.
- Drag operations inside picker (gradient stop drag, slider drag) don't trigger scroll.

---

## Other floating overlays

| Overlay | Scrollable? |
|---|---|
| Bulk rename modal | Live preview list scrolls; form is fixed |
| Variables modal | Variable list scrolls per-collection |
| Libraries modal | Library list scrolls |
| Page-context-menu | Fixed; if overflows screen, repositions |
| Boolean-ops dropdown | Fixed, no scroll |
| Font picker | Long font list scrolls |
| Frame preset list | Scrolls |
| Comment thread panel | Comment list scrolls |
| Version history rail | Version list scrolls |

---

## Logger considerations

- Scroll is typically not interesting to log unless the action results in a significant viewport change (e.g. user scrolls panel to find a specific section, then clicks an action there).
- Mock can omit explicit `scroll_panel` events; alternative is to log at "click" time and let trajectory infer.

---

## Source articles

- `view-layers-and-pages-in-the-left-sidebar` — left panel layout.
- `design-prototype-and-explore-layer-properties-in-the-right-sidebar` — right panel layout.
- `navigating-ui3` — overall chrome.

## Notes / gaps

- Exact stickiness behavior of section headers in the right panel is not pinned by docs; treat as scroll-with-content.
- Auto-scroll during drag inside the layers tree: documented at high level in `view-layers-and-pages-in-the-left-sidebar`; thresholds not enumerated.
