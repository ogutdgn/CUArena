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

### 3. Contextual surfaces & docs

- **Contextual surfaces**: use state-changing probes to discover UI that only exists in context
  (e.g. insert an object → new tabs appear). Document them as surfaces + trigger edges recording
  *when* they exist. Work on the throwaway fixture copy; reset after.
- Where official docs exist and are text-based/current, they may *guide* your grouping and hint
  at connections — but never create a node from docs alone; the live app confirms everything.

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
