# Engine re-vendor — impact analysis

> **Why this exists.** The first real attempt to build the vendored LibreOffice engine
> (2026-05-29) revealed that `libreoffice-codebase/` is **not pristine LibreOffice** — it is
> the **old reskin approach's modified, stripped tree**. This doc records exactly what was
> changed, why the build breaks, what re-vendoring pristine LO fixes, and which docs the
> re-vendor invalidates. It is the basis for the post-re-vendor documentation sweep.
>
> Baseline for all diffs: **pristine LibreOffice core @ commit `1f1121d1`**
> (version `26.8.0.0.alpha0+`, the same version string the vendored tree reports).

---

## Executive summary

- The committed engine was hacked by the superseded reskin: **5,726 files physically deleted**
  (~34 whole modules + scattered files) and **24 files added** (the `rllogger` module + a custom
  `notebookbar_cua.ui` + a few version-skew artifacts).
- The build dies because deleting modules from a gbuild tree leaves **dangling references** in the
  central build-wiring (`Repository.mk`, `RepositoryModule_host.mk`, `scp2`) — first `opencl`, then
  `helplinker`, and more would follow. It is **not patchable** sanely.
- **Fix:** re-vendor pristine LO @ `1f1121d1`. The Writer-focused slimness the reskin wanted is
  achieved the *correct* way — **configure flags, not file deletion** (`--disable-database-connectivity`,
  `--without-java`, no `--with-help`, optional `--disable-opencl`). Only **Math** has no clean disable.
- The `rllogger` (engine-embedded logger) **violates** the locked Boundary-A / no-core-edits rule;
  re-vendor removes it (our logger lives above the line).
- **Doc fallout:** several "engine is committed/fully buildable/not edited" claims and the
  no-core-edits guardrail are **false now, true only after re-vendor**; and — highest risk — the
  ribbon research verified LO-side facts against the hacked `notebookbar_cua.ui`, which a pristine
  tree does not contain, so those citations must be re-anchored to stock `notebookbar.ui`.

---

## 1. Reskin footprint & build effects

### 1.1 Deleted whole modules (restored by re-vendor)

| Subsystem | Modules deleted (file counts) |
|---|---|
| Base (database app) | `dbaccess` (811), `forms` (262) |
| Math | `starmath` (172) |
| Reports | `reportdesign` (262), `reportbuilder` (197) |
| Basic IDE | `basctl` (159) |
| Test infra | `qadevOOo` (1915), `smoketest` (35) |
| Java & UNO bindings | `ridljar` (156), `pyuno` (75), `cli_ure` (59), `jvmfwk` (50), `rust_uno` (43), `net_ure` (40), `javaunohelper` (30), `jsuno` (16), `jvmaccess` (16), `jurt` (13) |
| Help system | `xmlhelp` (39), `helpcompiler` (18) |
| Non-core import filters | `lotuswordpro` (417), `hwpfilter` (70) |
| Extension dialogs | `sdext` (132), `swext` (45) |
| GPU compute | `opencl` (15) |
| Platform-specific | `android` (281), `winaccessibility` (89), `apple_remote` (18), `ios` (16), `osx` (3) |
| Misc add-ons | `nlpsolver` (57), `bean` (35), `librelogo` (9), `remotebridges` (6) |

Whole sub-trees also gone (git submodules / data, expected): `dictionaries`, `translations`, `helpcontent2`.

### 1.2 The real damage in *kept* modules (source of the dangling refs)

- **Build-wiring not updated** — `Repository.mk` still registers `HelpIndexer`/`HelpLinker` (built by the
  deleted `helpcompiler`) and still lists `opencl`; both `gb_Helper_optional`-gated, so they only
  hard-break when the feature is enabled. `scp2` still includes `InstallModule_{base,math,python}.mk`
  whose bodies were deleted. `solenv` UI-sanitizer suppressions + `desktop`/`sysui` launchers for the
  removed apps remain.
- **Stranded public headers (34 under `include/`)** — incl. two **non-module core** headers that break
  kept code if absent: `include/vcl/weld/Window.hxx`, `include/i18nlangtag/applelangid.hxx`.

### 1.3 Version skew (not carve-outs)

`sc` (56), `sw` (4), `sd` (6), `cui` (3) "missing" files are simply **newer upstream files** — the reskin
was based on an **older LO checkout** than `1f1121d1`. Re-vendoring is therefore a clean full-tree reset;
fine, since no app code depends on the engine yet.

### 1.4 What the reskin added (dropped by re-vendor)

- **`rllogger/` (20 files)** — engine-embedded raw/semantic/outcome logger, wired into `Repository.mk:641`
  + `RepositoryModule_host.mk:93`. The one clean piece, but it belongs **above** Boundary A in our Qt
  layer, not in the engine — so it goes.
- **`notebookbar_cua.ui`** — project-custom Writer ribbon (not in pristine LO).
- A few version-skew artifacts (`cui` MacroManagerDialog, `external/` patches, `sources.ver`, `config.guess`).

### 1.5 Slimming the *right* way (configure flags, not `rm`)

- `--disable-database-connectivity` — drops Base/`dbaccess`, `forms`, `reportdesign`/`reportbuilder` at
  configure time. Biggest, cleanest win.
- `--without-java` — drops the whole Java/UNO-binding cluster. (Already implied by the architecture.)
- No `--with-help` (HELPTOOLS off) — leaves `HelpIndexer`/`HelpLinker` unbuilt, fixing the original
  `helplinker` break properly.
- `--disable-opencl` — optional slim (no longer a workaround once `opencl/` exists).
- **Math has no clean disable** — `starmath` builds whenever the suite builds; leave it built rather than
  hand-carving it (hand-carving recreates the dangling-ref hazard).

---

## 2. Documentation impact (post-re-vendor sweep)

**A. "Engine committed / fully buildable / not edited / fully editable" — false now, true after re-vendor:**
`docs/last-point.md:3-4,36-38`, `docs/execution-map.md:29-30,39`, `docs/architecture/ARCHITECTURE.md:155-158,187`,
`AGENTS.md:47-48,89-92`, `CLAUDE.md:61`, `README.md:28`.

**B. No-core-edits guardrail — currently violated by the rllogger + strip:**
`ARCHITECTURE.md:145-161`, `last-point.md:33-38`, `CLAUDE.md:27,39-40`, `AGENTS.md:32,45-48`,
`execution-map.md:28-29,79`, `research/README.md:55-56`, `research/ribbon/README.md:107`,
`research/tech-stack.md:155`, `ui/README.md:96`. Policy text stands; the *tree* must be made to match it.

**C. "Optional future engine strip" framing + `WRITER_CALC_EXTRACTION.md`** assume a pristine start, but the
tree is already (differently) stripped: `CLAUDE.md:58`, `execution-map.md:54`, all of
`WRITER_CALC_EXTRACTION.md` (esp. the stale git-state note ~`:1058`). Realigns correctly after re-vendor.

**D. HIGHEST RISK — ribbon research verified against the hacked `notebookbar_cua.ui`:** Design/Draw/Help
tabs anchor to its line numbers (`design-tab.md` esp., `draw-tab.md`, `help-tab.md`), and every ribbon-tab
doc's "checked against the vendored tree" footer cites the hacked corpus. Pristine LO has no
`notebookbar_cua.ui` → re-anchor to stock `notebookbar.ui` (different lines, possibly different membership).

**E. "stripped tree/checkout" verification caveats** become resolvable against a full tree:
`review-tab.md:339,343,422`.

**F. Reskin/rllogger "superseded; docs removed" notes** understate that the engine *still carries* the
rllogger + `notebookbar_cua.ui` until re-vendor: `AGENTS.md:20-22`, `last-point.md:18-21`, `CLAUDE.md:17-18`,
`README.md:11`, `execution-map.md:12`, `ARCHITECTURE.md:14`, `research/README.md:12`.

---

## 3. Re-vendor execution plan & risks

### 3.1 Steps (build locally first, commit nothing yet)

1. **Back up** the three git-ignored local build files (a filesystem delete would lose them, git can't
   restore them): `autogen.input`, `config.guess`, `.vscode/vs-code-template.code-workspace.in`.
2. **Materialize pristine LO @ `1f1121d1`** in a scratch dir (blobless clone + `git checkout 1f1121d1`).
3. **Replace** the engine dir: `rm -rf libreoffice-codebase` then `rsync -a --exclude='.git'` the pristine
   working tree in. (Monorepo `.git` is at repo root, untouched.)
4. **Re-apply** the local files: `config.guess` (+`chmod +x`), `.vscode` stub, and `autogen.input` —
   updating the slimming flags (drop the "opencl missing" workaround comment; add
   `--disable-database-connectivity`).
5. **Configure + build locally** (clean `PATH` for the WSL/mingw trap), keep all headless/OOM-safe flags.
6. **Verify** the build gets *past* gbuild module registration (the failure point) and starts compiling
   `sw`/`sc`/`vcl` — confirm `opencl/` exists and no "module not found".

### 3.2 Open decisions (after it builds green)

1. **Commit choice** — exact `1f1121d1` (parity) now; consider re-basing onto a stable tag later for a
   reproducible vendored engine instead of a moving alpha tip.
2. **Commit the ~1.4–2 GB tree to the monorepo at all?** Re-committing bloats every clone. Re-vendor is the
   natural moment to revisit **in-tree vs. git submodule vs. fetched build artifact**. Recommendation:
   build & verify locally first; decide deliberately before committing.
3. **Future Writer-only strip** — do it via supported gbuild gating / `--without-*`, never by deleting
   files (that is exactly what broke this tree).

### 3.3 Risks

- Pristine builds the full suite → bigger/slower build, more build-deps (install via `sudo -S`); keep the
  `--with-parallelism=8` + no-LTO/no-mergelibs caps (load-bearing on the 15 GB box).
- Grep the app (outside the engine) for `rllogger` / hardcoded deleted-module references before declaring
  the re-vendor complete.
