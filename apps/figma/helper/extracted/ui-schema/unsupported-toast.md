# Unsupported Feature Toast

**Region role:** Mock-specific UI element. When the user clicks any `visual-only` button or selects an unsupported menu entry, a toast appears at the bottom of the editor announcing that the feature isn't yet implemented.

**Anatomy:**
- Single-line toast with the format: `"{Feature name} is not yet supported"`.
- Optional close `×` icon.
- Auto-dismisses after a fixed timeout (~3-5s).

**Position:** Bottom-center of the editor (above the toolbar) or top-right (consistent with Figma's success/error toasts; implementer's choice — corpus does not pin location for unsupported-feature toasts because they're mock-specific).

**Behavior:**
- Coalescing: clicking the same unsupported feature multiple times before the toast dismisses replaces the existing toast (or shows a counter).
- Different unsupported features in quick succession → stacked toasts (max 3 visible).
- Click outside the toast: closes immediately.
- Esc: closes all visible toasts.

**Implementation map:**
- Mock app keeps a registry: `{ element_id → human_label }` for every UI element flagged `visual-only`.
- A central toast service receives `unsupported_feature_clicked` events from button click handlers and renders the toast.
- Logger emits the event for CUA test harness consumption (see `extracted/features/ui-shell/unsupported-feature-toast.md`).

**Element registry (sample mapping)**

| element_id | human_label | category |
|---|---|---|
| `share_button` | Share | sharing |
| `present_button` | Presentation view | prototype |
| `export_button` | Export | export |
| `actions_menu_root` | Actions menu | ai/actions |
| `actions_menu_<plugin>` | Plugin: <name> | plugins |
| `avatar_stack_click` | Multiplayer follow | multiplayer |
| `prototype_tab` | Prototype tab | prototype |
| `dev_mode_toggle` | Dev Mode | dev-mode |
| `figma_draw_toggle` | Figma Draw | draw-mode |
| `assets_tab` | Assets panel | components/libraries |
| `comment_tool` | Comment tool | comments (or FN basic) |
| `annotation_tool` | Annotation | comments-annotation |
| `mask_action` | Mask | masks |
| `set_thumbnail` | Set as thumbnail | misc |
| `import_sketch` | Import Sketch | imports |
| `import_file` | Import file | imports |
| `branches_modal` | Branches | branching |
| `version_history` | Version history | sharing |
| `publish_library` | Publish library | libraries |
| `enable_library` | Enable library | libraries |
| `swap_libraries` | Swap libraries | libraries |
| `cursor_chat` | Cursor chat | multiplayer |
| `spotlight` | Spotlight | multiplayer |
| `ai_make_image` | Make an image with AI | ai |
| `ai_make_design` | Make a design with AI | ai |
| `ai_rename_layers` | Rename layers (AI) | ai |
| `nudge_preferences` | Nudge preferences | preferences |
| `pixel_preview` | Pixel preview | rendering |
| `pixel_grid_toggle` | Pixel grid | rendering |
| `multiplayer_cursors` | Multiplayer cursors | multiplayer |
| `property_labels` | Property labels | rendering |
| `(per `state-matrix.md`)` | ... | ... |

This list is not exhaustive — every `visual-only` element in `regions/*.md` should appear here with a human label.

**Reference / source:**
- This toast is mock-specific (not a real Figma feature). Implements user requirement: "Robust buttons logic for all features on the screen (pop up '{feature_name} unsupported' error message if not yet implemented)".
- Cross-link: `extracted/features/ui-shell/unsupported-feature-toast.md` (the per-feature spec).
