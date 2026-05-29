# Research catalog — MS Word clone

> **Purpose.** This folder is the home for **all research that grounds the MS Word clone
> decisions**. Each stream is a question we have to answer with evidence before (or during)
> the build; when a stream's work is complete, its findings are written here as docs —
> exactly like [`ribbon/`](ribbon/), which holds the verified Word↔LibreOffice ribbon
> comparison. Decisions cite this folder; this folder does not speculate beyond what's
> verified.
>
> Note on location: it lives under `apps/libreoffice/` because the LibreOffice **engine**
> (rented via LOK) lives here. `apps/libreoffice/` is now the rented LibreOffice **engine**
> plus the MS Word clone **decision record & research**; the eventual home may move to
> wherever the clone app lives.

---

## The six research streams

| # | Stream | Scope | Status | Output |
|---|---|---|---|---|
| **#1** | Ribbon structure | Word↔LO control inventory across all ribbon tabs; classify the build work each control implies; ground the engine decision and parity scope | ✅ **DONE** | [`./ribbon/`](ribbon/) |
| **#2** | Tech-stack decision | Pick the implementation stack and process architecture (engine binding, UI toolkit, MCP boundary) on evidence | ✅ **DONE** | [`./tech-stack.md`](tech-stack.md) |
| **#3** | Per-feature behavior + state specs | Per in-scope control: what it does, how/where it's used, edge cases, and **state rules** (enabled/disabled/checked — e.g. *Copy* disabled with no selection). Feeds both the build and the verifier | ⏳ **FUTURE** — build-time, just-in-time per feature-group | (written at build time) |
| **#4** | UI design-token extraction | Word M365 exact colors, metrics, icons, typography → QML design-token singletons | ⏳ **FUTURE** — early in the build | (written early in build) |
| **#5** | MCP tool-surface design | Map the clone's command/state surface to MCP tools + resources for the sidecar server | ⏳ **FUTURE** — MCP phase | (written in MCP phase) |
| **#6** | Verifier design | How the RL environment grades a task; fed by stream #3 | ⏳ **FUTURE** — verifier phase | (written in verifier phase) |

---

## #1 — Ribbon structure (DONE)

The completed inventory lives in [`ribbon/`](ribbon/). Headline numbers:

- **692 controls** enumerated across **all 10 Word ribbon tabs** (Home, Insert, References,
  Mailings, Review, Layout, Design, View, Draw, Help).
- Each control is diffed against LibreOffice's `.uno:` command surface and classified into a
  **work bucket**:

  | Bucket | Total | Share |
  |---|--:|--:|
  | Free (wire the existing LO command) | 89 | 13% |
  | Our-layer UI (build the Word-faithful UI, dispatch the LO command) | 231 | 33% |
  | Behavior shim (massage in our dispatch layer) | 144 | 21% |
  | Engine gap (LO engine genuinely can't) | 114 | 16% |
  | Cut (out of scope; entry point removed) | 91 | 13% |
  | Optional our-layer feature | 23 | 3% |

- **The build surface we own** (Free + Our-layer UI + Behavior shim + Optional) = **487 (~70%)**.
- **Engine gap is zero in core document work** (editing, formatting, Track Changes, Mail Merge,
  References, Layout all map to LO commands) and falls **entirely on cuttable feature families**
  — the whole Draw/ink tab, Insert building-blocks + rich-media, Review Ink/TTS, Home rich
  typography, View M365 reading-modes, References Table-of-Authorities/style-citations, Design
  Style-Sets, and Layout section-artifacts.

This evidence locked the engine decision: **LibreOffice via LOK in-process (Boundary A) + scoped
parity + a no-core-edits guardrail**. See [`ribbon/README.md`](ribbon/README.md) for the full
per-tab tally and methodology.

---

## #2 — Tech-stack decision (DONE)

The stack analysis lives in [`tech-stack.md`](tech-stack.md). It locks the implementation stack:
a native **C++/Qt6 core** driving LOK in-process on one dedicated LOK-owning thread, **QML
Fluent UI** chrome (document pixels come from LOK's tile buffer), and the **MCP server as a
separate Python/TypeScript sidecar** over a local socket — because there is no mature C++ MCP
SDK and MCP is a first-class goal. The core stays the single source of truth; the sidecar holds
no state.

---

## Method

Research here is **verified, not assumed**. The ribbon stream (#1) ran a multi-agent pipeline
per tab:

```
multi-source extraction  →  reconcile into  →  map to LO     →  verify against     →  adversarial
(official idMso list ·       one canonical      .uno: command     the LO source         QA (completeness
 MS docs · reference sites)  control list                          tree (.sdi/.xcu)      + flags)
```

The cross-checking is the point: independent layers corrected each other's errors. Confidence
is recorded per tab.

**Streams #3 and #4 are done just-in-time during the build, not upfront** — #3 group by group
as each feature-group is implemented (behavior + state spec → implement → verify), and #4 early
in the build before the control kit is assembled. #5 and #6 land in their respective build
phases. Doing this research at build time keeps the specs honest against the actual engine
behavior rather than against a guess made months earlier.

---

## One-off decision-support investigations

Two investigations were run this session to support the decisions above; they are not standing
research streams:

- **Writer-app audit** — a multi-agent audit of the prior Qt6/QML `writer` prototype. It
  confirmed Boundary A works but found the prototype PoC-grade (test-only render symbol,
  full-repaint per keystroke, non-credible test ledger, broken dialog metric-fields, a ribbon
  that doesn't scale), motivating a clean rewrite that keeps the proven architecture.
- **Tech-stack comparison** — the evaluation behind stream #2's locked "Option A" (native
  C++/Qt6 + LOK in-process + MCP sidecar), rejecting the web/two-process and single-language
  FFI alternatives.
