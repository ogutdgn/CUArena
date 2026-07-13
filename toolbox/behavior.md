# behavior.md — measuring what a capability actually DOES

Method knowledge for Step 6 (playbook/06-behavior.md): extracting a capability's real
semantics from the live app. Distilled 2026-07-13 from the ms-word-clone project's
measurement corpus (`MEASURING-REAL-WORD.md` + its parity/ instruments), claims verified
against the actual scripts and results before adoption. Like every toolbox file: this tells
you HOW; you write your own per-app instruments into `kb/<app>/scripts/tools/`.

**The finding is FUNCTIONAL, the instrument readout is EVIDENCE.** You measure through XML
diffs and property reads, but what you WRITE is what a user/builder observes: "toggles bold;
first press on a mixed selection bolds everything", "Tab demotes the list item one level".
The raw delta (`w:b` appeared, `tblW pct 5000`) goes into the evidence artifact, not the
finding text. A builder must be able to implement the behavior from the finding alone.

## The experiment loop

> prepare a known state → act through the UI's REAL code path → read the delta on more than
> one channel → write the functional meaning + evidence + gesture + build → flag what you
> could not observe as PENDING instead of guessing it.

## The four reading channels (strongest available wins; probe availability in Step 1)

| Channel | What it shows | When it exists |
|---|---|---|
| **Saved file** | the complete document-state effect, including everything the app writes UNASKED (hidden defaults) | any app with a savable artifact (zip-XML, PNG, project file, plain text) |
| **Object model** | programmatic state: property values, counts, computed layout — no pixels needed | apps with COM/AppleScript/scripting APIs (Office, Adobe, CAD…) |
| **UI metadata** | enablement/toggle state for THOUSANDS of controls per staged context, without pressing anything | apps exposing command metadata (Office: `GetEnabledMso`); fallback = UIA `IsEnabled`/pattern-state dumps per context |
| **Screen + real input** | what only a user sees: live previews, caret placement, undo granularity, which tab activates | always — but slow; the spot-check channel |

File channel first when it exists — highest yield per effort, and it surfaces behavior you
didn't know to ask about (a fresh 3-col Word table splits 9,350 twips as 3116/3117/3117 with
a style stamped — no UI surface says any of that).

## The three experiment recipes

1. **Option-dimension enumeration** — the "what's the difference between these N menu
   items" answer. One experiment per option, all from the IDENTICAL starting state; diff the
   N outputs **against each other**: the deltas ARE the option semantics. Never enumerate
   combinations — one dimension at a time, plus targeted combination probes only where
   interaction is plausible. **Craft probe inputs so every hypothesis produces a different
   output** — a table-sort probe with values that happen to already be sorted is a silent
   no-op fixture (real incident: `b/a/c` fixture survived Word's auto-header detection
   unchanged and "passed").
2. **Baseline subtraction** — the defaults-finder. Diff the action's output against a
   blank-document save from the same producer; boilerplate cancels; the surplus = what the
   app does when you specify nothing.
3. **Noise self-diff** — run the SAME action twice; anything differing between the two
   outputs is per-save noise by definition (random ids, timestamps). Learn the noise list
   empirically — never guess it from documentation. Re-run the self-diff suite whenever you
   add a new action category.

## Gesture discipline (the single most important calibration)

**The automation API is not the app.** Measured on Word: the ribbon's Insert Table
auto-applies a style that the COM verb does not; ribbon Bullets writes a 9-level list where
the API writes single-level; even the SAME feature through two different gestures (dialog
autofit arg vs. the AutoFit ribbon command) writes different file content. Rules:

- Drive the UI's real code path — our agents click the real controls anyway, which is the
  honest side of this divide. Office middle path: `CommandBars.ExecuteMso(idMso)` runs the
  button's actual code headlessly; plain API verbs only where an A/B experiment proved them
  identical to the button.
- **Record the gesture on every behavior fact** (`gesture: "ribbon-click"` / `"dialog"` /
  `"keyboard"`). A fact without its gesture is not reproducible.
- **Pin the app build on every record.** Real incidents: an auto-update changed behavior
  mid-run; a fact measured on the Mac build was flat wrong on Windows.
- NEVER fire a programmatic invoke on a control that opens a MODAL from a non-pumping host —
  it deadlocks the app's UI thread (proven repeatedly; 5 workaround attempts all failed).
  Modals are driven with real input on the interactive desktop.

## State rules at scale

- **Toggle test:** press twice from the same state — second press reverts? toggle (Bold).
  Repeats the action? command (Insert Row).
- **Enablement matrix:** stage canonical contexts (bare caret / text selected / inside
  table / object selected / …) and read every control's enabled state per context through
  the metadata channel — thousands of rules per hour, hang-free, and the same sweep that
  yields `requires` preconditions. Office pin: `GetEnabledMso` over the idMso inventory
  (2,570 controls × context proven); generic fallback: UIA `IsEnabled` dumps.
- **Selection-follow test:** put the caret/selection into already-formatted content — does
  the control's visual state reflect it?
- **Persistence probes:** reopen the dialog/dropdown after use — did the choice stick?
  (Sequence-dependent state resists single-action instruments; script multi-step sessions
  or mark PENDING.)

## Interaction dynamics (screen channel only — priority-gate it)

Live previews on hover, caret landing after an action, undo/redo granularity ("one Ctrl+Z
removes the whole just-inserted table"; "redo restores the table but NOT the tab
activation"), contextual-tab activation on insert-vs-caret-entry. Only recordings with real
input see these; expectations for interaction behavior come from a recording, NEVER from
memory. Slow and per-feature → reserve for the highest layers; every recording carries a
provenance header (method, starting state, build, cleanup).

## Trusting your instruments (half of all serious errors are the instrument lying)

- **Self-diff suites**: same action twice → diff must be zero (this also OPERATIONALLY
  defines noise-list completeness).
- **Planted goldens**: hand-built pairs with a known expected diff — the only way
  text-blindness and order-blindness false-passes were ever provable as bugs.
- **Answer-key rediscovery**: before trusting a pipeline at scale, list the gaps you already
  know exist, forbid the pipeline from reading the list, require it to rediscover each one —
  a miss = a PIPELINE bug (a pilot run caught six instrument bugs this way).
- **Control experiments**: a suspicious measurement? Re-run the identical method on a
  known-clean feature; if the artifact appears there too, it's the method's, not the
  subject's.
- **Refuted-hypothesis records**: write down what turned out FALSE so nobody re-tests it;
  mark untested corners untested instead of extrapolating.

## What resists measurement (mark PENDING, don't fight)

Sticky/sequence-dependent state; cross-feature interaction matrices (quadratic — sample via
journey recordings, never enumerate); continuous dynamics (drag rules, animation, "feel");
combinatorial conditional formatting. The honest output is a confidence-labeled note or a
PENDING flag that may not be guessed closed — never a completed-looking table.

## Ops pins (Office family; adapt the pattern per app)

- Fresh hidden instance per experiment; never attach to the user's instance. PID hygiene:
  snapshot pre-existing app PIDs, refuse to run if any exist, kill only PIDs you spawned.
- `SaveAs2(path, 16)` = .docx; **backgrounded shells wedge inside SaveAs2** — keep oracle
  commands short and foreground. COM activation hangs in sandboxed shells.
- `Visible=false` changes what's measurable: screen-coordinate APIs need a visible window;
  use `Range.Information` for geometry instead.
- Property readbacks lie at the wrong granularity: paragraph-level reads collapse mixed runs
  to sentinels (bold=false, size=9999999) — read at the granularity the feature operates on.
  Some properties never read back at all → fall back to the file channel.
- The app is silently tolerant as a reader: invalid values ignored, orphaned references
  dropped. "It opens fine" proves nothing — read seeded markers back.
- Tooltips: UIA `HelpText` is empty on Word ribbon controls, but the `FullDescription`
  property (30159) DOES carry supertips (proven in our word runs — see uia.md). The
  ms-word-clone project never tried 30159; treat their "dead end" verdict as untested there.
