# LibreOffice Codebase Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reshape `apps/libreoffice/` so that the vendored LibreOffice fork (143,302 source files) lives inside a clearly-labelled `libreoffice-codebase/` subdirectory, while our project-specific docs (`CLAUDE.md`, `AGENTS.md`, `docs/`, `.claude/`) sit at the app root next to a fresh app-entry `README.md`. Same workflow as figma's `apps/figma/{mock,verifier,app-docs,...}` shape.

**Architecture:** Pure refactor — no functional change. `git mv` (or `mv` + rename detection) for all 143k entries except 4 doc paths. Build commands gain a one-line `cd libreoffice-codebase/` prefix; nothing in the LO build system needs editing because LO's gbuild is location-agnostic relative to its own root. Cross-app docs (`overview/*.md`) gain a 4th-app row.

**Tech Stack:** git mv, bash, WSL ext4 filesystem, no language additions.

---

## Where this runs

WSL at `~/cua-bench-lo`. The Windows checkout at `C:\Users\ogutd\OneDrive\Desktop\new-coding\cua-bench` is currently behind origin/main; we sync it at the very end (or the user re-clones). All operations in this plan are WSL-side to avoid Windows autocrlf + executable-bit + gitignore-filtering issues we hit on the initial import.

## File structure decision

The "apps/libreoffice/ top level should host the app-entry docs (figma's pattern), and the vendored LO sits in libreoffice-codebase/" rule means exactly these 4 paths stay at the app root after the refactor:

- `apps/libreoffice/CLAUDE.md` — entry-point agent guide (ours)
- `apps/libreoffice/AGENTS.md` — full project guide / Codex mirror (ours)
- `apps/libreoffice/docs/` — architecture, USAGE, all our markdown (ours)
- `apps/libreoffice/.claude/` — app-level skills directory (ours)

A new `apps/libreoffice/README.md` is written (our app-entry README; LO's original README.md ends up at `apps/libreoffice/libreoffice-codebase/README.md`).

Everything else from the 190 top-level entries moves to `apps/libreoffice/libreoffice-codebase/`:
- 23 LO doc/license files (BUCK, COPYING*, Makefile*, README.*, Repository*, TEMPLATE.*)
- 15 build infrastructure (autogen.sh, autogen.lastrun*, config.{guess,sub,log,status,warn}, config_host*, configure*, install-sh, instdir, workdir, autom4te.cache, sources.ver, vs-code.code-workspace.template, hardened_runtime.xcent, lo.xcent)
- 130+ LO source modules (UnoControls, animations, basegfx, basic, ..., wizards, writerperfect, xml*)
- 15 dotfiles (.buckconfig, .clang-format, .config, .cspell, .editorconfig, .git-blame-ignore-revs, .git-hooks, .gitattributes, .github, .gitignore, .gitmodules, .gitpod*, .gitreview, .vscode, .vsconfig)
- Our LO-internal additions that must live inside the LO build tree:
  - `rllogger/` (Phase 3 logger module)
  - `sources.ver` (build-unblocker)
  - `config.guess`, `config.sub`, `install-sh` (autotools aux)
  - All restored gitignored files (`.vscode/license.code-snippets`, etc.)

## Files modified beyond the moves

These existing files get content edits in this refactor (path references, layout diagrams, app-row additions):

**Inside apps/libreoffice/ (our docs, paths inside LO change to use libreoffice-codebase/ prefix):**
- `apps/libreoffice/CLAUDE.md` §5 (workflow loop) and §6 (paths)
- `apps/libreoffice/AGENTS.md` §1 (Home), §5 (Environment), §6 (build commands)
- `apps/libreoffice/docs/USAGE.md` (launch commands)
- `apps/libreoffice/docs/architecture/ROADMAP.md` (no path edits needed; review)

**Inside cua-bench root (cross-app docs to mention 4th app + new shape):**
- `README.md` — repo intro tree + status table
- `CLAUDE.md` — repo-root agent guide tree + app table
- `AGENTS.md` — mirror of CLAUDE.md
- `overview/system-overview.md` — 4-app mental model, real-binary vs TS mock
- `overview/log-contract.md` — note that libreoffice's rllogger emits the same three-stream contract
- `overview/roadmap.md` — add libreoffice's Phase 5 (Calc), Phase 6 (Impress), Phase 7 (Docker)

**New files created:**
- `apps/libreoffice/README.md` (app entry point — what's inside, how to build, where to read first)

---

## Task 1: Sync main + create feature branch

**Files:**
- (none — git state)

- [ ] **Step 1: Verify WSL cua-bench-lo is on main and clean**

Run: `cd ~/cua-bench-lo && git status && git branch --show-current`
Expected: `On branch main` + `nothing to commit, working tree clean`

- [ ] **Step 2: Pull latest main**

Run: `git pull origin main`
Expected: `Already up to date.` (or a fast-forward — accept either)

- [ ] **Step 3: Create feature branch**

Run: `git checkout -b refactor/libreoffice-codebase-split`
Expected: `Switched to a new branch 'refactor/libreoffice-codebase-split'`

- [ ] **Step 4: Tag rollback point (safety net)**

Run: `git tag pre-refactor-libreoffice-split`
(Local tag only — not pushed. Allows `git reset --hard pre-refactor-libreoffice-split` if anything goes very wrong.)

---

## Task 2: Move 186 top-level entries into libreoffice-codebase/

**Files:**
- Create: `apps/libreoffice/libreoffice-codebase/` (new directory holding everything below)
- Move: all entries except CLAUDE.md, AGENTS.md, docs/, .claude/

- [ ] **Step 1: cd into apps/libreoffice and create the new container**

Run:
```bash
cd ~/cua-bench-lo/apps/libreoffice
mkdir libreoffice-codebase
ls -1A | wc -l   # should show 190 (before move)
```

- [ ] **Step 2: Move everything using bash extglob (one big mv per entry-class)**

Run:
```bash
shopt -s dotglob extglob
mv !(libreoffice-codebase|CLAUDE.md|AGENTS.md|docs|.claude) libreoffice-codebase/
shopt -u dotglob extglob
```

Expected: command completes silently; `libreoffice-codebase/` now contains 186 entries; apps/libreoffice/ top has 5 entries (CLAUDE.md, AGENTS.md, docs, .claude, libreoffice-codebase).

- [ ] **Step 3: Verify the structure**

Run:
```bash
ls -1A ~/cua-bench-lo/apps/libreoffice
echo '---libreoffice-codebase count:'
ls -1A ~/cua-bench-lo/apps/libreoffice/libreoffice-codebase | wc -l
```
Expected:
- Top level shows: `AGENTS.md`, `CLAUDE.md`, `docs`, `.claude`, `libreoffice-codebase`
- libreoffice-codebase count: 186

- [ ] **Step 4: Verify build infrastructure landed in libreoffice-codebase/**

Run:
```bash
ls ~/cua-bench-lo/apps/libreoffice/libreoffice-codebase/autogen.sh \
   ~/cua-bench-lo/apps/libreoffice/libreoffice-codebase/Makefile.in \
   ~/cua-bench-lo/apps/libreoffice/libreoffice-codebase/rllogger/Module_rllogger.mk \
   ~/cua-bench-lo/apps/libreoffice/libreoffice-codebase/sw/Module_sw.mk \
   ~/cua-bench-lo/apps/libreoffice/libreoffice-codebase/sources.ver
```
Expected: all five paths exist (no "No such file").

- [ ] **Step 5: Raise git rename-detection limit (143k entries default 1000 — too low)**

Run:
```bash
cd ~/cua-bench-lo
git config diff.renameLimit 200000
git config merge.renameLimit 200000
```
(Repo-local config; the defaults are too small for this scale and would cause renames to look like delete+create in diffs.)

- [ ] **Step 6: git status preview (heavy output expected)**

Run: `git status --short | head -20`
Expected: many `R  apps/libreoffice/<old> -> apps/libreoffice/libreoffice-codebase/<old>` rename entries (git auto-detects). Or `D` + `??` pairs if rename detection didn't fire yet. Either is fine — `git add -A` will resolve.

- [ ] **Step 7: Stage moves**

Run: `git add -A apps/libreoffice/`
This will take 1-3 minutes on 143k entries.

- [ ] **Step 8: Verify staging shows rename, not delete+create**

Run: `git diff --cached --stat | tail -5`
Expected: total file count delta minimal (a few — mostly just our subsequent edits). If it shows many "create mode" / "delete mode" pairs instead of renames, rename detection still failed; revisit by re-adding with even higher diff.renameLimit.

- [ ] **Step 9: Commit the rename-only step**

Run:
```bash
git commit -m "refactor(libreoffice): move LO codebase under apps/libreoffice/libreoffice-codebase/

Pure file move. CLAUDE.md, AGENTS.md, docs/, .claude/ stay at apps/libreoffice/
root (our app-entry docs). Everything else (143k LO sources + build files +
our LO-internal mods like rllogger/ and sources.ver) goes one level deeper.

This aligns the libreoffice app with figma's apps/figma/{mock,verifier,app-docs}
shape so a reader landing in apps/libreoffice/ sees our entry-point docs
first, not 143k LO files.

No path references updated in this commit — done in the next commit so
this one stays a clean rename for git blame/log."
```

---

## Task 3: Update path references in our libreoffice docs

**Files:**
- Modify: `apps/libreoffice/CLAUDE.md` §5 workflow block, §6 environment paths
- Modify: `apps/libreoffice/AGENTS.md` §1 Home, §5 Environment, §6 build commands
- Modify: `apps/libreoffice/docs/USAGE.md` (all `instdir/program/soffice` references)

- [ ] **Step 1: Read CLAUDE.md §5 (current state) so we know what to edit**

Run: `sed -n '108,128p' ~/cua-bench-lo/apps/libreoffice/CLAUDE.md`
Expected output shows the current workflow with `cd apps/libreoffice` then `make sw sc sd` from there. We will add one more `cd libreoffice-codebase` so make runs from the LO root.

- [ ] **Step 2: Edit CLAUDE.md §5 workflow block**

Replace the workflow inside §5:

Old:
```sh
# Move into the libreoffice app sub-tree:
cd apps/libreoffice

# Edit (if any):
vim sw/source/uibase/...

# Build (in WSL — Windows checkout is edit-mirror only):
make sw sc sd

# Smoke test:
instdir/program/soffice --writer

# Commit (back at cua-bench root so the diff is rooted there):
cd ../..
git add apps/libreoffice
```

New:
```sh
# Move into the libreoffice app — then into the vendored LO tree where make runs:
cd apps/libreoffice/libreoffice-codebase

# Edit (if any):
vim sw/source/uibase/...

# Build:
make sw sc sd

# Smoke test:
instdir/program/soffice --writer

# Commit (back at cua-bench root so the diff is rooted there):
cd ../../..
git add apps/libreoffice
```

- [ ] **Step 3: Edit CLAUDE.md §6 path**

Find: `Claude (Windows): c:/Users/ogutd/OneDrive/Desktop/new-coding/cua-bench/apps/libreoffice`
Replace with: `Claude (Windows): c:/Users/ogutd/OneDrive/Desktop/new-coding/cua-bench/apps/libreoffice/libreoffice-codebase (build runs here; docs are one level up at apps/libreoffice/)`

- [ ] **Step 4: Edit AGENTS.md path references**

Run `grep -n 'apps/libreoffice' ~/cua-bench-lo/apps/libreoffice/AGENTS.md` to find every reference. For each one where the path describes a BUILD location (running `make`, looking at `instdir/`, `sw/source/...`), append `/libreoffice-codebase`. References to docs (`docs/architecture/...`) stay as-is because docs are at the app root.

Specifically:
- §1 "Home" sentence — leave the GitHub URL alone, add note that the build root is libreoffice-codebase/
- §5 "IDE: ... sees /mnt/c/.../cua-bench/apps/libreoffice" → `.../cua-bench/apps/libreoffice/libreoffice-codebase` (build view) + add a line that docs are one level up
- §6 "First-time setup" block: `cd lo-dev/apps/libreoffice` → `cd lo-dev/apps/libreoffice/libreoffice-codebase`
- §6 "Iteration patterns" block: `(cd ../..; git pull origin main)` → `(cd ../../..; git pull origin main)` (one extra level up)

- [ ] **Step 5: Edit docs/USAGE.md**

Run `grep -n 'instdir/program/soffice\|apps/libreoffice' ~/cua-bench-lo/apps/libreoffice/docs/USAGE.md` to find references. Update any absolute-from-app-root paths to include `/libreoffice-codebase` segment. If USAGE.md uses relative paths like `instdir/program/soffice` assumed to run from a `cd` context, those don't need editing — add a top note like "All commands below assume cwd = `apps/libreoffice/libreoffice-codebase/`. cd there first."

- [ ] **Step 6: Verify edits don't leave stale references**

Run:
```bash
grep -rn 'apps/libreoffice/[a-z]' ~/cua-bench-lo/apps/libreoffice/CLAUDE.md \
                                   ~/cua-bench-lo/apps/libreoffice/AGENTS.md \
                                   ~/cua-bench-lo/apps/libreoffice/docs/ 2>/dev/null \
  | grep -v 'libreoffice-codebase\|apps/libreoffice/docs\|apps/libreoffice/CLAUDE\|apps/libreoffice/AGENTS\|apps/libreoffice/README' \
  | head -20
```
Expected: no output, or only references that are correctly NOT under libreoffice-codebase (e.g., `apps/libreoffice/docs/architecture/...`). Sanity check.

- [ ] **Step 7: Commit path updates**

Run:
```bash
cd ~/cua-bench-lo
git add apps/libreoffice/CLAUDE.md apps/libreoffice/AGENTS.md apps/libreoffice/docs/
git commit -m "docs(libreoffice): update path references for libreoffice-codebase/ split

Build commands now require an extra cd into libreoffice-codebase/. Doc-only
edit; no code change."
```

---

## Task 4: Write the new apps/libreoffice/README.md (app entry point)

**Files:**
- Create: `apps/libreoffice/README.md` (new file)

- [ ] **Step 1: Write the file**

Create at `~/cua-bench-lo/apps/libreoffice/README.md` with this content:

```markdown
# libreoffice — stripped LibreOffice fork as a CUA runtime

Real-binary CUA environment. Writer / Calc / Impress, instrumented with the [rllogger](libreoffice-codebase/rllogger/) module that emits a three-stream raw/semantic/outcome log per session (same contract as figma's TS mock — see [../../overview/log-contract.md](../../overview/log-contract.md)).

## What's where

| Path | What |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Claude-specific agent guide — read first when working here |
| [AGENTS.md](AGENTS.md) | Full project guide (workflow, build, conventions, gotchas) |
| [docs/architecture/ROADMAP.md](docs/architecture/ROADMAP.md) | Canonical phase plan + decision log |
| [docs/USAGE.md](docs/USAGE.md) | Day-to-day commands (launch, logs, export) |
| [libreoffice-codebase/](libreoffice-codebase/) | Vendored LibreOffice fork (143k files) + our LO-internal additions ([rllogger/](libreoffice-codebase/rllogger/), Phase 4 UI mods in [sw/](libreoffice-codebase/sw/), build aux files) |

## Build (WSL ext4 only — never on /mnt/c)

```sh
cd apps/libreoffice/libreoffice-codebase
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
./autogen.sh --without-java --without-help --disable-xmlhelp \
    --disable-libcmis --disable-firebird-sdbc --disable-postgresql-sdbc \
    --disable-mariadb-sdbc --disable-online-update --disable-extension-update \
    --disable-pdfimport --disable-librelogo --disable-opencl
make
instdir/program/soffice --writer
```

Full first build: ~3 h cold, ~30 min if external/tarballs is pre-populated. `make sw sc sd` for incremental.

## Status

Phase 4 done (Writer UI parity with MS Word). Phase 3 logger V1.1 default-on. Calc + Impress equivalents (Phases 5-6) and Docker distribution (Phase 7) pending. See [docs/architecture/ROADMAP.md](docs/architecture/ROADMAP.md).
```

- [ ] **Step 2: Commit**

Run:
```bash
cd ~/cua-bench-lo
git add apps/libreoffice/README.md
git commit -m "docs(libreoffice): add app-entry README.md

Pointer doc at the apps/libreoffice/ level (figma's pattern) summarizing
what lives where + the minimal build invocation. LO's own README.md stays
at libreoffice-codebase/README.md."
```

---

## Task 5: Update cua-bench root docs (README, CLAUDE, AGENTS) for the new shape

**Files:**
- Modify: `README.md` (cua-bench root)
- Modify: `CLAUDE.md` (cua-bench root)
- Modify: `AGENTS.md` (cua-bench root)

- [ ] **Step 1: Update README.md tree diagram and status table**

Open `~/cua-bench-lo/README.md`. Replace the existing tree diagram and status table.

New tree (preserve existing comments style):
```
cua-bench/
├── apps/
│   ├── figma/        Figma Design mock + verifier         (active — TypeScript mock)
│   ├── sheets/       Google Sheets mock + verifier        (planned)
│   ├── docs/         Google Docs mock + verifier          (planned)
│   └── libreoffice/  LibreOffice fork (Writer/Calc/Impress) + rllogger
│       ├── CLAUDE.md / AGENTS.md / docs/  app-entry docs
│       ├── README.md                       app intro
│       └── libreoffice-codebase/           vendored 143k-file LO tree + our mods
├── overview/         Cross-app docs (system overview, log contract, conventions, roadmap)
├── shared/           Future home for the extracted shared verifier framework
└── .claude/          Repo-internal skills + settings (commit, session-end, research, ...)
```

Add a "Working on the libreoffice app?" bullet to the "Where to start" section pointing to [apps/libreoffice/README.md](apps/libreoffice/README.md), [apps/libreoffice/CLAUDE.md](apps/libreoffice/CLAUDE.md), [apps/libreoffice/docs/architecture/ROADMAP.md](apps/libreoffice/docs/architecture/ROADMAP.md).

Add a libreoffice row to the Status table:

| App | Shape | Mock / Runtime | Verifier | Tasks |
|---|---|---|---|---|
| figma | TS mock | shipping | shipping | 50 |
| libreoffice | real binary | Phase 4 done (Writer UI parity); logger V1.1; Calc/Impress pending | not started | — |
| sheets | TS mock | not started | not started | — |
| docs | TS mock | not started | not started | — |

- [ ] **Step 2: Update CLAUDE.md tree diagram and app table**

Open `~/cua-bench-lo/CLAUDE.md`. Change the opening sentence from "three apps" to "four apps".

Update the repo layout block under `apps/` to include libreoffice with the new shape:

```
├── apps/
│   ├── figma/                    active — Figma Design mock + verifier
│   │   ├── CLAUDE.md             ← READ THIS when working on the figma app
│   │   └── ... (existing figma subtree)
│   ├── sheets/                   planned — skeleton only
│   ├── docs/                     planned — skeleton only
│   └── libreoffice/              active — stripped LibreOffice fork (Writer + Calc + Impress)
│       │                          as a real-binary CUA runtime, instrumented with rllogger
│       ├── CLAUDE.md             ← READ THIS when working on the libreoffice app
│       ├── AGENTS.md             full project guide (workflow, build, gotchas)
│       ├── README.md             app entry point
│       ├── docs/                 architecture/ROADMAP.md, PHASE3_*.md, PHASE4_*.md, USAGE.md
│       └── libreoffice-codebase/ vendored 143k-file LO tree + Phase 4 mods in sw/ + rllogger/
```

Add a libreoffice row to the "Working on a specific app" table:

| App | Status | Entry point |
|---|---|---|
| **figma** | active | [apps/figma/CLAUDE.md](apps/figma/CLAUDE.md) |
| **libreoffice** | active (Phase 4 done; logger V1.1) | [apps/libreoffice/CLAUDE.md](apps/libreoffice/CLAUDE.md) |
| **sheets** | planned | (skeleton not yet created) |
| **docs** | planned | (skeleton not yet created) |

Add a note: "libreoffice is shape-different from the TS mock apps — it's a real Linux binary built from a vendored fork. The cross-app three-stream log contract still applies via its rllogger module."

- [ ] **Step 3: Update AGENTS.md (mirror of CLAUDE.md)**

AGENTS.md is the Codex-compatible mirror. Apply the identical changes from Step 2 to `~/cua-bench-lo/AGENTS.md`.

- [ ] **Step 4: Commit**

Run:
```bash
cd ~/cua-bench-lo
git add README.md CLAUDE.md AGENTS.md
git commit -m "docs(repo-root): reflect 4-app layout with libreoffice + libreoffice-codebase/ split

Tree diagrams, status tables, and app-routing tables now show:
- libreoffice as the 4th app (real binary, not TS mock)
- The apps/libreoffice/libreoffice-codebase/ vendored-fork shape
- A 'where to read first' pointer for libreoffice-app work"
```

---

## Task 6: Update cua-bench overview/*.md (cross-app conceptual docs)

**Files:**
- Modify: `overview/system-overview.md` (mental model — 3 apps → 4)
- Modify: `overview/log-contract.md` (note rllogger emits the same contract)
- Modify: `overview/roadmap.md` (add libreoffice phases)
- Read-only: `overview/conventions.md` (commit/branch rules — likely no change needed; skim and skip if applies as-is to libreoffice too)

- [ ] **Step 1: Read all four overview/ files first to know current shape**

Run:
```bash
ls ~/cua-bench-lo/overview/
wc -l ~/cua-bench-lo/overview/*.md
```
Then `cat` each one to understand what it says about "the 3 apps" so we can extend rather than replace.

- [ ] **Step 2: Update overview/system-overview.md**

Find the mental-model paragraph or diagram that lists 3 apps. Add libreoffice as the 4th with a clear note about its different shape:

"libreoffice is a real Linux binary (a stripped LibreOffice fork — Writer / Calc / Impress) rather than a TypeScript browser mock like the other three. The three-stream log contract (raw/semantic/outcome) still applies because its rllogger module emits the same shape; this means a verifier built for figma's log shape will work against libreoffice's logs with at most a CommandMap remap."

- [ ] **Step 3: Update overview/log-contract.md**

Find the section that describes how each app's logger emits the contract. Add a libreoffice subsection (or paragraph) noting:
- raw.jsonl: VCL key/mouse/focus events
- semantic.jsonl: .uno:* dispatches mapped to RL-friendly names with args + trigger + rawEventIdRange
- outcome.jsonl: doc URL, modified flag, counts, cursor, selection, format-at-cursor (rewritten every 250ms)
- Default base dir: `~/.lo-rl-logs/` (Linux/macOS) or `%LOCALAPPDATA%/lo-rl-logs/` (Windows). `LO_RL_LOG_DIR` overrides. `LO_RL_LOG_DISABLE=1` disables.

- [ ] **Step 4: Update overview/roadmap.md**

Add the libreoffice phases (Phase 5: Calc logger + UI parity vs Excel; Phase 6: Impress + PowerPoint; Phase 7: Docker multi-stage image bundling instdir/ as the deliverable). Mark Phases 1-4 as done.

- [ ] **Step 5: Skim conventions.md to see if anything needs adapting**

Run: `cat ~/cua-bench-lo/overview/conventions.md`

If it mentions "3 apps" or has any branch-name format that excludes libreoffice scopes, update. Otherwise skip — conventions usually apply uniformly.

- [ ] **Step 6: Commit overview/ updates**

Run:
```bash
cd ~/cua-bench-lo
git add overview/
git commit -m "docs(overview): add libreoffice as 4th app to cross-app docs

system-overview: 4-app mental model + real-binary vs TS-mock note
log-contract: libreoffice rllogger emits same raw/semantic/outcome shape
roadmap: libreoffice Phases 5-7 added (Calc, Impress, Docker)"
```

---

## Task 7: Build verification — does the refactor break anything?

**Files:**
- (none modified — pure verification)

- [ ] **Step 1: External tarballs symlink (skip 5+ GB download)**

Run:
```bash
cd ~/cua-bench-lo/apps/libreoffice/libreoffice-codebase
rm -rf external/tarballs 2>/dev/null
ln -s ~/lo-dev/external/tarballs external/tarballs
ls -la external/tarballs
```
Expected: symlink pointing to ~/lo-dev/external/tarballs.

- [ ] **Step 2: Clear stale configure state (just to be safe)**

Run:
```bash
rm -f config_host.mk config_host.mk.stamp config.log config.status Makefile
```
(We're not nuking workdir — too expensive — just the per-configure outputs. If workdir got corrupted by the path-prefix change we'll find out at make time.)

- [ ] **Step 3: Run autogen.sh + configure**

Run:
```bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
./autogen.sh --without-java --without-help --disable-xmlhelp --disable-libcmis \
    --disable-firebird-sdbc --disable-postgresql-sdbc --disable-mariadb-sdbc \
    --disable-online-update --disable-extension-update \
    --disable-pdfimport --disable-librelogo --disable-opencl 2>&1 | tail -25
```
Expected: no "error:" lines; final block ends with "To just build, run: /usr/bin/make"; `config_host.mk` exists at end.

- [ ] **Step 4: Run incremental make (sw + sc + sd — Writer/Calc/Impress modules)**

Run:
```bash
make sw sc sd 2>&1 | tail -15
```
Expected: exits 0; last few lines say `[build BIN] sw` / `[build BIN] sc` / `[build BIN] sd`. If full make was needed (workdir nuked), do `make` instead — will take longer (~30 min with pre-cached tarballs).

- [ ] **Step 5: Smoke test soffice --version**

Run:
```bash
instdir/program/soffice --version
```
Expected: `LibreOfficeDev 26.8.0.0.alpha0 <commit-hash>` plus an `rllogger: session ... active` line above it. Both lines must appear.

- [ ] **Step 6: Inspect logger session it created**

Run:
```bash
SESSION=$(ls -t ~/.lo-rl-logs | head -1)
echo "Session: $SESSION"
ls ~/.lo-rl-logs/$SESSION/
wc -l ~/.lo-rl-logs/$SESSION/*.jsonl
```
Expected: a session directory with raw.jsonl, semantic.jsonl, outcome.jsonl. `--version` alone won't generate many events but the files should exist.

---

## Task 8: Push and offer merge

**Files:**
- (none — git operations)

- [ ] **Step 1: Final status check**

Run:
```bash
cd ~/cua-bench-lo
git status
git log --oneline -10
```
Expected: clean working tree, branch is refactor/libreoffice-codebase-split with 5 commits ahead of main (Tasks 2-6 each commit + initial).

- [ ] **Step 2: Push to origin**

Run: `git push -u origin refactor/libreoffice-codebase-split`
Expected: branch pushed; tracking set up.

- [ ] **Step 3: Hand off to user for merge decision**

Stop here. Tell the user:
- Branch pushed: `refactor/libreoffice-codebase-split`
- 5+ commits ahead of main
- Build verified end-to-end in WSL (autogen + make sw sc sd + soffice --version + logger session created)
- They choose: (a) GitHub PR for audit trail, or (b) direct FF/merge from local

**DO NOT auto-merge.** User-facing action only.

---

## Risks + rollback

- **Rename detection fails**: If `git diff --cached --stat` after Task 2 Step 8 shows mostly "create mode" + "delete mode" pairs instead of renames, the commit will look like a delete-all-recreate. Mitigation: bump `diff.renameLimit` further (done in Task 2 Step 5; if still fails try 500000). Rollback: `git reset --hard pre-refactor-libreoffice-split` (the tag set in Task 1 Step 4).
- **Path-length issues on Windows after pull**: Adding `libreoffice-codebase/` adds 22 chars. Longest pre-refactor tracked path was 148 chars; max absolute after refactor is ~240 chars; under 260 MAX_PATH but tight. If Windows users hit issues post-merge, the fix is `git config core.longpaths true` on their Windows clone.
- **Build breaks for an unforeseen reason**: Task 7 catches this before push. If make fails, do NOT push. Either fix in-place (likely a missed path reference) or reset to the tag.

## What this plan deliberately does NOT do

- Does not modify any LO source code (no rllogger edits, no UI edits, no module deletions).
- Does not change the rllogger contract, log location, or env-var interface.
- Does not touch other apps (figma/sheets/docs).
- Does not push to main directly; user controls the merge.
