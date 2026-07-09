# Step 4 — Priority: rank what matters (P0–P4)

## Goal

Rank every feature/sub-feature into five layers **P0–P4**, so Step 5 spends deep-inspection
effort only where the app's identity lives. A priority is never a vibe — it is arithmetic over
three evidence-backed signals.

## The three signals (design/knowledge-base-design.md defines them)

1. **Connection density** — count/centrality over the `affects/uses` edges from Step 3. Compute
   it with a small script you write (deterministic — same graph in, same scores out).
2. **Real-world usage** — research what users of this app actually use most (web search / docs).
   Every usage score MUST carry its evidence: claim + source + how it maps to a node. No
   evidence, no score.
3. **Audience breadth** — from each node's `audience_breadth`: everyone > most > niche /
   role-specific.

## How

- Normalize each signal to 0–1, combine with recorded weights, sort, cut into P0–P4 at recorded
  boundaries. Write the working artifacts under `kb/<app>/priority/`:
  `signals/…`, `ranking.json` (scores + weights), `layers.json` (final P per node + boundaries).
- Sanity-check the result against common sense for this app category: the features every user
  touches constantly must outrank installation-specific or niche ones. If the ranking contradicts
  obvious reality, the inputs are wrong — investigate before accepting.

## Be sure of

- All common rules (`playbook/README.md`).
- Weights, boundaries, and all evidence are **recorded in the artifacts** — "why is X P0?" must
  be answerable by opening files.
- No signal invented: connectivity from the real graph, usage only with sources, audience from
  the nodes.

## Proof

1. `kb/<app>/priority/` complete: per-signal files, ranking with weights, layers with boundaries.
2. Every usage-signal entry has claim + source.
3. A one-paragraph justification of the top layer ("these are P0 because…") that a human can
   check against their own knowledge of the app.
