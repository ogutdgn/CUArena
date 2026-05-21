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

Full first build: ~3 h cold, ~30 min if `external/tarballs` is pre-populated. `make sw sc sd` for incremental.

## Status

Phase 4 done (Writer UI parity with MS Word). Phase 3 logger V1.1 default-on. Calc + Impress equivalents (Phases 5–6) and Docker distribution (Phase 7) pending. See [docs/architecture/ROADMAP.md](docs/architecture/ROADMAP.md).
