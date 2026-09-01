# ms-word-native — the rented-engine attempt (superseded)

> **Superseded. Kept as a decision record, not continued.**
> This was the first attempt at the Word environment: a native **Qt6** app that owns the UI,
> command dispatch, document state and logger, and **rents LibreOffice's real engine** via
> **LibreOfficeKit (LOK)** for layout, text shaping and `.docx`/`.odt` I/O — the line called
> **Boundary A**. It was replaced by [`envs/ms-word`](../ms-word/) (Electron + ProseMirror)
> on 2026-06-03.
>
> **Read the decision first:**
> [`docs/decisions/engine-rent-vs-own.md`](../../docs/decisions/engine-rent-vs-own.md).

## Why this folder still exists

Because the decision that killed it is the most useful thing this repo learned, and the
argument is only credible with the artifact that produced it.

Renting a real engine buys correct layout, text shaping and `.docx` for free. What it sells
is the seam the whole repo depends on: to emit the `semantic` stream
([log contract](../../docs/log-contract.md)) you have to tap the point where an operation is
dispatched — and in a rented engine that point is inside somebody else's code. Every tap is
a patch to a vendored tree you have promised not to modify, and every upstream re-vendor
threatens it.

Writing [`rllogger/`](rllogger/) — the C++ three-stream logger, in this folder, working — is
what made that cost concrete. The replacement environment gets the same stream from one
function it owns (`dispatchTransaction`), by construction.

## What's here

| Path | What |
|---|---|
| [rllogger/](rllogger/) | **the artifact** — C++ raw/semantic/outcome logger built into the LO binary (`RawCapture` · `SemanticEmitter` · `OutcomeSnapshot` · `CommandMap`) |
| [docs/research/ribbon/](docs/research/ribbon/) | the **692-control Word ↔ LibreOffice ribbon comparison**, 10 tabs — still the best control inventory in the repo, and reused downstream |
| [docs/research/tech-stack.md](docs/research/tech-stack.md) | the stack evaluation that picked C++/Qt6 + QML + in-process LOK |
| [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) | Boundary A — process model, components, the no-core-edits guardrail |
| [docs/architecture/WRITER_CALC_EXTRACTION.md](docs/architecture/WRITER_CALC_EXTRACTION.md) | which LibreOffice modules can be stripped, and what breaks |
| [app/](app/) | Phases 0–1 as built — `mwcore` logic + `mwengine` LOK binding, CMake/CTest, tile render path with a golden-frame test |
| [docs/execution-map.md](docs/execution-map.md) · [docs/last-point.md](docs/last-point.md) | the plan and the state it stopped at |

## What is *not* here

The vendored LibreOffice source tree (`libreoffice-codebase/`, ~1.4 GB checked out, ~400 MB
in git objects) has been **removed from the tree and from git history**. Nothing here builds
as-is; that is intentional. The engine was pristine upstream LibreOffice at `1f1121d1`,
rented unmodified — it can be re-vendored from upstream if this line is ever revisited.

## How far it got

Phases 0–1, verified: a CMake/CTest harness, a real LOK binding (headless load / dispatch /
save round-trip), a tile render path with a golden-frame test, and the logger above. Phase 2
(live QML window + UI kit) never started.

The research did not die with the code — the ribbon inventory and the parity scoping fed the
environment that replaced it, and the whole experience is what
[`pipeline/`](../../pipeline/) exists to make cheaper.
