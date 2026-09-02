# CUArena

**Turning real applications into instrumented RL/eval environments for computer-use agents.**

A computer-use agent (CUA) can only be trained or measured against an app you can
*reset, observe, and grade*. Real Word and real Figma are closed boxes — no ground-truth
state, no clean reset, no operation stream. So you rebuild the app as something you own.

This repo is three environments and one pipeline, built in that order over four months.
The order is the point: **I built two environments by hand, measured what the cost
actually was, and then automated that part.**

---

## The arc

```
 Apr–May 2026            Jun 2026                    Jul 2026
 ┌───────────────┐       ┌───────────────┐           ┌───────────────┐
 │ envs/figma    │       │ envs/ms-word  │           │ pipeline/     │
 │ build ONE env │──────▶│ do it on a    │──────────▶│ automate the  │
 │ end to end    │       │ 10x harder app│           │ expensive part│
 └───────────────┘       └───────────────┘           └───────────────┘
        │                        │                           │
   an env is not a UI      the bottleneck is not       so make the spec
   clone — it is UI +      implementation, it is       a machine-produced
   log contract + rubric   SPECIFICATION               artifact
```

Each stage exists because of what the previous one cost. The long version, with the
decisions and the dead ends, is in **[docs/arc.md](docs/arc.md)**.

---

## What's here

| | What it is | Built |
|---|---|---|
| **[envs/figma](envs/figma/)** | Figma Design mock (TS/React) + Python verifier + 50-task benchmark + Docker delivery + model runner | by hand |
| **[envs/ms-word](envs/ms-word/)** | Microsoft Word clone (Electron + ProseMirror + forked SuperDoc converter) — 10 ribbon tabs, 216 controls, real `.docx` round-trip | by hand |
| **[envs/ms-word-native](envs/ms-word-native/)** | The other Word attempt: native Qt6 renting LibreOffice's engine via LOK. Superseded — kept as the decision record, with its C++ [`rllogger`](envs/ms-word-native/rllogger/) | by hand |
| **[pipeline/](pipeline/)** | An agent drives the real app and emits a structured knowledge base of it — the step that dominated both hand-builds | by an agent |

Every environment speaks the same **three-stream log contract**
([docs/log-contract.md](docs/log-contract.md)): `raw` (every input event),
`semantic` (every meaningful operation), `outcome` (live document state). The verifier
reads `semantic` + `outcome`; `raw` is forensics.

That contract is the whole design. It is why an environment scores *how* a goal was
reached, not only whether it was: two agents both produce "a square inside a frame", one
in 3 operations and one in 8 via copy-paste-reparent, and the efficiency multiplier
separates them.

---

## It produces real numbers

The Figma environment has been run end-to-end against frontier models —
50 tasks × 3 attempts:

| Metric | Value |
|---|---|
| pass@1 | 6.7% (10/150) |
| pass@3 | 10.0% (5/50) |
| mean score | 0.269 |
| nonzero score | 141/150 (94%) |

94% of attempts score *something* and 10% pass: the tasks are reachable, the grading is
graded rather than binary, and the benchmark is nowhere near saturated.

---

## The knowledge base the pipeline produces

One command's worth of agent work on Microsoft Word (`Home`, `Insert`, `Design`,
`Layout` + every contextual tab they summon) →
[`pipeline/kb/word-4tabs-v1/`](pipeline/kb/word-4tabs-v1/):

- **38 features · 194 sub-features · 433 UI containers** (34 marked as honest stubs)
- a **232-node / 343-edge** UI graph — what opens what, what each control affects
- **priority layers P0–P4** — what an environment must implement first
- **389 verified screenshots**, and a `journal.jsonl` audit trail of every decision

This is the artifact that the `envs/ms-word` build needed a human month to write.

---

## Archive tags

Four annotated tags preserve work that was never merged to `main` and is kept as history:
`archive/ms-word-parity-pipeline`, `archive/ms-word-parity-v2`,
`archive/ms-word-ui-structure`, `archive/ms-word-ensure-parity` (266 unique commits).

The tags hold the parity-measurement machinery and the UI crawler built inside the Word
environment in early July 2026 — the prototype that became [`pipeline/`](pipeline/) the
following day. See [the bridge section in docs/arc.md](docs/arc.md).

## Repo map

```
CUArena/
├── envs/
│   ├── figma/             mock/ · verifier/ · delivery-1/ · cua-eval/ · scripts/
│   ├── ms-word/           src/ · specs/ · docs/decisions/ (ADR-0001…0006)
│   └── ms-word-native/    docs/research/ (692-control ribbon study) · app/ · rllogger/
├── pipeline/
│   ├── design/            what a knowledge base IS (schema, 3-level model, priority)
│   ├── playbook/          the steps the agent follows (goal · be-sure-of · proof)
│   ├── toolbox/           tool knowledge that compounds across apps
│   ├── kernel/            the only fixed code: schema writers + journal
│   └── kb/                the produced knowledge bases
└── docs/
    ├── arc.md             the three stages and what each one taught
    ├── log-contract.md    the cross-environment logging contract
    ├── decisions/         cross-environment ADRs
    └── conventions.md · roadmap.md · system-overview.md
```

## Status

| Piece | State |
|---|---|
| figma env | shipping — mock, verifier, 50 tasks, Docker, model runner, published scores |
| ms-word env | Word-faithful clone shipping; Home tab complete, Insert tab in progress; logger/verifier/MCP designed (ADR-0001) but not built |
| ms-word-native | superseded at Phases 0–1; kept as decision record |
| pipeline | produces a full KB for a 4-tab Word scope; the KB → environment-scaffold step is **not built yet** |

**The link that is still open:** the pipeline produces the specification, and the
environments consume one — but a human still does the consuming. Closing that loop
(KB → generated environment scaffold) is the next piece of work, and the KB schema was
designed against exactly what these two builds needed.

## Where to start

- The story and the reasoning → **[docs/arc.md](docs/arc.md)**
- Run something → [envs/figma/README.md](envs/figma/README.md) (`docker compose up -d --build mock`)
- The hardest technical decision → [docs/decisions/engine-rent-vs-own.md](docs/decisions/engine-rent-vs-own.md)
- How an app gets understood → [pipeline/playbook/](pipeline/playbook/)

> Not affiliated with Microsoft or Figma. The clones are independent look-alikes built as
> research environments.
