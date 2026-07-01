# Parity Pipeline — Honest Meta-Review (2026-07-01)

> Requested by the user: "What is the problem in my pipeline, how should I think, what is the
> point I am missing? Review my decisions, executions, memory. Be realistic and honest."
>
> Evidence base: parity/RUNBOOK.md + engines + oracle + results (full sweep), the complete
> Tables commit history (`b3fdeb2`…`e9f7140`, 12 iterations), the UI-fidelity verification
> audit (ribbon provenance, dialogs, flow/visual axes), docs/plan/last-point.md session log,
> and the cross-session memory.

---

## 0. Verdict

**You are not executing badly. You are measuring the wrong thing — or rather, only one of the
five things you care about — and everything downstream inherits that.**

Your stated goal has five axes: **UI structure, functionality, behavior, UI flow, design.**
Your pipeline has exactly **one hard, ground-truth-backed, gated axis: OOXML export diff.**
The other four either have no ground truth at all (visual design, dialog completeness,
interaction behavior) or exist as ungated prototypes covering <10% of controls (flow verifier,
clone-only visual judge).

Agents — and you — converge on what is gated. That is why dozens of Table iterations produced
byte-clean XML while **six dropdowns were literally dead in the UI** and nobody noticed until a
live click-through audit (`scripts/table-scorecard.js`, commit `0ce8856`) was finally written.
The gate could not see them, so the loop could not fix them.

The pipeline is not incapable. It is **half-built**: the harder half (file-format fidelity) is
excellent; the half you actually judge success by (what the app looks like and does when you
click it) was never given a target or a gate.

---

## 1. The core problem: measurement asymmetry ("you get what you gate")

| Axis you care about | Ground truth exists? | Automated gate? | Coverage |
|---|---|---|---|
| OOXML export | ✅ COM/ribbon-oracle captures | ✅ `run.py` differ, 0/0 required | 58 tasks (~52% of locked scope) |
| Ribbon/UI structure | ❌ hand-authored `raw-research.json` | ⚠️ flow-probe, T0/T1 only | ~20 of 212 controls |
| Live functionality (click → effect) | ❌ none | ⚠️ table-scorecard.js, tables only | 33 of 212 controls |
| Visual design (ribbon, dialogs, paint) | ❌ none (old screenshots, eyeballed) | ❌ LLM judge is **clone-only** | spot checks |
| Interaction flow / behavior (hover preview, toggles, enablement, dialogs' fields) | ❌ none | ❌ | 0 (46 findings explicitly flagged "needs live comparison", never done) |

Every "COMPLETE" declaration in the session log is a *single-axis* claim being read as an
*all-axes* claim:

- 2026-06-30: "TABLES FUNCTIONAL PARITY = COMPLETE for this push" — true for OOXML+bridge
  verbs, false for the UI you look at.
- 2026-07-01 05:21 (`64f915c`): "Tables parity loop COMPLETE" — 5 hours later the scorecard
  found 6 dead dropdowns, then a border-collapse paint bug.

This is the exact mechanism behind "I call this dozens of times and it's still not right."
The loop *was* converging — on the one axis it could see.

## 2. The second problem: the UI target was never captured

The OOXML axis works because you captured ground truth first (real `.docx` from real Word),
then diffed against it. The UI axes were never given the same treatment:

- **`ribbon-data.js` provenance = `docs/research/raw-research.json` = manual observation.**
  There is no UIA dump, no control inventory extracted from Word, no per-control screenshot
  baseline. You have been replicating a *recollection* of Word's UI, not Word's UI.
- **Dialogs are 100% hand-authored** (`dialogs.js`), with known missing tabs/fields
  (Font Advanced, Paragraph Line-and-Page-Breaks…), and no capture of Word's actual dialog
  layouts to diff against.
- **The real-Word UIA contextual-tab inventory was proposed on 2026-06-29 and deferred at
  least four times since.** It is the single highest-leverage artifact you haven't built.
  The RUNBOOK itself admits it: "Our only structured source today is `table-tools-pm.js`
  etc. = the CLONE's implementation, a SUBSET" — i.e. the clone is being verified against
  itself.

You cannot converge on a target you never recorded. When the target lives in your head, every
session re-derives it slightly differently, which is why the same feature gets rebuilt.

## 3. Case study: why Tables ate dozens of calls

Reconstructed from `b3fdeb2`…`e9f7140` (12 iterations) plus the 2026-06-30 sessions:

1. **Enumeration came after building, not before.** The 89-behavior A–F worklist
   (`tables_af_worklist.json`) was created *mid-flight*, after Design/Layout tabs had already
   been rebuilt once. Each iteration discovered scope the previous one didn't know existed.
   Borders alone were touched **five separate times** (group UI → `val=nil` fix → dead
   dropdowns → border-collapse paint → re-verification) — each pass revealing a gap the
   previous pass's evidence type couldn't show.
2. **"Done" was declared from export tests.** The loop closed at `64f915c` on export-XML
   evidence; the first *live* per-control audit ever run (`0ce8856`) immediately reopened it.
3. **The most visible content is blocked and quietly small.** The Table Styles gallery — the
   thing your eye hits first on the Design tab — holds **2 of Word's ~247 styles** because
   bulk COM extraction hangs. Byte-parity work continued elsewhere while the gallery stayed
   at 2/247. Effort allocation was inverted relative to visibility.
4. **Repeated re-prompting without a persistent contract.** "Make Tables exact same as real
   Word" was re-issued across sessions; each run re-scoped from scratch (session log shows
   scope statements re-negotiated each time: group E removed, Excel OLE excluded, stubs
   re-agreed). Without a per-feature target inventory that survives sessions, N calls produce
   N partial overlapping passes, not one converging sequence.
5. **The directive and the scoping contradict each other.** "Exact same as real MS Word,
   hidden features, all behaviors" coexists with honest stubs (Draw Table pen, Eraser, Border
   Painter, 2/247 styles). Both are defensible; holding both *silently* guarantees
   disappointment — the completion claims are graded against the scoped bar, your judgment is
   graded against the "exact" bar.

## 4. Is this pipeline/environment capable of your goal? (honest answer)

**Mostly yes — with one axis that is asymptotic.** Per axis:

- **OOXML/functionality: proven capable.** Already delivering 0/0 parity with real Word.
- **Ribbon structure incl. hidden features: capable, and cheaper than you think.**
  You do not need to scrape UIA for the ribbon inventory: **Microsoft publishes the complete
  Office Fluent UI control-identifier workbooks** ("Office 2016 Help Files: Office Fluent
  User Interface Control Identifiers" — an Excel sheet for Word listing *every* control's
  idMso, type, tab, group, parent). Combine with COM `GetLabelMso` / `GetEnabledMso` /
  `GetImageMso` (which returns the actual icon bitmaps) and you get an authoritative,
  enumerable ground truth for the entire ribbon — including contextual tabs and the "hidden"
  long tail — without a fragile UIA walk. (Verify the download matches build 16.0.20026; it
  will be ≥99% right and diffable.)
- **Dialog completeness: capable via UIA.** Dialogs aren't in the idMso workbook; a one-time
  UIA walk per dialog (fields, labels, tabs, defaults) is feasible on this machine and only
  needs to be done once per dialog.
- **Visual design: approximately capable, never perfectly.** Screenshot-vs-screenshot
  comparison (you already have `_capture_word_ribbon.ps1` + `ribbon-shot-probe.js` — built
  this week, the right instinct) judged by an LLM gets you to "indistinguishable at a
  glance." Pixel-perfect identity with Word's rendering (font rasterization, theme
  animation, DPI behavior) is asymptotic — set a tolerance and stop there deliberately.
- **Behavior/interaction flow: partially capable.** CUA can drive both real Word and the
  clone (memory confirms the dev Electron app is drivable) and record discrete flows
  (click → flyout → preview → apply). Use it for *spot ground truth* on high-value flows,
  not as a bulk gate — it is too slow and flaky to gate 212 controls. Continuous behaviors
  (drag feel, animation timing) will remain manual acceptance.

So the honest capability statement: **"indistinguishable from Word in normal use" is
reachable in this environment. "Byte-and-pixel identical everywhere" is not, and no pipeline
would make it so.** Pick the former bar explicitly and write it down; ambiguity between the
two bars is itself one of your problems.

## 5. What to change (in priority order)

1. **Capture the UI ground truth BEFORE the next feature loop.** One-time artifacts:
   - Import Microsoft's idMso control-identifier workbook for Word → `parity/oracle/`
     as the authoritative ribbon inventory (replaces `raw-research.json` as the spec).
   - `GetLabelMso`/`GetImageMso`/`GetEnabledMso` pass to attach labels/icons/enablement.
   - Per-dialog UIA field dump for the dialogs in locked scope.
   - Per-control screenshot baseline from real Word (extend `_capture_word_ribbon.ps1`).
   This has been deferred 4+ times. Nothing else on this list works without it.
2. **Make "done" multi-axis — and make the ledger show it.** A feature is complete only when
   all five columns are green: `OOXML 0/0` · `STRUCTURE 0 missing` (clone inventory vs idMso
   inventory) · `SCORECARD n/n` (every control click-verified live) · `VISUAL pass`
   (clone-vs-**Word** screenshot judge, not clone-only) · `FLOW pass` (declared interaction
   type matches). Rename single-axis claims accordingly ("OOXML-complete", never "complete").
3. **Generalize `table-scorecard.js` to all 212 controls and make it a gate.** It found in
   one run what dozens of export-gated iterations missed. That's your highest-ROI existing
   asset. (The 82-dropdown audit in `e9f7140` was the first step; finish it.)
4. **Unblock the Table Styles catalog with one manual session, not COM loops.** Built-in
   table styles materialize into `styles.xml` when used: one interactive Word session
   applying each of the ~113 modern styles to a table in a single document, saved once,
   yields the full byte-accurate catalog in that file's `styles.xml`. No hanging COM loop
   required. (Automatable with visible-Word + delays if you don't want 30 minutes of
   clicking; verify a 3-style pilot first.)
5. **Prioritize by 5-minute visibility, not by XML-diff counts.** Spec seeds currently come
   from missing XML nodes. Re-rank the backlog by what a Word user notices in the first five
   minutes: galleries with real content, dialog field completeness, live preview, selection/
   caret behavior, enablement graying. `w14:ligatures` byte-parity should never have outranked
   a 2/247 style gallery.
6. **Write a per-feature PARITY CONTRACT that survives sessions.** One file per feature:
   the target inventory (from artifact #1), the per-axis checklist, the agreed exclusions
   (stubs, scope-outs) *with your sign-off recorded*. Session N+1 resumes the contract instead
   of re-deriving scope. This converts "dozens of calls" into one converging sequence.
7. **Resolve the "exact same" vs "honest stubs" contradiction per feature, in writing.**
   Either a control is in scope for exactness (then it can't be a stub) or it's scoped out
   (then its absence can't count against completeness). The contract file is where this
   lives. Most of your disappointment is this ambiguity, not agent failure.

## 6. What NOT to change

- **The OOXML differ.** Baseline subtraction, signed deltas, rId/numId canonicalization,
  noise stripping, golden self-tests, the `review_differ.py` trust gate — this is genuinely
  strong engineering and it is the axis that makes documents open correctly in real Word.
  Keep it exactly as is; it just needs four siblings, not a replacement.
- **The ExecuteMso ribbon oracle.** The COM≠ribbon discovery (bullets, highlight,
  `Tables.Add`) was real and the ExecuteMso response was correct. Keep COM for scriptable
  actions; route galleries/building-blocks through the one-shot catalog trick instead.
- **The adversarial-review habit.** It has caught real bugs in nearly every cycle
  (clearing-leak, tcBorders ordering, CellSelection themeFill…). Keep it.
- **Spec-kit discipline, TDD, the three gates, honest-stub policy, the scope lock.** All
  sound. The scope lock in particular was a good decision — the problem is that completion
  claims don't reference it explicitly (see §5.7).
- **Do not rebuild the pipeline from scratch.** The foundation is right. It is missing its
  UI half, not built on the wrong idea. Rebuilding would throw away the best-engineered part
  (the differ) to fix a problem that lives elsewhere.

## 7. Edge questions, answered directly

- **"Was using COM a mistake?"** No — it was the right first tool and it proved itself for
  scriptable actions. The mistake was letting features whose ground truth COM can't capture
  (galleries, styles, dialogs) stay "deferred" indefinitely instead of building the
  alternative capture path.
- **"Is CUA the missing piece?"** Partially. CUA is the only way to ground-truth *behavior*
  (flows, previews, feel), but it's a spot-check instrument, not a 212-control gate. The
  missing piece is cheaper: the idMso inventory + generalized scorecard + Word-vs-clone
  screenshots. Add CUA traces on top for the ~20 flows that define "feels like Word."
- **"Can this ever be an exact copy?"** Asymptotically. File format: yes (proven). Structure
  and functionality: yes. Visual: to a tolerance. Behavior feel: to human acceptance. Write
  the bar as "a Word user can't tell the difference in N minutes of normal use" — that is
  achievable, testable (CUA/LLM judge), and stops the goalpost ambiguity.
- **"Were the agents failing me?"** Mostly no. They optimized exactly what the gates
  measured, flagged the gaps honestly (the deferrals ARE in the logs), and the review habit
  caught real bugs. The two genuine process failures were: declaring "COMPLETE" from one
  axis, and letting the UIA/ground-truth capture slip four times without anyone forcing the
  question "can we even see the thing we're grading?"
- **"Should I merge parity-pipeline?"** Out of scope for this review, but note the pattern:
  22+ commits unmerged raises the cost of every future rebase and mixes measurement
  infrastructure with product fixes in one branch. Consider splitting infra (differ, oracle,
  probes) from clone fixes at merge time.

---

*Prepared 2026-07-01 from three parallel evidence sweeps (pipeline mechanics, Tables commit
archaeology, UI-fidelity verification audit) plus the session log and cross-session memory.*
