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
3. **[word-palette.md](word-palette.md)** — Phase 2.1 palette
   reference. Full hex table + registry paths.

## Phase status

| Phase | Item | Status |
|---|---|---|
| 1.1 | ribbon-anatomy.md | shipped on main (PR #58, 2026-05-24) |
| 1.2 | sync-ui.sh + USAGE.md hot-reload section | shipped on main (PR #58, 2026-05-24) |
| 1.3 | notebookbar_cua.ui fork + ToolbarMode.xcu + UIConfig + a11y mirror | shipped on main (PR #58, 2026-05-24) |
| 2.1 | Office.UI ColorScheme — CUA Word Dark palette | shipped on main (PR #59, 2026-05-24) |
| 2.2 | GTK CSS retarget (auto-flows from 2.1 via `custom-theme.cxx`) | shipped on main (PR #59, 2026-05-24) |
| 2.3 | Icon strategy (current `sifr_dark` vs. forked `cua_word`) | pending — awaiting owner visual review of 2.1 |
| 3.x | DSL transpiler / file watcher / VCL patches | optional / on-demand |

## Visual verification (owner WSL)

After pulling main:

```sh
cd ~/lo-dev
git checkout main && git pull origin main
cd apps/libreoffice/libreoffice-codebase

# Build (full make is safest; if only officecfg changed since the
# last build, `make postprocess` suffices)
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
make

# Confirm no user-profile shadow
../scripts/sync-ui.sh --check-only

# Launch
pkill -f soffice 2>/dev/null
instdir/program/soffice --writer --norestore
```

**What to look for:**

- **Phase 1.3 ribbon evidence:** tab order is `File / Home / Insert /
  Design / Layout / References / Mailings / Review / View / Help`
  (Word M365). Vanilla "Tabbed" has different tabs (no Design, no
  Mailings) — seeing Design + Mailings is the proof CUA variant is
  active.
- **Phase 2.1 palette evidence:** ribbon background `#2B2B2B`
  (slightly lighter than vanilla DARK), accent (selection / active
  tab underline) Word blue `#2B5797`, hover/active state bright blue
  `#4A9EFF`. Both VCL and GTK paint surfaces should match.
- **Quick Access Toolbar:** Save / Undo / Redo buttons in the GTK
  HeaderBar (top-left of titlebar) — from `lo/ui-improve`.

**Hot-reload smoke test (Phase 1.2):**

```sh
$EDITOR sw/uiconfig/swriter/ui/notebookbar_cua.ui
# rename a button label, e.g. label="Bold" -> label="Kalın"

../scripts/sync-ui.sh
pkill -f soffice 2>/dev/null
instdir/program/soffice --writer --norestore
# Expect: renamed label visible. ~5s total, no rebuild.
```

**Gotcha — `View → User Interface` picker (`uipickerdlg.cxx`):**
the picker dialog UI is hardcoded to 7 built-in modes as radio
buttons; **custom variants like CUA do not appear in the list**,
and the dialog defaults to "Standard Toolbar" as the radio selection
regardless of what's actually loaded. **Do not click "Apply to
Writer" or "Apply to All" in this dialog with CUA active** — it
will silently overwrite the CUA default with whatever radio is
selected. Verify the active variant from terminal instead:

```sh
grep ActiveWriter ~/.config/libreoffice/4/user/registrymodifications.xcu 2>/dev/null
# (empty = using XCU shipped default = notebookbar_cua.ui)
```

## How this folder relates to the rest of `apps/libreoffice/docs/`

- **`docs/last-point.md`** — what has shipped on `main`.
- **`docs/execution-map.md`** — what's queued next.
- **`docs/architecture/ROADMAP.md`** — owns Phase 4 (Writer UI redesign).
  This folder is the working detail for that phase.
- **`docs/USAGE.md`** — Phase 1.2 "Ribbon iteration" section is the
  user-facing entry; this folder remains the developer reference.

## Conventions

- New UI docs go here, not in `docs/architecture/`. Architecture is for
  one-time decisions (phase design, mode contracts). This folder is the
  ongoing working area.
- Each new doc gets an entry in the read-order list above.
- After any ribbon structural edit, regenerate `ribbon-anatomy.md` —
  see §8 of that doc.
