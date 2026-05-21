# cua-bench

A benchmark for evaluating CUA (Computer Use Agent) models. Four CUA environments + a per-app verifier framework (where applicable). Agents interact with each environment; logs are scored against task rubrics.

```
cua-bench/
├── apps/
│   ├── figma/        Figma Design mock + verifier         (active — TypeScript mock)
│   ├── sheets/       Google Sheets mock + verifier        (planned)
│   ├── docs/         Google Docs mock + verifier          (planned)
│   └── libreoffice/  LibreOffice fork (Writer/Calc/Impress) + rllogger
│       ├── CLAUDE.md / AGENTS.md / docs/   app-entry docs
│       ├── README.md                        app intro
│       └── libreoffice-codebase/            vendored 143k-file LO tree + our mods
├── overview/         Cross-app docs (system overview, log contract, conventions, roadmap)
├── shared/           Future home for the extracted shared verifier framework
└── .claude/          Repo-internal skills + settings (commit, session-end, research, ...)
```

## Where to start

- **Working on the figma app?** → [apps/figma/README.md](apps/figma/README.md), [apps/figma/CLAUDE.md](apps/figma/CLAUDE.md)
- **Need containerized figma delivery?** → [apps/figma/docker-compose.yml](apps/figma/docker-compose.yml), [apps/figma/delivery-1/DOCKER_DELIVERY.md](apps/figma/delivery-1/DOCKER_DELIVERY.md)
- **Working on the libreoffice app?** → [apps/libreoffice/README.md](apps/libreoffice/README.md), [apps/libreoffice/CLAUDE.md](apps/libreoffice/CLAUDE.md), [apps/libreoffice/docs/architecture/ROADMAP.md](apps/libreoffice/docs/architecture/ROADMAP.md), [apps/libreoffice/docs/USAGE.md](apps/libreoffice/docs/USAGE.md)
- **Repo-level conventions / cross-app rules?** → [CLAUDE.md](CLAUDE.md), [overview/](overview/)
- **What is this benchmark, conceptually?** → [overview/system-overview.md](overview/system-overview.md)
- **What's planned next?** → [overview/roadmap.md](overview/roadmap.md)

## Status

| App | Shape | Mock / Runtime | Verifier | Tasks |
|---|---|---|---|---|
| figma | TS mock | shipping | shipping | 50 in `apps/figma/cua-eval/figma_tasks_finished.csv` |
| libreoffice | real binary | Phase 4 done (Writer UI parity); logger V1.1; Calc/Impress pending | not started | — |
| sheets | TS mock | not started | not started | — |
| docs | TS mock | not started | not started | — |
