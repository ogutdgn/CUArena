---
name: helper-blind-read-prevent
description: Use before reading any file under apps/<app>/helper/. Enforces the "go through 00-overview.md first" rule so agents do not waste context on raw research material or miss critical scope/status flags.
---

# Don't Read Helper Blind

**Status: ACTIVE.**

## The rule

Before reading any file under `apps/<app>/helper/` (other than `00-overview.md` itself), open `apps/<app>/helper/00-overview.md` first.

## Why

The helper corpus is large (figma's is hundreds of files). Reading it without the overview means:
- You waste context on material the overview would have told you was out of scope (DEF / out-of-scope features).
- You miss the FN / VO / DEF status taxonomy that gates whether a feature is implementable today.
- You miss the workflow-by-question reference table that says **which file answers your specific question** (saves 4–5 wrong reads).
- You pick up stale framing from historical planning docs that have been superseded.

## Procedure

1. Read `apps/<app>/helper/00-overview.md` end to end (or at least §7 "artifact map" + §7a "workflows" + the question-routing table at the end of §7a).
2. Identify which workflow applies (implementing a feature, adding UI, handling a VO click, looking up a feature).
3. Follow the workflow's prescribed file order.
4. Only then open specific helper files.

## Exceptions

- Reading `helper/00-overview.md` itself — go ahead.
- Following an explicit user instruction that names a specific helper file — go ahead, the user already routed you.
- Reading the `helper/` README in a non-figma app that has no overview yet (sheets/docs at skeleton stage) — use git tree to orient.

## When this skill saves you

- "I need to know how Figma's pen tool works" → overview routes you to `helper/extracted/features/vector/use-pen-tool.md`, not to the 175 source articles.
- "Is fillgrad in scope?" → overview routes you to `helper/analysis/feature-inventory-deep.md`, where status is FN/VO/DEF.
- "What does the right-panel show for a multi-select?" → overview's question table sends you straight to `helper/extracted/ui-schema/state-matrix.md`.
