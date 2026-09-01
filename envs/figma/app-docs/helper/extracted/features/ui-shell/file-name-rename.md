# Rename the file (file-name bar)

- **Category:** ui-shell
- **One-line summary:** Edit the file's title from the left-navigation file-name bar.

## Triggers
- Double-click on the file name in the left navigation panel header.
- Click the file-name dropdown chevron → **Rename file** (per `navigating-ui3`).

## Preconditions
- Editor view active.
- User has edit access (covered by `who-can-edit`).

## Inputs
- Typed new file name.
- Commit on Enter / blur.

## Behavior
1. Double-click converts the file-name label into an editable input.
2. User types and presses Enter (commits) or Esc (cancels).
3. The new name is persisted as the file's title (in the file metadata, not the scene graph).

## Outputs
- **Scene graph changes:** none directly.
- **Persistent file state:** file title updated.
- **UI state:** title bar reflects new name.

## UI feedback
- Editable field with current name pre-selected.
- Title bar updates on commit.

## Side effects
- Undo stack: file-rename is a metadata change. Whether it's part of the scene-graph undo is implementer's choice; real Figma includes it in undo.

## Related UI schema entries
- `regions/left-navigation.md` → file-name-bar
- `chrome.md` → file-name-bar

## Semantic event(s) candidate
- `rename_file { from_name, to_name, trigger: "double_click_filename" | "menu_rename" }`

## Source articles
- `navigating-ui3`

## Notes / gaps
- File-name dropdown also exposes other entries (Move file, Publish library, Branch, Version history, etc.). Each is documented separately; entries the mock doesn't implement should call `unsupported-feature-toast.md`.
