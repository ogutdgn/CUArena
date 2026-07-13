# Step 4 — Priority: rank what matters (P0–P4)

## Goal

Decide what the replica must contain: rank capabilities by **value to the target user**, then
derive each feature's replication scope from its children. A priority is never a vibe — every
verdict is written with its reasoning and evidence.

## The one value question

> **"Would our user actually use this?"**

Value is USAGE — nothing else. Dependency-richness is NOT value (a heavily interconnected but
unused subsystem — e.g. a mail-merge wizard — must not rise because of its internal wiring).
Connections play a different role (logistics — see below).

## Three value signals — all asking the usage question from different directions

1. **Product-purpose reasoning (primary, internal).** The KB already holds the app's identity
   (Step 0: what this app IS FOR) and every capability's function (Step 3: what it DOES). Put
   them together: *"Could a user accomplish this app's core job without this?"*
   - Rich-text editor → font, paragraph, tables, pictures: the core job is impossible without
     them → indispensable. Mail-merge: core job fine without it → peripheral.
   - Media player → play/seek/volume indispensable; subtitle-sync peripheral.
   - MANDATORY format for every verdict: `product is X (identity) + this does Y (measured) →
     therefore indispensable/important/peripheral` — written, auditable, never bare intuition.
2. **UI prominence (measured, internal).** Designers ship their own usage data in the layout:
   what is on the default/primary surface, large, first-in-order = the app's own bet on frequent
   use; what hides three menus deep = the app's own bet on rarity. Measured from the skeleton
   (surface, position, size, nesting depth). Works for EVERY app, even ones the web has never
   heard of.
3. **Web usage (external corroborator — not an oracle).** Research what real users use most.
   Every entry carries claim + source + node mapping. Its job is to confirm and to catch
   surprises the reasoning missed. When web data is thin or absent (niche/internal apps),
   signals 1+2 carry the ranking alone.

**Disagreement rule:** when the signals conflict ("reasoning says peripheral, web says everyone
uses it" — or the reverse), stop and investigate; record the resolution as a journaled
`decision` with reasoning. Silent overrides are forbidden.

## Scoring and derivation rules

- **Only sub-features are scored.** Usage lives at the capability level ("people use bold",
  not "people use the Font group"). Features NEVER get their own independent score.
- **Features are placed, not scored** — derived from their children and shown in the same list:
  - `layer` = the layer of their best child (a parent can never rank below its own child —
    structural, not aspirational);
  - `ratio` = how many of its children landed in P0–P3.
- **Replication scope per feature** comes from the ratio:
  - **Majority rule:** most children in P0–P3 → the feature is replicated WHOLE (full depth on
    the entire group — a group with one dead button feels broken in a replica). This is wired
    into Step 5's depth set (R5.5): whole-scope children enter it whatever their own layer.
  - **Gem rule:** only isolated children rank high → only those gems (+ their closure) get full
    depth; the rest of the group stays honestly shallow.
  - Ratio ~0 → not replicated (breadth knowledge only, honestly labeled).

## Logistics: closure and upward flow (connections' real job)

- **Closure:** the replication set = P0–P3 **+ everything reachable from it via `requires`
  edges** — a replicated capability must WORK. (picture-border P2 → insert-picture comes along,
  whatever its own score, marked `pulled-in-by`.) Pulled-in nodes get "enough to work" depth,
  not automatic full depth.
- **Upward flow:** what high-usage capabilities REQUIRE inherits importance (undo matters
  because used things need it — not because it has many edges).
- Connection **counts/centrality are NOT a value signal.** Do not add density to scores.

## How (mechanics)

- Normalize, combine with recorded weights, sort SUB-FEATURES, cut into P0–P4 at recorded
  boundaries; then derive feature rows; then compute closure. Artifacts under
  `kb/<app>/priority/`: `signals/…`, `ranking.json` (sub-feature scores + weights),
  `layers.json` (BOTH node kinds; features annotated `derived_from: {best_child, ratio,
  scope: whole|gems|none}`), closure list with `pulled-in-by` reasons.
- Sanity-check against the product reasoning: if a famously-core capability lands below P0–P2,
  or a known-dead area rises, the inputs are wrong — investigate before accepting (journal the
  investigation).

## Rules

- **R4.1** All common rules (CR1–CR8, `playbook/README.md`) bind.
- **R4.2** Weights, boundaries, verdict reasonings, and all evidence are **in the artifacts** —
  "why is X P0?" must be answerable by opening files.
- **R4.3** Every node ends up in a P layer — **including contextual ones** (Table Layout,
  Picture Format controls…) and every feature row. A node in no layer is a silent gap depth can
  never reach, not a low priority. [kernel-checked] (LESSONS 2026-07-12: an accidental edit
  corrupted one id inside priority.json and NOTHING noticed until this check existed)
- **R4.4** No feature scored independently; no connection-density in value; closure computed,
  not hand-waved.

## Worked mini-example (generic document editor — the same flow applies to ANY app)

```
INVENTORY (from step 3):          SCORING (sub-features only):
  feature: text-styling             bold:        core job impossible without ✚ prominent ✚ web top-10  → P0
    bold, italic, text-color        italic:      core-adjacent ✚ prominent                             → P1
  feature: object-insertion         insert-image: core job needs it ✚ prominent                        → P1
    insert-image, insert-diagram    insert-diagram: peripheral ✚ buried ✚ web: rare                    → P4
  feature: mail-tools               address-merge: core job fine without ✚ buried                      → P4
    address-merge, envelope         envelope:    same                                                  → P4

DERIVATION (features placed, never scored):        CLOSURE:
  TEXT-STYLING     layer P0 | ratio 3/3 → WHOLE     image-border (P2, elsewhere) requires
  OBJECT-INSERTION layer P1 | ratio 1/2 → GEMS       insert-image → already in set ✓
  MAIL-TOOLS       layer P4 | ratio 0/2 → NONE       (had it not been, it would be pulled in
                                                      "enough to work", labeled pulled-in-by)
```

Note what each mechanism did: scoring asked only "would our user use this?"; features inherited
their place from children; the ratio decided whole-vs-gems; closure guaranteed nothing replicated
arrives broken. No dependency-counting anywhere in the value column.

## Proof

1. `kb/<app>/priority/` complete: per-signal files, sub-feature ranking with weights,
   layers.json with derived feature rows (best_child + ratio + scope), closure list with
   pulled-in-by reasons.
2. Every product-reasoning verdict in the mandated format; every web entry with claim + source;
   every signal disagreement resolved in a journaled decision.
3. A one-paragraph justification of the top layer that a human who knows the app can check —
   plus the inverse: name three things that stayed LOW and why that is obviously right.
