# Dependency Clusters

_Source: `structure-helper/figma_docs/graph.json`. 216 nodes (articles), 1,046 internal edges (article-to-article links), 468 external link entries (off-corpus references)._

The link graph is the only signal for "feature X depends on / is explained alongside feature Y" in this corpus, since articles cross-reference each other when one feature presupposes another. High-degree nodes mark **hub features** (likely required by many flows); cross-product edges mark **integration seams**; per-product connected components reveal which articles stand alone.

---

## 1. Per-product node distribution

| Product | Nodes | Components | Largest component |
|---|---|---|---|
| Figma Design | 175 | 12 | 164 articles |
| Dev Mode | 19 | 1 | 19 articles |
| Projects (tutorials) | 19 | 12 | 5 articles |
| Figma Draw | 3 | 1 | 3 articles |

**Reading:** Figma Design and Dev Mode are tightly interlinked — almost every article connects to the rest. Projects tutorials are mostly **isolated** from each other (each tutorial is a self-contained build-along) but link **out** heavily to Figma Design / Draw articles. The 11 Figma Design singletons (e.g., "Offset a vector path", "Add guides to the canvas or frames", "Migrate a library to using slots", "Simplify a vector path") are leaf utilities not linked from anywhere else in the corpus — likely independent micro-features.

---

## 2. Hub articles by OUT-degree (links TO others — "starting points")

These are the canonical guide / overview articles a reader hits to fan out. Anything covered by these is "core surface area."

| Out-deg | Product | Title |
|---|---|---|
| 25 | Figma Design | Navigating UI3 |
| 24 | Figma Design | Design, prototype, and explore layer properties in the right sidebar |
| 19 | Figma Design | Explore design files |
| 19 | Figma Design | Guide to prototyping in Figma |
| 18 | Dev Mode | Guide to Dev Mode |
| 18 | Figma Design | Overview of variables, collections, and modes |
| 17 | Figma Design | Guide to text in Figma Design |
| 15 | Figma Design | Adjust alignment, rotation, position, and dimensions |
| 14 | Figma Design | Guide to libraries in Figma |
| 13 | Figma Design | Explore component properties |
| 13 | Figma Design | Explore text properties |
| 13 | Figma Design | Optimize design files for developer handoff |
| 12 | Dev Mode | Guide to inspecting |
| 12 | Figma Design | Access design tools from the toolbar |
| 12 | Figma Design | View layers and pages in the left sidebar |
| 12 | Figma Design | Use variables in prototypes |
| 11 | Figma Design | Create interactive components with variants |

(Plus three Projects tutorials at 11–13 out-deg — they reference many Design articles.)

---

## 3. Hub articles by IN-degree (most referenced — "load-bearing concepts")

Anything else in the corpus tends to point here. These are the **must-implement** primitives if the mock app aims for fidelity.

| In-deg | Product | Title |
|---|---|---|
| 22 | Figma Design | Play your prototypes |
| 21 | Figma Design | Frames in Figma Design |
| 21 | Figma Design | Connect your prototype |
| 19 | Figma Design | Guide to prototyping in Figma |
| 17 | Figma Design | Guide to variables in Figma |
| 16 | Figma Design | Guide to components in Figma |
| 16 | Figma Design | Explore text properties |
| 16 | Figma Design | Publish a library |
| 16 | Figma Design | Guide to auto layout |
| 15 | Dev Mode | Guide to Dev Mode |
| 14 | Figma Design | Parent, child, and sibling relationships |
| 14 | Figma Design | Select layers and objects |
| 14 | Figma Design | Create and manage variables and collections |
| 14 | Figma Design | Guide to libraries in Figma |
| 14 | Figma Design | Apply effects to layers |
| 13 | Figma Design | Edit vector layers |
| 13 | Figma Design | Use variables in prototypes |
| 13 | Figma Design | Apply and adjust stroke properties |
| 12 | Figma Design | Shape tools |
| 12 | Figma Design | Adjust alignment, rotation, position, and dimensions |

**Pattern:** the dependency graph is dominated by **frames + selection + layer hierarchy** at the foundation, then **components / variables / auto layout** as the design-system layer, then **prototyping** as the consuming layer on top. Almost every prototyping article points back to frames, components, and variables. This is the natural dependency stack.

---

## 4. Cross-product edges (168 total)

Source product → target product, edge counts:

| Edges | Source | Target | Interpretation |
|---|---|---|---|
| 98 | Projects | Figma Design | Tutorials walk through Figma Design features |
| 19 | Figma Design | Dev Mode | Design features explain how they surface in Dev Mode |
| 17 | Dev Mode | Figma Design | Dev Mode features link back to the Design concepts they inspect |
| 12 | Projects | Figma Draw | Tutorials use Draw mode |
| 8 | Figma Design | Projects | Design articles point at tutorials as examples |
| 7 | Figma Draw | Figma Design | Draw refers back to shared Design primitives |
| 4 | Figma Design | Figma Draw | Design articles flag Draw-specific behaviors |
| 3 | Figma Draw | Projects | Draw articles point to tutorials |

**Two real integration seams** (excluding tutorial fan-out):

- **Figma Design ↔ Dev Mode (19 + 17 = 36 edges)** — the only cross-product seam where both sides reference each other. Reflects Dev Mode being a *mode* of Figma Design, not a separate surface. Articles at this seam: *Optimize design files for developer handoff* (FD), *Mark sections / frames as ready for dev* (FD), *Guide to Dev Mode* (DM), *Guide to inspecting* (DM), *Inspect designs* (DM), Code Connect, variable inspection.
- **Figma Design ↔ Figma Draw (4 + 7 = 11 edges)** — Draw is a sub-mode reusing Design's vector primitives. Draw articles consistently link out to vector network / vector edit mode / boolean / outline-stroke articles in Design.

---

## 5. Top cross-product hub articles

Articles that link to more than 4 articles in *other* products. These are the **integration-seam articles** — read these to understand how the pieces snap together.

| Out-deg to other products | Product | Title |
|---|---|---|
| 13 | Projects | Create a social media post using Figma Draw |
| 12 | Projects | Create an orange illustration using transforms, effects, and text on a path |
| 9 | Projects | Create a loading animation in Figma |
| 8 | Projects | Illustrate a flower vase using shapes, transforms, and the glass effect |
| 8 | Projects | Create a photo gallery prototype |
| 8 | Projects | Create a simple button component |
| 7 | Projects | Create a noodle bowl illustration ... |
| 7 | Projects | Create a strawberry illustration ... |
| 6 | Projects | Create an onboarding flow with advanced prototyping |
| 5 | Dev Mode | Guide to Dev Mode |
| 5 | Dev Mode | Guide to inspecting |
| 5 | Projects | Create a tooltip component set |
| 5 | Projects | Create a responsive card with auto layout and constraints |
| 5 | Projects | Design a search icon |
| 5 | Projects | Create a reusable icon grid |
| 5 | Projects | Create an illustration in Figma Design |
| 4 | Figma Draw | Explore Figma Draw |
| 4 | Figma Draw | Draw with illustration tools |

**Reading:** Almost all cross-product hubs are tutorials. The two genuinely useful entries for the mock app are **Guide to Dev Mode** and **Guide to inspecting** — they map Design constructs to their Dev-Mode surfaces (Code section, variable rendering, asset detection, status badges).

---

## 6. Within-Figma-Design domain linkage (level-1 breadcrumb)

Edges between domains tell you which Figma Design domains depend on / extend each other. Figures = number of edges (source domain → target domain):

| Edges | Source domain | → | Target domain |
|---|---|---|---|
| 189 | Create designs | (internal) | Create designs |
| 163 | Build design systems | (internal) | Build design systems |
| 109 | Create prototypes | (internal) | Create prototypes |
| 68 | Work together in files | (internal) | Work together in files |
| 44 | Tour the interface | → | Create designs |
| 27 | Create prototypes | → | Create designs |
| 27 | Build design systems | → | Create designs |
| 23 | Create designs | → | Build design systems |
| 20 | Create prototypes | → | Build design systems |
| 19 | Build design systems | → | Create prototypes |
| 15 | Tour the interface | (internal) | Tour the interface |
| 14 | Tour the interface | → | Build design systems |
| 14 | Create designs | → | Create prototypes |
| 11 | Create designs | → | Tour the interface |
| 11 | Import and export | (internal) | Import and export |
| 10 | Tour the interface | → | Create prototypes |
| 7 | Import and export | → | Create designs |

**Three major dependency directions emerge:**

1. **Create designs is the foundation.** Every other domain depends on it (Tour: 44, Prototypes: 27, Design systems: 27, Import/export: 7 edges in). Implementing the canvas + layer model + selection + transform is a hard prerequisite for any other surface.
2. **Build design systems ↔ Create prototypes are bidirectionally coupled** (20 + 19 = 39 edges). Variables, components, and variants are *defined* in design systems and *consumed* in prototypes (smart animate / interactive components / variable-driven interactions). Cannot ship one in isolation if the mock supports both.
3. **Tour the interface is a "broadcasts to all" hub.** It links into Create designs (44), Build design systems (14), Create prototypes (10) — i.e., the UI chrome documentation references every functional area. This confirms Tour-the-interface as the canonical UI map source.

**Weak / negligible coupling:**

- Work together in files barely couples to other domains (4 to Build, 3 each to Prototypes / Tour / Create — mostly inbound). Comments / branching / multiplayer can be **removed from MVP** without breaking the rest.
- Import and export couples weakly (7 → Create, 4 → Build). It's primarily an output stage, not a dependency. Can be deferred for MVP.

---

## 7. Connected-component analysis (corpus integrity check)

| Product | Components | Notes |
|---|---|---|
| Figma Design | 12 (1 giant of 164, 11 singletons) | Singletons are leaf utilities not referenced by any other article: *Offset a vector path*, *Add guides to the canvas or frames*, *Migrate a library to using slots*, *Simplify a vector path*, plus 7 others. Safe to skip these for MVP. |
| Dev Mode | 1 component (19 articles) | Fully interlinked. *Guide to Dev Mode* (deg 18) is the spine. |
| Projects | 12 components | Each tutorial is mostly self-contained. The biggest component (5 articles) clusters around components-with-variants tutorials. The two FigJam-meeting articles form their own cluster. |
| Figma Draw | 1 component (3 articles) | Trivially connected. |

---

## 8. Recommended implementation tiers (derived from this analysis)

Inferred by dependency depth (low in-degree / no inbound = optional; high in-degree = required first).

### Tier 1 — Hard prerequisites (implement first)

These appear as in-degree hubs AND are referenced by every other domain:

- Frames + sections + groups (parent / child / sibling relationships, `Frames in Figma Design` in-deg 21, `Parent, child, and sibling relationships` in-deg 14)
- Selection model (`Select layers and objects` in-deg 14)
- Shape tools + canvas + transform + position/dimensions (`Shape tools` in-deg 12, `Adjust alignment, rotation, position, and dimensions` in-deg 12)
- Layer panel + page model (left sidebar)
- Right sidebar properties surface (the most-cited UI region)
- Toolbar + mode switcher
- Vector layer editing (`Edit vector layers` in-deg 13)
- Stroke + fill + effects (`Apply and adjust stroke properties` in-deg 13, `Apply effects to layers` in-deg 14)
- Text (`Explore text properties` in-deg 16)
- Auto layout (in-deg 16)

### Tier 2 — Design-system layer (implement after Tier 1)

- Components + variants (in-deg 16 + 11)
- Variables + modes (in-deg 17 + 14)
- Libraries + publishing (in-deg 16)

### Tier 3 — Prototyping (implement after Tier 2)

Prototyping presupposes frames, components, and variables — every prototyping article references all three. Significant own surface (Connect your prototype: in-deg 21, Play your prototypes: in-deg 22).

### Tier 4 — Optional for MVP

- **Dev Mode** — separate cross-product surface, ~36 cross-edges with Design. Defer unless the CUA tests explicitly include handoff flows.
- **Comments / branching / multiplayer** (Work together in files) — weakly coupled (4–6 edges to other domains), safe to drop from MVP.
- **Import / export** — output stage, low coupling. Drop from MVP.
- **Figma Draw** — additive mode toggle, 11 edges to Design. Drop unless illustration trajectories are in scope.
- **Singletons** in Figma Design (offset path, simplify path, slots migration, etc.) — leaf utilities, drop.

---

## 9. Notes on external link entries

468 external link entries point outside the scraped corpus (other Figma docs sites, blog posts, plugins, third-party). They confirm what's *not* in the corpus rather than what is — most reference Figma Slides, Figma Sites, FigJam web docs, plugin pages, and Anthropic / Microsoft pages for MCP / VS Code integrations. Not load-bearing for scope decisions.
