# Architecture — the MS Word clone

> **Purpose.** This is the canonical architecture record for the Microsoft Word clone
> we are building as a **CUA (computer-using-agent) RL environment** inside `cua-bench`.
> It states what we build, where the engine boundary sits, the process model, the
> components, and the discipline that keeps the build honest. Everything here is **decided**.
>
> Grounding lives in [`../research/ribbon/`](../research/ribbon/) (the Word↔LibreOffice
> ribbon comparison, 692 controls) and [`../research/tech-stack.md`](../research/tech-stack.md)
> (the tech-stack decision). This doc assumes both.
>
> Note on location: this lives under `apps/ms-word/` because the LibreOffice **engine**
> (rented via LOK) lives here. `apps/ms-word/` is now the rented engine **plus** the
> Word-clone decision record and research — the earlier LibreOffice-reskin approach is
> superseded (git history retains it).

---

## 1. What we are building

We are building a **native Qt6/C++ Microsoft-Word-like editor** that runs as an RL
environment for computer-using agents. The clone **owns** its entire interactive surface —
the UI, the command dispatch, the document state, an always-on raw/semantic/outcome logger,
and an MCP server for agent control — and **rents** LibreOffice purely as a document engine
through **LibreOfficeKit (LOK)** for layout, text shaping, and `.docx`/`.odt` I/O. The
fidelity bar is **scoped parity**: indistinguishable from Word within the scope we ship, with
out-of-scope entry points removed rather than stubbed. The grounded build surface is the
~487 controls (~70% of Word's ribbon) we can own with no engine reimplementation; the rest
is documented and deferred, not deleted.

---

## 2. Boundary A — the engine line

We draw the seam at the **LOK C API**. Everything that defines the product — what the agent
sees, what gets dispatched, what state exists, what gets logged — sits **above** the line and
is ours. Everything below is the rented LibreOffice engine, used only to lay out and persist
documents. We call this **Boundary A**.

```
┌──────────────────────────────────────────────────────────────────────────┐
│  OURS — native Qt6 / C++ core  (the product)                               │
│                                                                            │
│   ┌──────────────────────────────────────────────────────────────────┐   │
│   │  QML Fluent UI chrome                                             │   │
│   │  bespoke ribbon · galleries · menus · dialogs · design tokens     │   │
│   └──────────────────────────────────────────────────────────────────┘   │
│                                ▲   ▲                                       │
│        document pixels (tiles) │   │ commands / state / dialog events      │
│                                │   ▼                                       │
│   ┌───────────────┐  ┌─────────────────────────┐  ┌────────────────────┐  │
│   │ tile renderer │  │ command / dispatch seam │  │ document & state    │  │
│   │ (paintTile)   │  │ (logging + MCP hook)    │  │ (single source of   │  │
│   └───────────────┘  └─────────────────────────┘  │  truth)             │  │
│           ▲                    ▲                   └────────────────────┘  │
│           │          ┌─────────┴──────────┐  ┌──────────────────────────┐  │
│           │          │ JSDialog → QML     │  │ raw / semantic / outcome │  │
│           │          │ dialog renderer    │  │ logger (always on)       │  │
│           │          └────────────────────┘  └──────────────────────────┘  │
│   ┌───────────────────────────────────────────────────────────────────┐   │
│   │ engine binding (the only code that talks to LOK)                  │   │
│   └───────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────│───────────────────────────────────────┘
                                      │
============================  LOK C API  ====================================
  postUnoCommand · paintTile · getCommandValues · sendDialogEvent ·
  registerCallback (INVALIDATE_TILES, …) · documentLoad / saveAs
=============================================================================
                                      │
┌────────────────────────────────────│───────────────────────────────────────┐
│  ENGINE — LibreOffice, rented (below the line)                             │
│  layout · text shaping · .docx / .odt I/O · the .uno: command surface      │
│  no product logic, no UI of ours; never edited to chase a feature          │
└──────────────────────────────────────────────────────────────────────────┘
```

**Why the line is here.** LOK is a stable, documented C boundary that exposes exactly the
three things we need from an engine — dispatch a command (`postUnoCommand`), read state
(`getCommandValues`), and get rendered pixels (`paintTile`) plus dirty-region callbacks. It
does **not** impose a UI. That lets us keep the entire interactive surface (the part that has
to *be* Word) on our side, where we control fidelity, logging, and the agent contract, while
the engine does only the work that is genuinely hard and not worth reimplementing: reflow,
shaping, and file fidelity. The ribbon research confirms the line holds — engine gap is **0**
across core editing, formatting, Track Changes, Mail Merge, References, and Layout; every gap
that exists is a cuttable feature family, never core document work.

---

## 3. Process model

The core is **one native process**. Inside it, LOK runs **in-process on one dedicated
LOK-owning thread** — LOK is single-threaded per document, so a single thread owns the
document and is the only thread allowed to call into the engine. We advance the engine with a
**synchronous scheduler-pump step boundary**: each agent/RL step drives the LOK scheduler to
quiescence before the step is considered done, so observations are deterministic and a step
maps to a settled document state rather than a race against background idle work. Parallel RL
rollouts are achieved with **parallel processes / containers**, not threads — one document per
process.

The **MCP server is a separate sidecar process** (Python via FastMCP, or TypeScript) talking
to the core over a **local socket** (Unix domain socket in production; TCP for Windows
development). MCP is a first-class goal and there is no mature C++ MCP SDK, so the one
unavoidable process boundary is placed exactly where C++ is weak. The **core stays the single
source of truth**; the sidecar holds **no state** of its own — it bridges MCP **Tools**
(`postUnoCommand`, `sendDialogEvent`) and MCP **Resources** (`getCommandValues`, document
state) to and from the core.

```
   ┌──────────────────────────────┐         local socket          ┌────────────────────┐
   │  CORE  (one native process)  │  ◀───────────────────────────▶ │  MCP SIDECAR        │
   │  Qt6/C++ + QML UI            │   UDS (prod) / TCP (Win dev)   │  Python (FastMCP)   │
   │                              │                                │  or TypeScript      │
   │  ┌────────────────────────┐  │   Tools:    postUnoCommand,    │  (stateless bridge) │
   │  │ LOK-owning thread      │  │             sendDialogEvent    └────────────────────┘
   │  │ (in-process engine,    │  │   Resources: getCommandValues,
   │  │  synchronous pump)     │  │              state
   │  └────────────────────────┘  │
   └──────────────────────────────┘
```

Rejected alternatives (see [`../research/tech-stack.md`](../research/tech-stack.md)): a
web/two-process split (worst RL/headless fit, contradicts the native constraint) and a
single-language Rust/Go/Python core over LOK FFI (every LOK binding is conversion-only, so the
whole interactive surface would be greenfield unsafe FFI against an unstable API).

---

## 4. Components

Everything in this table is **ours**, above Boundary A.

| Component | Responsibility | Notes |
|---|---|---|
| **Engine binding** | The only code that calls LOK. Loads/saves documents, posts UNO commands, reads command values, drives the scheduler pump. | Isolates the rented engine behind one seam; runs on the LOK-owning thread. |
| **Tile renderer** | Turns the document into on-screen pixels via LOK `paintTile` into a tile buffer, presented in the QML canvas. | Toolkit-independent — the canvas is just LOK's tile buffer, so the pixels are Word-faithful regardless of Qt. Honors the `INVALIDATE_TILES` dirty rect; tile cache + zoom/scroll/HiDPI (see §6). |
| **Command / dispatch seam** | Single chokepoint every command flows through before reaching the engine. | **This is where logging and the MCP hook attach.** One seam ⇒ every action is observable and replayable. |
| **Document & state** | The single source of truth for document and app state (selection, cursor, formatting-at-cursor, and our-layer state the engine doesn't model). | Drives enabled/disabled/checked control states; the sidecar never duplicates it. |
| **Dialogs (JSDialog → QML)** | Renders LO's JSDialog JSON widget trees as **native QML dialogs**, themed by the design tokens; routes widget events back via `sendDialogEvent`. | Lets us reuse the engine's dialog logic while keeping the look entirely ours. |
| **UI (ribbon / galleries / menus)** | The bespoke Word-faithful chrome: a data-driven ribbon, galleries with live preview, menus. | No stock "Word ribbon" exists in any toolkit — these are custom QML controls. Fidelity comes from the **design-token system** (QML singletons: Word M365 colors, measured metrics, typography). |
| **Logging (raw / semantic / outcome)** | Always-on three-stream logger fed by the dispatch seam: `raw[]` input events, `semantic[]` commands, `outcome{}` end state. | The repo's cross-app three-stream log contract; feeds the verifier. |
| **MCP sidecar** | Separate stateless process exposing the command/state surface to agents as MCP Tools + Resources over the local socket. | Bridges to the core; see §3. |

---

## 5. The no-core-edits guardrail

We **rent** the engine; we do not fork its behavior to chase features. The guardrail:

- **We never edit LO engine logic to add or change a feature.** If a feature isn't reachable
  through the existing `.uno:` surface, it is a scope decision (build it in our layer, shim
  it, or defer it) — not a reason to patch the engine.
- **The one sanctioned engine touch** is registering dialogs in
  `vcl/jsdialog/enabled.cxx` — i.e. *exposing* existing engine dialogs to the JSDialog path so
  our QML dialog renderer can present them. This exposes, it doesn't change behavior.
- **The guardrail is policy, not a wall.** The engine source is committed and fully
  buildable/patchable. Deeper engine patches remain possible later as **tracked patches** if a
  specific feature justifies the cost — accepting that each patch adds fork-maintenance burden.
  The default is to stay off the engine; deviating is a deliberate, recorded decision.

This is what keeps the project a **front-end + orchestration build**, not an engine
reimplementation, and what keeps the rented engine cheap to carry.

---

## 6. Getting it right this time

A prior Qt6/QML prototype proved Boundary A works end to end — LOK binding, a JSDialog→QML
dialog renderer, a contract logger, a command catalog, and a data-driven ribbon. A multi-agent
audit also found it **PoC-grade**, and the rewrite keeps the proven architecture, this
research, and the audit's lessons while treating two foundations as things we must nail
**first**, before feature work:

- **A correct LOK render / scheduler path.** The prototype's render path `dlsym`'d a
  test-only engine symbol and full-repainted on every keystroke — no tile cache, no zoom,
  scroll, or HiDPI. The rewrite uses a **real idle mechanism that honors the `INVALIDATE_TILES`
  dirty rect** (repaint only what changed), backed by a **tile cache** and proper **zoom /
  scroll / HiDPI** handling. This is the difference between a demo and a usable editor.
- **A real CMake / CTest harness with committed fixtures.** The prototype's "ledger" was not
  credible — no CTest runner, and the one test passed only on a blank page. The rewrite ships a
  genuine **CMake/CTest** harness with **committed fixtures**, where **tests fail when the
  claim is false**. The audit also flagged arithmetically broken dialog metric-fields and a
  ribbon with no widget registry or orchestration layer; the rewrite fixes the dialog metrics
  and builds the ribbon on a real widget registry + orchestration layer so it scales to the
  ~487-control surface.

The verdict was a **clean rewrite**, not a salvage: keep the architecture, the research, and
the lessons; rebuild the implementation; the engine stays fully editable.

---

## 7. Distribution

The clone ships as a **multi-stage Docker** image built for **headless** operation
(offscreen platform + software rendering), suitable for parallel RL rollouts as parallel
containers. The LibreOffice **engine is built to a binary** in the build stage and only the
binary is copied into the runtime image — **engine source never ships**. The core process, the
QML UI assets, and the MCP sidecar are packaged alongside it. This is Phase 6 of the build
roadmap; earlier phases run the same core natively for development.

---

## See also

- [`../research/ribbon/`](../research/ribbon/) — the Word↔LibreOffice ribbon comparison
  (692 controls; the build-surface / engine-gap grounding for scope and the engine line).
- [`../research/tech-stack.md`](../research/tech-stack.md) — the locked tech-stack decision
  (native C++/Qt6 core + in-process LOK + MCP sidecar) and the rejected alternatives.
