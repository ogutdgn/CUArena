# Phase 0 — Architectural Alignment

This document records architectural decisions made during pre-phase alignment, along with proposals still pending approval and decisions deliberately deferred until later phases. It is updated as new decisions are made.

---

## Top 3 Locked Decisions

These are fixed. They stem from external constraints or pure architectural patterns, so downstream phase data is not expected to change them.

### 1. Interaction Model: A — Visual CUA

- **What:** The agent interacts with the mock app via **screenshots + mouse/keyboard events**. Not DOM/accessibility-tree access, not a programmatic API.
- **Why:** External constraint from the user ("I am in a situation where A is mandatory"). Real/off-the-shelf CUAs (Anthropic computer-use, other labs' CUAs) must be pluggable into this mock. Visual modality is the only answer that satisfies this constraint.
- **Implications:**
  - The mock app must be a real, rendered UI (likely web-based).
  - A bridge layer is required for raw mouse/keyboard event injection and screenshot capture.
  - Visual fidelity matters — the agent sees pixels; layout drift will cause misclicks.
- **Alternatives rejected:** B (DOM/tree), C (hybrid), D (pure API).
- **Revisit if:** The external constraint changes.

### 2. Target CUA Spec: Anthropic computer-use (initial)

- **What:** The bridge + adapter initially conform to the Anthropic computer-use API schema. Example message shapes:
  ```json
  {"action": "left_click_drag", "start_coordinate": [x,y], "coordinate": [x,y]}
  {"action": "mouse_move", "coordinate": [x,y]}
  {"action": "type", "text": "..."}
  {"action": "key", "text": "ctrl+c"}
  {"action": "screenshot"}
  ```
- **Why:** The user has no current access to the other-lab CUA they intend to use in production. Anthropic computer-use is the best-documented, widely-referenced CUA spec. Pragmatic starting point.
- **Implications:** Forces the adapter pattern (decision 3) — otherwise a new CUA would require rewriting the bridge.
- **Revisit if:** Access to the other-lab CUA is obtained; in that case a new adapter is added, and the Anthropic adapter is optionally retained.

### 3. Architectural Pattern: Y — Adapter Layer

- **What:** The system uses a **generic internal action vocabulary** at its core (e.g. `mouse_down`, `mouse_move`, `mouse_up`, `key`, `type`, `screenshot_request`). Each CUA has its own **thin adapter** that translates CUA-specific messages to this internal vocabulary.
- **Why:** The alternative (X — speak Anthropic natively) would force a bridge rewrite whenever a new CUA is introduced. The adapter pattern reduces that cost to writing a small translation layer.
- **Implications:**
  - The internal action vocabulary must be specified concretely (not yet done — Phase 2/3 work).
  - Each CUA gets a separate adapter file (rough estimate: 100–200 lines).
  - The bridge and downstream stack know only the internal vocabulary; they are CUA-agnostic.
- **Revisit if:** It becomes certain that only a single CUA will ever be supported (extremely unlikely given stated goals).

---

## Guiding Principle — Trajectory-level Verification

This principle underlies every architectural decision in the project:

**Test cases verify not only the final UI state, but also the trajectory (the sequence of actions) by which the agent reached it.**

Example: Task = "Move the box 10 units to the right."
- Agent performs a **drag-drop** → PASS (drag-drop was the behavior being tested).
- Agent performs **copy + paste + delete original** to reach the same end position → FAIL (visual outcome is correct, but the required behavior was not exercised).

Consequences:
- The mock app must maintain a semantic action log.
- The test harness must support assertions over both state (final position, properties) and trajectory (`required_actions`, `forbidden_actions`, ordering).
- Different agent paths to the same outcome must be distinguishable.

---

## Conceptual Architecture Sketch

Derived from the locked decisions. This is an interaction model, not an implementation specification — the concrete technology behind each box is still deferred.

```
[CUA (Anthropic / other lab)]
   ↕  CUA-specific JSON   (↑ actions, ↓ screenshots)
[CUA Adapter]
   ↕  Internal action vocabulary
[Bridge]
   ↕  Browser-level event injection (MouseEvent, KeyboardEvent) + screenshot capture
[Mock Figma App — rendered UI]
   ↓  DOM events + app state changes
[Event Classifier]  →  semantic actions
   ↓
[Action Log]   +   [State Snapshots]
   ↓
[Test Harness]  →  assertions (required_actions, forbidden_actions, final_state)  →  pass / fail
```

---

## Pending Decisions (proposed, awaiting approval)

### 4. Action Log Shape

- **Proposal:** Raw events (mousedown, keydown, etc.) **together with** semantic actions (drag_move, copy, etc.) in the same log.
- **Alternative:** Semantic actions only.
- **Rationale for proposal:** Fine-grained assertions (e.g. "was copy invoked via Ctrl+C or via the menu?") require raw events. Log volume is a secondary concern.
- **Status:** Deferred to after Phase 2 — feature scope will affect log volume and may change the calculus.

### 5. Classifier Approach

- **Proposal:** The classifier listens to the mock app's own **internal event system** (the app will already emit events like "drag completed"; the classifier subscribes to those and writes to the log).
- **Alternative:** Parse the raw DOM event stream and infer semantic actions.
- **Rationale for proposal:** The app already knows its own state, so no inference is needed. Less code, fewer edge cases.
- **Status:** Deferred to after Phase 2 — feature scope will affect classifier complexity.

---

## Tabled Decisions (awaiting Phase 1 / Phase 2 output)

The following decisions would be speculative at this point. Without corpus data and a locked scope, they are error-prone.

- **6. Feature scope** — which subset of Figma lands in the MVP? → Phase 1 (discovery) + Phase 2 (scope) output.
- **7. Action taxonomy** — which semantic actions will the classifier recognize? → Derived from feature scope, Phase 2.
- **8. Tech stack** — what will the mock app be built in? React + canvas library (Konva / Fabric) or custom? → Driven by scope complexity, Phase 3.
- **9. Bridge implementation** — Playwright or a custom WebSocket bridge? → Tied to stack choice, Phase 3.
- **10. Test case file format** — YAML/JSON schema; how are `required_actions`, `forbidden_actions`, `initial_state`, `final_state` expressed? → Phase 3.
- **11. Test harness architecture** — separate process or embedded in the mock app? How is test isolation handled (fresh state per test vs. carryover)? → Phase 3.
- **12. Task delivery mechanism** — how does a task reach the agent? Via the test harness, via an in-app panel, via an external JSON file? → Phase 3.
- **13. Determinism & timing** — is the mock app deterministic across runs? Timestamp source (wall clock vs. relative)? Timeout and error handling? → Phase 3.

---

## Phase Sequence

| Phase | Content | Effect on this document |
|-------|---------|-------------------------|
| **Phase 0** (this document) | Architectural alignment. Top 3 decisions locked. | — |
| **Phase 1** — discovery | Scan of `figma_docs/` corpus → feature inventory + identification of high-value features for CUA testing. | Produces data for item 6. |
| **Phase 2** — scope | MVP feature set selected from Phase 1 output. | Items 6, 7 locked. Items 4, 5 re-evaluated. |
| **Phase 3** — architecture | Tech stack + bridge + test harness + task delivery + file format decisions. | Items 4–13 locked. |
| **Phase 4** — implementation | Code. | — |

---

## Update Rule

- **New decision** → added to the relevant section (Locked / Pending / Tabled).
- **Pending approved** → moved to Locked; rationale and implications updated.
- **Tabled resolved** → moved to Locked or Pending when enough data is available.
- **Locked decision invalidated** → open a new "Revisions" section; archive the old decision with its rationale, record the new decision with justification for the change.
