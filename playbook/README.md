# playbook/ — the steps an agent follows to learn an app

The playbook is the pipeline's *plan*, expressed as knowledge, not code. Each file is one step
the agent works through to turn an application into a knowledge base. The agent supplies the
judgment and writes its own per-app tools (guided by `toolbox/`); the playbook tells it **what
to achieve, what to be sure of, and what proof to produce** before moving on.

Every step has the same three parts:

- **Goal** — what the agent must achieve.
- **Be sure of** — the invariants that hold at every step (drive-and-see, never save/delete,
  journal everything, obey the schema, prove every claim, mark `unexplored` honestly when stuck).
- **Proof** — the checkable artifact that means "this step is done." No proof, no done. This is
  the guard against confident-but-empty output.

## The steps (to be authored)

| # | Step | Produces |
|---|---|---|
| 0 | Stage — launch, reach the workspace, record the entry route | ready-state screenshot + replayable route |
| 1 | Probe & write your own tools — dump the live UI tree, learn its structure, write per-app readers/drivers under `kb/<app>/scripts/` | a working enumerator proven against a live surface |
| 2 | APP SKEL — document every top-level surface; press-observe-classify each control | containers with measured markers + screenshots |
| 3 | Features & sub-features — the 3-level tree + connections + contextual surfaces | the shallow knowledge tree |
| 4 | Priority — rank into P0–P4 from connections + real usage + audience breadth | an evidence-backed priority table |
| 5 | Depth — exhaust only P0–P2, following the depth-endpoint rule | full detail where the app's identity lives |

The KB these steps produce is defined in `design/knowledge-base-design.md`.
