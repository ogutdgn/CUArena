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
│       ├── docs/architecture/    ROADMAP.md, PHASE3_LOGGER_DESIGN.md, PHASE4_*.md
│       ├── docs/USAGE.md         day-to-day commands (launching soffice, logs, export)
│       ├── rllogger/             three-stream event logger (raw / semantic / outcome)
│       └── sw/, sc/, sd/ ...     LibreOffice source modules (Writer / Calc / Impress + deps)
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

## When in doubt

1. The user's instructions in the conversation override anything in this file.
2. If asked about something that is per-app, look at the app's CLAUDE.md.
3. If asked about something cross-app, look in `overview/` then `.claude/skills/`.
4. If you can't find an answer, ask. Don't fabricate paths or filenames.
