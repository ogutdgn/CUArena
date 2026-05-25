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

Base (proven, from the app README) + LOK/headless optimizations:

```sh
cd apps/libreoffice/libreoffice-codebase
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin   # strip mingw if present
./autogen.sh \
  --enable-release-build \
  --enable-mergelibs \
  --without-java --enable-python=no \
  --without-help --disable-xmlhelp \
  --disable-gtk3 --disable-gtk4 --disable-qt5 --disable-qt6 --disable-kf5 --disable-kf6 \
  --disable-cups --disable-dbus \
  --disable-avmedia --disable-gstreamer \
  --disable-libcmis --disable-firebird-sdbc --disable-postgresql-sdbc \
  --disable-mariadb-sdbc --disable-online-update --disable-extension-update \
  --disable-pdfimport --disable-librelogo --disable-opencl
make            # full first build (LOK is built as part of a normal make)
```

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
```
