# Step 3 — Features & sub-features: the 3-level knowledge tree

## Goal

Turn the measured skeleton into meaning: the app's **features** (level 2) and **sub-features**
(level 3), each answering *"what is this doing?"*, plus the **connections** between them. This is
where structure becomes knowledge.

## How (agent decides the details)

### 1. Build the tree — shallow, but complete for every node

**What is a feature? — copy the app's own grouping, don't invent yours.** Every UI framework
groups its controls for humans (ribbon groups, menu categories, toolbar clusters, sidebar
sections, panels). Those groups ARE the features: Font, Paragraph, Illustrations in a document
editor; Playback, Subtitle in a media player; Labels, Layers in a web app. Only if the app has
no usable grouping (a flat toolbar) do you group by measured shared-effect-target. Never group
from your own domain memory when the app has already grouped.

**Every feature has one of two NATURES — measure it and record `cohesion`.** The app's boxes
are honest about placement but say nothing about what KIND of box they are, and Step 4's scope
rules depend on the kind:

- **`capability`** — the children are FACETS of one capability: Font (bold/italic/size/color
  all shape character formatting), Table Layout (all operate the table). The group lives and
  dies as a unit — majority rule may replicate it WHOLE.
- **`catalog`** — the children are INDEPENDENT capabilities that merely share a drawer:
  Illustrations (Pictures / Charts / SmartArt / 3D are different worlds with different
  follow-up machinery). A catalog is a menu, not a capability — it NEVER replicates whole
  (04 R4.7); each child carries its own fate.

Three measured tests (in order; the first two usually agree):
1. **One-sentence test (the variation test, one level up):** can the group's purpose be stated
   as ONE capability sentence in which every child is a facet/variation? "Formats character
   appearance" ✅ capability. "Inserts… various visual things" — only works by going vague ❌
   catalog.
2. **Shared-affects test (mechanical):** do the children's measured `affects` targets point at
   the same state? Font children → all "selected text's character format" → capability.
   Illustrations children → picture object / chart object / diagram object → catalog.
3. **Dead-button tie-breaker:** if one child were missing, would the group feel BROKEN? A dead
   strikethrough in Font → broken → capability. No 3D-Models entry in Illustrations → just a
   shorter menu → catalog. (A paint app's tool palette: a dead eraser breaks it → capability.)

**Cohesion is judged per feature and never inherited.** A catalog's child may summon a world
that is itself a capability feature with its own cohesion and its own scope: Illustrations
(catalog) → `insert-pictures` → Picture Format (capability, its 13 children all shape the
selected picture) — Picture behaves exactly like Table there. The `requires` edge between the
world and its inserting capability is what keeps the pair replication-consistent (closure
inspector).

**What is a sub-feature? — the nameable capability.** The test: does *"this app can X"* make
sense? "This app can bold text" ✅, "can merge table cells" ✅, "can insert pictures" ✅ — but
"this app can match-case checkbox" ❌ (that's an OPTION inside Find, not a capability —
depth's business).

**Where does the sub-feature level STOP? — the variation test.** When a control's children are
*variations of the same effect*, do not descend further:
- Picture Border's dropdown holds color / weight / dashes / sketched → all variations of "the
  picture's border" → ONE sub-feature (`picture-border`); the variations are its options, depth
  documents them later if it ranks.
- Picture Effects: shadow / reflection / glow → variations of "the picture's visual effect" →
  ONE sub-feature.
- Contrast: Illustrations' children (pictures / shapes / chart / 3D) are NOT variations — they
  do different things with different follow-up capabilities → separate sub-features.
- The same test in other app paradigms: a media player's speed menu (0.5× / 1× / 1.5× / 2×) →
  variations → ONE sub-feature (`playback-speed`); but its Audio menu's children (track
  selection / equalizer / mute) → different capabilities → separate. A drawing app's brush-size
  slider values → variations (`brush-size`); its tool palette (pencil / fill / text / eraser) →
  separate capabilities.
- Tie-breaker when unsure: *"could these children carry DIFFERENT importance — could one be
  heavily used and another dead?"* Yes (picture vs 3D-model) → split. No (border color vs
  border weight — they live and die together) → don't split.
- This matters because breadth's job is to build the RANKING's candidate list: a node exists so
  it can carry its own importance signal. Things that can't differ in importance don't need to
  be nodes.

**Level bookkeeping:** the tree is always app → feature → sub-feature (3 levels; a group with
one control is still a feature with one sub-feature — uniformity beats cleverness). UI nesting
depth (tab > group > dropdown) lives in trigger paths, not in extra tree levels. "Big worlds"
like Picture (whose insertion spawns a whole contextual family) are represented in the GRAPH
(requires/contextual edges tie the family to `insert-picture`), never as deeper tree levels.

- Under each feature, record its sub-features per the tests above.
- **Shallow means we don't open every dialog and enumerate every option here** — we work at the
  level of the general surfaces/tables. It does NOT mean thin: **every feature AND every
  sub-feature — even in this shallow pass — must carry its core identity rubric**
  (schema in `design/knowledge-base-design.md`):
  - **what it is / what it does** — a real description, not just a name
  - **how it is triggered** — the trigger path (real id-chain from the skeleton) + any shortcut
  - **what it affects** — the state/target it changes (you measured this in Step 2's press-observe)
  - `audience_breadth` (everyone / most / niche / role-specific)
- A node with only a name is not done. You can't build a meaningful connection on top of a node
  whose purpose and trigger you haven't recorded — so the identity rubric comes first, then
  connections rest on it.
- **A sub-feature that opens a surface (e.g. Font Color → a color dialog) is still fully recorded
  here**: its rubric says what it does and that it `opens` that surface (measured in Step 2), and
  the surface it opens stays a **stub** (`explored: false`) — see Step 2. You are documenting the
  feature's identity, not the dialog's interior; that interior is Step 5's job, priority-gated.
  The node is NOT `unexplored`; only the opened surface's contents are deferred.

### 2. Discover connections — grounded in evidence, not vibes

Connections serve **logistics, not value**: they tell Step 4 what a replicated capability needs
in order to WORK (closure) and let importance flow up dependency chains. They are NOT a
popularity score — edge counts do not make a node valuable. Three kinds, strongest first:

- **`requires` (directional, the load-bearing kind):** B does not work without A. Three cheap
  MEASURED ways to find it:
  1. *Contextual discovery gives it free:* Table Layout appeared only after inserting a table →
     everything on it `requires` the table. One observation, dozens of edges.
  2. *Disabled-state gives it free:* many controls are disabled until a precondition exists
     (Paste disabled with empty clipboard; picture tools disabled without a selected picture).
     The prober already reads enabled/disabled — "X disabled without Y" is a measured edge.
  3. *Artifact relationship:* B operates on what A creates (border on picture). Observable.
  These edges power **closure** (Step 4) — replication-set membership for what high nodes
  require, never a layer change — get them right.
- **`affects-same` (medium):** two capabilities shape the same artifact (bold/italic → the
  selected text). Measured free from Step 2's state-diff targets. Co-usage hint only.
- **`co-location` (weakest):** the app placed them together. Free from the skeleton. Hint only —
  NEVER let co-location bulk (a 15-member group all cross-linked) drown real signals; that
  mistake once buried Paste under the Font group's internal wiring.
- **Inference (labeled):** you may PROPOSE any edge from domain knowledge, tagged
  `"source": "inference"`; confirm with a cheap observation where possible.
- Every edge records `{target, kind: requires|affects-same|co-location, why, source}` in the
  SOURCE node's `connections[]` (one direction; `requires` points at the prerequisite).

### 3. Contextual surfaces — discovered, then FED BACK IN (not dead ends)

Use state-changing probes to discover UI that only exists in context (e.g. insert an object →
new tabs appear). Work on the throwaway fixture copy; reset after. But discovery is only HALF
the job — the half that gets forgotten:

**A contextual surface is not a trophy to photograph; it is a new command surface whose
controls are real features.** Word example: inserting a table makes **Table Design** and
**Table Layout** tabs appear. Their controls — Header Row, Banded Rows, Delete Rows, Merge
Cells, Remove Background (on Picture Format), Crop — are genuine, heavily-used features: a user
who inserts a table spends most of their table-time INSIDE Table Layout. A KB that documents
the table-insert button to full depth but leaves Table Layout's 37 controls as unexplored
names knows how a table is *created* but not how a table is *used* — half the knowledge.

So for every contextual surface you discover, run the SAME loop as any other surface:

1. **Document the surface** (face + screenshot) with its **triggering condition** recorded
   ("exists only while an embedded table is selected; appeared on the 'table' probe").
2. **Feed its controls into THIS step's tree**: they become features/sub-features with the full
   shallow rubric (what-it-does / trigger path — which INCLUDES the context, e.g.
   `[insert table → select it → ui:ribbon-table-layout → el:merge-cells]` / affects / audience),
   and connections (they are at minimum connected to the feature that summons them — that edge
   is `source: "contextual"`).
3. **They enter Step 4's priority ranking like every other node.** The ranking decides whether
   Merge Cells matters more than Drop Cap — it cannot decide that if Merge Cells was never
   ranked. A contextual control absent from the ranking is a silent gap, not a low priority.
4. **Step 5 then deepens the ones that rank P0–P3**, exactly as it would any other node —
   pressing each control, following its `opens` chains to the bottom, writing the full rubric.
   The whole point of steps 1–3 above is to get contextual controls INTO the node set so this
   depth step can reach them; skip those steps and they are permanently invisible to depth.

**The failure this prevents (real, from a prior run):** `ui:ribbon-table-layout` was written with
37 children, every one `unexplored: true` and `triggers`/`opens` both null, and NOT ONE of them
became a sub-feature or entered the priority ranking. The tab's outline existed; all 37
table-editing features were invisible to the rest of the pipeline. The fix is the loop above: the
face is step 1, but steps 2–4 are what turn a screenshot into knowledge.

**Docs**: where official docs exist and are text-based/current, they may *guide* your grouping and
hint at connections — but never create a node from docs alone; the live app confirms everything.

## Rules

- **R3.1** All common rules (CR1–CR8, `playbook/README.md`) bind.
- **R3.2 No name-only nodes:** every feature/sub-feature has what-it-does + how-triggered +
  what-it-affects filled, even at this shallow depth.
- **R3.3** Every feature/sub-feature must be reachable: at least one trigger path into the
  skeleton. [kernel-checked]
- **R3.4** Every connection carries evidence (`why`) and a `source` tag; inference-only edges
  are labeled as such.
- **R3.5** Every feature carries a measured `cohesion` classification (`capability` /
  `catalog`, tests above) — Step 4's scope rules are meaningless without it, and a catalog
  mistaken for a capability drags dead weight into full depth. [kernel-checked: catalog +
  scope:whole is a flagged contradiction]

## Proof

1. The 3-level tree on disk (feature/sub-feature JSONs via kernel writers). **Mechanical check:
   no node is missing description, trigger path, or affects** — a name-only node fails the step.
2. Every node has a resolving trigger path (every skeleton `triggers` points at a node that
   exists, and every node points back — no orphans).
3. Connections recorded with `why` + `source`; every `connections[].target` resolves to an
   existing node (mechanical check — no dangling edges).
4. Contextual surfaces (if any exist in this app) documented with their triggering condition.
5. A short written map: features list with one-liners — readable by a human who knows the app
   ("does this look like the app?").
