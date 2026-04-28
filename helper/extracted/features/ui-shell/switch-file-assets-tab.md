# Switch File / Assets tab (left navigation)

- **Category:** ui-shell
- **One-line summary:** Switch the left navigation panel between the **File** tab (pages + layers tree) and the **Assets** tab (libraries + components).

## Triggers
- Click **File** or **Assets** tab label.
- Shortcuts:
  - **File tab:** `Opt 1` (Mac) / `Ctrl 1` (Win).
  - **Assets tab:** `Opt 2` / `Ctrl 2`.

## Preconditions
- Left navigation panel visible.

## Inputs
- Pointer click OR shortcut.

## Behavior
1. Active tab indicator updates.
2. Panel body swaps content:
   - **File**: file-name dropdown, pages selector, layers tree, find/replace icon, collapse-layers icon.
   - **Assets**: libraries-modal opener, search field, libraries-and-settings menu, grouped library list (file > page > frame).

## Outputs
- **Scene graph changes:** none.
- **UI state:** active tab toggled.

## UI feedback
- Tab styling (active vs inactive).

## Side effects
- Undo stack: unaffected.

## Related UI schema entries
- `regions/left-navigation.md` → tabs (File / Assets)

## Semantic event(s) candidate
- `switch_left_panel_tab { to_tab: "file" | "assets", trigger: "click" | "shortcut" }`

## Source articles
- `navigating-ui3`
- `view-layers-and-pages-in-the-left-sidebar`

## Notes / gaps
- Assets tab body in mock scope is `visual-only` (libraries / components out of functional scope unless explicitly added). Click on assets within the tab triggers `unsupported-feature-toast.md`.
