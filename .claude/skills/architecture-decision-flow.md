---
name: architecture-decision-flow
description: Use after research is committed and before writing app code. Covers brainstorming the stack/state/op-set with the user, recording the decision as an ADR, and producing the app's architecture.md.
---

# Architecture Decision Flow

**Status: PLACEHOLDER — to be filled when we run the first architecture-decision cycle for Sheets.**

## Expected outline

1. **Inputs**: the app's committed helper corpus (`apps/<app>/helper/`) + the cross-app log contract (`overview/log-contract.md`).
2. **Brainstorming session** with the user (use `superpowers:brainstorming` skill): what stack, what state shape, what op set, what coordinate/identity model. Output: a candidate set with trade-offs.
3. **Decision**: pick one candidate. Record as a short ADR-style doc in `apps/<app>/app-docs/decisions/NN-<topic>.md` (numbered, append-only). State alternatives, chosen path, why, and what would invalidate the decision.
4. **Architecture document**: write `apps/<app>/app-docs/architecture.md` summarizing the decided stack, state buckets, op set, transaction/undo model, logger streams, folder structure. Mirrors the figma version.
5. **Cross-check**: skim `overview/log-contract.md` to confirm the new app's logger plan satisfies the cross-app shape.

The figma example: `apps/figma/app-docs/architecture.md` is the destination format.
