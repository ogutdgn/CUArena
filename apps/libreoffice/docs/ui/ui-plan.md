# Writer UI Flexibility — 3-Week Plan

> Goal: turn the Writer side of the cua-bench LibreOffice fork into an
> environment where ribbon layout, buttons, icons, labels, colors,
> spacing, and overall visual design can be iterated on **without
> code rebuilds** and **without fighting hardcoded structure**, so
> that future "make it look like MS Word" work is fast and the CUA
> RL agent sees pixels close to Word M365.
>
> Owner: @ogutdgn. Drafted: 2026-05-22. Status: proposed, not yet
> committed to execution-map.

---

## 1. Problem, reframed

Owner's stated complaint: "I can't easily play with the UI. Everything
is too rigid. Every small change takes forever. I want React/Tailwind/
MUI-style flexibility."

That framing led to a natural follow-up — "should we integrate a modern
UI library (CEF / Sciter / Slint / QML)?" — but the research surfaced
two corrections that change the right move:

1. **The codebase is dramatically more flexible than it feels.** The
   ribbon is 100% XML; buttons are `action-name=".uno:Foo"` lines that
   resolve label/tooltip/icon at runtime from a registry; variants are
   3-line additions. The "rigid" feeling is mostly an *access* and
   *workflow* problem, not an architecture problem.

2. **The CUA agent sees pixels, not components.** A re-skinned GTK
   theme + Word-like icons + tweaked XML gets the agent the same
   thing a re-rendered HTML ribbon would. "Modern UI library" buys
   developer ergonomics; for an RL env, that's only valuable if the
   ergonomics translate into faster iteration on the *visual output*.

So the plan focuses on **closing the access/workflow gap on existing
infra** rather than introducing a parallel UI runtime. Modern library
integration (specifically Sciter, the only realistic embed for a
10M-LOC C++ host) is intentionally deferred — we revisit it only if
this plan finishes and concrete blockers remain.

See [Section 8](#8-deferred-decisions) for the deferred decisions and
the trigger conditions for revisiting them.

---

## 2. What's already flexible (key findings)

Concrete things the research at
`apps/libreoffice/libreoffice-codebase/` confirmed. These are the
levers Phase 1–3 build on.

| Surface | Flexibility | How |
|---|---|---|
| Ribbon tab/group/button structure | Full | `sw/uiconfig/swriter/ui/notebookbar.ui` is pure GtkBuilder XML, 17K lines, no C++ wiring per button |
| Button label / tooltip | Full | Resolved at runtime via `vcl::CommandInfoProvider` from `.uno:` command registry; can be overridden inline in `.ui` (`label="..."`) |
| Button icon (which file) | Full | Resolved via `XImageManager` from icon theme by command name; change `icon-name` in `.ui` or swap theme |
| Notebookbar variant | Full | New variant = copy `notebookbar.ui` → `notebookbar_cua.ui` + add an entry to `officecfg/registry/data/org/openoffice/Office/UI/ToolbarMode.xcu` |
| Color palette (GTK paint surfaces) | Full | `vcl/unx/gtk3/custom-theme.cxx` auto-generates GTK CSS from `ThemeColors`; `ThemeColors` is loaded from `Office.UI/ColorScheme` (see `svtools/source/config/colorcfg.cxx:356-393`), **not** `Office.Common`. |
| Color palette (VCL paint surfaces) | Mostly | VCL widgets read `StyleSettings` at paint time; same `ThemeColors` from `Office.UI/ColorScheme` feeds it for most colors |
| Icon set | Per-theme | Themes live at `icon-themes/<name>/`, packed into `images_<name>.zip` at build (icon file changes need rebuild) |
| Sidebar panels | Plugin-style | XML-defined panels via `sfx2/source/sidebar/`; addons can register |

| Surface | Hardcoded | Where |
|---|---|---|
| Button padding | C++ | `vcl/source/control/button.cxx:185-250` |
| Border radius | Not supported in VCL primitives | Rectangles only — would need paint code change |
| Focus rect thickness | C++ constants | `vcl/source/control/button.cxx` |
| Font sizes (ribbon) | `StyleSettings` defaults | Global zoom only, no per-region sizing |
| Search box / recent files dropdown in ribbon | C++ | `sfx2/source/notebookbar/SfxNotebookBar.cxx` |

Punch line: **the things the owner most often wants to change (layout,
icons, labels, colors) are all in the "Full" rows.** The things in the
hardcoded rows (border radius, padding, animations) are aesthetic
polish that the CUA agent's vision model won't reliably perceive
anyway.

---

## 3. Principles

- **No new UI runtime.** No CEF, no Sciter, no Slint, no QML, no
  Flutter. Reasons in [Section 8](#8-deferred-decisions).
- **No rebuild for ribbon iteration.** `.ui` XML changes must be
  visible after a `soffice` restart only — no `make sw` in the inner
  loop.
- **Vanilla preserved.** Our custom UI lives in a fork (new variant,
  new theme), not by patching vanilla files. Upstream sync stays
  cheap.
- **Source-of-truth maps.** Every "where do I change X?" question
  must be answerable from a single doc in seconds, not a grep
  session.
- **Build for the agent, not for us.** When a choice trades developer
  ergonomics against visual fidelity to Word, pick visual fidelity —
  the agent is the consumer.

---

## 4. Phase 1 — Access + Workflow (Week 1)

Goal: kill the "I don't know where to touch / every change takes
forever" feeling. After this phase the owner can add, remove,
rename, reorder, or re-icon any ribbon button in <60 seconds with
no rebuild.

### 4.1 Ribbon Anatomy doc

**Deliverable:** `apps/libreoffice/docs/ui/ribbon-anatomy.md`.

**Content:** A table per ribbon tab. For each button:
- Line range in `sw/uiconfig/swriter/ui/notebookbar.ui`
- UNO command (`action-name`)
- Label source (inline / registry / command-info)
- Icon name (resolved theme path)
- Group it belongs to

Plus a header section explaining the macro structure (`<GtkNotebook>`
→ tab pages → `GtkBox` group containers → `sfxlo-NotebookbarToolBox`
toolbar groups → `GtkToolButton` items).

**Approach:** half-day exploration session. Parse the XML, walk the
tree, emit the table. Spot-check 10 buttons against a running LO to
confirm labels/icons match what we said.

**Why this exists:** without it, every "change button X" task starts
with grep. With it, every such task starts at a known file:line.

### 4.2 Hot-reload workflow

**Deliverable:** `apps/libreoffice/scripts/sync-ui.sh` + a new
section in `apps/libreoffice/docs/USAGE.md`.

**Mechanism (Codex-verified):** `SfxNotebookBar::StateMethod` reads
the active variant filename from registry and constructs a
`NotebookBar` via `VclBuilder`, loading from `AllSettings::GetUIRootDir()`
which expands to `$BRAND_BASE_DIR/$BRAND_SHARE_SUBDIR/config/soffice.cfg/`
(`vcl/source/app/settings.cxx:2721-2725`,
`sfx2/source/notebookbar/SfxNotebookBar.cxx:453-533`,
`vcl/source/control/notebookbar.cxx:86-103`). No XML cache, no
resource zip — restart-based iteration is sound.

Workflow:
1. Edit source `.ui`
2. `sync-ui.sh` copies it to `instdir/` (no `make`)
3. Restart `soffice` — change visible

Total inner loop: ~5 seconds.

**Critical caveat: user-profile UI override (Codex-flagged).**
`NotebookBar` checks the user profile path
(`${UserInstallation}/user/config/soffice.cfg/modules/swriter/ui/`)
**before** the shared `instdir` path (`vcl/source/control/notebookbar.cxx:32-44,86-89`).
If anything in the owner's WSL user profile has ever customized
the Writer notebookbar (or done a manual file drop there), our
shared-instdir edits will be silently shadowed and the developer
will be debugging a phantom.

`sync-ui.sh` must therefore:
- Either also write to (or clear) the user-profile copy
- Or print a warning if a user-profile `notebookbar*.ui` exists,
  with the exact path to remove
- Add a sanity-check step that confirms which file LO actually
  loaded (one option: log it from a small `--ui-dump` debug
  invocation, or simply diff `instdir/` vs the user-profile copy
  before each restart)

**Same-file reload limitation:** In-process reload of the *same*
file (without restart) is skipped by `StateMethod()` unless
`bReloadNotebookbar` is true (`SfxNotebookBar.cxx:465-470,687-694`).
Restart is the reliable path; in-process reload needs a variant
re-switch.

### 4.3 CUA notebookbar variant fork

**Deliverable:** new variant `Tabbed (CUA)` registered as default.

**Files:**
- `sw/uiconfig/swriter/ui/notebookbar_cua.ui` — copy of current
  `notebookbar.ui`, then ours to mutate
- `sw/UIConfig_swriter.mk` — **must register the new .ui file**, or
  the build won't package it into `instdir/`. Add `notebookbar_cua`
  to the explicit list around line 249-255 (right after `notebookbar`).
  Found the hard way during smoke test 2026-05-22: without this entry,
  `make sw` is a no-op for the new file, soffice can't find the variant
  at runtime, and the "default to CUA" config silently fails.
- `solenv/sanitizers/ui/modules/swriter.false` — **must mirror the
  notebookbar.ui a11y suppressions** to cover notebookbar_cua.ui.
  Build invokes `gla11y --fatal-all`; vanilla notebookbar.ui has 696
  suppressed fatals in this file (orphaned MenuItem labels etc.).
  Adding notebookbar_cua.ui without mirroring those fails the build
  with 800+ "new fatals". One-liner to mirror:
  `grep '^sw/uiconfig/swriter/ui/notebookbar\.ui:' file | sed
  's|/notebookbar\.ui:|/notebookbar_cua.ui:|' >> file`
- `solenv/sanitizers/ui/modules/swriter.suppr` — same mirror needed
  (8 lines of orphan-label suppressions). Same one-liner with
  this file's path.
- `officecfg/registry/data/org/openoffice/Office/UI/ToolbarMode.xcu`
  — add full `ModeEntry` under `Applications/Writer/Modes`. The
  schema (`ToolbarMode.xcs:34-78`) makes `MenuPosition`, `Toolbars`,
  `UserToolbars`, `Sidebar`, `HasNotebookbar`, `CommandArg`
  non-nillable, so a minimal "3-line entry" will fail registry
  validation. Codex-verified shape:
  ```xml
  <node oor:name="CUA" oor:op="replace">
    <prop oor:name="Label"><value xml:lang="en-US">CUA (Word)</value></prop>
    <prop oor:name="CommandArg"><value>notebookbar_cua.ui</value></prop>
    <prop oor:name="MenuPosition"><value>0</value></prop>
    <prop oor:name="HasMenubar"><value>true</value></prop>
    <prop oor:name="HasNotebookbar"><value>true</value></prop>
    <prop oor:name="Toolbars"><value/></prop>
    <prop oor:name="UserToolbars"><value/></prop>
    <prop oor:name="Sidebar"><value>Arrow</value></prop>
    <prop oor:name="IsExperimental"><value>false</value></prop>
  </node>
  ```
  Cross-check against an existing entry like `<node oor:name="Tabbed">`
  in the same file before committing — copy any other non-nillable
  fields the schema requires that aren't listed here.

- **Default selection — two keys must agree** (Codex-verified, this
  was originally marked TBD):
  - `org.openoffice.Office.UI.ToolbarMode/ActiveWriter = notebookbar_cua.ui`
    — read by `SfxNotebookBar::lcl_getNotebookbarFileName` at
    `sfx2/source/notebookbar/SfxNotebookBar.cxx:204-209` to pick
    which XML to load on startup.
  - `org.openoffice.Office.UI.ToolbarMode/Applications/Writer/Active = notebookbar_cua.ui`
    — read at `SfxNotebookBar.cxx:342-372` for active-state checks;
    also written by the `.uno:ToolbarMode` handler in
    `sfx2/source/appl/appserv.cxx:978-1028` when the user switches
    variants. Skipping this causes the runtime to revert.

- **Writer-only is allowed** — Codex confirmed `Applications` is
  per-app and the schema/loader honor it. Calc / Impress sections
  do not need matching CUA entries. Caveat: do not use the "Apply
  to All" picker (`cui/source/dialogs/uipickerdlg.cxx:66-95`) with
  CUA active, because Calc/Impress can't apply a variant they don't
  declare.

**Why fork instead of edit-in-place:** owner will iterate heavily;
upstream LO will at some point change `notebookbar.ui`; we want
reduced merge conflicts. Note: `ToolbarMode.xcu`, `configure.ac`,
and other shared config files remain vanilla-file edits, so "zero
conflicts" is overstated — but the giant XML is forked.

### 4.4 Phase 1 exit criteria

- [ ] `docs/ui/ribbon-anatomy.md` lists every button on every Home
      tab (full table; other tabs can be tier 2)
- [ ] `scripts/sync-ui.sh` works; demonstrated on a single button
      rename (no rebuild, change visible after restart)
- [ ] `notebookbar_cua.ui` registered and selectable in
      Tools → Toolbar Layout
- [ ] `USAGE.md` has a "Ribbon iteration" section pointing at the
      above
- [ ] One end-to-end demonstration: rename "Bold" → "Kalın" in
      `notebookbar_cua.ui`, sync, restart, see "Kalın" in the
      ribbon. Total elapsed time <60 seconds from edit to visible.

---

## 5. Phase 2 — Word Visual Parity (Week 2)

Goal: when `soffice --writer` opens, the visual impression is "this is
Word, in a Linux skin" rather than "this is LibreOffice with a dark
theme." No structural ribbon changes yet — pure skinning on top of the
Phase 1 fork.

### 5.1 Office.UI ColorScheme → Word M365 palette

**Mechanism (Codex-verified):** `ThemeColors` is a 25-color singleton
that VCL paint code reads. Despite the name, it is **not** loaded
from `Office.Common`. It's loaded by `svtools::ColorConfig_Impl`,
rooted at `Office.UI/ColorScheme` (see
`svtools/source/config/colorcfg.cxx:137-139,356-393`). The current
scheme is picked by `Office.UI/ColorScheme/CurrentColorScheme`; each
scheme's color values live under
`Office.UI/ColorScheme/ColorSchemes/<scheme>/<Color>/Color`.

`Office.Common/Appearance` only owns the high-level toggle for
"use system theme vs custom" and `Common/Misc/SymbolStyle` (icon
theme selection). The actual palette is `Office.UI`.

**Action:** add a new color scheme entry in
`officecfg/registry/data/org/openoffice/Office/UI.xcu` under
`ColorScheme/ColorSchemes` (e.g. `COLOR_SCHEME_CUA_WORD_DARK`) and
set `ColorScheme/CurrentColorScheme` to it. Specifically tune the
25 documented color keys used by the ribbon / window / menus —
WindowColor, ButtonColor, ButtonTextColor, AccentColor, MenuBarColor,
MenuBarTextColor, ActiveColor, etc.

**Reference:** existing schemes in `UI.xcu:1127,1482-1507` for shape;
schema in `Office/UI.xcs:1080-1089`. Word 2021 / M365 default light
palette + dark palette. We commit both, the user picks at launch
via `CurrentColorScheme`.

**Do NOT** put palette values in `Common.xcu` — Codex confirmed this
would have no effect on `ThemeColors`.

### 5.2 GTK CSS theme — `custom-theme.cxx` retargeted

The existing `custom-theme.cxx` already produces CSS from
`ThemeColors`. Once 5.1 lands, this gets us GTK paint surfaces for
free (HeaderBar, menubar, scrollbar, file picker, dialogs that use
native GTK widgets).

**Optional polish:** if any GTK-side surface still looks off after
5.1, add targeted CSS overrides in `custom-theme.cxx` (or, as a
follow-on, externalize the CSS string to a file we hot-reload — see
5.4).

### 5.3 Icon theme — `cua_word`

**Mechanism (Codex-corrected):** Icon themes live at
`icon-themes/<name>/` and are discovered at runtime from packaged
`images_<name>.zip` files (`vcl/source/app/IconThemeInfo.cxx:39-107`,
`vcl/source/app/IconThemeScanner.cxx:24-34,62-67`). The active theme
is selected via `Office.Common/Misc/SymbolStyle` (`Common.xcu:409-411`).

Adding a brand-new theme is **not config-only** — it requires:

1. **`configure.ac` allow-list entry** — the build refuses unknown
   theme names. Add `cua_word` to the `WITH_THEMES` allow-list at
   `configure.ac:14546-14555`.
2. **`postprocess/CustomTarget_images.mk` packing** — the build
   packs `icon-themes/<name>/` into `images_<name>.zip`
   (`postprocess/CustomTarget_images.mk:16,43-62`). Confirm
   `cua_word` is picked up; if not, the make rule needs updating.
3. **Source tree:** `icon-themes/cua_word/` with the SVGs.

**Realistic phasing (Codex-recommended):**

- **Phase 2.3a (do first):** swap the default to an existing
  theme — `sifr_dark` is already our default, but `colibre_dark`
  is closer to Word in tone. Try setting `SymbolStyle = colibre_dark`
  via `Common.xcu` and see if Word-fidelity improves enough without
  any new theme.
- **Phase 2.3b (do only if 2.3a insufficient):** create `cua_word/`.
  Replace 50-100 highest-visibility ribbon icons (Home tab + most-used
  Insert/Layout/View buttons) with Word M365 equivalents. Sources:
  Fluent UI System Icons (MS official, MIT-licensed), Lucide (ISC),
  Office UI Fabric. Verify MPL compatibility before bulk import.
- After either: rebuild required (one-time bulk; individual icon
  swaps thereafter still need rebuild).

**Do not** assume "drop SVG, restart" works for new themes. It does
not — the zip-packing step gates it.

### 5.4 Optional: externalize GTK CSS for hot-reload

If iteration on GTK-side colors is happening frequently, lift the CSS
string out of `custom-theme.cxx` into a file at
`instdir/share/config/cua-theme.css` and load it via
`gtk_css_provider_load_from_path()`. Then GTK-paint color iteration
becomes edit-restart, no rebuild.

Skip if Phase 2 settles after 5.1 + 5.2 + 5.3 — don't over-engineer.

### 5.5 Phase 2 exit criteria

- [ ] Side-by-side screenshot of CUA Writer vs. Word 2021 light theme
      — visually similar enough that a casual observer can't tell at
      thumbnail size
- [ ] Same for dark theme
- [ ] CUA icon theme registered, applied to CUA notebookbar variant
- [ ] Color palette overrides documented in
      `docs/ui/word-palette.md` with hex values + the registry path
      they live at

---

## 6. Phase 3 — Comfort + Optional Depth (Week 3)

Goal: convert the manual workflows from Phases 1–2 into ergonomics
that make further iteration painless, and tackle the small number
of genuinely-hardcoded VCL paint constraints if they matter for
visual parity.

### 6.1 Notebookbar DSL transpiler

**Problem:** even with our fork, `notebookbar_cua.ui` is 17K lines of
GtkBuilder XML. Authoring directly in it is tedious; small edits are
fine but structural rework is painful.

**Proposal:** a TypeScript or Python script `scripts/build-notebookbar.ts`
that reads a friendly DSL (~500 lines of YAML or TS) and emits the full
`.ui` XML. Rough sketch:

```yaml
variant: cua
tabs:
  - id: home
    label: Home
    groups:
      - id: clipboard
        label: Clipboard
        buttons:
          - { command: .uno:Paste, size: large }
          - { command: .uno:Cut }
          - { command: .uno:Copy }
          - { command: .uno:FormatPaintbrush }
      - id: font
        label: Font
        ...
```

**Trade-off:** adds a build step. Mitigation: integrate into
`sync-ui.sh` so the user still edits one file, transpiler runs, output
syncs. Total elapsed: still ~5 seconds.

**Decide-or-defer:** if Phase 2 ribbon work didn't feel painful at
XML level, skip this. The DSL is a "we'll do a lot of structural
rework" optimization, not a foundation.

### 6.2 File watcher daemon

**Mechanism:** `inotifywait` (Linux) watches `sw/uiconfig/swriter/ui/
notebookbar_cua.ui` and the CSS file from 5.4. On change: run
`sync-ui.sh`, optionally SIGTERM `soffice` to force a reload.

**Deliverable:** `scripts/watch-ui.sh`, documented in `USAGE.md`.

**Skip if** the manual `sync-ui.sh` + restart loop is already fast
enough. This is pure quality-of-life.

### 6.3 Targeted VCL paint patches (only if needed)

If after Phase 2 there are specific visual gaps from "Word fidelity"
that the agent visibly notices in CUA eval runs, this is the escape
hatch:

- Border radius on ribbon buttons → patch `vcl/source/control/button.cxx`
  paint code to draw rounded rectangles (Cairo path: 1-2 days)
- Focus ring style → same file, paint code constants
- Specific padding adjustments → `button.cxx:185-250`

These are surgical C++ changes that *do* need rebuild. Treat each as
its own scoped task with a feature checklist entry. Do not generalize
to "rewrite VCL paint" — keep the surface area minimal.

### 6.4 Phase 3 exit criteria

Only the ones that turned out to matter:
- [ ] If DSL built: at least one ribbon edit cycle done via the DSL
      (proves it's usable, not just written)
- [ ] If watcher built: live-reload demonstrated on one edit
- [ ] Any VCL paint patches: build green, smoke test passes,
      documented in `docs/architecture/ROADMAP.md` decision log

---

## 7. What this plan delivers (and doesn't)

### Delivers

- Add / remove / reorder / rename any ribbon button in seconds,
  no rebuild
- Re-point a ribbon button to a **different already-installed icon**
  (XML `icon-name` swap) — no rebuild
- Restructure tabs and groups freely
- Toggle color palette by switching `Office.UI/CurrentColorScheme`
  between Word light / Word dark / any custom scheme — no rebuild
- Author ribbon structure in a high-level DSL instead of raw XML (if
  Phase 3.1 happens)
- 5-second inner loop for XML / palette iteration vs. 3-5 minute
  rebuild loop today
- Reduced upstream merge conflicts — the large `notebookbar_cua.ui`
  is fully forked. Note: `ToolbarMode.xcu`, `configure.ac`,
  `Common.xcu`, and `UI.xcu` remain vanilla-file edits, so
  conflict-free is not absolute

### Does NOT deliver

- React-style component reuse / npm ecosystem inside LO (no UI
  library can deliver this for a legacy native app at realistic cost)
- CSS animations, hover transitions, smooth scrolling, blur
  effects (VCL doesn't render these; out of scope for an RL env)
- Border radius / drop shadow on every widget out of the box (only
  via targeted Phase 3.3 patches)
- **Rebuild-free SVG icon edits or new icon themes** — both
  require a `make` run because icons are packed into
  `images_<theme>.zip` and new theme names must be in the
  `configure.ac` allow-list
- Live preview of unsaved changes without a restart (file watcher
  gets close but still kills and reopens `soffice`)
- "Modern" component API for plugin authors — out of scope

If any of those become genuinely blocking, see [Section 8](#8-deferred-decisions)
— Sciter for a single panel is the escape hatch, with full eyes-open
on the cost.

---

## 8. Deferred decisions

These were considered and explicitly deferred — not rejected forever.

### 8.1 Sciter for one panel (e.g., ribbon)

- **What it'd give us:** real HTML5 + CSS3 rendering for one panel,
  ~8 MB DLL, in-process embedding
- **Why deferred:** 2-4 weeks of integration work for something the
  CUA agent doesn't differentiate from VCL-rendered output; permanent
  two-UI-system maintenance cost
- **Revisit if:** after this plan completes, there's a *specific* UI
  capability we can articulate (e.g., "we need a Monaco code editor
  in the ribbon" or "we need a Mermaid live preview") that XML+VCL
  genuinely cannot do, and that capability moves CUA eval scores

### 8.2 CEF (full Chromium embed)

- **Verdict:** no, regardless of how Phase 1-3 goes
- **Reason:** +180 MB binary, 6-12 weeks per panel, multi-process IPC
  tax forever, no precedent of anyone retrofitting CEF into a legacy
  office suite

### 8.3 LOOL/WASM rewrite — OnlyOffice-style web shell

- **Verdict:** no, out of scope
- **Reason:** months of architectural work; rebuilds the whole client
  around an architecture LOOL took the Collabora team years to
  harden; right answer only if the project pivots from "Word-like
  LibreOffice fork for CUA" to "build a new editor"

---

## 9. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **P1**: New `ModeEntry` missing non-nillable schema fields (`MenuPosition`, `Toolbars`, `UserToolbars`, etc.) → config validation / runtime failure | Medium if rushed | Phase 1.3 stalls; possibly silent runtime fallback | Use the full template in §4.3; cross-check against an existing `<node oor:name="Tabbed">` entry before commit. Evidence: `ToolbarMode.xcs:34-78` |
| **P1**: User-profile UI override silently shadows shared `instdir` ribbon edits | High on a workstation that's seen prior LO use | Developer chases phantom; loses hours | `sync-ui.sh` warns / clears `${UserInstallation}/user/config/soffice.cfg/modules/swriter/ui/notebookbar*.ui`. Evidence: `vcl/source/control/notebookbar.cxx:32-44,86-89` |
| **P2**: New icon theme not picked up because `configure.ac` `WITH_THEMES` allow-list rejects unknown names | High if 2.3 attempted without allow-list edit | Phase 2.3 stalls (looks like silent failure) | Phase 2.3 spec now lists the allow-list edit explicitly. Evidence: `configure.ac:14546-14555`; `postprocess/CustomTarget_images.mk:16,43-62` |
| **P2**: Palette tuning targeted at wrong registry path (`Common.xcu` vs `Office.UI/ColorScheme`) — no visible effect | Was high; now low after §5.1 correction | 1-2 days lost debugging "why don't colors change" | §5.1 now specifies `Office.UI/ColorScheme`. Evidence: `svtools/source/config/colorcfg.cxx:137-139,356-393` |
| `.ui` hot-reload not actually rebuild-free for notebookbar | Low (Codex verified the load path) | Phase 1 stalls | Verified — restart-based loop works. Same-file in-process reload needs variant reswitch (`SfxNotebookBar.cxx:465-470,687-694`). |
| New variant registration breaks Tools → Toolbar Layout | Low | Phase 1.3 stalls | Test on a vanilla profile; revert XCU entry if broken |
| `ThemeColors` overrides don't propagate to all VCL widgets | Medium | Some surfaces stay LO-looking | Tier the palette work: ribbon + menubar + sidebar first; dialogs second tier |
| Owner adds new requirement mid-plan ("now make it animated") | High (based on history) | Scope creep | Honor the deferred list in Section 8; new requirements get their own design doc |
| VCL paint constants resist override more than expected | Low | Phase 3.3 scope grows | Each VCL patch scoped individually; cap at 3-5 such patches before re-evaluating |

---

## 10. File-level summary

Files that will be created or touched, by phase:

**Phase 1**
- `apps/libreoffice/docs/ui/ribbon-anatomy.md` *(new)*
- `apps/libreoffice/scripts/sync-ui.sh` *(new)*
- `apps/libreoffice/docs/USAGE.md` *(append section)*
- `apps/libreoffice/libreoffice-codebase/sw/uiconfig/swriter/ui/notebookbar_cua.ui` *(new — copy)*
- `apps/libreoffice/libreoffice-codebase/officecfg/registry/data/org/openoffice/Office/UI/ToolbarMode.xcu` *(edit — add CUA variant + flip defaults)*
- `apps/libreoffice/libreoffice-codebase/sw/UIConfig_swriter.mk` *(edit — register notebookbar_cua in build)*
- `apps/libreoffice/libreoffice-codebase/solenv/sanitizers/ui/modules/swriter.false` *(append — mirror 696 a11y fatal suppressions)*
- `apps/libreoffice/libreoffice-codebase/solenv/sanitizers/ui/modules/swriter.suppr` *(append — mirror 8 orphan-label suppressions)*

**Phase 2**
- `apps/libreoffice/libreoffice-codebase/officecfg/registry/data/org/openoffice/Office/Common.xcu` *(new or edit — palette overrides)*
- `apps/libreoffice/docs/ui/word-palette.md` *(new)*
- `apps/libreoffice/libreoffice-codebase/icon-themes/cua_word/` *(new — copy of sifr_dark)*
- Icon SVGs in `cua_word/cmd/` *(bulk replacements)*
- `apps/libreoffice/libreoffice-codebase/vcl/unx/gtk3/custom-theme.cxx` *(optional 5.4 — externalize CSS)*

**Phase 3 (each optional)**
- `apps/libreoffice/scripts/build-notebookbar.ts` *(new — DSL transpiler)*
- `apps/libreoffice/scripts/watch-ui.sh` *(new — file watcher)*
- `apps/libreoffice/libreoffice-codebase/vcl/source/control/button.cxx` *(targeted edits if needed)*

---

## 11. Sequencing and gates

- Phase 1 must finish before Phase 2 starts (Phase 2 builds on the
  CUA variant fork)
- Phase 2.1 (palette) must finish before 2.2 (GTK CSS) — GTK CSS reads
  from the palette
- Phase 2.3 (icons) is parallelizable with 2.1/2.2
- Phase 3 items are independent; do the ones that the Phase 2 ending
  state actually demands

After each phase: update `apps/libreoffice/docs/last-point.md` and
`apps/libreoffice/docs/execution-map.md` per the standard session-end
workflow.

---

## 12. Open questions — answered (Codex review 2026-05-22)

1. **Exact registry path for default Writer variant** —
   **Answered.** Set **both** keys (loader uses one, switcher writes
   the other):
   - `org.openoffice.Office.UI.ToolbarMode/ActiveWriter = notebookbar_cua.ui`
     (`SfxNotebookBar.cxx:204-209`)
   - `org.openoffice.Office.UI.ToolbarMode/Applications/Writer/Active = notebookbar_cua.ui`
     (`SfxNotebookBar.cxx:342-372`; written by `appserv.cxx:978-1028`)

2. **Calc/Impress matching entries** — **Answered.** Writer-only is
   allowed (schema `ToolbarMode.xcs:132-136`; loader honors
   per-app at `SfxNotebookBar.cxx:161-177`). Caveat: don't use the
   "Apply to All" picker (`cui/source/dialogs/uipickerdlg.cxx:66-95`)
   while CUA variant is active — Calc/Impress can't apply a variant
   they don't declare.

3. **Light/dark palette** — **Decided 2026-05-22: dark only for
   now.** Phase 2 ships a single Word-dark `Office.UI/ColorScheme`.
   Light scheme deferred until owner explicitly asks. Matches
   current Phase 4 V1 dark default.

4. **Icon source license** — **Still needs owner/legal input.**
   Fluent UI System Icons are MIT, Lucide is ISC — both should be
   MPL-compatible for bundling (permissive licenses, attribution
   required). Owner should confirm before bulk-importing 50-100
   icons. Code can consume the theme once built.

5. **Should `sync-ui.sh` reload registry overrides** — **Answered:
   No.** Palette lives in `Office.UI/ColorScheme/...` (not
   `Common.xcu`), and registry changes are not the same hot loop as
   `.ui` file copy. Palette tuning is a separate `make` cycle after
   editing `UI.xcu`. `sync-ui.sh` is `.ui`-only.

## 13. Newly open questions (from Codex review)

1. **Existing-theme-first viability** — Codex recommends trying
   `colibre_dark` or sticking with `sifr_dark` as default before
   building `cua_word`. Owner should evaluate whether visual fidelity
   to Word is acceptable with an existing theme. If yes, skip
   Phase 2.3b entirely.
2. **Light/dark scheme product default** — answered: dark only for now (see §12.3).
3. **Icon licensing confirmation** — see §12.4 above.
4. **Phase 1.2 sync-ui.sh user-profile handling** — write to user
   profile, or clear user profile, or warn? Owner preference.
