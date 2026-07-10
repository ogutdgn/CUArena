# journal — append-only evidence log + rebuildable output (the crawl protocol)

> Evidence paths below refer to the MS-Word crawler this was distilled from
> (mirrored in `references/word-crawler/`).

## Purpose

Not a library — the protocol that makes everything else trustworthy. Every observation and
action streams into an **append-only JSONL journal**; the final knowledge-base output is
**rebuilt from the journal by a reconciling emitter**. This gives you: crash-safe attribution,
re-emit without re-driving the app, deterministic diffable runs, and a place where every
"why is this missing?" question has an answer.

## How to use

**Journal record shape** (`crawler/journal.py`): every `append` stamps `seq`, `ts`,
`schema_version`. Core record types the crawl protocol needs
(`crawler/prober.py::probe`, `crawler/run_p0.py`, `crawler/capture.py`):

- `press-attempted` — written **BEFORE** injecting the click (crash between press and outcome
  still leaves evidence; enables quarantine)
- `press-outcome` — the classification + diagnostics (e.g. popup window classes/areas)
- `reset-verified` — did the world return to baseline after this control?
- `surface-discovered` — a ref + the entry point that revealed it
- `surface-captured` — the full payload of a captured surface
- `surface-retyped` — press-time truth correcting a static classification
- `boundary` — a surface deliberately not entered (policy + decision id, optional ref)
- `ambiguous` — anything unresolved, WITH a reason string (the debugging goldmine)

**Anti-livelock quarantine:** ≥2 `press-attempted` for a control with no `press-outcome` →
skip it and journal `ambiguous` (`crawler/prober.py::probe`).

**Reset-verify after every control:** restore (action-specific, see `input.md`), then check
windows/popups gone, pane count back, doc-hash unchanged — and journal the boolean. One stuck
dialog otherwise corrupts every control after it (`crawler/prober.py::_restore`).

**Seen-set recursion:** every recursive drain carries one `seen` set of surface ids; a surface
reached by a second path is referenced, never re-crawled — this breaks cycles and bounds the
walk (`crawler/run_p0.py::_drain_dialog` docstring).

**The reconciling emitter** (`crawler/emit.py::emit`) rebuilds ALL output files from the
journal every time:

- `entry_points` = exact inverse of `surface-discovered` (generated, never hand-maintained)
- `frontier` = discovered − captured − boundary-resolved − disabled-resolved (the honest
  "what's left" ledger)
- retype reconciliation: rewrite the owning item's action, move the discovery to the true ref
- dialog dedup: structural signature (title + per-tab field names + buttons, ≥2 fields of
  evidence) with screenshot-hash fallback for field-poor panels; on merge, rewrite every ref,
  discovery, AND entry sub-address to the keeper
- closure gates: every `ref` and every entry sub-addr stem must resolve to an emitted,
  discovered, or boundary surface → `dangling` must be empty
- orphan sweep: delete output files the current journal no longer justifies

## Known traps

- **Deleting a merged duplicate without rewriting entry sub-addresses ships dead back-links** —
  and a refs-only closure check reports clean because sub-addrs (`surface#item`) aren't refs.
  Rewrite entries through the alias map and gate on entry stems too
  (`crawler/emit.py` dedup block; found by executing `emit()` against a reproducing journal).
- **A "frontier empty" completion gate is unattainable unless every deliberate non-capture
  retracts its discovery**: window-boundaries carry their ref so the emitter can resolve it out;
  disabled-opener skips are collected into `disabled_state`. Silent skips = permanent phantom
  frontier entries (`crawler/emit.py` boundary_refs/disabled_refs, `crawler/run_p0.py::_window_boundary`).
- **Merging on weak structural evidence asserts lies.** Two DIFFERENT zero-field alert boxes
  (same title, same OK button) are structurally identical; require real field evidence or
  identical pixels before merging — a false NON-merge costs a duplicate file, a false merge
  claims two controls open the same dialog (`crawler/emit.py::_dlg_sig` comment).
- **Static label heuristics will be wrong somewhere** ("…" ⇒ opens-dialog — but Word's
  "Selection Pane…" opens a docked pane). Don't fight it at capture time; emit a
  `surface-retyped` record when pressing reveals the truth and reconcile in the emitter
  (`crawler/run_p0.py::_drain_popup` pane fallback, `crawler/emit.py` retype block).

## Lessons learned

- 2026-07-09 — **Journal first, act second.** Writing `press-attempted` before the click and
  `reset-verified` after the restore turned every mid-run crash and every flaky control into a
  queryable record instead of a mystery.
  (learned from `crawler/prober.py::probe`)
- 2026-07-09 — **Rebuild, never patch, the output.** Because the emitter regenerates everything
  from the journal, output-layer bugs (dedup, entry rewriting, frontier accounting) were fixed
  and re-verified **without re-driving the app** (`--emit-from <run_dir>`), and hand-editing
  output became structurally impossible.
  (learned from `crawler/run_p0.py` `--emit-from`, `crawler/emit.py`)
- 2026-07-09 — **Determinism is the acceptance test:** the same crawl run twice must produce an
  identical normalized output. Non-determinism always pointed at a real bug (timing, stale
  baselines, flaky class heuristics) — treat any diff as a defect, not noise.
  (learned from the source project's P0 report / `docs/DEPTH_REVIEW.md`)
- 2026-07-09 — **Ambiguous reasons must be precise strings** — the emitter and later debugging
  key on them ("not drained: item disabled…" resolves to `disabled_state`; "no child dialog"
  triggered a root-cause hunt). A generic "failed" reason destroys that signal.
  (learned from `crawler/run_p0.py` ambiguous records, `crawler/emit.py` disabled_state filter)
- 2026-07-09 — **Every knowledge claim needs an entry path.** Surfaces record `entry_points`
  (who opened me) generated from discovery records — reviewers used the inverse mapping to find
  orphaned surfaces and phantom links no human noticed.
  (learned from `crawler/emit.py` entry_points build + `docs/DEPTH_REVIEW.md` findings)
- 2026-07-09 — **Route every per-app script's paths through ONE `common.py` and the whole
  toolchain re-binds to a new KB workspace untouched.** The word-home-insert-v2 run reused the
  v1 session/enumerator/prober/capture modules with zero code edits — only `common.py` (APP
  constant) and the step runners (output writers) changed. Structure per-app tools that way from
  the start: measurement code and output-schema code age at different speeds.
  (learned from kb/word-home-insert-v2 setup: same-build reuse, step 0-1 re-proved live)
