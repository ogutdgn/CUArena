# Version history

- **Category:** sharing
- **One-line summary:** Browse, restore, or compare past auto-saved snapshots and named versions of the file.

## Triggers
- Left navigation file-name dropdown → **Show version history**.

## Preconditions
- File has at least one prior version.

## Inputs
- Pointer click on a version in the right rail → preview.
- Right-click → **Restore this version** / **Add to this version** / **Compare**.
- Name a version: enter title + description.

## Behavior
1. File replaced with read-only preview at the chosen version's snapshot.
2. **Restore** branches a new file or replaces current (depends on version type).
3. **Compare** highlights diffs between versions.

## Outputs
- **Persistent state:** when restored, file content updated.
- **UI state:** version history panel.

## UI feedback
- Right rail with chronological version list; canvas as preview.

## Side effects
- Standard undo / restore semantics.

## Related UI schema entries
- `regions/floating-overlays.md` → version-history-panel

## Semantic event(s) candidate
- `open_version_history { file_id, trigger }`
- `restore_version { version_id }`
- `name_version { version_id, title, description }`
- `compare_versions { from_id, to_id }`

## Source articles
- `see-viewer-history-for-your-files`
- (related branching: `view-and-manage-branches`)
