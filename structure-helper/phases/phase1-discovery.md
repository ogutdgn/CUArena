# Phase 1 — Discovery

## Your Role

You are a product analyst. Your job is to understand Figma Design's features,
UI structure, and workflows by reading the documentation corpus.

## Objectives

1. **Feature Inventory** — What can Figma Design do? List every distinct feature
   with its inputs, outputs, and UI location.

2. **UI Map** — What is the spatial layout of Figma's interface?
   Toolbar, left sidebar, right sidebar, canvas, menus, panels, modals.

3. **Workflow Extraction** — What are the step-by-step user flows?
   e.g., "Create a component" = select layers → right click → Create component → name it → set properties.

4. **Dependency Graph Analysis** — Which features depend on which?
   Use `structure-helper/figma_docs/graph.json` edges to identify clusters and chains.

5. **State Transitions** — What UI state changes when an action is taken?
   e.g., "Add auto layout" → right sidebar shows auto layout panel, layer icon changes.

## How to Work

### Step 1: Read the hub articles first
These are the overview/guide articles with the most outgoing links.
Read them from `structure-helper/figma_docs/articles/<slug>/content.md`:
- "Navigating UI3" → `structure-helper/figma_docs/articles/navigating-ui3/content.md`
- "Design, prototype, and explore layer properties in the right sidebar"
- "Explore design files"
- "Access design tools from the toolbar"
- "Guide to prototyping in Figma"
- "Guide to Dev Mode"
- "Guide to auto layout"
- "Guide to components in Figma"
- "Guide to variables in Figma"
- "Guide to libraries in Figma"

These give you the big picture before diving into specifics.

### Step 2: Build feature inventory per domain
For each domain (Create designs, Build design systems, etc.), produce:

```
Feature: [Name]
Domain: [Which domain]
UI Location: [Where in the interface — toolbar, right sidebar, menu, shortcut]
Trigger: [How the user activates it — click, shortcut, menu item]
Inputs: [What the user provides — selection, values, settings]
Outputs: [What changes — canvas, panels, layer tree]
Related Features: [From structure-helper/figma_docs/graph.json edges]
Article: [Source article title]
```

### Step 3: Extract workflows
A workflow is a sequence of actions to achieve a goal. Extract from articles:

```
Workflow: [Goal name]
Steps:
  1. [Action] → [UI feedback]
  2. [Action] → [UI feedback]
  ...
Preconditions: [What must be true before starting]
Result: [Final state]
Articles: [Source articles]
```

### Step 4: Identify UI panels and their states
From the hub articles, map out:

```
Panel: [Name, e.g., "Properties Panel"]
Location: [Right sidebar]
Shows when: [Condition — e.g., "any layer selected"]
Contains: [List of sections/controls]
Changes when: [What actions modify this panel]
```

## Output Format

Save your analysis as structured markdown files in `analysis/` directory:
- `analysis/feature-inventory.md`
- `analysis/ui-map.md`
- `analysis/workflows.md`
- `analysis/panel-states.md`
- `analysis/dependency-clusters.md`

## Token Budget Tips

- Read `structure-helper/figma_docs/index.json` first to find articles by title.
- Read `structure-helper/figma_docs/articles/<slug>/metadata.json` before `content.md` — it has links and breadcrumb without the full body.
- For graph analysis, `structure-helper/figma_docs/graph.json` has everything — don't read individual metadata files for link data.
- Process one domain at a time, not all 197 articles at once.
