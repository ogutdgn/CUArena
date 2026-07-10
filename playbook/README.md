# playbook/ — the steps an agent follows to learn an app

The playbook is the pipeline's *plan*, expressed as knowledge, not code. Each file is one step
the agent works through to turn an application into a knowledge base. The agent supplies the
judgment and writes its own per-app tools (guided by `toolbox/`); the playbook tells it **what
to achieve, what to be sure of, and what proof to produce** before moving on.

**Before you start, read [`LESSONS.md`](LESSONS.md)** — the pipeline's memory of what prior runs
got wrong and the rule that now prevents each mistake. It is short; every entry was paid for once.
When your run finishes, append your own post-mortem (like toolbox give-back) — that is part of the
job.

Every step has the same three parts:

- **Goal** — what the agent must achieve.
- **Be sure of** — the invariants that hold at every step (drive-and-see, never save/delete,
  journal everything, obey the schema, prove every claim, mark `unexplored` honestly when stuck).
- **Proof** — the checkable artifact that means "this step is done." No proof, no done. This is
  the guard against confident-but-empty output.

## Common rules (bind at EVERY step)

1. **Drive and see** — verify the visible result of every action before relying on it.
2. **Measured, not assumed** — `opens`/`triggers` markers only from observed outcomes.
3. **Never destructive** — no save/send/delete/purchase; work only on throwaway fixture copies;
   discard save-prompts (never Save).
4. **Journal everything** — every action and outcome via the kernel journal; failures and
   ambiguity are valid outcomes, silence is not. **Decisions too:** whenever you make a
   significant judgment call (grouping choice, exploration order, skipping something, resolving
   an ambiguity), journal it as `action="decision"` with your reasoning in `data` — the journey
   must show not only what you did but why you chose it.
5. **Schema is law** — all knowledge written through `kernel/kb_writer.py`; rejected = fix it,
   don't work around it.
6. **Prove or mark** — every claim traceable to evidence; when stuck, mark `unexplored` honestly
   and move on.
7. **Give back** — new tool lessons get appended (dated) to `toolbox/*.md`.

## Execution contract — this is an autonomous loop

Once started, the run needs **no human hand**. The agent drives itself to completion:

1. **Work the steps in order, as a loop:** do the step → produce its Proof → **check the proof
   yourself** (mechanical checks + your own eyes on the evidence) → if it passes, advance to the
   next step immediately; if it fails, diagnose, fix, and redo — do not advance on a failed proof,
   and do not ask a human to approve a passed one.
2. **Never stop to wait for a human.** Blocked on something you can work around → journal it,
   mark the affected area `unexplored`, continue. Only a truly fatal environment problem (app
   won't launch at all, disk unwritable) ends the run — loudly, with the journal explaining why.
3. **The run is resumable.** All state lives on disk (`kb/<app>/`: journal, worklist, routes,
   written knowledge) — a fresh session reads the journal and the last proofs, determines the
   current step, and continues from exactly there. Long apps may take many sessions; the loop
   doesn't care.
4. **Done means Step 5's definition-of-done passes** — not "I ran out of things I felt like
   doing." Until then, the loop continues.

## The steps

| # | Step | Produces |
|---|---|---|
| 0 | [Stage](00-stage.md) — launch, reach the workspace, record the entry route | workspace screenshot + replayable route + version pin |
| 1 | [Tools](01-tools.md) — dump the live UI tree, write your own per-app tools | evidence-pinned enumerator/driver in `kb/<app>/scripts/tools/` |
| 2 | [APP SKEL](02-app-skel.md) — press-observe-classify every top-level surface | containers with measured markers + screenshots |
| 3 | [Features](03-features.md) — the 3-level tree + connections + contextual surfaces | the shallow knowledge tree |
| 4 | [Priority](04-priority.md) — rank P0–P4 from connections + usage + audience | evidence-backed `priority/` artifacts |
| 5 | [Depth](05-depth.md) — exhaust P0–P2 per the depth-endpoint rule; shortcuts; icons | the complete KB, definition-of-done checked |

The KB these steps produce is defined in `design/knowledge-base-design.md`.
