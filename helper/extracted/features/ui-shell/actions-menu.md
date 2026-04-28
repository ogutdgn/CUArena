# Actions menu (Cmd K command palette)

- **Category:** ui-shell
- **One-line summary:** Universal command palette / search overlay — search for any action, AI tool, plugin, asset, or component.

## Triggers
- Toolbar icon (right of creation tools) — actions-menu icon.
- Shortcut: `⌘ K` (Mac) / `Ctrl K` (Win).

## Preconditions
- Editor view active.

## Inputs
- Free-text search.
- Click an entry to invoke.

## Behavior — real Figma
1. Opens a floating panel anchored to the icon.
2. Lists categories: actions, AI tools, plugins, widgets, asset search, find similar designs.
3. Free-text matches across all categories.
4. Selecting an entry runs the corresponding action.

## Behavior — mock
- The actions menu is `visual-only` for the mock body.
- Click on the icon: opens a stub panel with a search bar but a placeholder result like "Actions menu coming soon" or routes to `unsupported-feature-toast.md` with feature label `"Actions menu (Cmd K)"`.
- Inside the panel, any clicked entry (if entries are stubbed in) triggers `unsupported-feature-toast.md`.

## Outputs
- **Scene graph changes:** none (in mock scope).
- **UI state:** stub panel renders.
- **Logger:** `unsupported_feature_clicked`.

## UI feedback
- Floating panel.

## Side effects
- None in mock scope.

## Related UI schema entries
- `regions/toolbar.md` → actions-menu icon
- `regions/floating-overlays.md` → actions-menu-panel

## Semantic event(s) candidate
- `open_actions_menu { trigger: "icon" | "shortcut" }`
- `unsupported_feature_clicked { feature_key: "actions_menu_*", feature_label }` for sub-entries.

## Source articles
- `use-the-actions-menu-in-figma-design`
- `navigating-ui3`

## Notes / gaps
- Real Figma includes AI tools, plugins, widgets — all out of functional scope for mock.
