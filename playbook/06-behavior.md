# Step 6 — Behavior: measure what the depth set actually DOES

## Goal

Step 5 exhausted the STRUCTURE of the depth set (what exists, what opens what, the option
lists, the screenshots). This step measures the SEMANTICS: for every depth-set node, what
running it actually does — its effect, what its options mean differently, its defaults, its
state rules, and (for the top layers) how it feels in interaction. The test raises Step 5's
bar one level: **a builder who has never seen the app could implement not just the button,
but the BEHAVIOR behind the button, from the record alone.**

The findings live at the FUNCTIONAL level — the user-visible contract:

> Bold: "applies bold to the selection; **pressing it on already-bold text removes bold
> (toggle)**; with no selection it applies to the word under the caret; on a mixed selection
> the first press bolds everything."
> Multilevel list: "**Tab demotes the item one level, Shift+Tab promotes it**; each level
> carries its own numbering scheme."

NOT the instrument readout ("`w:b` appeared in the XML", "moved 3px") — that belongs in the
evidence artifacts backing the finding.

## How (agent decides the details)

1. **Read the channel map** recorded in Step 1 (which behavior channels this app has:
   savable file format? object model? UI metadata? — `toolbox/behavior.md`). Build your
   measurement harness as your own scripts in `kb/<app>/scripts/tools/` — the toolbox tells
   you how, including the experiment recipes and their proven traps.
2. **Work the depth set** (Step 5's output: P0–P3 + whole-scope children + closure pulls),
   sub-feature by sub-feature:
   - **Effect**: known state → act through the real UI path → read the delta on the
     strongest channel → write its functional meaning.
   - **Options**: one experiment per option from the IDENTICAL start; diff outputs against
     each other; write each option's functional difference (the AutoFit question).
   - **Defaults**: baseline subtraction — what does the app do/write when you specify
     nothing? Which option comes pre-selected?
   - **State rules**: toggle test (press twice), selection-follow, persistence probe, and
     the enablement matrix (one metadata sweep serves ALL nodes — it is also Step 3's
     `requires` precondition evidence; do it once, reference it everywhere).
   - **Dynamics** (P0–P1 only — the screen channel is slow): recordings with real input for
     caret placement, live previews, undo granularity, contextual activation. Journal the
     deliberate skip for P2–P3.
3. **Write through the kernel**: each node's `behavior_record` (schema in
   `kernel/models.py`) — slots structured, content free-form functional prose, every claim
   pointing at its experiment (journal id / before-after artifact pair), gesture + build
   pinned, unmeasured slots listed in `pending`.
4. **Unasked discoveries** (baseline subtraction always finds some) go in `extra` — never
   dropped for not fitting a slot.

## Rules

- **R6.1** All common rules (CR1–CR8) + Step 0/2 hygiene bind: experiments run on scratch
  fixture copies, never real data; every experiment journaled.
- **R6.2 Findings are FUNCTIONAL.** Write what a user/builder observes ("toggle; applies to
  word under caret when nothing selected"), never instrument readouts as findings ("XML
  gained w:b", "shifted 3px"). The readout is the EVIDENCE, archived and referenced — the
  finding is its meaning. A record a builder can't implement from is not done.
- **R6.3 No evidence, no finding.** Every filled slot points at the experiment that proved
  it (journal experiment ids / artifact paths). A claim without evidence is not written as
  prose — it becomes a `pending` entry. [kernel-checked: a behavior record with zero
  evidence refs fails]
- **R6.4 Gesture + build on every record.** The same capability through two gestures can
  behave differently (measured fact — API vs button, dialog vs command); a fact without its
  gesture and app build is not reproducible. Drive the UI's REAL path.
- **R6.5 PENDING may not be guessed closed.** What resists measurement (sticky state,
  cross-feature interactions, continuous dynamics — `toolbox/behavior.md`) is listed in
  `pending` with a reason. Memory/training knowledge of the app is NOT a measurement.
- **R6.6 Priority-gated depth of experiments.** Effect/options/defaults/state-rules for the
  whole depth set; dynamics recordings only for P0–P1 (journal the skip). P4-outside-whole
  gets no behavior work at all — outline stays outline.

## Proof — extends the definition of done

1. Every depth-set SUB-FEATURE carries a `behavior_record` with: effect + options (each
   option from Step 5's structure covered: found or pending) + defaults + state_rules
   evidenced; dynamics evidenced for P0–P1; honest `pending` for the rest.
2. Kernel completeness passes the behavior checks (records evidenced; no depth-set node
   recordless once the run produced any records).
3. The channel map exists in the KB (which channels this app offers, which were used).
4. Spot-audit: pick 3 records; a reader implements the behavior on paper from the record
   alone and cannot find a question the record leaves open that isn't in `pending`.
5. The journal reconstructs every experiment: state → gesture → delta → conclusion.
