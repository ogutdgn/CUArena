# Verification protocol — MS Word clone

> **Purpose.** How every build phase and every feature *proves* it works, so an agent
> **self-verifies instead of self-asserting**. This operationalizes the repo's goal-driven
> guideline (Karpathy #4) and the "getting it right this time" foundations in
> [`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md) §6.
>
> The bar is one sentence: **"done" means green tests that fail when the claim is false** —
> no eyeballing as the sole proof, and no test that passes on a blank document.

---

## Why this exists

The prior prototype was audited as PoC-grade for exactly these reasons: its render path
`dlsym`'d a test-only engine symbol, it full-repainted on every keystroke, its "ledger" had no
CTest runner and its one test passed on a blank page, and it shipped dropdowns that looked
active but dispatched nothing. Every one is a *verification* failure — work asserted done with
no check that would have failed if it weren't. This protocol makes the check mandatory and
defines what a real check looks like for this codebase.

---

## The rule

A unit of work (a feature, a fix, a phase deliverable) is **done** only when:

1. A behavior it claims is covered by an automated test.
2. That test is **green** in the CMake/CTest harness, run **headless**.
3. That test **fails when the behavior is broken** — proven by a negative check, not assumed.
4. The test asserts the **real effect** — actual content / state / pixels — not "did not
   crash", and not on an empty document.

If any of these is missing, the work is *in progress*, not done.

---

## The self-verify loop

For each unit of work, walk this loop — goal-driven execution made concrete:

1. **State the verifiable goal.** Turn "implement Bold" into "dispatching `.uno:Bold` on a
   selection toggles the run's bold property, and the Bold control's checked state reflects it."
2. **Write the test first; watch it fail.** A failing test proves the test exercises the thing.
3. **Implement** the minimum to make it pass.
4. **Watch it pass**, then **break the implementation** and confirm the test goes red (the
   negative check). Restore.
5. **Done** only when the test is green *and* its red state has been observed.

Loop per behavior, not per feature-group — a group is done when each of its behaviors is.

---

## Test types

| Type | Asserts | Seam used | Prevents (audit) |
|---|---|---|---|
| **A. Unit / integration** | our-layer logic: dispatch routing, state model, enable/disable/checked rules | none (pure C++) | — |
| **B. Headless LOK integration** | load → dispatch → save round-trips through the real engine | LOK via the engine binding, **synchronous scheduler pump** | test-only render symbol; race-y idle |
| **C. Render golden-frame** | rendered pixels match a committed golden (real content, not blank) | `paintTile` → bitmap → hash / diff | "passes on a blank page"; full-repaint regressions |
| **D. Behavior + state** | a control's effect *and* its enabled / disabled / checked state | dispatch seam + `getCommandValues` + document model | "theater" controls that dispatch nothing |
| **E. Log-contract** | each logged command emits a well-formed raw / semantic / outcome triple; `outcome.document` = end state | the logger on the dispatch seam | un-replayable / unobservable actions |
| **F. RL verifier** | a task's end state + efficiency grade (built later, Phase 5) | reuses the **#3** specs as the oracle | — |

Detail on the two that are easiest to fake:

- **C — render golden-frame.** Render a known fixture to a bitmap at a **pinned font set, DPI,
  theme, and zoom**, and compare to a committed golden (exact hash, or pixel-diff within a
  stated tolerance). The golden must contain **real laid-out content** — a test that renders an
  empty page and asserts "non-null buffer" is banned. Cover at least one invalidation case:
  edit → assert only the `INVALIDATE_TILES` dirty rect repainted (catches full-repaint
  regressions and dead tile caches).
- **D — behavior + state.** Each in-scope control gets two assertions, both sourced from its
  **#3 behavior+state spec**: (i) **effect** — dispatch the command, assert the document model
  changed as specified and the outcome log recorded it; (ii) **state** — set up the precondition
  and assert the control's enabled / disabled / checked value via `getCommandValues` (e.g. *Copy
  disabled with no selection*, *Bold checked when the selection is bold*). A control with no
  passing effect-assertion is not shipped — that is the anti-"theater" check.

---

## Determinism (shared requirement)

Every test must be **byte-deterministic and headless** — they run in CI and in the Phase-6
container:

- **Pinned, bundled fonts** (no host-font dependence), **fixed DPI**, **fixed theme + zoom**.
- **Drive the synchronous scheduler-pump step boundary** to quiescence — never a wall-clock
  `sleep`. A step maps to a settled document state (see ARCHITECTURE §3).
- **Committed fixtures and goldens** under the harness; inputs fixed / seeded.
- Offscreen platform + software rendering, matching the distribution image.

A non-deterministic test is worse than none — it trains the team to ignore red.

---

## Definition of done

**Per feature (Phase 3):**
- [ ] Its **#3 behavior+state spec** exists.
- [ ] A **D-effect** test is green (and red when the effect is removed).
- [ ] A **D-state** test covers each enabled / disabled / checked rule in the spec.
- [ ] An **E** log-contract assertion covers the command.
- [ ] If it changes rendering, a **C** golden frame covers it.

**Per phase:**
- [ ] The phase's required test types (table below) are green headless in CTest.
- [ ] Each new test's red state was confirmed.
- [ ] No banned anti-pattern (below) was introduced.
- [ ] `last-point.md` records *what is verified*, citing the test names — not prose claims.

---

## Per-phase verification bar

| Phase | Must be green before "done" |
|---|---|
| **1 — Foundations** | **A + B + C**: the CTest harness itself runs headless; a B smoke (load → dispatch → save) drives the real pump; a C golden proves real content renders and the dirty-rect path repaints only what changed. |
| **2 — UI kit** | Token / snapshot checks that the design tokens apply; the chrome does not regress the C golden. |
| **3 — Feature loop** | **D + E** per feature, on top of A / B — the per-feature DoD above. |
| **4 — MCP sidecar** | Contract tests: each MCP Tool maps to a dispatch and returns the engine's outcome; each Resource reflects core state; the sidecar holds no state of its own. |
| **5 — Verifier** | **F**: the verifier grades a known-good and a known-bad task transcript correctly, fed by #3 specs. |
| **6 — Distribution** | The **whole CTest suite runs green inside the headless container** (CI parity), not just on the dev host. |

---

## Banned anti-patterns

Each was an actual prototype failure or a direct route to one:

- **Test-only engine symbols** — `dlsym`'ing a non-production symbol to make a path work under
  test. Tests drive the *real* LOK path or they prove nothing.
- **Full-repaint per change** — honor the dirty rect; a render test must catch a regression here.
- **Tests on a blank document** — a green test on an empty page is the canonical false positive.
- **"Did not crash" as success** — assert the *effect*, not the absence of a crash.
- **Theater controls** — a control that renders but dispatches nothing fails its D-effect test by
  construction; don't ship it.
- **Wall-clock `sleep` to settle** — use the synchronous pump; sleeps are flaky by design.

---

## See also

- [`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md) — §6 the two foundations this
  protocol guards (render / scheduler path + CMake/CTest harness), §3 the scheduler-pump step
  boundary the tests drive.
- [`execution-map.md`](execution-map.md) — the phases this protocol gates.
- [`research/README.md`](research/README.md) — stream **#3** (behavior+state specs, the D-test
  oracle) and **#6** (the verifier, type F).
