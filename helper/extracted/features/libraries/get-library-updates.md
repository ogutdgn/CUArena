# Get / review library updates

- **Category:** libraries
- **One-line summary:** When a subscribed library is republished, accept updates per asset (or in bulk).

## Triggers
- Updates badge on the file → click → review modal.
- Right sidebar — also surfaces "Out of date" indicators per instance.

## Preconditions
- File subscribes to a library that has new updates.

## Inputs
- Modal: per-update accept / dismiss; **Update all** button.

## Behavior
1. Each update shows a before/after preview.
2. Accept updates the local instances; reject leaves them on the older snapshot.

## Outputs
- **Scene graph changes:** instances re-render with new main definitions.
- **Persistent state:** subscribed library version updated.

## UI feedback
- Modal closes; instances reflect changes.

## Side effects
- Undo stack: one entry covering the bulk update.

## Related UI schema entries
- `regions/floating-overlays.md` → library-updates-modal

## Semantic event(s) candidate
- `accept_library_updates { library_id, update_ids, trigger }`

## Source articles
- `get-updates-from-main-files`
- `review-and-accept-library-updates`
- `apply-changes-to-instances`
- `incomplete-merges-or-updates`
