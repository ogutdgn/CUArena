# Create branch

- **Category:** branching
- **One-line summary:** Create a side-branch of the current file for isolated work; merge back into main when ready.

## Triggers
- Left navigation file-name dropdown → **Create branch**.
- Branches modal → **+** new branch.

## Preconditions
- Branching enabled (Org / Enterprise plan typically).

## Inputs
- Branch name + optional description.

## Behavior
1. New branch created off current main.
2. Editor switches to the branch.
3. Branch indicator visible in chrome.

## Outputs
- **Persistent state:** new branch.

## UI feedback
- Branch indicator chip in chrome.

## Side effects
- N/A.

## Related UI schema entries
- `regions/floating-overlays.md` → branches-modal
- `chrome.md` → branch-indicator

## Semantic event(s) candidate
- `create_branch { file_id, branch_name, description? }`

## Source articles
- `guide-to-branching`
- `view-and-manage-branches`
- `share-a-branch`
- `request-a-branch-review`
- `review-branch-changes`
- `merge-branch-into-main-file`
- `incomplete-merges-or-updates`
