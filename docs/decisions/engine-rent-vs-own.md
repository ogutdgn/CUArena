# ADR — Rent the document engine, or own the model?

- **Status:** Decided (own the model). Cross-environment; supersedes the native line.
- **Date decided:** 2026-06-03 (locked in `envs/ms-word` ADR-0001 / ADR-0002)
- **Applies to:** any environment in this repo whose app has a real document format

## Context

An environment in this repo has to emit three streams
([log-contract.md](../log-contract.md)): `raw` input events, `semantic` operations, and an
`outcome` document snapshot. `raw` is easy anywhere. `semantic` and `outcome` are the ones
the verifier reads, and both require reaching *into* the thing that owns the document.

Microsoft Word forced the question, because Word has a real document format. Two ways to
get one:

- **Rent:** vendor a real engine (LibreOffice, driven through LibreOfficeKit) and build
  your own UI, dispatch and state on top of it — "Boundary A" in
  [`envs/ms-word-native`](../../envs/ms-word-native/). You inherit correct layout, text
  shaping and `.docx` I/O for free.
- **Own:** implement the document as a schema'd model you control (ProseMirror) and pay
  for layout yourself.

Both were built far enough to judge.

## Decision

**Own the model.** The Electron + ProseMirror line in
[`envs/ms-word`](../../envs/ms-word/) is the one that ships; the native Qt6 + LOK line is
preserved as a decision record, not continued.

## Rationale

The deciding artifact is [`rllogger`](../../envs/ms-word-native/rllogger/) — the C++
three-stream logger written for the rented engine. It works. Writing it is what made the
cost visible:

| | Rent (LOK) | Own (ProseMirror) |
|---|---|---|
| layout / shaping / `.docx` | free, correct | reimplemented, approximate |
| `semantic` stream | a patch inside a 1.4 GB vendored tree, at a dispatch point you do not own | `dispatchTransaction` — one function in your own code |
| operation granularity | UNO commands, mapped by hand (`CommandMap.cxx`) | serialisable, invertible PM Steps, by construction |
| `outcome` snapshot | extracted across the LOK boundary | `state.doc.toJSON()`, headless in Node |
| upstream re-vendor | threatens every tap | not applicable |
| repo cost | ~400 MB of vendored engine in git history | none |

The rented engine gives you the half of the problem that is *already solved elsewhere*, and
charges you the half that is *specific to this repo*. Instrumentation is not a feature that
gets bolted onto an environment afterwards — it is the reason the environment exists. So it
has to sit in code you own.

## What was actually given up

This is a real trade, not a free win:

- **Layout fidelity.** The owned model approximates on-screen pagination; PDF/print export
  is paginated for real by Chromium, but per-sheet reflow with repeated headers/footers is
  not the same thing as a typesetting engine. Documented in the env's `NOT_IMPLEMENTED.md`.
- **`.docx` round-trip is structural, not byte-identical.** Gated by a round-trip test
  rather than by an engine guarantee.
- **The native work.** Phases 0–1 (CMake/CTest harness, LOK binding, tile render path,
  golden-frame test) and the 692-control ribbon study. The research survives and was reused;
  the C++ did not.

## Consequences

- Every future environment with a real document format starts from "own the model", and
  the log contract is a design input, not an afterthought.
- `envs/ms-word-native` stays in the tree, without its vendored engine (removed from git
  history — it was ~400 MB), because the argument above is only credible with the artifact
  that produced it.
- Environments whose app has no document format (Figma-style canvases) never faced this
  question: they own the model by default. That is why Stage 1 never had to answer it, and
  why Stage 2 is where the repo learned something.
