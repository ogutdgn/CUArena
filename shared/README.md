# shared/

**Currently empty by design.**

This folder is the future home of the shared verifier framework — the parts of `apps/figma/verifier/` that are app-agnostic (Task / Rubric / Check / CheckResult dataclasses, log loader, CLI runner skeleton, efficiency math).

## Why empty now

We have one app shipping (figma). Extracting "shared code" from a single example is premature abstraction — we'd guess wrong about what the second app actually needs. The plan is:

1. Build Sheets by **copying** `apps/figma/verifier/` to `apps/sheets/verifier/` and adapting in-place.
2. Once Sheets is end-to-end and producing scores, look at the diff between figma's verifier and sheets' verifier.
3. The parts that are identical (or trivially parameterizable) move to `shared/`. The parts that diverge stay per-app.

Until then, any "shared library" decisions made now are speculation.

## Migration plan (when Sheets ships)

- Create `shared/verifier/` with: `types.py`, `loader.py`, `config.py`, `runner.py`, `efficiency.py`, the abstract Rubric/Check base classes, and any check primitives that are truly geometry-agnostic.
- Each app's `verifier/` imports from `shared.verifier.*` and contributes only its app-specific check classes (figma's shape checks, sheets' cell/formula checks).
- Per-task scripts (`apps/<app>/verifier/tasks/*.py`) stay per-app — they're inherently bound to the app's primitives.

Until then, **don't put anything here**. If you're tempted to factor something out, write it in the per-app verifier and revisit when there are two examples.
