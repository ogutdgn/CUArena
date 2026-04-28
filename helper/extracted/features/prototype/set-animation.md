# Set prototype animation (transition + easing + spring)

- **Category:** prototype
- **One-line summary:** Configure the transition between frames — Instant / Dissolve / Smart animate / Move in / Move out / Push / Slide in / Slide out / etc., with easing curves (linear, ease-in/out, custom bezier, spring).

## Triggers
- Connection selected → Prototype panel → Animation section.

## Preconditions
- A connection exists.

## Inputs
- Transition type dropdown.
- Direction (for directional transitions).
- Duration (ms).
- Easing curve (built-in presets or custom bezier).
- Spring parameters (mass / tension / friction).

## Behavior
- At runtime, transition plays per the configured params.
- **Smart animate** auto-tweens shared layers between frames (per `smart-animate-layers-between-frames`).
- Spring animations use physics simulation parameters (per `prototype-easing-and-spring-animations`).

## Outputs
- **Scene graph changes:** connection's `animation` config updated.

## UI feedback
- Animation params in panel.

## Side effects
- Undo stack: per change.

## Related UI schema entries
- `regions/right-properties.md` → prototype-section → animation-controls

## Semantic event(s) candidate
- `set_prototype_animation { connection_id, type, duration, easing, spring_params?, trigger }`

## Source articles
- `prototype-animations`
- `prototype-easing-and-spring-animations`
- `smart-animate-layers-between-frames`
