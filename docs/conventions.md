# Conventions

> **Status: SKELETON.** Sections are stubs to be filled as we settle on each convention. Today only the branch + commit basics are decided; the rest will be filled by `.claude/skills/*` and refined as we run the flows.

---

## Branch strategy

- Trunk-based: `main` is always shippable.
- Short-lived feature branches per change.
- Branch name format: `<scope>/<short-slug>` — e.g. `feat/figma-fillgrad`, `fix/sheets-formula-eval`, `restructure/monorepo-skeleton`, `docs/figma-architecture-refresh`.
- Open a PR for non-trivial changes; merge to `main` after self-review.
- Force-push only on your own branch, never on `main`.

## Commit style

The detailed protocol lives in [`.claude/skills/commit-style.md`](../.claude/skills/commit-style.md). High-level:
- Subject line: `<scope>: <imperative summary>` (e.g. `figma: add gradient fill`, `verifier: tighten polygon tolerance`).
- Stage files explicitly; do not blanket-add.
- One logical change per commit. If a refactor and a feature need to ship together, split them and commit in order.

## Per-session protocol

Detailed in [`.claude/skills/session-end.md`](../.claude/skills/session-end.md).

At session start, for figma work: `envs/figma/app-docs/feature-checklist.md` + `execution-map.md` are the inputs. Plan the wave, write a session entry.

At session end:
- Tick newly-shipped items in the relevant app's `feature-checklist.md`.
- Add a top-of-log entry to that app's `execution-map.md` describing what shipped.
- Delete completed items from the lower plan (the session log is the record).
- If a feature shipped that unlocks a new task scope, update the relevant `tasks.csv`.

## Documentation rules

- Every app must keep its `CLAUDE.md` synchronized with `AGENTS.md` (Codex/other tooling reads the latter). If you edit one, mirror to the other.
- New cross-environment rules go in `docs/`, not in any single app's docs.
- Skills go in `.claude/skills/` and are placeholders until their first run, then filled.
- Helper corpora are read through their `00-overview.md` only — see [`.claude/skills/helper-blind-read-prevent.md`](../.claude/skills/helper-blind-read-prevent.md).

## Multi-agent usage

Detailed protocol TBD. High-level intent (subject to refinement):
- **Claude Code**: planning, search, execution, file writes.
- **Codex**: review, bug finding, architecture critique, second-opinion implementation passes.
- **Superpowers skills**: process scaffolding (brainstorming, TDD, debugging, planning, finishing).
- Avoid running multiple writing agents in parallel against the same files.
