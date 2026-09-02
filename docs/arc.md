# The arc — three stages, and what each one cost

This repo was not designed top-down. It is three projects, built in sequence, where each
one exists because of a bill the previous one made me pay. This document is the reasoning
in order, including the parts that did not work.

---

## Stage 1 — Build one environment, end to end (Figma · Apr–May 2026)

**Thesis:** before generalising anything, get one environment all the way to a score.

What got built: a Figma Design mock in TypeScript/React, a three-stream logger, a Python
verifier framework (10 rubrics over 11 check modules), 50 authored tasks, a Docker
delivery, and a runner that drives real frontier models through episodes.

**What it taught — an environment is not a UI clone.** The clone is the cheap third of it.
An environment is three things that have to agree:

1. a UI faithful enough that a skill learned here transfers to the real app,
2. a **log contract** — because a pixel stream is not gradeable,
3. a **rubric** that turns the log into a number.

The log contract is where the actual design lives. Splitting the stream into `raw`
(forensics), `semantic` (the operations the engine actually dispatched) and `outcome`
(document state) is what makes it possible to score *method*, not just result. Two agents
both end with a square inside a frame; one did it in 3 operations, the other in 8 via
copy-paste-reparent. Only the semantic stream can tell them apart, and the efficiency
multiplier is what makes that difference cost something.

**The bill.** Writing 50 tasks that are unambiguous, gradeable, and actually reachable
meant knowing Figma exhaustively — every tool, every panel, every preset, what each
control does to the document. That research was slower than building the mock.

---

## Stage 2 — Do it on an app ten times harder (MS Word · Jun 2026)

**Thesis:** if the approach is real, it survives Microsoft Word — 10 ribbon tabs, 62
groups, 216 controls, a 14-section backstage, and `.docx`.

Two attempts ran here, and the difference between them is the most useful thing in the
repo.

### Attempt A — rent a real engine (`envs/ms-word-native`)

A native Qt6 app that owns the UI, dispatch, state and logger, and **rents LibreOffice**
through LibreOfficeKit for layout, text shaping and `.docx` I/O. Real engine, real
fidelity, no reimplementation of typography. It reached a working LOK binding, a tile
render path, a golden-frame test — and a C++ three-stream logger,
[`rllogger`](../envs/ms-word-native/rllogger/), compiled into the binary.

It also produced the [692-control Word ↔ LibreOffice ribbon
comparison](../envs/ms-word-native/docs/research/ribbon/) that scoped the whole thing.

**Why it was superseded.** Writing `rllogger` is what exposed the problem. To emit a
`semantic` stream you must tap the point where an operation is dispatched — and in a
rented engine that point is *inside somebody else's code*. Every tap is a patch to a
vendored 1.4 GB tree you have promised not to modify, and every upstream re-vendor
threatens it. Renting the engine buys fidelity and sells the exact seam Stage 1 proved
the environment depends on.

### Attempt B — own the model (`envs/ms-word`)

An Electron clone on a **ProseMirror** authoritative document model, with a vendored fork
of SuperDoc's converter for `.docx` round-trip. The trade is inverted: you reimplement
layout, but you get `dispatchTransaction` — one function, in your own code, through which
every edit passes as serialisable, invertible steps. That is the `semantic` stream, for
free, by construction. And `state.doc.toJSON()` is the `outcome` snapshot the verifier
needs, headless, in Node.

This is the line that shipped. The full argument is in
[ADR-0002](../envs/ms-word/docs/decisions/0002-prosemirror-document-model.md), and the
cross-environment version in [decisions/engine-rent-vs-own.md](decisions/engine-rent-vs-own.md).

**What Stage 2 taught — the bottleneck is specification, not implementation.** The ribbon
in `envs/ms-word` is not hand-written; it is *generated* from research data
(`scripts/gen.js` → `ribbon-data.js`), because 216 controls is past the point where
hand-curation stays honest. And that research — what is in the Insert tab, what each
control does, what it opens, what it affects — was the month. Writing the code was not the
month.

Two environments in, the same line item dominated both. That is a pattern, not an accident.

---

## The bridge — how Stage 2 turned into Stage 3 (early Jul 2026)

The jump from "building environments by hand" to "an agent produces the specification"
was not a leap. It happened inside the Word environment, over the first week of July, and
the work is preserved on four branches that were never merged to `main`:

| Tag (`archive/ms-word-…`) | Commits | What it built |
|---|---|---|
| `parity-pipeline` | 103 | The first parity-measurement pipeline: scorecard axes, a STRUCTURE triage pass, and a run that **clicks every ribbon control in the live clone** |
| `parity-v2` | 69 | A six-axis acceptance rubric (`parity/RUBRIC.md`, `RUNBOOK.md`), behavior cards, a feature-parity audit, and the `.docx` import losses it exposed |
| `ensure-parity` | 3 | The measurement machinery extracted on its own, for step-by-step use |
| `ui-structure` | 91 | **`parity/tools/ui_crawl/`** — a crawler with a resumable orchestrator, plus 95 captured **oracle JSON** files, 46 behavior cards, and per-boundary coverage records |

The question that started it was ordinary: *the clone claims parity with Word — how would I
know?* Answering it required measuring the clone against the real application, which
required driving both, which required capturing what each one *is* in a structured form.
By the time `ui-structure` landed a resumable crawler emitting oracle JSON with explicit
coverage boundaries, the tool had stopped being a parity checker and had become an
app-understanding tool that happened to live inside one app's repo.

**`ui-structure`'s last commit is 2026-07-06. `pipeline/`'s first commit is 2026-07-07.**
The next day the same idea was rebuilt standalone and app-agnostic — an agent driving the
real application and writing its own inspection tools, with the per-app code treated as
disposable and the lessons as the thing that compounds.

These tags are kept as unmerged, read-only history. They are prototype-grade and were
superseded within a day; their value is that they are the actual seam between the two
stages, not a story told afterwards.

---

## Stage 3 — Automate the expensive part (`pipeline/` · Jul 2026)

**Thesis:** the specification should be a machine-produced artifact, not a human's month.

The pipeline is deliberately *not* a code generator. An agent drives the real application
(UI Automation, COM, win32, screenshots), **writes its own per-app inspection tools**, and
emits a structured knowledge base. The design bet is stated in the pipeline's own README:
code does not generalise across apps, **lessons do** — so the per-app scripts are
disposable and the `toolbox/` gets richer with every app.

Only four things are fixed:

| | |
|---|---|
| `design/` | what a knowledge base *is* — schema, the 3-level model, priority |
| `playbook/` | the steps the agent follows: goal · be-sure-of · proof |
| `toolbox/` | tool knowledge and traps that compound across apps |
| `kernel/` | the only live code — schema writers + journal |

The quality gates are mechanical rather than trusted: depth ratios across priority layers
P0–P3, transitive stub closure (a container you opened but never explored is recorded as
`explored:false`, not silently dropped), a per-step definition of done, and a
`journal.jsonl` that records decisions with reasoning so a run can be audited and resumed.

The output for a four-tab Word scope
([`kb/word-4tabs-v1`](../pipeline/kb/word-4tabs-v1/)): 38 features, 194 sub-features, 433
UI containers with 34 honestly-marked stubs, a 232-node UI graph, priority layers, and 389
verified screenshots — the same class of artifact Stage 2 produced by hand, produced by an
agent.

---

## Where this stops being finished

The loop is not closed. The pipeline produces the specification; the environments consume
one; a human is still the thing in between. The KB schema was designed against what the
Word and Figma builds actually consumed — feature trees, trigger paths, priority layers —
so KB → generated environment scaffold is the next stage, not a rewrite.

Being honest about that boundary is the same discipline the pipeline enforces on itself:
an unexplored container is marked `explored:false` rather than quietly omitted.
