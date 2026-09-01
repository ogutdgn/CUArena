# lessons.md — what previous runs got wrong (read this BEFORE you run)

Every run teaches something. This file is the pipeline's memory of its own mistakes: each entry
is a real failure from a real run — symptom, root cause, and the rule that now prevents it.
Read it during orientation; **append your own run's post-mortem when you finish** (that is part
of the job, like toolbox give-back). Keep entries in the same format.

Format:
```
## <date> — <app / scope>
- SYMPTOM: what looked wrong in the output
- ROOT CAUSE: why it happened
- RULE NOW: what prevents it (link the playbook/design section)
```

---

## 2026-07-08 — MS Word / Home tab (first full run)

- **SYMPTOM:** Depth stopped one level deep. A P1 capability's dropdown was entered, but the
  dialogs that dropdown's items opened ("Paste Special", "More Underlines…") stayed
  `explored: false`. Looked done; wasn't.
- **ROOT CAUSE:** "depth" was read as "open the node's first surface", not "follow every branch
  to its end". Nested stubs were invisible to the DoD check.
- **RULE NOW:** `05-depth.md` — descend TRANSITIVELY; a P0–P2 node is done only when NO
  `explored:false` container is reachable from it by any chain of `opens`.

- **SYMPTOM:** P0 held only 3 nodes and the ranking felt off — Paste (the app's #1 command by
  real usage) landed P1, buried beneath Font-group members that all cross-linked to each other.
- **ROOT CAUSE:** connection density was used as a VALUE signal and all edge types weighed
  equally, so a large co-located clique inflated its own members' centrality.
- **RULE NOW:** value = usage only (`04-priority.md`: product-reasoning + UI-prominence + web);
  connections are logistics, not value; edge types ranked requires > affects-same > co-location
  (`03-features.md` §2).

- **SYMPTOM:** the ranking listed `subfeature:font` (P0) above `feature:font` (P1) — a
  sub-feature outranking its own parent.
- **ROOT CAUSE:** features and sub-features were scored in one flat pool.
- **RULE NOW:** only sub-features are scored; a feature's layer is DERIVED as its best child's
  layer, so a child can never outrank its parent (`04-priority.md`).

## 2026-07-08 — MS Word / Home + Insert (second run)

- **SYMPTOM:** contextual tabs were dead ends. `ui:ribbon-table-layout` was captured with 37
  children, every one `unexplored` / triggers-opens both null; NONE became a sub-feature, NONE
  entered the ranking. We knew a table's outline but nothing about how a table is used.
- **ROOT CAUSE:** contextual surfaces were photographed then abandoned — never fed back into the
  feature tree or priority, so depth could never reach them.
- **RULE NOW:** `03-features.md` §3 — a contextual surface runs the FULL loop: document the face
  → turn its controls into feature/sub-feature nodes (context-inclusive trigger paths) → connect
  → feed into priority → depth deepens the P0–P2 ones. `04-priority.md`: every node incl.
  contextual ones must be ranked.

- **SYMPTOM (caught in design review, not shipped):** a pull toward making every dropdown entry
  (border color / weight / dashes…) its own sub-feature — would explode the tree and inflate
  connections.
- **ROOT CAUSE:** no rule bounding how deep the sub-feature level should go.
- **RULE NOW:** `03-features.md` §1 — the variation test: children that are variations of the
  same effect are OPTIONS (depth documents them), not sub-features. Tie-breaker: "could these
  carry different importance?"

## 2026-07-10 — MS Word / Home + Insert (v2, consolidated layout — the fix run)

Scope: HOME + INSERT + all contextual tabs they summon. Output: `kb/word-home-insert-v2/`.
Result: DoD PASS, `graph_builder.generate()` CLEAN. 34 features, 172 sub-features, 231 UI
containers, 25 shortcut keys; P0–P2 = 49 sub-features at full transitive depth.

- **WIN (the v1 dead-end, reversed):** every contextual tab ran the FULL press-observe loop,
  not just a face capture. 235 contextual controls measured (117 opens / 50 triggers). Table
  Layout — the tab that shipped 37 `unexplored` names in v1 — is now 20 real sub-features
  (Merge Cells, Split Table, Insert Rows/Columns, Cell Alignment…), and Merge Cells / Insert
  Rows / Picture Crop / Wrap Text rank **P1 on their own usage**. The rule that worked:
  contextual controls become nodes → enter the ranking → depth deepens the P0–P2 ones
  (`03-features.md` §3, `04-priority.md`).

- **SYMPTOM:** the same control slug means different things on different contextual tabs —
  `more`/`less` = cell-size on Table Layout but header-position on Header&Footer and object-size
  on the object tabs; `outline-color-picker` = Picture Border on Picture Format but Shape
  Outline elsewhere. A pure suffix→sub-feature map mis-folded them.
  - **ROOT CAUSE:** folding contextual controls by id-suffix alone ignores the hosting tab.
  - **RULE NOW:** keep a small **(tab, suffix) → sub-feature override** table checked before the
    generic suffix map. The shared-capability model (one `object-arrange`/`object-size`/
    `shape-styles` sub reached from many tabs via multi-host trigger paths) is right and dedupes
    the repeated Arrange/Size/Styles groups — but collisions still need per-tab disambiguation.

- **SYMPTOM:** a depth re-drive helper passed the CONTAINER id as the walker's `owner`, so every
  re-driven endpoint got `triggers: <container-id>` — 271 gaps at DoD (an endpoint must fire a
  NODE, never a container).
  - **ROOT CAUSE:** the walker uses `owner` as the endpoint's trigger target; a helper that
    doesn't thread the real owning sub-feature poisons every leaf it writes.
  - **RULE NOW:** any code that drives a surface must thread the owning sub-feature id, not the
    surface id, as `owner`. Cheap reconciliation: propagate ownership down the `opens`-chain from
    the ribbon opener (`el_owner`) and rewrite any `triggers` pointing at a container.

- **SYMPTOM:** two entered surfaces (Remove Background, a crop `Fill` cascade) were `explored:true`
  with empty `children` → DoD "empty but explored" (a dishonest done).
  - **ROOT CAUSE:** they are interactive MODES / single actions, not menus — the hit-test walk
    found nothing enumerable, but they are NOT deferrals either (we did enter them).
  - **RULE NOW:** a mode/action surface with no enumerable items gets ONE honest child that
    `triggers` its owner with a "mode, not a menu" note — neither an empty-explored lie nor a
    false `unexplored` stub.

- **RULE NOW (depth driving is fragile — budget for it):** re-driving a split-button DROPDOWN
  from a cached open-point fails once the ribbon shifts (the click lands on the primary zone,
  arming the mode, opening nothing). Re-enumerate the LIVE split element at press time and click
  its exact dropdown-child rect (the step-2/3 approach), never a point cached at tab-activation.
  Same class: the UIA `win` wrapper goes stale after heavy interaction (esp. an OS file dialog) —
  re-attach the frame and retry `select_tab` before giving up.

## 2026-07-10 — v2 post-run AUDIT (the reviewer's own mistakes — audits obey the same rules)

- **SYMPTOM:** the audit reported a `feature:feature:equation-tools` double-prefix defect in
  `priority.json`. The data was clean — a repo-wide grep finds ZERO occurrences of
  `feature:feature`. The "defect" existed only in the audit script's own output: a print
  statement prepended `feature:` to an id that already carried the prefix.
  - **ROOT CAUSE:** the reviewer reported a defect from a FORMATTED display of the data instead
    of the raw bytes, and never verified the claim against the actual file before reporting it.
  - **RULE NOW:** a claimed defect must be confirmed in the RAW file (grep/read the exact
    bytes) before it is reported. Never trust a derived/pretty-printed view of the thing you
    are auditing — the view can inject the bug it claims to find.

- **SYMPTOM (same class, same review):** the run's `priority/` dir was labelled a "legacy
  leftover" fit for deletion. On inspection it holds UNIQUE evidence: `signals/` (raw
  product-purpose verdicts, prominence measurements, web-usage research dump) and
  `justification.md` (the Step 4 proof prose) — none of it duplicated in `priority.json`.
  - **ROOT CAUSE:** a dir was judged by its name and position, not its contents.
  - **RULE NOW:** look INSIDE before proposing deletion; "redundant" is a claim about contents,
    proven by diffing them, never by the filename.

## 2026-07-12 — v2 audit round 2 (example-driven review; classification lies + unasked questions)

Walking single examples (table-autofit, table-style-options, multilevel-list) exposed two
failure families the structural checks could not see: **lies told at classification time**
(a false `triggers` legally terminates a chain, so every later check inherits it as truth) and
**questions no check was asking**. Five rules came out of it (now numbered in the playbook).

- **SYMPTOM:** 11 in-ribbon galleries (Table Styles, Picture Styles, Chart Styles…) recorded as
  one `menuitem` endpoint each — the full gallery flyout and its bottom commands ("New/Modify/
  Clear …", which open dialogs) absent from the KB entirely.
  - **ROOT CAUSE:** a tile press was taken as the whole control's classification; the expand
    arrow was never driven. No rule named galleries (the split-button rule stopped at 2 zones).
  - **RULE NOW:** R2.5 — a gallery is a THREE-zone control; the expand arrow is its own `opens`
    element (`toolbox/uia.md` 2026-07-12 for the how).

- **SYMPTOM:** ~14 "…"-labeled controls ("Convert Text to Table…" on a P0 node, "Options…",
  "More Gradients…") closed as endpoints with the note "no surface appeared on press".
  - **ROOT CAUSE:** when a press produced no detected surface, the walker's fallback was
    "endpoint" — the platform convention (… = opens a dialog) was never encoded as an
    expectation, so no contradiction fired.
  - **RULE NOW:** R2.4 [kernel-checked] — ellipsis-labeled elements may carry `opens` or stay
    `unexplored`, never `triggers`; a surfaceless press is a FAILED press, journaled as such.

- **SYMPTOM:** 2 of those galleries said `pressed: no observable effect` AND `triggers` in the
  same record — a claim with its own counter-evidence attached.
  - **ROOT CAUSE:** classification fell through to "endpoint" as a default instead of honesty.
  - **RULE NOW:** R2.3 — no effect, no endpoint: journal the failure, mark `unexplored`.

- **SYMPTOM:** `subfeature:smartart-layout` sat in NO priority layer; all checks passed. (Plot
  twist found at commit time: the RUN had ranked it correctly — an accidental local edit had
  corrupted the id string inside priority.json to garbage, post-commit. The finding stands and
  gets stronger: hand-touchable JSON silently rotted and nothing screamed.)
  - **ROOT CAUSE:** "every node is ranked" existed as playbook prose with no mechanical check —
    so neither a run's omission NOR later data corruption had anything watching for it.
  - **RULE NOW:** R4.3 [kernel-checked] — graph_builder flags any node absent from every layer.
    The check earned its keep immediately: it is what exposed the corruption.

- **SYMPTOM:** the transitive depth walk reported v2 CLEAN while 24/92/80 unexplored elements
  were reachable from P0/P1/P2 nodes (e.g. the Replace dialog's own "Find Next" button).
  - **ROOT CAUSE:** an element that was never pressed creates no container, and the walk only
    inspected containers — element-level gaps were structurally invisible.
  - **RULE NOW:** R5.4 [kernel-checked] — the depth walk inspects BOTH levels: reachable
    `explored:false` containers and reachable non-chrome `unexplored` elements both fail DoD.

## 2026-07-13 — v2 / behavior fields (why Step 6 + BehaviorRecord exist)

- **SYMPTOM:** v2's `behavior` fields on P0–P2 nodes were filled yet meaningless — e.g.
  table-autofit's read "Opens AutoFit (dropdown). Contents (3 controls): AutoFit Contents,
  AutoFit Window, Fixed Column Width" — a re-listing of the menu (structural echo), zero
  semantics. A builder could draw the menu but not implement the difference between the
  three commands. The DoD passed: "behavior non-null" was the whole bar.
  - **ROOT CAUSE:** behavior was ONE free-text field with no slot structure (gaps
    invisible), no evidence requirement (claims unfalsifiable), no functional-language rule
    (label-echo counted as content), and no measurement step that owned it.
  - **RULE NOW:** Step 6 (playbook/06-behavior.md) owns semantics measurement over the
    depth set; findings go into `BehaviorRecord` — structured SLOTS (effect / options /
    defaults / state_rules / dynamics / extra / pending), FREE functional prose inside
    (R6.2: what a user observes, never instrument readouts), every claim evidenced (R6.3
    [kernel-checked]), gesture + build pinned (R6.4), unmeasured = pending, never guessed
    (R6.5). Method knowledge: toolbox/behavior.md (verified distillation of the
    ms-word-clone measurement corpus, 2026-07-13).

## 2026-07-13 — v2 audit round 3 (scenario-driven review: created artifacts, scrollable surfaces)

- **SYMPTOM:** `cover-page-insert` carried ZERO connection toward the shape machinery —
  though Word cover pages are literally BUILT of shapes/text-boxes (selecting a part summons
  Shape Format). Had cover-page entered the replication set, closure could not have pulled
  what it never saw; the replica would insert a cover page made of machinery it doesn't have.
  - **ROOT CAUSE:** no rule required poking the artifact an insert-endpoint CREATES; the
    walker recorded "document changed → triggers ✓" and moved on, so composition edges only
    ever appeared where an agent happened to click around (tables), not deterministically.
  - **RULE NOW:** R5.6 — after an insert/create endpoint fires, select the created artifact;
    record the contextual worlds it summons + composition `requires` edges (measured).

- **SYMPTOM:** `ui:font-dropdown` holds 23 items — on a machine with 317 installed font
  families, and the captured names are the alphabet's head (Abadi, ADLaM, Agency…): the
  first screenful, never scrolled. 47 containers carry scrollbar traces; none records
  whether it was scrolled to the end.
  - **ROOT CAUSE:** the scroll recipe existed as toolbox knowledge (input.md: wheel +
    re-enumerate until nothing new) but no playbook rule made it binding, no field recorded
    it, and no check asked. Knowledge without rule = applied by luck.
  - **RULE NOW:** R2.8 [kernel-checked, gated] — scrollability is detected and addressed:
    `scrolled_to_end: true` (exhausted) or `false` + journaled honest partial ("23 of ~317").
    Screenshots follow the scroll as an ordered SERIES covering the whole content.

## 2026-07-13 — MS Word / HOME + INSERT + DESIGN + LAYOUT (word-4tabs-v1, full run)

Scope: HOME + INSERT + DESIGN + LAYOUT ribbon tabs + all contextual tabs/surfaces they summon.
Output: `kb/word-4tabs-v1/`. Result: DoD PASS, `graph_builder.generate()` CLEAN (0 problems).
38 features, 194 sub-features, 408 UI containers (374 explored / 34 P4-outline), 25 shortcut
keys; P0–P3 depth set = 149 sub-features at full transitive depth; 149 evidenced BehaviorRecords.
Build 16.0.20131 (same as v2 — tool code reused via `common.py` re-bind, every marker
re-measured live).

- **WIN (the new ground — DESIGN + LAYOUT):** the two always-present tabs integrated cleanly.
  Document Formatting (capability) + Page Background (catalog) on Design; Page Setup + Paragraph
  (capability) on Layout. The Layout **Arrange** group is object-gated (disabled on bare text) —
  it is the SHARED `feature:object-arrange` machinery, folded in by measuring it with a shape
  selected (`run_step3_layout_arrange`) and mapping the controls as extra trigger paths into the
  same object-arrange subs the contextual object-format tabs feed. `page-margins` ranked P1,
  `orientation`/`breaks` P2 — the everyday page-setup levers surface correctly.

- **SYMPTOM:** the current kernel (post-`R5.4`-element-check, P0–**P3** depth set) is STRICTER
  than the one v2 shipped CLEAN against — `graph_builder.generate('word-home-insert-v2')` now
  reports 57 R5.4 gaps. So "v2 was CLEAN" is not a free pass; a new run is held to the current
  kernel.
  - **ROOT CAUSE:** R5.4 flags every non-chrome `unexplored` element and every `explored:false`
    stub reachable from any P0–P3 node (not just P0–P2). Deep nested option-dialog openers
    ("More Fill Colors…", "3-D Options…", "Convert Text to Table…") the transitive walk left
    deferred all became gaps.
  - **RULE NOW (applied, honest):** resolve them three ways — (1) seen-set: an opener whose
    dialog was captured elsewhere resolves to `opens` that shared container (Colors dialog,
    Format-Object pane, Borders&Shading); (2) genuine BOUNDARIES (global Word Options,
    Stock/Online pictures, Copilot, nth-level format sub-panes of P2–P3 features) get the
    LESSONS 2026-07-10 mode/action pattern — `opens` a per-opener stub that is `explored:true`
    with ONE honest child that `triggers` the owner and NOTES the boundary (never an
    `unexplored` child, which R5.4 re-flags); (3) commit buttons ("Apply") → `triggers` owner.
    This is a **priority-bounded depth boundary**, defensible per the design (depth is bought
    with priority), but it IS a deliberate scoping choice — a fuller run would drive each deep
    option pane. Reconcilers: `reconcile_depth` / `reconcile_options` / `reconcile_final`.

- **SYMPTOM:** the depth walk hung on tab activation after entering the Insert-Pictures flyout
  ("This Device…" = OS file dialog, "Generate an Image…" = Copilot) — 40 later targets failed
  `tab-activate` because a stuck surface blocked the ribbon and the retry only re-attached the
  UIA wrapper.
  - **RULE NOW:** the tab-activate retry does a HARD win32-only reset first —
    `_force_close_nonframe` closes every non-frame top-level window (no COM, the point is to
    unblock a COM the modal is holding), waits for COM to answer, re-resolves the frame hwnd,
    then re-attaches. Add "generate an image"/"copilot" to the network-boundary hints so the
    walk never enters those. (`run_step5_enter` retry block.)

- **SYMPTOM:** the header/footer contextual tab would not appear — `sel_header()` did
  `Headers(1).Range.Select()`, which moves the selection into the header story but does NOT
  switch the window into header-edit MODE, so no tab, and the UIA tab-strip read empty.
  - **RULE NOW:** enter header/footer editing via `View.SeekView = 9` (wdSeekCurrentPageHeader),
    exit with `= 0`; a Range.Select() alone is not the trigger. (toolbox/com.md 2026-07-13.)

- **SYMPTOM (Step 6):** the first behavior sweep measured only 21/66 command effects — the
  generic fingerprints (tables.Count, format_sig) miss TABLE STRUCTURE changes (a merged/added
  cell/row/column leaves tables.Count = 1) and clipboard/draft effects.
  - **RULE NOW:** the enablement matrix (`GetEnabledMso` across 10 staged contexts) is the
    reliable BULK channel — it gave state_rules + `requires` for all 136 idMso-resolved nodes in
    one hang-free sweep (e.g. merge-cells "enabled in-table only"). For EFFECT, `ExecuteMso` +
    a delta on the strongest channel works, but the channel must match the feature: a
    STRUCTURE-aware fingerprint (`Tables(1).Rows/Columns/Range.Cells.Count`) for table ops, the
    doc-text hash for Cut, format_sig for Highlight — re-measured in `run_step6_remeasure`.
    Clipboard-only (Copy) and pending-draft (InsertNewComment) effects are genuinely
    unobservable on any offline channel → honest `pending`, never guessed (R6.5). Openers are
    NOT ExecuteMso'd (modal-deadlock, toolbox/behavior.md) — their effect is the functional
    outcome (what applying an option changes) + the enumerated options, per-option semantics
    `pending`.

- **RULE NOW (Spinner controls):** ribbon value fields are `Spinner` leaves with SIBLING
  More/Less steppers, not a composite — add `Spinner` to the interactive set or a whole group
  (Layout > Paragraph) vanishes; widen the format signature with RightIndent/SpaceBefore/After
  or the steppers read false no-effect; type-drive the field for a MEASURED trigger rather than
  fabricating one (R2.3). (toolbox/uia.md 2026-07-13.)

## 2026-07-13 — word-4tabs-v1: R2.5 recurred (a rule wired into one worker path, not its sibling)

- **SYMPTOM:** the 4-tabs run repeated v2's exact defect — 11 in-ribbon STYLE galleries (Table/
  Picture/Graphics/Shape/Chart/SmartArt/WordArt Styles, SmartArt Layout, Equation Symbols)
  closed as `triggers` endpoints; the expand arrow never pressed, so the full flyouts (105
  Table Styles + "New/Modify/Clear" dialog openers) were absent. 8 more galleries sat
  `unexplored`.
  - **ROOT CAUSE:** `run_step2` HAD the R2.5 in-ribbon-gallery branch (Home Quick Styles,
    Design Style Set were correct); the CONTEXTUAL crawl path (`run_step3_contextual`) did not.
    A rule applied to one worker path and not its sibling fails silently on everything only the
    sibling touches. The mechanical check that would have caught it did not exist yet.
  - **RULE NOW:** kernel R2.5 check [kernel-checked] — on a TAB surface, a gallery-named element
    closed as `triggers` with no expand twin is flagged. Output-level checks beat path-level
    discipline: the check does not care WHICH worker wrote the node. (It found the 11 instantly
    on both v2 and 4tabs.) Also fixed: the R2.8 scroll-trace detector keyed on bare
    "horizontal"/"vertical" labels and false-flagged a Text Direction dialog's "Horizontal"
    radio — scrollbar detection now requires the line/page steppers + "position".

- **REPAIR (this session, in-KB):** `scripts/tools/repair_galleries.py` staged each object
  family via COM, activated its contextual tab, pressed the LIVE gallery's expand zone,
  enumerated the full flyout (tiles + bottom commands, openers descended into their dialogs),
  rewrote each element to `opens`, filled `behavior_record.options` from the tiles, and wired
  pure-duplicate galleries by seen-set reference. `reshoot_gallery_series.py` added the R2.8
  screenshot SERIES (scroll + capture until the frame repeats; a flyout whose content fits one
  screen keeps one frame — correct, not a miss). Two `Change Shape` galleries stayed honest
  `unexplored` (need a SmartArt SUB-shape selected; niche P4) — an honest defer, not a false
  endpoint. Result: kernel CLEAN, graph.json regenerated, 84 sub-features carry option data.
  Two bugs fixed mid-repair: a rect/point click mismatch (expand-rect vs zone-point), and an
  options backfill that read a crawl-time variable instead of the recorded ui.json tiles.

## 2026-07-13 — the ratio's high-set was still P0–P2 (a boundary move that half-happened)

- **SYMPTOM:** word-4tabs-v1's derived feature scopes were computed with the OLD boundary —
  `hi = children in {P0,P1,P2}`. Verified by recomputing all 38 features both ways: 26 of the
  discriminating ones matched the P0–P2 formula, ZERO matched P0–P3. Consequence: 21 features
  that should be `whole` under the P0–P3 depth boundary were under-scoped (chart-design 1/7→7/7,
  object-arrange 1/8→8/8, picture-format 1/13→10/13, table-layout 8/20→15/20…) — their P3
  children silently excluded from replication.
  - **ROOT CAUSE:** when the depth boundary moved P0–P2 → P0–P3 (2026-07-12), the run's
    `combine_priority.py` had that constant in FIVE places; the fix updated four (boundaries,
    layer loops, depth-set membership, closure) and missed the one `hi = [... P0,P1,P2]` line
    that feeds the ratio. A boundary that lives in several places moves in several edits, and
    one gets left behind — exactly the "rule wired into one path, not its sibling" failure, one
    layer down.
  - **RULE NOW:** the ratio formula is written explicitly in `04-priority.md` (hi = children in
    P0–P3; ratio = hi/n; majority×2>n → whole unless catalog; hi==0 → none; else gems), and the
    kernel RECOMPUTES stored ratio AND scope from layers + cohesion and flags any mismatch
    [kernel-checked] — a run carrying a stale boundary in its own scripts can no longer ship its
    derivation. (Precedent this session: the same "output-level check beats path-level
    discipline" that caught the R2.5 galleries.)
  - **CONSEQUENCE (honest):** widening the depth set to the corrected `whole` scopes pulled
    previously-out-of-set children INTO it, exposing genuine pre-existing depth debt in those
    nodes (ellipsis endpoints, un-entered dialog interiors, an unset scroll flag). That debt was
    always there — the wrong ratio was hiding it. Closing it is a targeted re-crawl of the newly
    promoted surfaces, tracked as the run's remaining DoD gap.

## 2026-07-13 — closing the depth debt the ratio fix exposed (15 → 0)

Widening the depth set (P0–P2 → P0–P3 ratio) pulled newly-promoted whole-children in, exposing
15 pre-existing gaps in them. Closed by class, each with the honest treatment matching the run's
own established patterns:

- **Dialog leaf fields (19 elements, unexplored → triggers):** Sort / Hyphenation dialog fields
  (edit/combo/radio/checkbox/spinner/Yes-No) were enumerated but left `unexplored`. The KB norm
  for enumerated dialog leaves is `triggers` (font-dialog: 60/61 fields are triggers) — a labeled
  option field is a leaf endpoint by the depth-endpoint rule. Data reclassify, no live app.
- **Ellipsis "…Options…" openers (6, triggers → opens):** the KB has 266 ellipsis openers done
  right (`opens`); these 6 were `triggers` because their owner (text-effects, artistic-effects)
  was breadth-only at crawl time. The run's IDENTICAL Shadow/Glow/Reflection Options on Shape
  Format were measured to open `object-format-pane`, and the run created
  `ui:options-deep-option-boundary` as the honest shared target for nth-level format sub-panes.
  Pointed the 6 there — matching a measured precedent, not an invented one. The fragile 3-level
  text-effects cascades were NOT re-driven (LESSONS: cached cascade points fail).
- **Empty stubs (live-crawled):** Text Outline color picker → opened live, swatch grid + commands
  captured (8 children), the sibling tab's stub referenced by seen-set (same owner/palette).
  `Right to Left` → measured to open NO surface → it is a direct toggle, owner reclassified
  `triggers`, empty stub dropped.
- **Task-pane scroll (R2.8 scoping):** a Format pane's window scrollbar ("Page up/left") tripped
  the scroll-completeness check. R2.8 targets scrollable TILE/LIST surfaces (galleries,
  dropdowns) where items hide below the fold; a task pane's chrome scrollbar is not that. Kernel
  now exempts `kind == "pane"` from R2.8.

Result: word-4tabs-v1 kernel CLEAN (0 problems), graph.json regenerated, v2 unchanged (88).

## 2026-07 — Environment lessons (every Windows GUI run)

- **RULE:** cloud-synced (OneDrive) folders silently enable AutoSave → the canonical fixture gets
  mutated and close-time save dialogs vanish. Always launch a scratch COPY from the OS temp dir.
- **RULE:** screenshots must be window-true (PrintWindow), never screen-region grabs (a
  foreground window gets captured instead of the target); LOOK at each capture to confirm it.
- **RULE:** window titles and UI labels are locale-dependent ("Dosya", "Not Defteri") — match on
  automation ids / locale-tolerant patterns, never English strings.
- **RULE:** store-app launchers are stubs — pin the version from the ATTACHED window's process,
  not the launcher exe.

## 2026-07-10 — Windows 11 Paint (modern WinUI app — first non-Office target, full run)

Scope: the WHOLE modern Paint app. Output: `kb/paint/`. Result: DoD PASS,
`graph_builder.generate()` CLEAN (0 problems). 12 features, 47 sub-features, 28 UI containers,
16 shortcut keys; P0–P2 = 37 sub-features at full depth. Version pinned 11.2603.251.0.

- **WIN (a whole app end-to-end, and much smaller than Word):** Paint's entire surface is ~170
  UIA nodes and launches straight to the workspace (no fixture/welcome). The Word lessons
  transferred (press-observe-classify, window-class = dialog/flyout, window-true PrintWindow
  capture, state-gated controls need a representative state) even though NONE of the Word driving
  code applied — the toolbox (knowledge) carried across, the code did not, exactly as designed.

- **SYMPTOM:** the run HUNG for minutes on the Edit-colours control and had to be killed.
  - **ROOT CAUSE (two compounding bugs):** (1) modern WinUI opens surfaces TWO ways — a windowed
    `PopupWindowSiteBridge`/PopupHost (File/Edit/View menus, Rotate/Flip/Copilot) AND an IN-TREE
    XAML surface with NO new window (Brushes/Size flyouts, Resize&Skew & Edit-colours dialogs, the
    Settings page). Edit-colours is in-tree, but a coincident tiny "White" ScreenTip rendered as
    its own PopupHost window, so a window-delta-only detector classified it as a windowed popup,
    enumerated the tooltip, and the reset (which only looked for top-level windows) never closed
    the real in-tree modal — which then blocked all input. (2) the "what opened?" detector walked
    the full UIA tree with pywinauto wrappers, which took 150s+ with the rich dialog open.
  - **RULE NOW:** detect an opened surface as window-set-delta UNION main-window UIA-subtree-delta;
    area-floor windowed popups (~8000px²) so tooltips don't mask in-tree surfaces; close in-tree
    ContentDialogs via their Cancel button, verified by BOTH no popup window AND no Cancel-in-tree.
    Walk the tree with the RAW IUIAutomation ControlViewWalker, never pywinauto wrappers (150s → 1s);
    key nodes by (control_type, name, rect), not per-node GetRuntimeId (a COM round-trip each).
    (`kb/paint/scripts/tools/surface.py`, `driver.reset_surfaces`; toolbox win32.md/uia.md/input.md.)

- **SYMPTOM:** the whole toolbar re-drive resolve-failed after the Settings control; and later,
  `write_ui` rejected containers keyed `subfeature:pencil`.
  - **ROOT CAUSE:** (a) Settings opens a FULL-PAGE in-window view that Escape cannot close (it needs
    the Back arrow), so it hid the toolbar and every later control vanished; (b) selecting a TOOL
    changes the tree as a side effect (the Size/Opacity sliders appear, Text spawns a contextual
    band), so `observe` reported "in_tree" and the code built a container out of a tool's trigger id.
  - **RULE NOW:** exit full-page views via their Back control (put such controls LAST as a backstop);
    decide a control's marker by its KNOWN handling FIRST — tools/colours/commands are always
    `triggers` (any tree side-effect IS the state change, not a surface) and never create containers;
    only opener handlings enumerate surfaces. (`run_step2.py` is_opener gate.)

- **RULE NOW (ElementFromHandle is a flaky, slow COM call):** `Desktop().window(handle=)` +
  `ElementFromHandle` intermittently raises `UIA_E_ELEMENTNOTAVAILABLE` and is slow. Resolve the
  frame's RAW element ONCE, cache it on the session, and drive all raw walks/finds from that;
  re-attach a pywinauto wrapper only for control resolution, and only on an actual miss — not every
  iteration. (`session.raw_frame`, `uia_read.attach` retry.)

- **RULE NOW (no COM object model → build the oracle from what you can measure):** Paint exposes no
  automation object model (unlike Word). The press-observe oracle was assembled from: window-set
  delta, UIA subtree delta, the Brushes/Color-1 selected-state flip (a measured `triggers` signal),
  and a canvas pixel-hash. Absent a doc/format fingerprint, these ARE the measurement.