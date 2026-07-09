# kernel/ — the only live code

Everything else in this project is knowledge (design, playbook, toolbox) or memory
(references, kb). The kernel is the small set of code that must **not** be rewritten per app,
because these are guarantees where "the agent did it differently this time" is a bug, not a
feature.

| File | Guarantee it provides |
|---|---|
| `models.py` | The KB schema. Every knowledge record is validated against it — the format is the product's contract that every downstream phase (features, priority, later replica generation) depends on. |
| `kb_writer.py` | Schema-enforcing writers. They **refuse** invalid or malformed records, so whatever the agent produces is valid KB by construction. |
| `journal.py` | The append-only audit log. One canonical recorder → cross-run and cross-app comparability, reproducibility, and honest failure records. |

## What is NOT in the kernel (deliberately)

- **Perception and driving** (reading the UI, clicking, screenshots) — the agent writes these
  per app, guided by `toolbox/` knowledge. Proven examples: `references/word-crawler/` and
  previous apps' own `kb/<app>/scripts/tools/`.
- **Safety** — in this architecture the agent writes its own driving code, so safety is enforced
  by **environment isolation** (scratch-copy fixtures, no real accounts/data — a mistaken Save
  hits a throwaway file) plus playbook instruction, not by intercepting the agent's clicks.

The kernel grows only by deliberate, reviewed promotion — never as a side effect of a run.

## If the kernel is missing something you need (rule for agents)

If your mission requires a model/field the kernel doesn't have, you may extend it **additively**
(new models, new optional fields — never weaken or change the meaning of what exists). But every
kernel change MUST be **flagged prominently**: journal it as a `decision` with your reasoning,
and call it out explicitly in your final report. Kernel changes get human review after the run —
an unflagged kernel change is a rule violation even if the change itself was correct.
(Precedent: the Word Home-tab run correctly added the tree models — Connection, TriggerPath,
`explored` — which were reviewed and adopted.)
