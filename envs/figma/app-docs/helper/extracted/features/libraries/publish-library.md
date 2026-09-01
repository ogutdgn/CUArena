# Publish library

- **Category:** libraries
- **One-line summary:** Publish the file's components, styles, and variables as a library that other files can subscribe to.

## Triggers
- Left navigation file-name dropdown → **Publish library**.
- Variables modal → publish action.

## Preconditions
- File contains at least one publishable asset (component, style, or variable).
- User has publish permission (typically pro+).

## Inputs
- Modal listing publishable items with checkboxes.
- Optional release-notes text.
- **Publish** button.

## Behavior
1. Selected items are pushed to the team library.
2. Subscribers see "Updates available" indicator and can review / accept changes.

## Outputs
- **Persistent state:** library snapshot updated.
- **UI state:** publish modal closes.

## UI feedback
- Toast: "Library published".

## Side effects
- Undo stack: not affected (publish is a metadata action).

## Related UI schema entries
- `regions/floating-overlays.md` → publish-library-modal

## Semantic event(s) candidate
- `publish_library { file_id, item_ids, release_notes?, trigger }`

## Source articles
- `publish-a-library`
- `enable-a-library-for-a-team`
- `enable-access-to-libraries-in-your-drafts`
- `unpublish-a-library`
- `move-published-components`
- `hide-styles-components-and-variables-when-publishing`
