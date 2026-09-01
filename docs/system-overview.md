# System Overview

How an environment in this repo actually works. For *why* the repo is shaped this way, read
[arc.md](arc.md); for the map, [../README.md](../README.md).

---

## The pieces

```
┌──────────────────┐     ┌──────────────────┐
│ Environment (UI) │ ──► │ Three log streams│
│                  │     │  raw / semantic  │
│ figma | ms-word  │     │  / outcome       │
└──────────────────┘     └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Per-env verifier │
                         │ Task → Rubrics   │
                         │ → Checks         │
                         └────────┬─────────┘
                                  ▼
                         final_score = base × efficiency multiplier
```

Per environment the contract is: the app writes `<env>-log-<sessionId>.json`; the verifier
reads it, runs the task's rubrics, applies the efficiency multiplier, and returns a score
in `[0, 1]`.

## The point: score the method, not just the end state

Two agents both produce "a square inside a frame". One created it directly in the frame
context (3 operations); the other copy-pasted and reparented (8 operations). Both end
states are identical, so an outcome-only grader calls them equal. The semantic stream and
the efficiency multiplier do not.

This is why the environment has to be something we own. A closed application gives you
pixels and a final file; it does not give you the operation stream.

## The three streams

| Stream | Source | Read by verifier? |
|---|---|---|
| `raw` | every input event (pointer, key, wheel, clipboard) | no — forensics only |
| `semantic` | every meaningful operation the engine dispatched | yes — efficiency rubric reads turn count |
| `outcome` | live snapshot of the full document + summary counts | yes — fundamentals / alignment / colour / etc. |

Full schema: [log-contract.md](log-contract.md).

## Why more than one environment

A single environment tests agents against one UI archetype:

| Environment | Shape | Primitives | What it stresses |
|---|---|---|---|
| **figma** | TS mock | shapes on a canvas, properties panel, frames | spatial reasoning, drag, geometry, fills/strokes |
| **ms-word** | Electron + ProseMirror | text runs, paragraphs, styles, lists, tables, `.docx` | text editing, caret/range, formatting persistence, file round-trip |
| **ms-word-native** *(superseded)* | native Qt6 + rented LO engine | the same, over a real OS window | native window/focus/clipboard behaviour a browser mock abstracts away |

The native line was the attempt to cover real-OS behaviour; it was superseded for the
reason in [decisions/engine-rent-vs-own.md](decisions/engine-rent-vs-own.md). Covering that
surface again is future work, not a solved problem.

## Per-environment structure

```
envs/<env>/
├── CLAUDE.md              env-level agent guide
├── app-docs/ or docs/     all docs: feature-checklist, execution-map, decisions, research
├── mock/ or src/          the environment UI codebase
├── verifier/              rubric framework (Python)
├── delivery-1/            per-task package (prompt.md + verifier.py per task)
└── scripts/               CLI entry-points (run_task / score_log / qa_verifiers) + outputs
```

These are **per-environment, not shared**. Once a second environment ships a verifier
end-to-end, the common parts get extracted.
