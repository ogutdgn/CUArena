# Phase 1 — Discovery

## Your Role

You are a product analyst. Your job is to understand Figma's features, UI
structure, and workflows by reading the documentation corpus.

The corpus covers four products:

- **Figma Design** — the main design tool
- **Figma Draw** — illustration / vector drawing
- **Dev Mode** — handoff, inspect, code generation
- **Projects** — sample projects / project organization

Features that cut across products (e.g. a Design article that references a
Dev Mode flow) are common — use `target_product` on internal links and the
`product` field on graph nodes to follow those connections.

## Objectives

1. **Feature Inventory** — What can each product do? List every distinct
   feature with its inputs, outputs, UI location, and owning product.

2. **UI Map** — What is the spatial layout of Figma's interface?
   Toolbar, left sidebar, right sidebar, canvas, menus, panels, modals.
   Note which product(s) each UI region belongs to.

3. **Workflow Extraction** — What are the step-by-step user flows?
   e.g., "Create a component" = select layers → right click → Create
   component → name it → set properties. Workflows often span products
   (e.g. design in Figma Design → inspect in Dev Mode).

4. **Dependency Graph Analysis** — Which features depend on which?
   Use `structure-helper/figma_docs/graph.json` edges to identify clusters
   and chains. Cross-product edges are especially interesting — they flag
   the integration seams between products.

5. **State Transitions** — What UI state changes when an action is taken?
   e.g., "Add auto layout" → right sidebar shows auto layout panel, layer
   icon changes.

## How to Work

### Step 1: Read the hub articles first

These are the overview / guide articles with the most outgoing links. Open
each from the correct product folder:

- *Navigating UI3* → `structure-helper/figma_docs/articles/Figma Design/navigating-ui3/content.md`
- *Design, prototype, and explore layer properties in the right sidebar* → Figma Design
- *Explore design files* → Figma Design
- *Access design tools from the toolbar* → Figma Design
- *Guide to prototyping in Figma* → Figma Design
- *Guide to Dev Mode* → Dev Mode
- *Guide to auto layout* → Figma Design
- *Guide to components in Figma* → Figma Design
- *Guide to variables in Figma* → Figma Design
- *Guide to libraries in Figma* → Figma Design

Use `index.json` to confirm the exact slug and product folder before reading.
These give you the big picture before diving into specifics.

### Step 2: Build feature inventory per product + domain

Process one product at a time. For each feature, produce:

```
Feature: [Name]
Product: [Figma Design | Figma Draw | Dev Mode | Projects]
Domain: [Within-product grouping — e.g. Create designs, Build design systems]
UI Location: [Where in the interface — toolbar, right sidebar, menu, shortcut]
Trigger: [How the user activates it — click, shortcut, menu item]
Inputs: [What the user provides — selection, values, settings]
Outputs: [What changes — canvas, panels, layer tree]
Related Features: [From graph.json edges — note cross-product links]
Article: [Source article title + product]
```

### Step 3: Extract workflows

A workflow is a sequence of actions to achieve a goal. Flag workflows that
span products:

```
Workflow: [Goal name]
Primary Product: [e.g. Figma Design]
Touches: [Other products involved, if any — e.g. Dev Mode for inspect]
Steps:
  1. [Action] → [UI feedback]
  2. [Action] → [UI feedback]
  ...
Preconditions: [What must be true before starting]
Result: [Final state]
Articles: [Source articles with their product]
```

### Step 4: Identify UI panels and their states

From the hub articles, map out:

```
Panel: [Name, e.g., "Properties Panel"]
Product(s): [Where this panel appears]
Location: [Right sidebar]
Shows when: [Condition — e.g., "any layer selected"]
Contains: [List of sections/controls]
Changes when: [What actions modify this panel]
```

## Output Format

Save your analysis as structured markdown files in `analysis/` directory:
- `analysis/feature-inventory.md` — organize by product, then by domain
- `analysis/ui-map.md`
- `analysis/workflows.md` — flag cross-product workflows explicitly
- `analysis/panel-states.md`
- `analysis/dependency-clusters.md` — include cross-product clusters

## Token Budget Tips

- Read `structure-helper/figma_docs/index.json` first to find articles by
  title and product.
- Read `structure-helper/figma_docs/articles/<Product>/<slug>/metadata.json`
  before `content.md` — it has links, breadcrumb, and pre-tagged
  `target_product` on each internal_link without the full body.
- For graph analysis, `structure-helper/figma_docs/graph.json` has node
  `product` tags and all edges — don't read individual metadata files just
  for link data.
- Process one product at a time, then one domain within it — not all
  articles at once.
