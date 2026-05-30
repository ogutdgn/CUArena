# Execution map — MS Word clone

> **Purpose.** The phased build roadmap: what ships in each phase, the key
> deliverables, and where each research stream lands. This is the *what's next*
> companion to the locked decision record + research under [`research/`](research/)
> (engine, tech-stack, scope) and the grounding inventory at
> [`research/ribbon/README.md`](research/ribbon/README.md).
>
> Note on location: this lives under `apps/ms-word/` because the LibreOffice
> **engine** (rented via LOK) lives here. From now on this app directory is *the
> rented LibreOffice engine + the MS-Word-clone decision record & research*; the
> prior LibreOffice-reskin approach is superseded.

---

## Immediate next action

**Phase 2 — the live UI kit.** Phases 0–1 are **built and verified** on the `ms-word/build`
branch: the engine was re‑vendored to pristine LibreOffice, the LOK render/scheduler path + the
CMake/CTest harness are in, and the **A + B + C** verification bar is green (`ctest` → 5/5 — see
[`last-point.md`](last-point.md#build-status)). Next is the interactive QML window (Qt‑GUI ⇄
dedicated‑LOK‑thread tile canvas) and the design‑token control kit.

---

## What's decided (one-line recap)

- **Engine:** rent LibreOffice's real engine via **LibreOfficeKit (LOK), in-process** —
  "Boundary A": we own the UI + command dispatch + document state + an always-on
  raw/semantic/outcome logger + an MCP server; we rent the engine only for layout, text
  shaping, and `.docx`/`.odt` I/O. Discipline = scoped parity + a **no-core-edits**
  guardrail (the engine source stays committed and fully buildable; deeper patches are
  possible later as tracked patches if a feature justifies it).
- **Tech stack ("Option A"):** native **C++/Qt6** core driving LOK on one dedicated
  LOK-owning thread, **QML Fluent** UI for the chrome, and the **MCP server as a separate
  Python/TypeScript sidecar** over a local socket.
- **Scope (v1):** build the **~487-control** build surface (Free + Our-layer UI +
  Behavior shim + Optional, ≈70% of 692). Engine-gap / cloud-AI / niche families are
  **deferred and documented, not deleted**.
- **Why a rewrite:** the prior Qt6/QML prototype proved Boundary A works but audited as
  PoC-grade. We keep the proven architecture + this research + the audit's lessons and
  rebuild clean; the engine stays fully editable.

---

## Build phases

| Phase | Goal (one line) | Key deliverables |
|---|---|---|
| **0 — Merge & scaffold** ✅ | Land the decisions, stand up the fresh app. | Done: decisions/research merged to `main`; clone app scaffolded in `app/` on `ms-word/build`. |
| **1 — Foundations** ✅ | Get the LOK render/scheduler path and the test harness right this time. | Done: engine re-vendored to pristine LO; LOK binding + render path; deterministic pump (`Scheduler::ProcessEventsToIdle` under the SolarMutex — no test-only symbol); tile cache honoring the `INVALIDATE_TILES` dirty rect; real **CMake/CTest** harness + fixtures. Verified A+B+C green (`tst_tilegrid`/`tilecache`/`rendercontroller`, `tst_lok_smoke`, `tst_render_golden`). Live QML window + scroll/zoom/HiDPI carry into Phase 2. |
| **2 — UI kit** | Build the Word-faithful chrome on a token system. | UI design-token extraction (Word M365 exact colors / metrics / typography, measured at known DPI) as QML singletons; the bespoke custom QML control kit — ribbon, galleries, menus; Microsoft Fluent UI System Icons recolored to Word tints; the JSDialog → native QML dialog renderer, themed by the same tokens. |
| **3 — Feature build loop** | Ship the in-scope controls, group by group. | Per feature-group: behavior + state spec → implement → verify, walked in scope order across core editing / formatting + Insert / References / Mailings (full mail-merge via orchestrating LO's wizard) / Review (full Track Changes) / Layout / Design / View. |
| **4 — MCP server** | Expose the command/state surface as MCP. | The Python (FastMCP) or TypeScript **sidecar** over a local socket — Tools (`postUnoCommand` / `sendDialogEvent`) + Resources (`getCommandValues` / state). The core stays the single source of truth; the sidecar holds no state. |
| **5 — Verifier** | Grade RL tasks. | The verifier for the RL environment, fed by the Phase-3 behavior + state specs. |
| **6 — Distribution** | Run headless in a container. | Docker / headless distribution; parallel RL rollouts run as parallel processes / containers (LOK is single-threaded per document). |
| **Optional — Engine strip** | Shrink the rented engine. | Strip the LO engine to Writer-only. |

> **Every phase is gated by the [verification protocol](verification.md).** A deliverable is
> *done* only when its required tests are green headless and **fail when the claim is false**;
> the per-phase verification bar and the per-feature definition of done live there.

---

## Research streams → phases

Two of the six streams are done and locked; the rest are scheduled just-in-time.

| # | Stream | Status | Lands in |
|---|---|---|---|
| **#1** | Ribbon structure (Word ↔ LO, 692 controls) | ✅ done — [`research/ribbon/`](research/ribbon/) | grounds scope (Phase 0 / 3) |
| **#2** | Tech-stack decision | ✅ done — [`research/tech-stack.md`](research/tech-stack.md) | grounds Phases 1–6 |
| **#3** | Per-feature behavior + state specs (what each in-scope control does, how/where used, edge cases, and enabled/disabled/checked rules — e.g. Copy disabled with no selection) | future — just-in-time per feature-group | **Phase 3** (also feeds the verifier) |
| **#4** | UI design-token extraction (Word colors / metrics / icons / typography → QML tokens) | future | **Phase 2** |
| **#5** | MCP tool-surface design (map command/state surface to MCP tools + resources) | future | **Phase 4** |
| **#6** | Verifier design (how the RL env grades a task; fed by #3) | future | **Phase 5** |

---

## Deferred & documented (not deleted)

Doors kept open; the engine stays patchable. Per-tab cut rationale lives in each ribbon
tab doc's "Out of scope" section.

- **Group A — engine-gap families:** Draw/ink, SmartArt / Icons / 3D, WordArt text-effects,
  Building-Blocks galleries, Table of Authorities, APA/MLA style-citations, Style Sets.
  Future-add cost tiers: our-layer / cheap (Style Sets, Building Blocks) · bounded engine
  patch (Table of Authorities, style-citations) · huge even with engine work (ink/Draw,
  SmartArt, 3D).
- **Group B — cloud/AI:** Copilot, Dictate, Transcribe, AI Editor, Smart Lookup, Researcher,
  Acronyms, OneNote, Outlook, online pictures. Mostly our-layer additions later.
- **Group C — niche:** CJK envelopes/postcards, postal barcodes, M365 reading modes,
  Activation. Mostly our-layer additions later.
