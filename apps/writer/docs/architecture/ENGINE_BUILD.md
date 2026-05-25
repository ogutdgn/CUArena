# Engine Build Recipe — Writer-only headless LOK (W1)

> How we build the LibreOffice engine down to a **headless, Writer-only
> LibreOfficeKit (LOK)** that our Qt app links against. All `--enable/
> --disable` flags below were verified to exist in this tree's
> `configure.ac` (W0). Engine tree:
> `apps/libreoffice/libreoffice-codebase/`.
>
> Last updated: 2026-05-25 (W1 design; not yet executed — blocked on build deps).

---

## 1. Configure line

**ACTUAL working line (W1, 2026-05-25, built LO 26.8.0.0.alpha0):**

```sh
cd apps/libreoffice/libreoffice-codebase
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin   # strip mingw if present
./autogen.sh \
  --without-java --enable-python=no \
  --without-help --disable-xmlhelp \
  --disable-gtk3 --disable-gtk4 --disable-qt5 --disable-qt6 --disable-kf5 --disable-kf6 \
  --disable-avmedia \
  --disable-libcmis --disable-firebird-sdbc --disable-postgresql-sdbc \
  --disable-mariadb-sdbc --disable-online-update --disable-extension-update \
  --disable-pdfimport --disable-librelogo --disable-opencl
make            # LOK is built as part of a normal make
```

**Flags dropped from the original plan** (configure rejected or unconfirmed,
under `--enable-option-checking=fatal`): `--disable-gstreamer` (not a valid
option), `--disable-cups`, `--disable-dbus`, `--enable-mergelibs`,
`--enable-release-build` (no `AC_ARG_ENABLE` / rejected). These are deferred
optimizations — the baseline build works without them. Revisit `mergelibs`
(smaller/faster LOK) in a later pass. Note: **without mergelibs there is no
`libmergedlo.so`** — LOK loads via `libsofficeapp.so` + the individual libs
(188 `.so` in `instdir/program`, ~622 MB). `lok_init` dlopens them at runtime.

### Why each addition (vs the README base)

| Flag | Why |
|---|---|
| `--enable-mergelibs` | Merge libs into `libmergedlo` — smaller footprint + faster LOK startup; standard for LOK/Online deployments. |
| `--disable-gtk3/gtk4/qt5/qt6/kf5/kf6` | **We provide the UI (Qt6, ours). The engine runs headless** via the `svp` VCL backend. No native LO UI backend is needed. Disabling them removes the gtk/qt/cups build-dep chain. *Consequence:* `libreofficekitgtk` + `gtktiledviewer` won't build — fine, we use the **core LOK C API** (`LibreOfficeKitInit.h` → `libmergedlo`), not the gtk glue. |
| `--disable-cups --disable-dbus` | No printing / desktop bus in an RL runtime. (cups dev was missing locally; this removes the need.) |
| `--disable-avmedia --disable-gstreamer` | No audio/video in a text RL env. |
| `--enable-release-build` | Product/release (not debug) — faster runtime for the RL env. |
| `--enable-python=no`, `--without-java` | No scripting bridges; we drive via LOK/UNO from our own process. |

**Conservative on purpose:** we do *not* add `--with-system-*` (keep LO's
bundled externals — robust, reproducible) and do not over-disable beyond the
clearly-unneeded. Tune further only if a specific module proves unnecessary.

---

## 2. What LOK actually is here (link surface for the Qt app)

- LOK is built by a normal `make` (no special "enable-lok" flag).
- Init entrypoint: `include/LibreOfficeKit/LibreOfficeKitInit.h`
  (`lok_init` / `lok_init_2`) loads the engine from `instdir/program`.
- C++ API wrapper: `include/LibreOfficeKit/LibreOfficeKit.hxx` (`lok::Office`,
  `lok::Document`).
- With `--enable-mergelibs`, the engine lives in
  `instdir/program/libmergedlo.so` (+ `soffice.bin`). Our app passes
  `instdir/program` to `lok_init`.
- We do **not** link `libreofficekitgtk` (gtk glue) — disabled.

---

## 3. Proof-of-life (W1 exit gate)

After a green build, prove the engine works headless (no GUI):

Option A — reuse the in-tree headless test (fastest first signal):
```sh
make CppunitTest_libreofficekit_tiledrendering    # exercises load+paintTile+uno headless
```

Option B — our own minimal C harness (we write this in W1):
- `lok_init("instdir/program")`
- `documentLoad("private:factory/swriter")` (or a test .docx)
- `initializeForRendering`, `getDocumentSize`, `paintTile` → assert non-empty bitmap
- `postUnoCommand(".uno:Bold")`, type text via `postKeyEvent`
- `saveAs("/tmp/out.docx", "docx")` → assert file exists & re-loads
- print OK

Document the exact run + output in `docs/progress/`. **Exit when:** engine
builds Writer-only; LOK loads + paints + dispatches + saves a .docx headless;
link surface (above) recorded.

---

## 4. Strip plan (AFTER first green build — D5)

Order matters; keep a known-good baseline first. Build-verify after each group:

1. Build vanilla-flagged Writer engine + proof-of-life (above) → baseline.
2. Delete **Calc** (`sc/`), **Impress** (`sd/`), **Math** (`starmath/`) +
   their `Module_*`, `Repository.mk` entries, and any cross-refs. `make` +
   proof-of-life after each.
3. Delete remaining peer modules not already removed in the old Phase 1.
4. **Do not touch the shared core** (vcl, sfx2, svx, editeng, framework,
   oox, writerfilter, sax, i18n, font/shaping) — Writer + LOK need it (D5).

Note: the old paused branches (`chore/strip-to-writer-calc-impress`,
`refactor/apps-core-folder-split`) failed at stripping (manifest/gbuild
breakage) — reference their commit messages, do **not** cherry-pick. Strip
incrementally, build-verified, reversible.

---

## 5. Build-dependency note (owner action — needs sudo)

The disabled backends (gtk/qt/cups) shrink the dependency set, but the most
robust install remains the canonical LO build-dep set. See the session
progress note for the exact `sudo apt` commands. Qt6 dev is needed
separately for **our** app (W2), independent of the engine.

Cold first build ≈ 3 h (the local `external/tarballs` cache is empty, so all
externals download + compile). Incremental: `make sw` etc.

---

## 6. W1 RESULT — built + proof-of-life PASSED (2026-05-25)

Engine built: **LibreOfficeDev 26.8.0.0.alpha0**, `instdir` ~622 MB, 188
`.so`. Headless smoke (`SAL_USE_VCLPLUGIN=svp`): `--version` OK; txt→docx
(filter "Office Open XML Text") and txt→pdf both OK.

**LOK proof-of-life** (`apps/writer/tests/lok_proof_of_life.cpp`) PASSED:
headless `lok_cpp_init` → `documentLoad(private:factory/swriter)` →
`getDocumentSize` (12808×16408 twips) → `postUnoCommand(.uno:InsertText, .uno:Bold)`
→ `paintTile` (256×256, rendered content) → `saveAs` docx+odt. Verified the
saved **docx contains our exact text + `<w:b/>` bold run** → `.uno` dispatch
takes effect and docx fidelity is preserved. **Boundary A proven end-to-end.**

### Gotchas / lessons (for reproducibility + Docker, Phase W7)

- **Missing gitignored files had to be restored** (dropped in the vendored
  import because LO's own `.gitignore` ignores them):
  - `config.guess` + `missing` → copied from `/usr/share/automake-1.16/`.
  - `.vscode/vs-code-template.code-workspace.in` → created as `{}` (IDE
    template referenced by `AC_CONFIG_FILES`; non-essential).
  - `desktop/scripts/soffice.sh` (`.gitignore` line 105) → fetched from LO
    upstream (`raw.githubusercontent.com/LibreOffice/core/master`). This is
    the launcher copied to `instdir/program/soffice`; the build's final
    `Package.mk` step fails without it. **A Docker build must restore these
    four files before `make`.**
- **autogen caches flags in `autogen.lastrun`** — `rm autogen.lastrun` before
  re-running with changed flags, or it reuses the old set.
- **LOK client compiles header-only**: `g++ -I <engine>/include foo.cpp -ldl`
  — `lok_init` dlopens the engine at runtime; **no linking against LO libs**.
- **Tiled-rendering API is behind `#define LOK_USE_UNSTABLE_API`** (before
  including the header) — else `paintTile`/`postUnoCommand`/`getDocumentSize`
  are not declared.
- **`saveAs` format is the extension** (`"docx"`, `"odt"`, `"pdf"`), NOT the
  full filter name.
- **Dev-build LOK teardown (`delete office`) aborts (SIGABRT)** on shutdown —
  a known dev-build quirk, irrelevant to functionality. The real app keeps the
  `Office` alive for its lifetime; the harness bypasses teardown with `_exit(0)`.
- **Engine `rllogger` is compiled in and on by default** — set
  `LO_RL_LOG_DISABLE=1` when driving via LOK (our own logger replaces it, D7).
- **Strip (Calc/Impress/Math) NOT yet done** — baseline built full; strip is
  deferred (optimization, not a blocker). See §4.
```
