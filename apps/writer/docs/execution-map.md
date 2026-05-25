# Writer — Execution Map

> **What's queued next** — nothing else. Refresh at session end. Pairs with
> [`last-point.md`](last-point.md) (what's done). Full design context in
> [`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md).
>
> Last updated: 2026-05-25.

---

## Phase roadmap (W0–W8)

| Phase | Goal | Status |
|---|---|---|
| **W0** | Foundations: decisions locked, LOK feasibility research, docs scaffold, permissions, branch | **done** |
| **W1** | Engine: Writer-only deep-strip + headless LOK build + SDK boundary; LOK proof-of-life | **in progress** (recipe + command catalog done; build **blocked on owner deps**) |
| **W2** | Qt app skeleton + LOK binding: CMake, C++ `Office`/`Document` wrapper, tile render→QML canvas, load/save, key/mouse injection, core callbacks **+ logger raw-stream scaffold** | |
| **W3** | Command mechanism + ribbon UI: catalog from `*.xcu`, dispatch (**native semantic emit**), Word-like QML ribbon + Fluent icons, `STATE_CHANGED` state | |
| **W4** | Dialogs: `JSDIALOG`→native Qt/QML, `sendDialogEvent`, coverage audit + extend engine `enabled.cxx` for gaps | |
| **W5** | Logger figma-parity: full semantic registry, outcome snapshot, `semanticEventCount`, consolidator, contract conformance | |
| **W6** | MCP surface: dispatch + state + document ops as MCP tools | |
| **W7** | Docker multi-stage: engine→LOK + app → binary runtime, logger default-on | |
| **W8** | Theming/polish: Word palette, Fluent refinement, context menus, a11y | |

---

## W1 — Engine (Writer-only LOK) — in progress

Done:
- ✅ Build recipe finalized → [`architecture/ENGINE_BUILD.md`](architecture/ENGINE_BUILD.md)
  (flags verified vs `configure.ac`; headless `svp`, core LOK C API).
- ✅ Engine location: keep at `apps/libreoffice/libreoffice-codebase/`,
  demarcated as engine (resolves ARCHITECTURE §11 open Q for now).
- ✅ Command catalog (`tools/gen_command_catalog.py` → 1520 cmds) —
  build-independent, done.

**BLOCKED on owner deps (sudo)** — exact `sudo apt` in
[`progress/2026-05-25-w0-w1-kickoff.md`](progress/2026-05-25-w0-w1-kickoff.md).

Remaining (the moment deps land):
1. `autogen.sh` (ENGINE_BUILD.md line) → `make` (background, ~3 h).
2. **LOK proof-of-life** (exit gate): `tiledrendering` cppunit test or our
   own C harness — headless load `.docx` → `paintTile` (non-empty) →
   `postUnoCommand` → `saveAs` round-trip. Log in `progress/`.
3. **Strip** Calc (`sc`) / Impress (`sd`) / Math (`starmath`) + peers, after
   the first green baseline; build-verify each group; reversible. Never the
   shared core (D5).
4. **Record** the LOK link surface for W2.

**W1 exit criteria:** Writer-only engine builds; LOK loads+paints+dispatches
+saves a .docx headless; link surface documented.

---

## Open decisions (carry until resolved)

- Engine location & strip depth (W1.1)
- Minimal Writer-only LOK build flags (W1.2)
- Engine-thread ↔ Qt-loop integration (W2)
- Tile cache / HiDPI strategy (W2)
- Dialog coverage gap size vs `completeWriterDialogList()` (W4)
- MCP transport: stdio sidecar vs in-process (W6)
- Log env-var names + outcome cadence (W2/W5)
```
