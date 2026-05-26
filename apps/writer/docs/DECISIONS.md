# Writer — Critical Decisions Log

> Running log of the *critical* engineering decisions for `apps/writer/`,
> with rationale and rejected alternatives, so future sessions know **why**,
> not just what. Append new decisions at the bottom with the next D-number.
> Core values that arbitrate ties: **quality > speed**, easy UI iteration,
> MCP-ready, logger-complete.

---

## D1 — Layered ownership ("Boundary A"), not full reimplement, not reskin
**Date:** 2026-05-25 · **Status:** locked

We own UI + dialogs + command/dispatch mechanism + document state + logging
+ MCP + a thin LOK binding. We rent LibreOffice's real engine (via LOK) for
**layout + text shaping + .docx/.odt I/O** and the shared core they need.

**Why:** a word processor is ~7 layers. The layers above the line benefit
from a modern rewrite; the layers below (layout/shaping/docx filters) are
~15-20 years of LO work and reimplementing them yields *lower* quality for
years — directly contradicting the owner's hard constraints "every feature
works" + "highest quality". This line satisfies all constraints at once.

**Rejected:**
- *Full reimplement (incl. layout + I/O)* — maximum ownership but quality
  trap; no project (AbiWord, Calligra, JS editors) reaches Word/LO
  layout+docx fidelity. Contradicts "every feature, highest quality".
- *Reskin LO's own UI* (the previous app's approach) — fights LO-internal
  hardcoded behaviour; not "our own modern mechanism".

---

## D2 — Engine is a separate dependency, not part of the app codebase
**Date:** 2026-05-25 · **Status:** locked (physical layout finalized in W1)

The Writer-stripped LO source that builds LOK is a **build-time
dependency** kept clearly separate from `apps/writer/` (our clean app). We
do not edit it day-to-day.

**Why:** owner wants a tidy, modern structure unlike LO's "everything in
root", and to not have "the other apps in the codebase".

---

## D3 — Stack: Qt 6 (C++ core + QML UI)
**Date:** 2026-05-25 · **Status:** locked

**Why:** owner requires a *real native* desktop app (explicitly rejected
Electron/web integration). Among native options, Qt 6 is the most
battle-tested for a heavy document app + C++ LOK interop; QML gives modern,
hot-reloadable, "easy to play with" UI. **Rejected:** Electron/Tauri (web
runtime), Flutter (weaker C++/LOK interop + less proven for this app class).

---

## D4 — Use LO's real engine via LOK (not "examples only")
**Date:** 2026-05-25 · **Status:** locked

Owner floated "take examples from LO's engine, build our own". For
layout/shaping/I/O that path = D1's rejected full-reimplement. So we use the
**real** engine through the LOK API boundary, while studying its internals
as reference for our command catalog and dialog mapping. W0 research
confirmed LOK exposes everything required (see LOK_REFERENCE.md).

---

## D5 — Strip to Writer-only, but accept the shared-core floor
**Date:** 2026-05-25 · **Status:** locked

Delete Calc (`sc`), Impress (`sd`), Math (`starmath`), remaining peer
modules. **But** the shared core (vcl, sfx2, svx, editeng, framework, oox,
writerfilter, sax, i18n, font/shaping) stays — it is Writer's own
foundation and LOK requires it. There is no "tiny Writer library".

---

## D6 — Dialog coverage via JSDialog; extending `enabled.cxx` is the one sanctioned engine patch
**Date:** 2026-05-25 · **Status:** locked (executed in W4)

"Every feature works" depends on dialogs. LO's `vcl/jsdialog/` serializes
dialogs to JSON for native rendering, but coverage is selective
(`enabled.cxx`). Where a needed Writer dialog isn't enabled, we register it
in `enabled.cxx` — a small, upstream-shaped, tracked engine patch. This is
the **only** routine exception to "don't touch the engine" (D2).

---

## D7 — Logger lives in our layer (engine `rllogger` retired for this app)
**Date:** 2026-05-25 · **Status:** locked

Because we own the dispatch seam (D1), raw/semantic/outcome are emitted from
our code, cleaner than the engine-embedded `rllogger`. Must reach
figma-parity and conform to `overview/log-contract.md`. See LOGGING.md.

---

## D8 — Distribution: dev builds from engine source; Docker ships binary
**Date:** 2026-05-25 · **Status:** locked (executed in W7)

Multi-stage Docker: build stage compiles engine→LOK + app; runtime stage
ships only binaries (logger default-on). Source never ships downstream.
This is why D2's "engine in repo at dev time" is fine — it's a build-time
dependency, not a shipped artifact.

---

## D9 — LOK needs its scheduler pumped (event-loop integration); model updates ≠ render updates
**Date:** 2026-05-25 · **Status:** open — W2 #1 task

W2 finding: driving LOK purely by calling its methods from the Qt thread is
**not enough**. `postUnoCommand`/`postKeyEvent` update the document *model*
(verified: a binding-saved docx contains inserted text), but the **layout +
tile rendering + `INVALIDATE_TILES` callbacks do not run** — so the canvas
never reflects edits and live typing doesn't render. LO's internal scheduler
(SolarMutex / `Application::Yield`) must be pumped.

**Investigated 2026-05-25/26 — `runLoop` does not take over the loop in our
embedding (both attempts reverted; synchronous binding kept working):**

- *Attempt 1 — `runLoop` on a worker `std::thread`:* traced — `lok_cpp_init`
  succeeds but **`runLoop` returns immediately, poll never called**.
- *Attempt 2 — "inverted loop": `runLoop` on the MAIN thread, pump Qt
  (`processEvents`, `QSG_RENDER_LOOP=basic`) in the poll callback:* traced —
  **`runLoop` STILL returns immediately on the main thread** (`[lok] runLoop
  RETURNED`). So it is *not* purely a wrong-thread issue.

**Refined root cause:** `lo_runLoop` → `soffice_main()` → `Desktop::Main` /
`Application::Execute()` returns immediately in our context — most likely
because, in headless LOK with **no top-level VCL window and no loaded document
at runLoop time**, there is nothing to keep `Execute()` alive. (`app.cxx` has
`comphelper::LibreOfficeKit::isActive()` branches that change startup.) This
needs deeper LO-internals work to confirm the exact precondition.

**Viable paths (next push — needs focused investigation, not a quick fix):**
1. **Make `runLoop` actually run:** study `Desktop::Main`/`Execute()` under
   `LibreOfficeKit::isActive()`; replicate Collabora COOL's exact init order
   (it may load a doc and/or set options/`setOptionalFeatures` before runLoop,
   or keep the loop alive via the poll source). Possibly load the document
   *before* `runLoop`, or set a feature flag. Then poll fires → layout +
   `INVALIDATE_TILES` run → edits render.
2. **Two processes (robust fallback):** headless LOK process (its `runLoop`
   owns its own main thread, nothing else competing) + the Qt GUI process over
   IPC — exactly COOL's WSD/Kit design. Heaviest; proven in production.

**Rejected:** synchronous per-call flush hack (no public LOK "tick"; fragile).
The static blank page renders today because a blank doc needs no layout pass;
edits need the scheduler. **This is a genuine sub-project**, deliberately not
rushed at session end.

---

## D-icons — Microsoft Fluent UI System Icons
**Date:** 2026-05-25 · **Status:** locked

MIT-licensed, ~2000 icons, exact Word M365 visual match. **Rejected:**
Lucide/Tabler (not a 1:1 Word match), mixed set (unnecessary complexity now).
```
