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
- **Stubs — how to defer an interior you're not entering yet.** When an element opens more UI
  whose interior is deeper machinery you won't enumerate in this pass, you still record TWO
  things honestly: (1) the element keeps its **measured `opens` marker** — you pressed it and saw
  a surface open, so you know what it *does*; (2) the opened surface is written as a **stub
  container** — `id`, `kind`, `label`, one screenshot, `children: []`, and **`explored: false`**.
  A stub says "this surface exists; I deliberately have not gone inside." Its interior is filled
  only in Step 5 (depth), and only if priority warrants. The element is NOT `unexplored` (you
  measured what it opens); only the surface's *contents* are deferred.

## Rules

- **R2.1** All common rules (CR1–CR8, `playbook/README.md`) bind.
- **R2.2** `opens`/`triggers` markers ONLY from a measured outcome. Unpressed = `unexplored`.
- **R2.3 No effect, no endpoint.** A press with no observable effect must NOT be classified
  `triggers` — journal the failed/ambiguous press and leave the element `unexplored` (or retry
  in a valid context). "Pressed: no observable effect" next to a `triggers` marker is a
  contradiction: the claim has no evidence. (LESSONS 2026-07-12)
- **R2.4 Ellipsis contract.** A label ending in "…"/"..." promises a dialog (platform
  convention). Such an element may carry `opens` or stay `unexplored` — NEVER `triggers`. If no
  surface appeared on press, the press failed (wrong context, missed window) — record the
  failure; do not reclassify the control as an action. [kernel-checked] (LESSONS 2026-07-12)
- **R2.5 A gallery is a THREE-zone control** (tiles + scroll arrows + expand arrow), the
  split-button rule's bigger sibling. Pressing a tile measures the TILE only. The expand arrow
  is a separate element that `opens` the full gallery flyout — which almost always carries extra
  commands at the bottom ("New/Modify/Clear …") that open dialogs of their own. Closing a whole
  gallery as one endpoint is the failure this rule bans. (→ `toolbox/uia.md` for how to find the
  expand zone; LESSONS 2026-07-12)
- **R2.6 Stub vs. dishonest-empty — know the difference.** A container with `children: []` is
  only allowed as an explicit **stub** (`explored: false` — an honest "not entered yet"). A
  container written as if complete but empty because your clicks failed / you didn't read it is
  a **lie** — forbidden. Empty + `explored:false` = fine; empty + claiming done = banned.
- **R2.7** Verify you are LOOKING at the surface you're documenting (your action's result, on
  screen) before writing it.

## Proof

1. One container JSON per top-level surface — every element exactly one marker, every `opens`
   value resolving to an existing container file (which may be a stub). No container is empty
   *without* `explored: false` — empty-and-unmarked (a dishonest "done") fails the step.
2. Screenshots that visibly match their containers (spot-checkable by a human).
3. Journal shows a press/reset pair (or an honest skip) for every interactive element, and the
   run's end state equals its start state.
4. A coverage note: what was documented, what stayed `unexplored` and why.
