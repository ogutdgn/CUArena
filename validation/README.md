# validation/ — findings and results of building the pipeline

This folder is where the execution of each implementation plan (A, B, C, …) becomes **readable
evidence**. One subfolder per plan; each contains:

- `report.md` — the questions the plan set out to answer, each with an explicit verdict
  (**ANSWERED-YES / ANSWERED-NO / PARTIAL**) and a link to the evidence. This is the file to read.
- `results/` — frozen snapshots of acceptance-run outputs (KB samples, journal excerpts,
  test-run summaries). Snapshots survive here even when `kb/<app>/` is deleted and regenerated
  during development.

## Rules

1. **Questions → verdicts.** Reports start from the plan's validation questions. No verdict
   without evidence; no evidence without a link or snapshot.
2. **Evidence lives here; design does not.** A finding that changes the design goes into the
   spec (`docs/superpowers/specs/`), and the report links the commit. This folder never becomes
   a second source of truth for design.
3. **A plan is not done without its report.** Filling `report.md` is an acceptance criterion of
   every plan.
4. **Snapshots are copies, not references.** `kb/` output cited as evidence is copied into
   `results/` at acceptance time, because `kb/` is disposable during development.
