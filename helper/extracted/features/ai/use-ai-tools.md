# Use Figma AI tools

- **Category:** ai
- **One-line summary:** Set of AI-powered features — generate UI, rename layers in bulk, make/edit images, find similar designs, etc.

## Triggers
- Toolbar Actions menu (`Cmd K`) → search for AI tool.
- Specific entry points: color picker → "Make an image" (image fill); right-click on layers → "Rename layers (AI)".

## Preconditions
- Figma AI features enabled for account / file.

## Inputs
- Per-tool prompt or selection.

## Behavior
- Each AI tool runs an asynchronous request and returns a result.
- Per `use-ai-tools-in-figma-design`: includes "Make designs", "Make/edit image with AI", "Rename layers", and similar.

## Outputs
- Per-tool: scene-graph or fill / asset changes.

## UI feedback
- Loading spinner during request; results shown in panel or applied to selection.

## Side effects
- May be billed / metered.

## Related UI schema entries
- `regions/floating-overlays.md` → actions-menu / per-tool dialogs

## Semantic event(s) candidate
- `run_ai_tool { tool_name, prompt?, selection_ids?, result_summary, trigger }`
- For mock: `unsupported_feature_clicked { feature_key: "ai_<tool>" }` per tool entry.

## Source articles
- `use-ai-tools-in-figma-design`

## Notes / gaps
- AI tools are out of mock scope; treat each as a stub that triggers `unsupported-feature-toast.md`.
