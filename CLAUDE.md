# CUArena — Repo-Root Agent Guide

You are working in `CUArena`: **three CUA environments and one knowledge-base
pipeline**. An environment reproduces a real application as something we own, so an agent
can be reset, observed and graded against it. The pipeline automates the step that
dominated building the first two by hand — understanding the app.

Read [README.md](README.md) for the shape, [docs/arc.md](docs/arc.md) for why each piece
exists. If you were dispatched to a single environment, read that environment's CLAUDE.md
and treat this file as wider context.

---

## Repo layout

```
CUArena/
├── README.md                     the arc + status
├── CLAUDE.md (this file)         repo-root agent guide
├── AGENTS.md                     mirror of CLAUDE.md (for Codex / other tooling)
├── docs/
│   ├── arc.md                    the three stages and what each taught
│   ├── log-contract.md           cross-env log schema (raw / semantic / outcome)
│   ├── system-overview.md        the env + log + verifier mental model
│   ├── conventions.md            commit / branch / session-end protocols
│   ├── roadmap.md                sequencing + milestones
│   └── decisions/                cross-environment ADRs
├── .claude/
│   ├── settings.json             permissions, hooks
│   └── skills/<name>/SKILL.md    repo-internal skills (research, dev, commit, ...)
├── envs/
│   ├── figma/                    shipping — Figma mock + verifier + 50 tasks + runner
│   │   ├── CLAUDE.md             ← READ THIS when working on the figma env
│   │   ├── app-docs/             all docs (mock-doc/ + verifier-doc/ + scripts-doc/ + helper/)
│   │   ├── mock/                 the TS/React mock
│   │   ├── verifier/             flat Python library (no __init__.py — namespace package)
│   │   ├── delivery-1/           50-task source of truth (prompt.md + verifier.py per task)
│   │   └── cua-eval/, scripts/   benchmark runs + CLI entry-points
│   ├── ms-word/                  shipping — Electron + ProseMirror Word clone
│   │   ├── CLAUDE.md             ← READ THIS when working on the word env
│   │   ├── docs/decisions/       ADR-0001…0006 (pivot, PM model, SuperDoc fork, docx)
│   │   ├── src/                  main/ + renderer/ (ribbon chrome, PM bridge, fork)
│   │   ├── specs/ + .specify/    spec-kit workspace — see "Working in ms-word" below
│   │   └── .claude/skills/       env-level skills (speckit-*, plan-tracking, commit-style)
│   ├── ms-word-native/           SUPERSEDED — Qt6 + LibreOfficeKit attempt, kept as record
│   │   ├── docs/research/ribbon/ 692-control Word↔LibreOffice comparison (still useful)
│   │   ├── app/                  Phases 0–1 C++ (mwcore + mwengine, CMake/CTest)
│   │   └── rllogger/             the C++ three-stream logger — the artifact behind the ADR
│   └── (sheets, docs)            planned — not created
└── pipeline/
    ├── design/                   what a knowledge base IS (schema, 3-level model, priority)
    ├── playbook/                 the steps the agent follows (goal · be-sure-of · proof)
    ├── toolbox/                  tool knowledge that compounds across apps
    ├── kernel/                   the only fixed code — schema writers + journal
    └── kb/                       produced knowledge bases (word-4tabs-v1 is the current one)
```

The vendored LibreOffice engine that `ms-word-native` used to contain has been **removed
from the tree and from git history** (~400 MB). Its decision record, research and logger
remain. See [docs/decisions/engine-rent-vs-own.md](docs/decisions/engine-rent-vs-own.md).

---

## Working on a specific piece

| Piece | Status | Entry point |
|---|---|---|
| **figma** | shipping | [envs/figma/CLAUDE.md](envs/figma/CLAUDE.md) |
| **ms-word** | shipping — Home done, Insert in progress | [envs/ms-word/CLAUDE.md](envs/ms-word/CLAUDE.md) |
| **ms-word-native** | superseded — read-only record | [envs/ms-word-native/CLAUDE.md](envs/ms-word-native/CLAUDE.md) |
| **pipeline** | produces a full KB; KB→env scaffold not built | [pipeline/README.md](pipeline/README.md) |

When the request is ambiguous about which piece, **ask** — don't assume.

### Working in ms-word (spec-kit)

`envs/ms-word/` carries its own `.specify/` workspace and `.claude/skills/` (the
`speckit-*` family). Spec-kit resolves paths from the project root, so when working on the
Word environment **start Claude Code from `envs/ms-word/`**, not from the repo root.
Everything else in this repo works from the root.

---

## Cross-environment conventions

- **Three-stream log contract**: every environment produces `raw[]` + `semantic[]` +
  `outcome{}`. The verifier reads `outcome.document` for end-state checks and `semantic[]`
  for the efficiency multiplier. See [docs/log-contract.md](docs/log-contract.md). This is
  the repo's central design constraint — see [docs/arc.md](docs/arc.md).
- **Own the model.** Any environment whose app has a real document format implements the
  document itself rather than renting an engine, because the semantic stream has to be
  tappable in code we own. [docs/decisions/engine-rent-vs-own.md](docs/decisions/engine-rent-vs-own.md).
- **Per-env session workflow**: feature-checklist + execution-map per environment,
  refreshed every session. See each environment's CLAUDE.md.
- **Branch strategy**: trunk-based, short-lived feature branches, PR per change. Branch
  name format: `<scope>/<short-slug>` (e.g. `feat/figma-fillgrad`).
- **Commit style**: see [.claude/skills/commit-style/SKILL.md](.claude/skills/commit-style/SKILL.md).
- **Helper-corpus reading**: NEVER read `envs/<X>/app-docs/helper/` blind — always go
  through that environment's `app-docs/helper/00-overview.md` first.
- **Documentation-first**: every new environment starts with research → filtered helper →
  architecture decision → implementation. See
  [.claude/skills/research-flow/SKILL.md](.claude/skills/research-flow/SKILL.md).

---
## Skills (repo-internal)

The skills under `.claude/skills/<name>/SKILL.md` encode **how to work in this repo**. Most are placeholders right now; the ones marked ACTIVE are ratified and should be invoked.

| Skill | Status | Trigger |
|---|---|---|
| `codex-fix-pipeline` | **ACTIVE** | Bug fix or feature development — audit → file → plan → codex review → implement → codex review → per-bug commits → push approval. Invoke at the start of any such task. |
| `research-flow` | placeholder | Starting a new app's documentation corpus (raw fetch → AI filter → committed helper) |
| `architecture-decision-flow` | placeholder | After research, before coding — picking stack, state shape, op set |
| `development-flow` | placeholder | Implementing a feature (feature-checklist → execution-map plan → TDD → session-end) |
| `session-end` | placeholder | At end of session — tick checklist, update execution-map, check task scope changes |
| `commit-style` | partial | Before any commit |
| `helper-blind-read-prevent` | active | Before reading any helper/ content |

---

## Decision-making guidelines

Behavioral guidelines for every agent working in this repo, derived from [Andrej Karpathy's notes on common LLM coding pitfalls](https://x.com/karpathy/status/2015883857489522876). Installed as the `andrej-karpathy-skills:karpathy-guidelines` skill — invoke it when writing, reviewing, or refactoring code. They bias toward caution over speed; for trivial tasks, use judgment.

1. **Think before coding.** State assumptions explicitly; if uncertain, ask. If multiple interpretations exist, present them — don't pick silently. If a simpler approach exists, say so and push back. If something is unclear, stop, name what's confusing, and ask.
2. **Simplicity first.** Write the minimum code that solves the problem — nothing speculative. No features beyond what was asked, no abstractions for single-use code, no unrequested "flexibility," no error handling for impossible scenarios. If 200 lines could be 50, rewrite it.
3. **Surgical changes.** Touch only what you must. Don't "improve" adjacent code, comments, or formatting; don't refactor what isn't broken; match existing style even if you'd do it differently. Remove only the imports/variables/functions your own changes orphaned — mention pre-existing dead code, don't delete it. Every changed line should trace directly to the request.
4. **Goal-driven execution.** Turn tasks into verifiable goals ("fix the bug" → "write a test that reproduces it, then make it pass"). For multi-step work, state a brief plan with a verify check per step, and loop until verified.

---

## When in doubt

1. The user's instructions in the conversation override anything in this file.
2. If asked about something that is per-environment, look at the environment's CLAUDE.md.
3. If asked about something cross-environment, look in `overview/` then `.claude/skills/<name>/SKILL.md`.
4. If you can't find an answer, ask. Don't fabricate paths or filenames.
