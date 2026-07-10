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

## 2026-07 — Environment lessons (every Windows GUI run)

- **RULE:** cloud-synced (OneDrive) folders silently enable AutoSave → the canonical fixture gets
  mutated and close-time save dialogs vanish. Always launch a scratch COPY from the OS temp dir.
- **RULE:** screenshots must be window-true (PrintWindow), never screen-region grabs (a
  foreground window gets captured instead of the target); LOOK at each capture to confirm it.
- **RULE:** window titles and UI labels are locale-dependent ("Dosya", "Not Defteri") — match on
  automation ids / locale-tolerant patterns, never English strings.
- **RULE:** store-app launchers are stubs — pin the version from the ATTACHED window's process,
  not the launcher exe.