# cua-bench — Repo-Root Agent Guide

You are working in `cua-bench`, a monorepo for CUA evaluation. There are **four apps** here (figma, sheets, docs, libreoffice); each is a CUA environment with its own logger + (where applicable) verifier + helper corpus. Cross-app conventions live at the repo root.

If you were dispatched to work on a single app, read that app's CLAUDE.md instead and treat this file as the wider context.

---

## Repo layout

```
cua-bench/
├── README.md                     repo intro
├── CLAUDE.md                     repo-root agent guide
├── AGENTS.md (this file)         mirror of CLAUDE.md (for Codex / other tooling)
├── overview/                     cross-app docs — read these for the big picture
│   ├── system-overview.md        the 3-app + log + verifier mental model
│   ├── log-contract.md           cross-app log schema (raw / semantic / outcome)
│   ├── conventions.md            commit / branch / session-end protocols
│   └── roadmap.md                sequencing + milestones
├── .claude/
│   ├── settings.json             permissions, hooks
│   └── skills/                   repo-internal skills (research, dev, commit, ...)
├── apps/
│   ├── figma/                    active — Figma Design mock + verifier
│   │   ├── CLAUDE.md             ← READ THIS when working on the figma app
│   │   ├── app-docs/             all docs (mock-doc/ + verifier-doc/ + scripts-doc/ + helper/)
│   │   ├── mock/
│   │   ├── verifier/             flat Python library (no __init__.py — namespace package)
│   │   ├── delivery-1/           50-task source of truth (prompt.md + verifier.py per task)
│   │   └── scripts/              CLI entry-points + logs/scores output
│   ├── sheets/                   planned — skeleton only
│   ├── docs/                     planned — skeleton only
│   └── libreoffice/              active — stripped LibreOffice fork (Writer + Calc + Impress)
│       │                          as a real-binary CUA runtime, instrumented with rllogger
│       ├── CLAUDE.md             ← READ THIS when working on the libreoffice app
│       ├── AGENTS.md             full project guide (workflow, build, gotchas)
│       ├── README.md             app entry point
│       ├── docs/architecture/    ROADMAP.md, PHASE3_LOGGER_DESIGN.md, PHASE4_*.md
│       ├── docs/USAGE.md         day-to-day commands (launching soffice, logs, export)
│       └── libreoffice-codebase/ vendored 143k-file LO tree + our LO-internal mods
│           ├── rllogger/         three-stream event logger (raw / semantic / outcome)
│           ├── sw/, sc/, sd/ ... LibreOffice source modules (Writer / Calc / Impress + deps)
│           ├── Makefile.in       build entry (cd here before running make)
│           └── instdir/, workdir/  build outputs (gitignored)
└── shared/                       future: extracted shared verifier framework
                                  (intentionally empty until a 2nd app is shipped)
```

Note: **libreoffice is shaped differently** from figma/sheets/docs — it's a real LibreOffice binary instrumented with a logger, not a TypeScript mock. No verifier yet (planned for a later phase). The three-stream log contract still applies (see [apps/libreoffice/docs/architecture/ROADMAP.md](apps/libreoffice/docs/architecture/ROADMAP.md)).

---

## Working on a specific app

For app-specific work, **start at the app's CLAUDE.md** — it is the source of truth for that app's architecture, document map, session workflow, and conventions:

| App | Status | Entry point |
|---|---|---|
| **figma** | active | [apps/figma/CLAUDE.md](apps/figma/CLAUDE.md) |
| **libreoffice** | active (Phase 4 done; logger V1.1) | [apps/libreoffice/CLAUDE.md](apps/libreoffice/CLAUDE.md) |
| **sheets** | planned | (skeleton not yet created) |
| **docs** | planned | (skeleton not yet created) |

When the user's request is ambiguous about which app, **ask** — don't assume.

---

## Cross-app conventions

These apply to every app in this repo:

- **Three-stream log contract**: every mock produces `raw[]` + `semantic[]` + `outcome{}`. The verifier reads `outcome.document` for end-state checks and `semantic[]` for the efficiency multiplier. See [overview/log-contract.md](overview/log-contract.md).
- **Per-app session workflow**: feature-checklist + execution-map per app, refreshed every session. See each app's CLAUDE.md.
- **Branch strategy**: trunk-based, short-lived feature branches, PR per change. Branch name format: `<scope>/<short-slug>` (e.g. `feat/figma-fillgrad`, `restructure/monorepo-skeleton`).
- **Commit style**: see [.claude/skills/commit-style.md](.claude/skills/commit-style.md).
- **Helper-corpus reading**: NEVER read `apps/<X>/app-docs/helper/` blind — always go through that app's `app-docs/helper/00-overview.md` first.
- **Documentation-first**: every new app starts with research → filtered helper → architecture decision → implementation. See [.claude/skills/research-flow.md](.claude/skills/research-flow.md).

---

## Skills (repo-internal)

The skills under `.claude/skills/` encode **how to work in this repo**. Most are placeholders right now; the ones marked ACTIVE are ratified and should be invoked.

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
2. If asked about something that is per-app, look at the app's CLAUDE.md.
3. If asked about something cross-app, look in `overview/` then `.claude/skills/`.
4. If you can't find an answer, ask. Don't fabricate paths or filenames.
