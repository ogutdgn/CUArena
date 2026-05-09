# cua-bench

A benchmark for evaluating CUA (Computer Use Agent) models. Three mock applications + a per-app verifier framework. Agents interact with each mock; logs are scored against task rubrics.

```
cua-bench/
├── apps/
│   ├── figma/      Figma Design mock + verifier  (active)
│   ├── sheets/     Google Sheets mock + verifier (planned)
│   └── docs/       Google Docs mock + verifier   (planned)
├── overview/       Cross-app docs (system overview, log contract, conventions, roadmap)
├── shared/         Future home for the extracted shared verifier framework
└── .claude/        Repo-internal skills + settings (commit, session-end, research, ...)
```

## Where to start

- **Working on the figma app?** → [apps/figma/README.md](apps/figma/README.md), [apps/figma/CLAUDE.md](apps/figma/CLAUDE.md)
- **Need containerized figma delivery?** → [apps/figma/docker-compose.yml](apps/figma/docker-compose.yml), [apps/figma/delivery-1/DOCKER_DELIVERY.md](apps/figma/delivery-1/DOCKER_DELIVERY.md)
- **Repo-level conventions / cross-app rules?** → [CLAUDE.md](CLAUDE.md), [overview/](overview/)
- **What is this benchmark, conceptually?** → [overview/system-overview.md](overview/system-overview.md)
- **What's planned next?** → [overview/roadmap.md](overview/roadmap.md)

## Status

| App | Mock | Verifier | Tasks |
|---|---|---|---|
| figma | shipping | shipping | 50 in `apps/figma/cua-eval/figma_tasks_finished.csv` |
| sheets | not started | not started | — |
| docs | not started | not started | — |
