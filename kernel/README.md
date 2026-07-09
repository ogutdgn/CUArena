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
  per app, guided by `toolbox/` knowledge. See `references/legacy/` for proven implementations.
- **Safety** — in this architecture the agent writes its own driving code, so safety is enforced
  by **environment isolation** (scratch-copy fixtures, no real accounts/data — a mistaken Save
  hits a throwaway file) plus playbook instruction, not by intercepting the agent's clicks.

The kernel grows only by deliberate, reviewed promotion — never as a side effect of a run.
