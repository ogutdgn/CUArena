# CLAUDE.md

> Context file for Claude Code (and other Anthropic Claude-based
> agents) working in this repo. This file is **short**. All real
> project guidance lives in [`AGENTS.md`](AGENTS.md).

---

## Read this first

1. **[`docs/last-point.md`](docs/last-point.md)** — what's shipped on
   `main` right now. Read this first to know the current state.
2. **[`docs/execution-map.md`](docs/execution-map.md)** — what's
   queued next. Read this second to know what to work on.
3. **[`AGENTS.md`](AGENTS.md)** — full project context, workflow,
   build steps, conventional commits, known gotchas.
4. **[`docs/architecture/ROADMAP.md`](docs/architecture/ROADMAP.md)** —
   canonical plan for all phases + decision log.
5. **[`docs/USAGE.md`](docs/USAGE.md)** — day-to-day operational
   commands (launching soffice, inspecting logs, exporting).
6. Then start the task.

The first two files are auto-maintained by the `update-last-point`
and `update-execution-map` skills — refresh them after big changes
and at session end.

---

## Project in one sentence

A **LibreOffice fork** being trimmed down to Writer + Calc + Impress
as a runtime environment for RL agents. Owner does UI editing work
on the `dev` branch. Discipline: **build-driven** — every change
goes through a build verification; the plan-driven approach was
abandoned.

---

## Current state: Phase 3 logger V1.1 integrated

A `rllogger/` module has been merged into `dev`. The moment you
launch soffice, it logs everything in the background — for Writer:
key/mouse events, every `.uno:*` dispatch (args + trigger + gesture
range), and a document snapshot every 250 ms (cursor + selection +
format-at-cursor).

- **On by default**, no env var needed. Logs go to `~/.lo-rl-logs/<sessionId>/`
- `LO_RL_LOG_DIR=/path` redirects (CI / tests)
- `LO_RL_LOG_DISABLE=1` zero-overhead opt-out
- Consumer side: `rllogger/util/rllogger-export.py <sessionDir> -o out.json` → single packaged session.json

Full contract: [`AGENTS.md`](AGENTS.md) §4.3.
Design + verification: [`docs/architecture/PHASE3_LOGGER_DESIGN.md`](docs/architecture/PHASE3_LOGGER_DESIGN.md).
Day-to-day commands: [`docs/USAGE.md`](docs/USAGE.md).

Typical logger-change smoke test (run from `apps/libreoffice/libreoffice-codebase/`):

```sh
cd apps/libreoffice/libreoffice-codebase
rm -rf /tmp/rl-test && LO_RL_LOG_DIR=/tmp/rl-test \
  instdir/program/soffice --writer --norestore
# Do a few things in Writer, close it
SESSION=$(ls -t /tmp/rl-test | head -1)
cat /tmp/rl-test/$SESSION/semantic.jsonl
cat /tmp/rl-test/$SESSION/outcome.jsonl
```

`make rllogger desktop` (from inside `libreoffice-codebase/`) is enough for
incremental rebuild (sofficemain links rllogger, so desktop also needs to
relink; sw/sc/sd do not).

---

## Claude-specific rules

### 1. Never use `Co-Authored-By: Claude` in commits

Owner asked for this explicitly. Deviate from default Claude Code
commit behavior. Do **not** add anything Claude-related to the
footer. The message is just the conventional-commit body.

If you accidentally make such a commit: if not pushed yet,
`git commit --amend`. If pushed, tell the owner and decide together.

### 2. Conventional Commits

Format: `<type>(<scope>): <subject>` — details in [`AGENTS.md`](AGENTS.md) §8.

### 3. Build-error discipline

When you see a LibreOffice build error:

- **Read the context first** — the full error message, which step,
  which module.
- **Don't rush to commit** — keep things reversible.
- **Check whether the same error showed up on prior branches** —
  `chore/strip-...` and `refactor/apps-core-folder-split` may have
  hit it.
- After fixing: `make sw sc sd` incremental rebuild + smoke test.
  Commit only if green.

### 4. Skill usage

- **`keep-docs-in-sync`** (project skill, `.claude/skills/`) —
  mandatory after every plan / contract / structural change. Update
  the docs in the **same commit** as the code; never leave a
  "docs catch-up" PR pending. Past drift has always slipped; this
  skill structures the checklist.
- `superpowers:systematic-debugging` → when investigating a build /
  runtime error.
- `superpowers:test-driven-development` → when writing a new
  feature / bugfix. CppUnit tests are available
  (`make sw.check`, etc.).
- `superpowers:verification-before-completion` → before declaring
  "done, it works", actually run the smoke test command.

### 5. Workflow loop

After the cua-bench import, branches live in the cua-bench repo (not the
old libreoffice-core-rl-env fork). Work happens on short-lived feature
branches off cua-bench `main`, scoped to `feat/libreoffice-*` or
`fix/libreoffice-*`. The build itself runs from inside
`apps/libreoffice/libreoffice-codebase/` — that's where Makefile.in,
autogen.sh, configure.ac, and the entire vendored LO tree live. Docs
(this file, AGENTS.md, docs/) are one level up at `apps/libreoffice/`.

```sh
# At the repo root (cua-bench), sync first:
git pull origin main

# Move into the vendored LO tree (where soffice / make expect to be):
cd apps/libreoffice/libreoffice-codebase

# Edit (if any — Phase 4 UI work lives in sw/, logger in rllogger/):
vim sw/source/uibase/...

# Build (in WSL — Windows checkout is edit-mirror only):
make sw sc sd

# Smoke test:
instdir/program/soffice --writer

# Commit (back at cua-bench root so the diff is rooted there):
cd ../../..
git add apps/libreoffice
git commit -m "feat(libreoffice): ..."
git push origin <your-feature-branch>
```

Do not start the next change without seeing the build pass.

### 6. Local environment awareness

This project lives as **one app inside the `cua-bench` monorepo**:

- Claude (Windows): `c:/Users/ogutd/OneDrive/Desktop/new-coding/cua-bench/apps/libreoffice/libreoffice-codebase` (build runs here; docs are one level up at `apps/libreoffice/`)
- Owner (WSL Ubuntu): `/home/ogutd/lo-dev` (or similar — kept separate from the cua-bench checkout to avoid OneDrive sync churn during builds)
- GitHub: source of truth is now [`ogutdgn/cua-bench`](https://github.com/ogutdgn/cua-bench) (private repo). The old standalone `ogutdgn/libreoffice-core-rl-env` fork is **frozen as a baseline archive** — it has the full Phase 1/3/4 commit history that wasn't carried over in the import. Code archaeology (`git blame`, when-was-this-changed) for pre-import lines should consult that repo.
- Builds happen **on the WSL Linux fs**; `/mnt/c` is slow and OneDrive doubles that cost

Claude can dispatch commands into WSL via `wsl -e bash -lc "..."`.
Strip mingw64 from PATH or configure mistakes WSL for a "wsl-as-helper"
build:

```sh
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

### 7. Memory vs. these files

Don't re-record rules that already live in these files into memory.

Things **not** to keep in memory:
- Workflow / convention info already written in these files
- Decisions on past plan documents (they live on `chore/strip...`
  and `refactor/apps-core-folder-split`)

Things to keep in memory:
- The owner's changing preferences / new feedback
- Useful context that isn't in these files and may matter later

---

## About the user

- Single-person project owner (`@ogutdgn`).
- Speaks Turkish + English mixed; **reply in Turkish for Turkish
  questions** even though project docs are English.
- Wants **trade-offs stated explicitly** on engineering decisions —
  not blind agreement.
- Said "don't try to convince me" — push back with a counter-view
  when warranted.
- Tolerant of long analysis documents (e.g.
  [`docs/architecture/WRITER_CALC_EXTRACTION.md`](docs/architecture/WRITER_CALC_EXTRACTION.md)).
- Dislikes "authored by Claude" / AI-attribution wording.

---

## Prior work — reminder

Two paused branches exist on GitHub:

- `chore/strip-to-writer-calc-impress` — 16 commits, ~5900 files
  deleted (peer apps, language bridges, mobile, etc.). Build was
  not verified, manifest fixes may be incomplete. **Don't
  cherry-pick** — reference only.
- `refactor/apps-core-folder-split` — 6 commits on top of the above;
  sw/sc/sd moved to `apps/`, ~91 modules to `core/`. Build never
  fully greened (suppression files, stale workdir, etc.). Same:
  **no cherry-picking, reference only**.

On `dev` we redo these incrementally and build-verified. Plan in
[`docs/architecture/ROADMAP.md`](docs/architecture/ROADMAP.md).
