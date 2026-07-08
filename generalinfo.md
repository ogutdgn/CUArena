# General Info — Study Guide for the App Pipeline Project

*A plain-language explanation of what this project is, how the design works, where we are right
now, and what happens next. Written to be studied and re-explained. The technical source of truth
is the spec (`docs/superpowers/specs/2026-07-07-knowledge-base-pipeline-design.md`); this document
explains it.*

---

## 1. The big picture

The project goal: **replicate whole applications from a single prompt** — `build microsoft word`,
`build gmail`, `build figma` → a working replica.

A prompt like `build gmail` carries almost no information by itself. Before anything can be
generated, the system must first *know* what Gmail actually is — precisely enough to rebuild it.
That is why the very first phase, and our **only current focus**, is:

> **P1: the Knowledge Base Pipeline** — a general, executable pipeline that takes an app's name
> and produces a complete, evidence-backed knowledge base (KB) about that app.

Everything else (planning a replica, generating it, verifying it) comes later and stands on P1.
None of it is designed yet — deliberately.

---

## 2. The core design idea

**Live app inspection is ground truth.** The pipeline does not describe an app from memory or
from marketing pages — it opens the *real, running app* and inspects it: reads its UI, clicks
its buttons, watches what happens, takes screenshots. Three supporting knowledge sources exist,
each with strict rank:

- **Model knowledge** guides (tells the inspector where to look) — never trusted as fact.
- **Web documentation** informs (when it passes a quality gate) — never creates knowledge.
- **The live app confirms** — on any conflict, the live app wins.

The output is not prose. It is a **machine-readable graph of JSON files** plus screenshots —
precise enough that later phases can rebuild the app from it without guessing.

---

## 3. What the knowledge base contains

### 3.1 Three levels of nodes

| Level | Anchor question | Holds |
|---|---|---|
| **App skeleton** (1 per app) | *What is this app?* | Identity (what it is, what for, **who uses it** — asked only here) + the UI shell: layout regions, menu map, navigation |
| **Features** | *What is this feature doing?* | Function, trigger paths, what it affects, what it looks like (+screenshot), where it lives, audience (only when it differs, e.g. Track Changes → reviewers) |
| **Sub-features** | *What is this sub-feature doing?* | Same fields, finer grain (Bold, Italic inside Text Formatting) |

Structure stops at three levels in the broad pass; anything smaller (a checkbox, a dropdown
option) is detail *inside* a sub-feature node, not a new node.

### 3.2 Three kinds of edges

1. **`contains`** — the hierarchy: app → feature → sub-feature.
2. **`triggers`** — how things get activated. The skeleton is the *mouse* trigger surface
   (Home tab → Font group → **B** button → Bold); shortcuts are the *keyboard* trigger surface
   (Ctrl+B → Bold). Trigger paths are chains of real ids, not text.
3. **`affects/uses`** — feature connections (Bold ↔ text rendering; search-by-label ↔ Labels).
   Allowed between **any** two nodes at any level. These edges drive priority.

Key insight: skeleton and features are connected *by construction* — every feature is triggered
from somewhere in the skeleton. This makes completeness checkable (see §6).

### 3.3 The UI tree

Dialogs, dropdowns, panes, menus, tabs, sections are all technically the same thing: **UI
containers**. Each is one JSON file with `children[]` (what's inside it) and elements that carry
**exactly one** of three markers:

- `opens: "ui:<id>"` — this element reveals more UI (a button that opens a dialog)
- `triggers: "<node-id>"` — this element fires a feature (an endpoint)
- `unexplored: true` — deliberately not expanded (low priority)

Every element record must carry **control type, icon, and label** — the raw material for
replicating the UI. Icons get a text description *and* a cropped image.

### 3.4 Shortcuts

A separate registry (`shortcuts/<keys>.json`) is the source of truth: one file per key
combination, with **context-scoped bindings** (Escape does different things in a dialog vs. on a
selection), each stating *when* it's active, *how* it acts, and *what* it triggers/opens. Nodes
only carry display strings ("Ctrl+B"). No separate depth policy — shortcuts surface on whatever
the pipeline already scans.

### 3.5 What is deliberately NOT knowledge

- **User flows** ("compose → attach → send") — derivable from a complete graph; not stored.
- **KB testing machinery** — a future component, designed separately.

---

## 4. How knowledge is gained: two passes, gated by priority

The central economic idea: **you cannot go deep on everything — depth is bought with priority.**

### Pass 1 — Breadth (wide and shallow)
Map the *whole* app at the three-level structure: identity, skeleton, every feature and
sub-feature with a shallow rubric, and — mandatorily — their **connections**. The skeleton's
**surface layer is always exhaustive** regardless of priority (in Word: every ribbon tab and
every button on every tab's face, with type/icon/label), but container *interiors* are only
expanded until every feature has a trigger path; the rest become `unexplored` stubs.

### Priority scoring (the gate)
Every feature/sub-feature is ranked into **five layers P0–P4** from three signals:

1. **Connection density** — computed centrality over `affects/uses` edges (Font touches
   everything that renders text → high).
2. **Real-world usage** — web research, evidence required (claim + source + node mapping).
3. **Audience breadth** — `everyone` outranks `niche` (Font vs. Mailings).

Mechanics are arithmetic, not judgment: normalize, weighted sum (weights recorded), sort, cut at
boundaries. Everything lives in `kb/<app>/priority/` — **a priority is never a vibe**; "why is
Font P0?" is answered by opening files.

### Pass 2 — Depth (narrow and deep)
| Layer | Treatment |
|---|---|
| **P0–P2** (high) | Documented exhaustively — every behavior, option, dialog, state, screenshot — descending until the **depth endpoint rule** fires |
| **P3** (medium) | All rubric questions thoroughly + immediate dialogs/dropdowns one level |
| **P4** (low) | Stays at breadth; UI stays at the surface layer |

**Depth endpoint rule:** while clicks keep opening more UI (dialog → dialog → dropdown), keep
collecting; the moment an element *fires an action* instead of revealing UI — endpoint, record
the trigger, stop. In the data this is literal: descending = writing `opens`; endpoint = writing
`triggers`.

Skeleton depth rides on features: deep-inspecting a P0 feature drags the inspector through its
full trigger machinery, so exactly the dialogs that matter get mapped. A skeleton element
inherits the priority of the features it triggers.

---

## 5. The pipeline stages

```
Stage 0   Setup        launch app, PIN VERSION, load boundaries config
Stage 1   Skeleton     map the frame + feature inventory (trigger path each)
Stage 1b  Docs harvest opportunistic + QUALITY-GATED (Word's video-heavy docs fail the gate);
                       docs guide and cross-check, NEVER create nodes
Stage 2   Breadth      one inspector per feature, in parallel — shallow rubric + connections
Stage 3   Assembly     merge graph, completeness check, docs cross-check, priority scoring
Stage 4   Depth        priority-gated deep inspection (P0–P2 full, P3 mid)
Stage 5   Finalize     recompute priority once, emit graph.json + overview.md
```

---

## 6. The discipline (how the pipeline stays honest)

Four field-proven rules (mined from real replication work — see `references/`):

1. **Append-only journal** — every action and outcome logged to `journal.jsonl`; KB files are
   reconciled from it. Buys resumability, audits, and honest failure records.
2. **Snapshot-diff classification** — `opens` vs `triggers` is *measured*: snapshot state before
   a press, press mechanically, snapshot after, diff. Metadata heuristics lie; state deltas don't.
3. **Version pinning** — a KB describes ONE version of an app; drift fails loudly.
4. **Boundaries config** — deliberate exclusions (add-ins, nag popups, out-of-scope areas) as
   per-app *data*, journaled as skips.

**Completeness check (mechanical, three states):** every interactive element is either
**resolved** (has `triggers`/`opens`), **unexplored** (deliberate, labeled), or a **gap** (goes
back to inspection). Same check runs in reverse (every feature must have a trigger path) and on
the shortcut registry (missing targets, duplicate key+context).

---

## 7. Tools, scripts, and references

- **`tools/` — the pipeline's instruments.** Implementations of a *curated catalog* of vetted
  tools (UIA tree reading, hit-testing for owner-drawn UI, window detection, real input
  injection, capture + pixel sampling, browser automation for web, research, schema-enforcing
  KB writers). Entry criteria: returns structured data (not guesses) and enforces safety
  internally (an inspector exploring Gmail can never actually send an email). App-agnostic,
  written by us, changed only deliberately.
- **`kb/<app>/scripts/` — generated per app** during runs: `drive/` (launch, fixtures,
  navigation), `extract/` (harvesting), `verify/` (state checks). They are provenance — a fact
  can cite the script that produced it.
- **`references/` — donated example scripts** (a Word ribbon crawler, a docs harvester).
  Law: **inspire, never dictate** — read for patterns, never copied, never trusted as facts.
- **Provenance everywhere:** every fact records which tool produced it (`uia`, `hit-test`,
  `pixel`, `vision`, `docs`, …). Structured sources are strong; vision/docs-only facts are
  flagged for re-verification.
- **Promotion rule:** a per-app script pattern that proves general graduates into `tools/` — as
  a reviewed step, never a runtime side effect.

---

## 8. Where everything lives

```
app-pipeline/
  README.md            front door
  generalinfo.md       this file
  docs/superpowers/
    specs/             THE design (source of truth)
    plans/             build plans (Plan A written)
  pipeline/            pipeline source (to be built)
  tools/               shared tool library (to be built)
  references/          example scripts — inspire, never dictate
  validation/          per-plan reports: questions → verdicts + frozen evidence
  configs/apps/        per-app DATA (the only place app names may appear)
  kb/<app>/            THE PRODUCT: one knowledge base per inspected app
```

Rule: **a run writes only inside `kb/<app>/`.**

---

## 9. Where we are right now

**Design: finished.** The spec answers every design question we raised (data model, edges, UI
tree, shortcuts, priority mechanics, depth rules, discipline, tools, docs harvest, layout).

**Construction: not started.** There is no runnable code yet. `python -m pipeline.run notepad`
would fail today. Plans A/B/C build the pipeline into existence.

---

## 10. The build: Plans A, B, C

Each plan builds a slice of the pipeline **and proves it** on real test apps (Notepad = trivial
smoke target, Word = the benchmark: if the pipeline can map the deepest UI in existence, easier
apps follow). Test apps are *test targets, not design targets* — the pipeline stays general.

| Plan | Builds | Questions it answers | We gain |
|---|---|---|---|
| **A** (written, ready) | Foundations (models, journal, writers, configs) + desktop tools (UIA, windows, input, capture, hit-test) + Stages 0–1 + CLI | Can tools drive real apps? Does the schema fit reality? Does ONE codebase drive two different apps (configs only)? Can the skeleton agent build a sensible feature inventory? Is the discipline real? | The pipeline **exists and runs**: `run notepad` → skeleton KB |
| **B** | Breadth fan-out (Stage 2) + assembly + priority (Stage 3) | Can parallel agents fill the rubric without chaos? **Does the priority design actually work?** (Font must beat Mailings — we know the right answer) Does the completeness check catch planted gaps? | Full shallow map + evidence-based P0–P4 ranking |
| **C** | Depth pass (Stage 4) + shortcuts + docs harvest + finalize (Stage 5) | Does the depth endpoint rule terminate in practice? Can we capture nested dialogs, shortcuts, icons? Is a "done" KB actually done (checks pass) and correct (human-recognizable)? | The **complete KB** per spec; Plan C's acceptance run = the first real product |

After C: the **web backend** (browser tools) extends the same pipeline to Gmail/Figma-class apps.

### The improvement loop (how issues are found and fixed)

Run → detect → diagnose → general fix → regenerate → re-run. Detection is layered: schema
rejections, failing tests, the completeness check, journal `failed:` entries, known-answer checks
(we know what Word's ranking should look like), and human reads of `overview.md`.

**Fixes are general by discipline:** an issue *surfaces* on a specific app but the fix targets
the *UI condition*, never the app ("if the element tree is empty for a visible container → fall
back to hit-testing", never "if app == word"). Three enforcement mechanisms: app names are banned
from pipeline code (grep check), every fix must keep ALL test apps passing (a fix that helps Word
but breaks Notepad is rejected), and genuinely unique quirks go into per-app config/scripts, not
code.

### How results stay visible

- `kb/<app>/` is always real, openable JSON + screenshots — at any point of A/B/C you can read
  the actual files (e.g. `kb/word/priority/layers.json` after Plan B).
- Mid-construction KBs are disposable (regenerating after a pipeline improvement is one command);
  the evidence behind each plan's verdicts is *frozen* into `validation/plan-X/results/`.
- Each plan ends with `validation/plan-X/report.md`: every question → an explicit verdict with
  evidence. **A plan is not done without its report.**

### Verification cost (the test pyramid)

Unit tests (milliseconds, no GUI) → Notepad smoke tests (seconds) → scoped stage runs on Word
(minutes, e.g. `--max-containers 10`) → full KB build (hours, only as a plan's final milestone).
Day-to-day assurance never costs a full build.

---

## 11. What success looks like

When A, B, C (+ web backend) are done:

```
> run figma
...
kb/figma/   — complete knowledge base: graph, UI tree, shortcuts,
              priority layers, screenshots, journal, overview
```

One command per app. That is P1 fulfilled: the knowledge foundation the rest of the project
(replica planning → generation → verification) will be built on — each of those phases designed
only after P1 proves itself.

---

## 12. Glossary

| Term | Meaning |
|---|---|
| **KB** | Knowledge base — the JSON+screenshot folder the pipeline produces per app |
| **Skeleton** | The app's UI shell: layout regions, menus, navigation — the trigger surface |
| **Surface layer** | Top-level UI, always exhaustively documented regardless of priority |
| **Trigger path** | Id-chain from skeleton to a feature (Home tab → Font group → B → Bold) |
| **Marker** | Each element's single truth: `opens` / `triggers` / `unexplored` |
| **Depth endpoint rule** | Opens-more-UI → keep going; fires-an-action → stop, record trigger |
| **P0–P4** | Priority layers; P0–P2 get full depth, P3 mid, P4 breadth only |
| **Breadth / depth pass** | Wide-shallow mapping of everything / deep dive on high-priority only |
| **Journal** | Append-only log of every inspection action and outcome |
| **Boundaries** | Per-app config of deliberate exclusions (nags, add-ins, out-of-scope) |
| **Provenance** | Which tool produced each fact (`uia`, `pixel`, `docs`, …) |
| **Promotion rule** | Per-app script patterns graduating into `tools/` via review |
| **Quality gate** | Docs are used only if official, current, text-based, structured |
| **Known-answer check** | Testing pipeline output against facts we already know (Font > Mailings) |
| **Test target vs design target** | Apps we validate against vs. what the code is written for — the pipeline has NO design target; it is general |
