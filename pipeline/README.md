# App Pipeline

Replicate whole applications from a single prompt (`build microsoft word`, `build gmail`, …).

The first phase — the current focus — is **P1: the Knowledge Base Pipeline**: given an app's
name, produce an accurate, structured knowledge base about it. Nothing can be replicated that
isn't first accurately understood.

## Architecture

An **agent** learns the app by driving it; the project gives that agent everything it needs to
succeed — but keeps almost nothing as fixed code. The pipeline is four kinds of thing:

| Folder | What it is | Who owns it |
|---|---|---|
| `design/` | What a knowledge base *is* — schema, the 3-level model, priority, discipline | fixed spec |
| `playbook/` | The steps the agent follows to learn an app (goal · be-sure-of · proof) | knowledge, not code |
| `toolbox/` | Knowledge about tools (UIA, COM, win32, screenshots…): how to use them, their traps, and lessons that compound across apps | knowledge, not code |
| `kernel/` | The only live code: schema writers + journal (guarantees that must not vary per app) | us, rarely |
| `configs/` | Per-app data + fixtures | data |
| `references/` | Proven example code (the Word crawler, our pre-pivot pipeline) — inspire, never dictate | read-only |
| `kb/<app>/` | The agent's workspace: the tools it writes per app + the KB it produces | the agent |

**The core idea:** the agent reads the playbook (what to do) and the toolbox (how to use the
tools), then writes its *own* per-app inspection code into `kb/<app>/scripts/`, proving each
step. Code doesn't generalize across apps; **lessons do** — so every app inspected makes the
toolbox richer and the next app easier. The only thing we hand-maintain is the tiny kernel.

## Status

- **Design:** stable (`design/knowledge-base-design.md`).
- **Architecture:** pivoted (2026-07-09) to agent-writes-its-own-tools. Earlier hand-built code
  (Plan A + B1: launch, prober, discard handling, safety, window-true capture) is preserved in
  `references/legacy/` as proven, lesson-rich seed material — not the live system.
- **Next:** author the `playbook/` steps and seed the `toolbox/` files from the legacy lessons,
  then run the agent through step 0–1 on MS Word.
