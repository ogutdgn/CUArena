# Step 3 — Features & sub-features: the 3-level knowledge tree

## Goal

Turn the measured skeleton into meaning: the app's **features** (level 2) and **sub-features**
(level 3), each answering *"what is this doing?"*, plus the **connections** between them. This is
where structure becomes knowledge.

## How (agent decides the details)

### 1. Build the tree — shallow, but complete for every node

- Group the skeleton's measured controls into user-recognizable **features** (what a user would
  name if asked "what can this app do?"). Under each, the concrete **sub-features** (the
  individual actions/controls: bold, insert-table, page-margins…).
- **Shallow means we don't open every dialog and enumerate every option here** — we work at the
  level of the general surfaces/tables. It does NOT mean thin: **every feature AND every
  sub-feature — even in this shallow pass — must carry its core identity rubric**
  (schema in `design/knowledge-base-design.md`):
  - **what it is / what it does** — a real description, not just a name
  - **how it is triggered** — the trigger path (real id-chain from the skeleton) + any shortcut
  - **what it affects** — the state/target it changes (you measured this in Step 2's press-observe)
  - `audience_breadth` (everyone / most / niche / role-specific)
- A node with only a name is not done. You can't build a meaningful connection on top of a node
  whose purpose and trigger you haven't recorded — so the identity rubric comes first, then
  connections rest on it.
- **A sub-feature that opens a surface (e.g. Font Color → a color dialog) is still fully recorded
  here**: its rubric says what it does and that it `opens` that surface (measured in Step 2), and
  the surface it opens stays a **stub** (`explored: false`) — see Step 2. You are documenting the
  feature's identity, not the dialog's interior; that interior is Step 5's job, priority-gated.
  The node is NOT `unexplored`; only the opened surface's contents are deferred.

### 2. Discover connections — grounded in evidence, not vibes

Record `affects/uses` edges between any two nodes at any level, each with a `why` and a `source`.
Find them, in order of how measured they are:

- **A. Co-location (measured, free):** controls the app itself groups together are connected —
  same ribbon group / dialog section / menu. Evidence: `co-located in ui:<container>`. Falls out
  of the skeleton you already mapped.
- **B. Shared effect target (measured, from Step 2):** two controls whose press-observe state-
  diffs touch the **same** target are connected (Bold and Font Size both mutate the selection's
  character format). Evidence: the observed shared state target.
- **C. Dependency (observable):** feature B only works when feature A's artifact exists
  (search-by-label needs Labels). Testable — does B function without A's output?
- **D. Contextual co-appearance (measured):** surfaces that appear together in the same context
  (select a table → Table Design + Layout tabs) are connected to their trigger and each other.
- **E. Domain inference (judgment — labeled):** your knowledge that two things relate. Allowed to
  PROPOSE edges, but any edge resting only on this carries `"source": "inference"`; confirm it
  with a cheap observation where you can.
- Every edge records `{target, kind: affects|uses, why, source: measured|observed|inference}`,
  stored in the SOURCE node's `connections[]` (one direction is enough; assembly counts both
  ways for centrality). These edges drive priority in Step 4 — skimping corrupts the ranking.

### 3. Contextual surfaces — discovered, then FED BACK IN (not dead ends)

Use state-changing probes to discover UI that only exists in context (e.g. insert an object →
new tabs appear). Work on the throwaway fixture copy; reset after. But discovery is only HALF
the job — the half that gets forgotten:

**A contextual surface is not a trophy to photograph; it is a new command surface whose
controls are real features.** Word example: inserting a table makes **Table Design** and
**Table Layout** tabs appear. Their controls — Header Row, Banded Rows, Delete Rows, Merge
Cells, Remove Background (on Picture Format), Crop — are genuine, heavily-used features: a user
who inserts a table spends most of their table-time INSIDE Table Layout. A KB that documents
the table-insert button to full depth but leaves Table Layout's 37 controls as unexplored
names knows how a table is *created* but not how a table is *used* — half the knowledge.

So for every contextual surface you discover, run the SAME loop as any other surface:

1. **Document the surface** (face + screenshot) with its **triggering condition** recorded
   ("exists only while an embedded table is selected; appeared on the 'table' probe").
2. **Feed its controls into THIS step's tree**: they become features/sub-features with the full
   shallow rubric (what-it-does / trigger path — which INCLUDES the context, e.g.
   `[insert table → select it → ui:ribbon-table-layout → el:merge-cells]` / affects / audience),
   and connections (they are at minimum connected to the feature that summons them — that edge
   is `source: "contextual"`).
3. **They enter Step 4's priority ranking like every other node.** The ranking decides whether
   Merge Cells matters more than Drop Cap — it cannot decide that if Merge Cells was never
   ranked. A contextual control absent from the ranking is a silent gap, not a low priority.
4. **Step 5 then deepens the ones that rank P0–P2**, exactly as it would any other node —
   pressing each control, following its `opens` chains to the bottom, writing the full rubric.
   The whole point of steps 1–3 above is to get contextual controls INTO the node set so this
   depth step can reach them; skip those steps and they are permanently invisible to depth.

**The failure this prevents (real, from a prior run):** `ui:ribbon-table-layout` was written with
37 children, every one `unexplored: true` and `triggers`/`opens` both null, and NOT ONE of them
became a sub-feature or entered the priority ranking. The tab's outline existed; all 37
table-editing features were invisible to the rest of the pipeline. The fix is the loop above: the
face is step 1, but steps 2–4 are what turn a screenshot into knowledge.

**Docs**: where official docs exist and are text-based/current, they may *guide* your grouping and
hint at connections — but never create a node from docs alone; the live app confirms everything.

## Be sure of

- All common rules (`playbook/README.md`).
- **No name-only nodes:** every feature/sub-feature has what-it-does + how-triggered + what-it-
  affects filled, even at this shallow depth.
- Every feature/sub-feature must be reachable: at least one trigger path into the skeleton.
- Every connection carries evidence (`why`) and a `source` tag; inference-only edges are labeled
  as such.

## Proof

1. The 3-level tree on disk (feature/sub-feature JSONs via kernel writers). **Mechanical check:
   no node is missing description, trigger path, or affects** — a name-only node fails the step.
2. Every node has a resolving trigger path (every skeleton `triggers` points at a node that
   exists, and every node points back — no orphans).
3. Connections recorded with `why` + `source`; every `connections[].target` resolves to an
   existing node (mechanical check — no dangling edges).
4. Contextual surfaces (if any exist in this app) documented with their triggering condition.
5. A short written map: features list with one-liners — readable by a human who knows the app
   ("does this look like the app?").
