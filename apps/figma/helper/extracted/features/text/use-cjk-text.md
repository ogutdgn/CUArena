# Use CJK (Chinese / Japanese / Korean) text

- **Category:** text
- **One-line summary:** Type CJK languages with IME composition support; line-breaking respects CJK rules.

## Triggers
- Active text edit + typing CJK characters via the OS IME.

## Preconditions
- Text layer active.
- OS IME enabled for the language.

## Inputs
- IME composition input.

## Behavior
1. Composition events render the in-progress reading underlined; commit replaces with selected character(s).
2. Line breaks respect CJK conventions (no spaces between characters; break on CJK character boundaries).
3. Some properties (like letter-spacing) apply differently — corpus does not enumerate exact differences for the mock.

## Outputs
- **Scene graph changes:** text content updated.

## UI feedback
- IME underline during composition.

## Side effects
- Undo stack: typically one entry per IME commit (but coalesces in typing bursts).

## Related UI schema entries
- `regions/canvas-overlays.md` → text-edit-overlay (IME affordance)

## Semantic event(s) candidate
- `insert_text { layer_id, position, text, ime: bool, trigger: "ime_commit" | "keyboard" }`

## Source articles
- `add-text-in-chinese-japanese-and-korean`

## Notes / gaps
- IME nuances are OS-driven; the mock should pass through OS composition events rather than re-implement them.
