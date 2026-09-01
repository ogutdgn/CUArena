# Context Menu (right-click overlays)

**Region role:** Right-click floating menu that appears at the cursor. Contents change based on the right-clicked target — selection type, layer count, mode (canvas vs panel vs vector edit).

**Global behavior:**
- Anchored to cursor (or just below).
- Click outside or Esc closes.
- Hover sub-menu items expand right.

---

## 1. Empty canvas (no selection)

| Entry | Status |
|---|---|
| Paste here | [FN] (paste at cursor position) |
| Paste over selection | [FN] (paste-properties on selection) |
| Select all | [FN] |
| Show outlines | [FN] |
| Show pixel grid | [VO] |
| Frame selection | [FN] (only with selection) |

---

## 2. Single layer selected

| Entry | Status |
|---|---|
| Copy / Cut / Paste / Paste here / Paste over | [FN] |
| Duplicate | [FN] |
| Delete | [FN] |
| Select layer (when locked layers underneath) | [FN] |
| Group selection | [FN] |
| Frame selection | [FN] |
| Use as mask | [DEF] |
| Create component | [FN] |
| Boolean operations → Union / Subtract / Intersect / Exclude / Flatten | [FN core, FN flatten] |
| Bring to front / forward | [FN] |
| Send backward / to back | [FN] |
| Lock / Unlock | [FN] |
| Show / Hide | [FN] |
| Rename | [FN] |
| Copy properties / Paste properties | [FN] |
| Copy as PNG / SVG / link | [DEF] |
| Edit object (vector edit) | [FN] |
| Outline stroke (convert stroke to path) | [FN] |
| Flatten | [FN] |
| Set as thumbnail | [VO] |
| Show / Hide layer | [FN] |
| Plugins → ... | [VO] |
| Widgets → ... | [VO] |

---

## 3. Multi-select (mixed types)

Same as single-layer with these differences:
- **Boolean ops** apply only when ≥ 2 supported types selected.
- **Frame selection** wraps all in a frame.
- **Group selection** groups all.
- **Tidy up** appears when selection is alignable.
- **Distribute horizontal / vertical** appears with 3+ layers.

---

## 4. Frame selected

Adds:
- **Use auto layout** [FN] (Shift A)
- **Resize to fit** [FN]
- **Ungroup** [FN] (Cmd Shift G — unwraps frame)
- **Frame preset** dropdown sub-entry [FN]

---

## 5. Component / Instance selected

| Entry | Status |
|---|---|
| Detach instance | [FN] |
| Reset all overrides / Reset to default | [DEF] |
| Go to main component | [FN] |
| Replace instance with another component | [FN] (swap) |
| Restore instance | [DEF] |
| Set as main / Set as instance | [DEF] |

---

## 6. Boolean group selected

| Entry | Status |
|---|---|
| Ungroup (revert boolean) | [FN] |
| Edit children (already non-destructive) | [FN] |

---

## 7. Vector layer selected

| Entry | Status |
|---|---|
| Edit object (enter vector edit) | [FN] |
| Flatten | [FN] |
| Outline stroke | [FN] |
| Convert text to vector (text only) | [FN] |
| Simplify path | [FN] |
| Offset path | [FN] |

---

## 8. Inside vector edit mode

| Entry | Status |
|---|---|
| Move tool | [FN] |
| Pen tool | [FN] |
| Bend tool | [FN] |
| Lasso tool | [FN] |
| Cut tool | [FN] |
| Paint tool | [FN] |
| Variable width tool | [FN] |
| Shape builder | [FN] |
| Split vector (for branching paths) | [DEF] |
| Reverse direction | [DEF] |
| Done / Esc | [FN] |

---

## 9. Right-click on a layer in the Layers panel

Same as canvas right-click on that layer. Plus panel-specific:
- **Rename** (inline) [FN]
- **Reorder** (drag) — not via menu
- **Lock / Unlock** (panel padlock) [FN]
- **Show / Hide** (panel eye) [FN]
- **Find similar** [DEF]

---

## 10. Right-click on a page in the Pages selector

Per `ui-shell/page-context-menu.md`:
- **Rename** [FN]
- **Duplicate page** [FN]
- **Delete page** [FN] (cannot delete only page)
- **Set as thumbnail** [VO]
- **Copy link to page** [VO]

---

## 11. Right-click on a comment pin

| Entry | Status |
|---|---|
| Reply | [FN] |
| Mark resolved / unresolved | [FN] |
| Mark unread | [FN] |
| Copy link | [VO] |
| Delete (author only) | [FN] |

---

## 12. Right-click on a text layer in edit mode

| Entry | Status |
|---|---|
| Cut / Copy / Paste | [FN] |
| Paste matching style | [DEF] |
| Add link | [DEF] |
| Insert emoji | [DEF] |
| Spell check / dictation (OS-driven) | [VO] |

---

## 13. Right-click on the canvas with a tool active

Tool-dependent. Generally exits the tool back to default.

---

## Conventions for unsupported entries

Per `ui-shell/unsupported-feature-toast.md`, every `[VO]` entry routes through the toast — clicking it surfaces "{Feature name} is not yet supported".

## Source articles

- Most context-menu entries trace to the same articles documenting their underlying feature. Cross-references:
  - `select-layers-and-objects` — Select layer (locked underneath)
  - `lock-and-unlock-layers` — Lock / Unlock
  - `toggle-visibility-to-hide-layers` — Show / Hide
  - `rename-layers` — Rename / bulk-rename
  - `boolean-operations` — Boolean → entries
  - `flatten-layers` — Flatten
  - `convert-strokes-to-vector-paths` — Outline stroke
  - `convert-text-to-vector-paths` — Convert text to vector
  - `frames-in-figma-design` — Frame / Ungroup
  - `the-difference-between-frames-and-groups` — Group / Ungroup
  - `copy-and-paste-objects` — Copy / Paste / Paste here
  - `copy-and-paste-properties-between-layers` — Copy / Paste properties
- Plugin/widget entries are `[VO]` per scope.

## Notes / gaps

- The full enumerated context-menu inventory varies slightly between Figma versions and selection contexts. The list above is best-effort from the corpus.
- Per `ui-shell/cursor-chat.md`, a separate hover-anchored "/" chat invocation isn't strictly a context menu but a similar overlay.
