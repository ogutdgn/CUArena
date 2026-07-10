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

## 2026-07 — Environment lessons (every Windows GUI run)

- **RULE:** cloud-synced (OneDrive) folders silently enable AutoSave → the canonical fixture gets
  mutated and close-time save dialogs vanish. Always launch a scratch COPY from the OS temp dir.
- **RULE:** screenshots must be window-true (PrintWindow), never screen-region grabs (a
  foreground window gets captured instead of the target); LOOK at each capture to confirm it.
- **RULE:** window titles and UI labels are locale-dependent ("Dosya", "Not Defteri") — match on
  automation ids / locale-tolerant patterns, never English strings.
- **RULE:** store-app launchers are stubs — pin the version from the ATTACHED window's process,
  not the launcher exe.