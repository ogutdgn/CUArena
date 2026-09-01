# App Pipeline — automating the understanding step

> **Stage 3 of [`rl-for-cua`](../README.md).** After building two CUA environments by hand
> ([`envs/figma`](../envs/figma/), [`envs/ms-word`](../envs/ms-word/)), the same line item
> dominated both: not writing the app, but *specifying* it — knowing exactly what is in
> Word's Insert tab, what each control does, what it opens, what it affects. This pipeline
> makes that specification a machine-produced artifact. Full reasoning:
> [`docs/arc.md`](../docs/arc.md).

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
- **Architecture:** pivoted (2026-07-09) to agent-writes-its-own-tools. Earlier hand-built
  code (Plan A + B1: launch, prober, discard handling, safety, window-true capture) is
  preserved in `references/legacy/` as proven, lesson-rich seed material — not the live
  system.
- **Playbook + toolbox:** authored (steps 0–6), seeded from the legacy lessons.
- **Runs completed:** three, each one feeding lessons back into `playbook/LESSONS.md` and
  `toolbox/` — `word-home-tab` → `word-home-insert(-v2)` → `word-4tabs-v1`.

### Latest output — [`kb/word-4tabs-v1/`](kb/word-4tabs-v1/)

Microsoft Word, scoped to the `Home` / `Insert` / `Design` / `Layout` ribbon tabs plus every
contextual tab they summon:

| | |
|---|---|
| features · sub-features | **38 · 194** |
| UI containers | **433** (34 recorded as honest stubs, `explored:false`) |
| UI graph | **232 nodes · 343 edges** — what opens what, what each control affects |
| priority layers | P0=11 · P1=34 · P2=27 · P3=106 · P4=54 |
| shortcuts · screenshots | 25 · **389** verified |
| audit trail | `journal.jsonl` — every action *and* decision, with reasoning |

This is the same class of artifact that [`envs/ms-word`](../envs/ms-word/) needed a month of
human research to produce.

## What is not built yet

The loop is open at the far end: this pipeline produces the specification, and the
environments consume one, but **a human is still the thing in between**. KB → generated
environment scaffold is the next stage. The KB schema was designed against what the Figma
and Word builds actually consumed — feature trees, trigger paths, priority layers — so it
is a codegen problem, not a redesign.

The second claim still untested: that per-app scripts are disposable and only `toolbox/`
lessons compound. All three runs so far were Word. Running the playbook against a
structurally different app is what would prove it.
