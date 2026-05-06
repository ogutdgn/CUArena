---
name: development-flow
description: Use during feature implementation work. Covers reading the feature-checklist + execution-map at session start, picking the wave, writing the implementation, and updating the docs at session end.
---

# Development Flow

**Status: PLACEHOLDER — to be filled out from the figma session pattern that already works.**

## Expected outline

1. **Session start (per app)**:
   - Open the app's `app-docs/feature-checklist.md` (customer feature list).
   - Open the app's `app-docs/execution-map.md` (wave plan + session log).
   - Discuss with the user which feature(s) this session targets. Add or update a wave entry to reflect the plan.

2. **Pre-implementation reading**:
   - Read the feature spec under `apps/<app>/helper/extracted/features/<...>` via the helper overview.
   - Cross-check related UI schema regions and analysis docs.
   - Surface any `[gap: not in corpus]` flags with the user before coding.

3. **Implementation**:
   - Engine + UI + logger together (per the figma rule). No half slices.
   - Use TDD where the surface is stable; skip TDD for purely visual work where there's nothing to assert.
   - Keep the change scoped — don't refactor adjacent code unless required by the change.

4. **Session end**:
   - Run the `session-end` skill (see `.claude/skills/session-end.md`).
   - Commit per `commit-style` skill.

The figma session pattern is documented in `apps/figma/CLAUDE.md` "Session workflow" section — that's the working reference.
