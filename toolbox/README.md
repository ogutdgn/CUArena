# toolbox/ — knowledge about the tools, not the tools themselves

This is the "tool library" — but it holds **knowledge**, not code. One markdown file per
capability, teaching the agent how to use that tool to drive/inspect an app: what it's for, how
to use it, its known traps, and — crucially — **what past runs learned about it.**

The agent reads these before writing its own per-app tools (into `kb/<app>/scripts/`). Because
the *lessons* transfer across apps even when the *code* doesn't, every app inspected makes these
files richer, so the next app starts smarter. This is where the pipeline compounds.

## Files (to be authored — seeded from `references/legacy/` hard-won lessons)

| File | Covers |
|---|---|
| `uia.md` | UI Automation: reading element trees, control types, AutomationId==idMso, split-buttons, pattern-availability quirks, deep modern trees |
| `win32.md` | Window enumeration, foreground enforcement, dialog-vs-flyout by class, new-window detection, broker-process pids |
| `com.md` | App object models (e.g. Office COM): isolated instances, state verification, deterministic no-prompt close |
| `input.md` | Real mouse/keyboard injection, why synthetic input fails on some flyouts, foreground preconditions |
| `screenshot.md` | Window-true capture (PrintWindow) vs screen grab, why coordinate-grabs photograph the wrong window |
| `pixel.md` | Pixel sampling + hit-testing for owner-drawn surfaces (palettes, ribbon galleries) invisible to UIA |
| `research.md` | Web search + docs harvesting for the usage signal and app-specific documentation |

## Format of each file

Each tool file carries: **Purpose** · **How to use (with idioms)** · **Known traps** ·
**Lessons learned** (append-only, dated, sourced from a specific app+run — the compounding memory).

Seed material: `references/legacy/tools/*.py` and `references/word-crawler/` contain real,
proven code whose docstrings already record many of these lessons — distill, don't invent.
