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
| **W0** | Foundations: decisions locked, LOK feasibility research, docs scaffold, permissions, branch | **in progress** |
| **W1** | Engine: Writer-only deep-strip + headless LOK build + SDK boundary; LOK proof-of-life | next |
| **W2** | Qt app skeleton + LOK binding: CMake, C++ `Office`/`Document` wrapper, tile render→QML canvas, load/save, key/mouse injection, core callbacks **+ logger raw-stream scaffold** | |
| **W3** | Command mechanism + ribbon UI: catalog from `*.xcu`, dispatch (**native semantic emit**), Word-like QML ribbon + Fluent icons, `STATE_CHANGED` state | |
| **W4** | Dialogs: `JSDIALOG`→native Qt/QML, `sendDialogEvent`, coverage audit + extend engine `enabled.cxx` for gaps | |
| **W5** | Logger figma-parity: full semantic registry, outcome snapshot, `semanticEventCount`, consolidator, contract conformance | |
| **W6** | MCP surface: dispatch + state + document ops as MCP tools | |
| **W7** | Docker multi-stage: engine→LOK + app → binary runtime, logger default-on | |
| **W8** | Theming/polish: Word palette, Fluent refinement, context menus, a11y | |

---

## Next: W1 — Engine (Writer-only LOK)

Concrete steps (build-verified; smoke-tested):

1. **Decide engine physical location & strip depth** (resolve
   ARCHITECTURE §11 open Q). Default: keep at
   `apps/libreoffice/libreoffice-codebase/`, demarcate as engine.
2. **Configure a headless, Writer-only LOK build.** Establish the
   `autogen.sh`/`configure` flags for LOK (`--enable-...`? `--disable-*`
   set from the existing build line), build LOK + `instdir/`.
3. **Strip Calc (`sc`), Impress (`sd`), Math (`starmath`)** + remaining
   peer modules (continue old Phase 1). Build-verify after each removal
   group; keep reversible. Do **not** touch shared core (D5).
4. **LOK proof-of-life** (the W1 exit gate): a tiny harness (or
   `gtktiledviewer`/`tiledrendering` test as the reference) that
   headlessly: loads a `.docx`, calls `paintTile` (non-empty bitmap),
   posts `.uno:Bold`, and `saveAs` round-trips. Document the exact
   commands in `progress/`.
5. **Record** the LOK link surface (lib paths, headers, init entrypoint)
   the Qt app (W2) will consume.

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
