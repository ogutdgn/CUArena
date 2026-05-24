# docs/ui — UI Flexibility Work

> Working area for the Writer UI flexibility / Word-parity effort.
> Everything related to "make it easy to play with the UI" lives here.

## Read order

1. **[ui-plan.md](ui-plan.md)** — the 3-week plan. Phases, principles,
   deferred decisions, risks. Read this first to understand WHY each
   doc here exists.
2. **[ribbon-anatomy.md](ribbon-anatomy.md)** — source-of-truth map
   for every button in the Writer notebookbar. Use this when you need
   to find "where do I change X?" — file, line, UNO command, label
   source, icon name. Phase 1.1 deliverable.

## Phase status

| Phase | Item | Status |
|---|---|---|
| 1.1 | ribbon-anatomy.md | done (2026-05-22) |
| 1.2 | sync-ui.sh + USAGE.md hot-reload section | done (2026-05-22) — functional verify OK in lo-dev WSL |
| 1.3 | notebookbar_cua.ui fork + ToolbarMode.xcu + UIConfig + a11y mirror | done (2026-05-22) — WSL build green; runtime: soffice launches with CUA default (rllogger sessions + profile registry confirmed); screenshot deferred (xvfb render issue, functional evidence sufficient) |
| 2.1 | Office.UI ColorScheme overrides (Word palette) | pending — needs owner light/dark decision |
| 2.2 | GTK CSS retarget (auto-flows from 2.1) | pending |
| 2.3 | Icon strategy (try sifr_dark/colibre_dark first, cua_word only if needed) | pending — needs owner existing-theme-first decision |
| 3.x | DSL transpiler / file watcher / VCL patches | optional / on-demand |

## Phase 1 verification (owner WSL)

After pulling the Phase 1 changes:

```sh
# 1. Build (incremental; officecfg + sw changes need this)
cd ~/lo-dev/apps/libreoffice/libreoffice-codebase
make sw

# 2. Confirm no profile-shadow shadowing
./../scripts/sync-ui.sh --check-only

# 3. Launch — Writer should open with "CUA (Word)" variant active
pkill -f soffice 2>/dev/null
instdir/program/soffice --writer --norestore

# 4. Verify in UI: Tools -> Toolbar Layout -> "CUA (Word)" present + selected

# 5. Hot-reload smoke test: edit notebookbar_cua.ui (e.g. rename a button
#    label inline), sync, restart, see the change without a rebuild
$EDITOR sw/uiconfig/swriter/ui/notebookbar_cua.ui
./../scripts/sync-ui.sh
pkill -f soffice 2>/dev/null; instdir/program/soffice --writer --norestore
```

## How this folder relates to the rest of `apps/libreoffice/docs/`

- **`docs/last-point.md`** — what has shipped on `main`. Phase items
  here move into `last-point.md` only after they are merged.
- **`docs/execution-map.md`** — what is being worked on next. The
  "Next" pointer should reference items from the Phase status table
  above while UI work is the active effort.
- **`docs/architecture/ROADMAP.md`** — owns Phase 4 (Writer UI redesign).
  This folder is the working detail for that phase.
- **`docs/USAGE.md`** — once Phase 1.2 ships, the "Ribbon iteration"
  section there is the user-facing entry point; this folder remains
  the developer reference.

## Conventions

- New UI docs go here, not in `docs/architecture/`. Architecture is for
  one-time decisions (phase design, mode contracts). This folder is the
  ongoing working area.
- Each new doc gets an entry in the read-order list above.
- After any ribbon structural edit, regenerate `ribbon-anatomy.md` —
  see §8 of that doc.
