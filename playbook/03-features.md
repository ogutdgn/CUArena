# Step 3 — Features & sub-features: the 3-level knowledge tree

## Goal

Turn the measured skeleton into meaning: the app's **features** (level 2) and **sub-features**
(level 3), each answering *"what is this doing?"*, plus the **connections** between them. This is
where structure becomes knowledge.

## How (agent decides the details)

- Group the skeleton's measured controls into user-recognizable **features** (what a user would
  name if asked "what can this app do?"). Under each, the concrete **sub-features** (the
  individual actions/controls: bold, insert-table, page-margins…).
- For every node fill the rubric (schema in `design/knowledge-base-design.md`): what it does,
  how it's triggered (**trigger path = real id-chain** from the skeleton), what it affects, what
  it looks like (screenshot ref), `audience_breadth` (everyone / most / niche / role-specific).
- Record **connections** (`affects/uses`) between any two nodes at any level, each with a short
  *why*. These edges drive priority in Step 4 — skimping here corrupts the ranking.
- **Contextual surfaces**: use state-changing probes to discover UI that only exists in context
  (e.g. insert an object → new tabs appear). Document them as surfaces + trigger edges recording
  *when* they exist. Work on the throwaway fixture copy; reset after.
- Where official docs exist and are text-based/current, they may *guide* your grouping — but
  never create a node from docs alone; the live app confirms everything.

## Be sure of

- All common rules (`playbook/README.md`).
- Every feature/sub-feature must be reachable: at least one trigger path into the skeleton.
- Connections need evidence (the measured behavior or observed dependency), not vibes.

## Proof

1. The 3-level tree on disk (feature/sub-feature JSONs via kernel writers), every node with a
   resolving trigger path.
2. Connections recorded with reasons; no orphan nodes (mechanical check: every skeleton
   `triggers` marker points at a node that exists, and vice versa).
3. Contextual surfaces (if any exist in this app) documented with their triggering condition.
4. A short written map: features list with one-liners — readable by a human who knows the app
   ("does this look like the app?").
