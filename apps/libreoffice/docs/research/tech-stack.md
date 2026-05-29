# Tech-stack decision

> **Purpose.** This is **MS Word clone decision-research** (research stream #2). It records
> the tech-stack decision for the clone: the language and process model for the core, where the
> LibreOffice engine lives, how the chrome is rendered, and where the MCP server sits. The companion
> doc is the ribbon comparison at [`ribbon/README.md`](ribbon/README.md), which establishes *what*
> we build (the ~487-control build surface); this doc establishes *how* it is built.
>
> Note on location: this lives under `apps/libreoffice/` because the LibreOffice **engine** (rented
> via LOK) lives here. The eventual home may move to wherever the clone app lives.

---

## 1. The decision

**Native C++/Qt6 core driving LOK in-process + QML Fluent UI for the chrome + an MCP server as a
separate Python/TypeScript sidecar over a local socket. This is "Option A".**

The core is a single native C++ process. It owns the UI, the command dispatch, the document state,
the always-on raw/semantic/outcome logger, and it drives the LibreOffice engine through
LibreOfficeKit (LOK) on one dedicated LOK-owning thread. All chrome is QML (Qt's Fluent style as the
base; the ribbon, galleries, menus, and dialogs are bespoke custom QML controls). The MCP server
runs as a stateless sidecar in a separate process, speaking to the core over a local socket.

This is the "Boundary A" architecture from the engine decision: **we own the UI + dispatch + state +
logger + MCP; we rent the engine only for layout, text shaping, and `.docx`/`.odt` I/O.**

---

## 2. The four gating constraints

The stack has to satisfy four hard requirements at once, and they pull in different directions:

| # | Constraint | What it demands |
|---|---|---|
| **1** | **LOK interop** | We rent LibreOffice's real engine via LibreOfficeKit, in-process. The interactive surface (dispatch, tile paint, dialog events, command state) must be reachable cheaply and synchronously. |
| **2** | **MCP first-class** | An MCP server is a first-class goal, not an afterthought — the RL env exposes the document's command + state surface as MCP tools and resources. |
| **3** | **Professional Word-M365 UI** | The chrome must be indistinguishable-at-a-glance from Word M365 within scope (the bespoke ribbon, galleries, menus, themed dialogs), backed by a design-token system. |
| **4** | **RL / headless / Docker** | The whole thing runs headless in a container for RL rollouts, with a deterministic step boundary and parallel rollouts. |

The tension: constraint **1** forces a C/C++ in-process core (see §3), which is exactly the
environment where MCP (**2**) has no good native option, and where building a professional UI (**3**)
and a clean headless/deterministic runtime (**4**) are non-trivial. The decision is about resolving
this tension with the fewest compromises — putting each piece where it is strongest and the one
unavoidable process boundary where C++ is weakest.

---

## 3. Why the stack is heavily constrained

The space of real choices is much smaller than it looks, because **LOK's interactive surface is
C/C++-in-process only.** The interactive entry points — dispatching commands (`postUnoCommand`),
painting tiles (`paintTile`), feeding dialog events (`sendDialogEvent`), reading command state
(`getCommandValues`) — are a C/C++ API designed to be called in the same process as the engine.

Every LOK binding in another language (Rust, Python, Go) is **conversion-only**: it wraps the I/O
and document-lifecycle calls, not the live interactive surface. Driving the interactive surface from
one of those languages would mean writing greenfield, unsafe FFI against an unstable C++ API — the
worst possible place to be.

So the conclusion is forced: **there is always a C++ LOK core.** That is not a free variable. The
only real choices left are:

1. **The UI chrome** — native (Qt/QML) vs. a web front-end.
2. **Where MCP lives** — in-process in the C++ core, or in a separate sidecar process.

Everything below is about those two choices.

---

## 4. Options compared

| Option | Core | UI chrome | MCP | Verdict |
|---|---|---|---|---|
| **A — native (recommended)** | C++/Qt6, in-process LOK | QML Fluent (bespoke ribbon) | Python/TS sidecar over local socket | **Chosen** |
| **Runner-up — in-process C++ MCP** | C++/Qt6, in-process LOK | QML Fluent | MCP inside the C++ core | Close, but no mature C++ MCP SDK |
| **Rejected — web / two-process** | C++ LOK service + web UI | browser / web | either | Worst RL/headless fit; contradicts the native constraint |
| **Rejected — single-language FFI** | Rust/Go/Python over LOK FFI | that language's toolkit | native | Conversion-only bindings; interactive surface is unsafe greenfield FFI |

**A — native (recommended).** A single native C++/Qt6 process owns everything except MCP. The
document canvas is LOK's tile buffer blitted into a QML surface, so the chrome toolkit is independent
of the engine. Determinism, headless operation, and small containers all fall out naturally (§6).
The one weakness — MCP has no native home — is pushed out to a sidecar (§5), exactly where C++ is
weakest anyway.

**Runner-up — in-process C++ MCP.** Architecturally the cleanest: MCP lives in the same process as
the state it serves, no socket, no second language. The blocker is practical, not conceptual —
**there is no mature C++ MCP SDK.** Choosing this means building and maintaining MCP plumbing in
C++ by hand, against a first-class project goal, when a battle-tested SDK exists one process boundary
away. The cost outweighs the elegance, so it is the runner-up rather than the pick.

**Rejected — web / two-process.** A C++ LOK service behind a web UI is the worst fit for the RL
target: it adds a browser/web stack, complicates headless and deterministic stepping, and contradicts
the native constraint that the whole point of Option A is to honor.

**Rejected — single-language Rust/Go/Python FFI.** Tempting for a one-language codebase, but every
LOK binding outside C++ is conversion-only. The interactive surface would be greenfield, unsafe FFI
against an unstable engine API — taking on the hardest possible integration to avoid a second
toolchain.

---

## 5. MCP placement

MCP lives in a **separate, stateless sidecar process**, written in **Python (FastMCP) or TypeScript**,
talking to the core over a **local socket** (a Unix domain socket in production; TCP for
Windows-dev). This is forced by §4: there is no mature C++ MCP SDK, and MCP is a first-class goal, so
the sidecar buys a battle-tested SDK at the cost of one process boundary — placed exactly where C++
is weak.

The discipline that keeps this clean:

- **The core is the single source of truth.** All document state, command dispatch, and logging stay
  in the C++ core.
- **The sidecar holds no state.** It is a thin bridge: it exposes **Tools** (`postUnoCommand`,
  `sendDialogEvent`) and **Resources** (`getCommandValues`, state) by forwarding to the core and
  returning the result.

Because the core is the source of truth and the sidecar is stateless, the one process boundary in the
system carries no risk of divergent state — it is a transport, not a second brain.

---

## 6. RL / headless / Docker fit

Option A is the best fit for the RL target precisely because it is single-process and native:

- **Offscreen + software QPA.** Qt runs with an offscreen / software rendering platform, so there is
  no display server requirement; the document pixels come from LOK's tile buffer (a `paintTile`
  memcpy), which is rendered the same way headless or not.
- **Deterministic step boundary.** LOK is single-threaded per document and runs on one dedicated
  LOK-owning thread; a synchronous scheduler-pump step boundary gives the RL loop a deterministic
  "advance one step" semantics rather than racing an async event loop.
- **Small container.** A single native binary plus the engine and a thin sidecar is a compact image —
  no browser, no web runtime.
- **Parallel = N containers.** Because LOK is single-threaded per document, parallelism is achieved by
  running parallel processes / containers (N rollouts = N containers), not by threading a single LOK
  instance.

---

## 7. Key trade-offs and risks

The decision is deliberate, but it is not free. The known costs:

- **Two toolchains.** The core is C++/Qt6 and the sidecar is Python/TypeScript. This is an accepted
  cost: it is what buys a mature MCP SDK and keeps the one unavoidable boundary where C++ is weakest.
- **`dlsym` scheduler-pump engine-sensitivity.** Driving the LOK scheduler pump for the deterministic
  step boundary depends on engine internals. The prior prototype reached the render path by `dlsym`-ing
  a **test-only** engine symbol — not viable for the rewrite. Phase 1 of the build replaces this with a
  correct, real LOK render/scheduler path: a real idle mechanism that honors the `INVALIDATE_TILES`
  dirty rect, a tile cache, and zoom/scroll/HiDPI support.
- **JSDialog `enabled.cxx` maintenance.** The only sanctioned engine touch is registering dialogs in
  `vcl/jsdialog/enabled.cxx` so their JSON widget trees render as native QML dialogs. This is an
  ongoing maintenance surface against the engine source, governed by the no-core-edits guardrail.
- **Pixel-determinism needs locked fonts + DPI + a golden-frame test.** Because the canvas is real
  rendered pixels, reproducible output requires locked fonts (metric-compatible open substitutes such
  as Selawik for Segoe UI in the distributed image) and a fixed DPI, verified by a golden-frame test in
  the CMake/CTest harness.

---

## Summary

LOK's interactive surface is C/C++-in-process only, so the core is **always** a native C++ LOK process —
that is not a choice. The choices are UI chrome and MCP placement, and **Option A** resolves both: a
single native **C++/Qt6** core driving **in-process LOK**, **QML Fluent** chrome (bespoke ribbon, themed
JSDialog dialogs), and the **MCP server as a stateless Python/TS sidecar** over a local socket. It gives
the best RL/headless/Docker fit (offscreen QPA, deterministic step boundary, small container, parallel =
N containers) and puts the one unavoidable process boundary exactly where C++ is weakest. The runner-up
(in-process C++ MCP) is close but blocked by the absence of a mature C++ MCP SDK; the web/two-process and
single-language FFI options are rejected as the worst RL fit and the unsafe-greenfield-FFI trap
respectively.
