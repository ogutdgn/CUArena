# App Pipeline

Replicate whole applications from a single prompt.

The goal of this project is to build a pipeline that can take one prompt — e.g. `build microsoft word`, `build microsoft excel`, `build figma`, `build gmail` — and produce a working replica of that application.

## P1: Knowledge Base Pipeline — current and only focus

Before anything can be generated, the pipeline must first build an accurate, structured knowledge base about the application being replicated. Without accurate knowledge of the application, we cannot replicate it. **P1 is the sole focus right now** — later phases stay undefined until P1 produces reliable results.

The full design lives in the spec: [`docs/superpowers/specs/2026-07-07-knowledge-base-pipeline-design.md`](docs/superpowers/specs/2026-07-07-knowledge-base-pipeline-design.md). In brief:

- **Live app inspection is ground truth.** Inspector agents drive the real app (web or desktop) through a curated catalog of vetted tools; model knowledge guides, docs inform, the live app confirms.
- **The KB is a graph:** app skeleton → features → sub-features, connected by `contains`, `triggers` (the UI/keyboard trigger surfaces), and `affects/uses` edges — plus a UI tree of containers, a shortcut registry, screenshots, and optional harvested docs.
- **Two passes, gated by priority:** a breadth pass maps everything shallowly; an evidence-based ranking (connection density + real usage + audience breadth) cuts features into layers P0–P4; a depth pass exhaustively documents only the top layers.
- **Discipline:** append-only journal, snapshot-diff classification, version pinning, boundaries config, mechanical completeness checks.

## Repository layout

```
docs/superpowers/specs/   # design specs
pipeline/                 # pipeline source: orchestrator + stage logic   (to be built)
tools/                    # shared tool library — the vetted catalog      (to be built)
references/               # donated example scripts — inspire, never dictate
kb/<app>/                 # pipeline output: one knowledge base per inspected app
```

## Roadmap

- **P1: Knowledge Base Pipeline** — design complete; **Plan A built and validated** (runnable skeleton pass: `python -m pipeline.run <app>`); Plan B (breadth + priority) next. *(current focus)*
- Later phases (planning, generation, verification of replicas) will be defined once P1 produces reliable knowledge bases.
