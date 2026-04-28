# Enable library in file

- **Category:** libraries
- **One-line summary:** Subscribe the current file to a published library, exposing its assets in pickers.

## Triggers
- Left navigation **Assets** tab → **Libraries** modal opener → toggle libraries on.

## Preconditions
- The library has been published (or accessible via team).

## Inputs
- Toggle per library.

## Behavior
1. Enabled libraries' components, styles, and variables become available in pickers.
2. Disabling: assets currently used remain bound but new pickers don't show them.

## Outputs
- **Persistent state:** file's enabled-libraries list updated.

## UI feedback
- Modal toggle reflects state.

## Side effects
- Undo stack: not affected.

## Related UI schema entries
- `regions/floating-overlays.md` → libraries-modal

## Semantic event(s) candidate
- `enable_library { file_id, library_id, to_state, trigger }`

## Source articles
- `add-or-remove-a-library-from-a-design-file`
- `enable-access-to-libraries-in-your-drafts`
- `swap-libraries`
- `remove-your-access-to-a-library`
- `guide-to-libraries-in-figma`
