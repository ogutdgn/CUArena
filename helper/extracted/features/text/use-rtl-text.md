# Use right-to-left (RTL) text

- **Category:** text
- **One-line summary:** Display and edit RTL languages (Arabic, Hebrew) with mirrored layout; toggle force-RTL behavior.

## Triggers
- Type RTL characters; rendering automatically flips alignment for that range.
- Right-click → **Force RTL** toggle (per `add-right-to-left-text`).

## Preconditions
- Text layer active.

## Inputs
- Typing RTL characters, or force-RTL toggle.

## Behavior
1. Bidi rendering: mixed LTR + RTL within one paragraph follows Unicode bidi algorithm.
2. Force-RTL overrides auto-detection: paragraph treated as RTL even when characters are LTR.
3. Alignment defaults flip (left ↔ right) for RTL paragraphs.

## Outputs
- **Scene graph changes:** layer's `force_rtl` flag may be set; rendering reflects bidi resolution.
- **Selection changes:** none.

## UI feedback
- Canvas redraws with mirrored alignment.

## Side effects
- Undo stack: per-action.

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu → Force RTL

## Semantic event(s) candidate
- `set_force_rtl { layer_ids, to_state, trigger }`

## Source articles
- `add-right-to-left-text`
