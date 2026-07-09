# Step 2 — APP SKEL: map the trigger surface, measured

## Goal

Document the app's skeleton: **every top-level surface** (each ribbon-tab face, each menu, the
main window regions) and **what every control on them actually does** — measured by pressing,
never assumed from names.

## How (agent decides the details)

- Use the tools you built in Step 1. Work surface by surface from a worklist you write first.
- For every control: **press → observe → classify → reset** (the core method,
  `references/word-crawler/` is the model):
  - new window of dialog class → `opens` a dialog
  - new window of flyout class / inline expansion → `opens` a dropdown/menu
  - app/document state changed, no UI opened → `triggers` a feature
  - nothing observable → journal it honestly (`no-effect` / `ambiguous`)
- **Reset-verify after every press**: window set back to baseline? document unchanged? If not —
  fix it first, journal the incident. One stuck dialog silently corrupts every control after it.
- Keep a **seen-set**: a surface reached by a second path gets referenced, never re-crawled.
- Capture each opened surface's contents (walk its tree; owner-drawn surfaces → hit-test +
  pixel sampling per `toolbox/pixel.md`) and a window-true screenshot.
- Write containers via the **kernel writers** (`kernel/kb_writer.py`) — one JSON per surface,
  element ids, exactly-one marker per element (`opens` / `triggers` / `unexplored`). Schema:
  `design/knowledge-base-design.md`.

## Be sure of

- All common rules (`playbook/README.md`).
- `opens`/`triggers` markers ONLY from a measured outcome. Unpressed = `unexplored`.
- Never write an empty container — read its contents or don't write it.
- Verify you are LOOKING at the surface you're documenting (your action's result, on screen)
  before writing it.

## Proof

1. One container JSON per top-level surface — none empty, every element exactly one marker,
   every `opens` value resolving to an existing container file.
2. Screenshots that visibly match their containers (spot-checkable by a human).
3. Journal shows a press/reset pair (or an honest skip) for every interactive element, and the
   run's end state equals its start state.
4. A coverage note: what was documented, what stayed `unexplored` and why.
