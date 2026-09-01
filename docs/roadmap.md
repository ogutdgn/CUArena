# Roadmap

Current state and the order of work. Status is deliberately blunt; see
[arc.md](arc.md) for how the repo got here.

## Where things stand

| Piece | State |
|---|---|
| **figma** | Shipping. Mock, verifier (10 rubrics / 11 check modules), 50 tasks, Docker delivery, model runner, published scores (pass@3 = 10%). |
| **ms-word** | Word-faithful clone shipping. Home tab complete; Insert tab in progress against a completeness ledger. Logger / verifier / MCP are designed (ADR-0001) and **not built** — this is the biggest single gap in the repo. |
| **ms-word-native** | Superseded at Phases 0–1. Kept as a decision record + the `rllogger` artifact. Not continued. |
| **pipeline** | Produces a complete KB for a four-tab Word scope (`kb/word-4tabs-v1`). The KB → environment-scaffold step is **not built**. |

## Next, in order

1. **Word env: logger.** Tap `dispatchTransaction`, emit the three streams, match the
   contract in [log-contract.md](log-contract.md). This is what makes the second
   environment an actual environment rather than a clone.
2. **Word env: verifier + first task set.** Reuse the figma rubric framework; this is the
   forcing function for extracting the shared parts into `shared/`.
3. **Close the pipeline loop.** KB → generated environment scaffold (ribbon data, control
   inventory, priority-ordered feature list). The KB schema was designed against what the
   figma and Word builds consumed, so this is a codegen problem, not a redesign.
4. **Second pipeline app.** Run the playbook against a non-Word app — the design bet is
   that per-app scripts are disposable and `toolbox/` lessons compound. That claim is
   untested until app #2.

## Not planned

- Continuing the native Qt6 line.
- `sheets` / `docs` environments — placeholders in earlier docs; not started, and not next.
