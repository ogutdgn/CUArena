# Step 1 — Probe the app and write your own tools

## Goal

Before documenting anything, **learn how this app's UI is actually built** — then write your own
per-app inspection tools, pinned to that evidence. Code written before looking is guessing; you
saw the tree first, so your tools won't lie.

## How (agent decides the details)

1. **Read `toolbox/*.md` first** — how each tool (UIA, COM, win32, input, screenshot, pixel)
   works, and every trap past runs already paid for.
2. **Dump the live UI tree** of the workspace, deep. Study it: what container hierarchy does the
   app use? What control types? Are there stable command ids (some apps expose them in
   AutomationId)? Where do the command surfaces live?
3. **Pin what you found**: write LOCATORS/constants from the dump — never from assumption.
   (Reference model: `references/word-crawler/uia.py` — "PINNED from a live UIA tree dump, not
   guessed".)
4. **Write your tools** into `kb/<app>/scripts/tools/`: at minimum a reader (enumerate a
   surface's controls with name/id/type/bounds) and a driver (activate a surface, click a
   control, with foreground enforcement). Use raw libraries directly; the toolbox tells you how.
5. **Validate against the live app**, fix, repeat until stable. This includes the **capture
   tool**: confirm it returns the *correct* image for different targets — a whole surface, a
   single button/icon, a dialog, a dropdown/flyout — by looking at each result and checking it
   shows the intended thing (not the wrong window, an empty region, or a stale frame). If a
   capture type comes back wrong, fix the tool now — the whole KB's visual evidence depends on it.
6. **Give back**: append dated lessons you learned to the relevant `toolbox/*.md` files — the
   next app starts smarter because of you.

## Rules

- **R1.1** All common rules (CR1–CR8, `playbook/README.md`) bind.
- **R1.2** Tools must *measure*, not trust: verify reads against a screenshot at least once.
- **R1.3** Tools stay honest about failure — raise/log loudly, never swallow.
- **R1.4** The capture tool is validated per target type (whole surface / single button / dialog
  / dropdown) by LOOKING at each result — before Step 2 starts. Wrong captures poison every
  visual proof after them.

## Proof

1. Your enumerator, run against ONE full command surface (e.g. one ribbon tab / menu), outputs
   every control with name + id + type + bounds — and a screenshot confirms the surface it
   describes is the one on screen.
2. The tool code exists under `kb/<app>/scripts/tools/` and re-runs cleanly twice.
3. At least one dated lesson appended to a `toolbox/*.md` file.
