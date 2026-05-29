# UI approach — the Word-clone chrome

> **Purpose.** This doc records **how the Word clone's interface is built**: the
> rendering split between our QML chrome and the engine's document pixels, the icon
> and control toolkit, the design-token system that carries Word fidelity, font
> substitution for a distributable image, and how engine dialogs surface as native
> QML. It is a **decision record** for the UI layer, grounded in the locked
> tech-stack and engine decisions (see [`../research/tech-stack.md`](../research/tech-stack.md)
> and [`../research/ribbon/README.md`](../research/ribbon/README.md)).
>
> Scope note: under **Boundary A** we own the UI, command dispatch, document state,
> the always-on logger, and the MCP server; we rent the LibreOffice engine via
> **LOK** (in-process) only for layout, text shaping, and `.docx`/`.odt` I/O. This
> doc covers the **UI half of Boundary A**.

---

## 1. Principle — QML chrome, LOK document pixels

The interface splits cleanly in two:

- **Chrome** — ribbon, galleries, menus, dialogs, status bar, rulers — is **QML**,
  owned entirely by us.
- **Document canvas** — the page the user edits — is **not** drawn by QML. The
  pixels come from **LOK's tile buffer**: the engine renders tiles via `paintTile`,
  and we `memcpy` that buffer onto the canvas surface.

This split is the foundation of the whole UI strategy. Because the document pixels
originate in the engine's tile buffer, they are **toolkit-independent** — the canvas
looks the same regardless of which UI toolkit hosts it. QML is therefore a free
choice for the chrome: it carries no fidelity risk for the document itself, and the
chrome is where Word's look actually lives. We invest the fidelity effort exactly
where it pays off — in the chrome — and let the engine own the pixels it already
knows how to draw.

## 2. Icons — Microsoft Fluent UI System Icons, recolored

The clone uses the **Microsoft Fluent UI System Icons** — the real M365 icon family,
released by Microsoft under the **MIT** license. These are the same glyphs that ship
in Word, so the ribbon reads as Word rather than as a look-alike.

Icons are **recolored to Word tints** to match the M365 palette (the Word brand blue,
the neutral grays of the chrome) rather than used in their default coloring.
Recoloring is a presentation step in our layer; the glyph geometry is Microsoft's.

## 3. Controls — FluentWinUI3 baseline, bespoke ribbon

The **base control style is Qt's `FluentWinUI3`**, which gives standard widgets
(buttons, checkboxes, fields, combo boxes) a Fluent appearance for free.

The Word-specific surfaces, however, are **bespoke custom QML controls**: the
**ribbon, the galleries, and the menus** are all built by us. There is **no stock
"Word ribbon"** in any toolkit — the tabbed ribbon, the live-preview galleries, and
the M365 menu styling do not exist off the shelf and must be authored as custom
components. `FluentWinUI3` handles the ordinary widgets; we build the rest.

## 4. The design-token system — the key to fidelity

**This is the mechanism that makes the clone read as Word.** Fidelity does not come
from any single control; it comes from every control drawing from one shared set of
**design tokens**, implemented as **QML singletons**. Three token families:

- **Colors** — the Word M365 **exact palette**, plus theme variants. Every surface,
  border, hover, and accent references a named color token, never a hard-coded value.
- **Metrics** — paddings, margins, button sizes, **ribbon height**, and the rest of
  the spatial system. These are **measured from real Word at a known DPI** so the
  layout matches Word's proportions rather than approximating them.
- **Typography** — the type ramp for the chrome (sizes, weights, line metrics).

Because every control reads from the same singletons, the look is consistent by
construction and tunable in one place. Getting the tokens right — especially the
measured metrics — is what separates "looks like Word" from "looks roughly like a
ribbon."

## 5. Fonts — Microsoft families, open substitutes for distribution

Word uses **Segoe UI** for the chrome and **Aptos** as the document default. Both are
**Microsoft fonts** and are not freely redistributable.

For a **distributed RL image**, the clone therefore uses **open, metric-compatible
substitutes** — **Selawik** stands in for Segoe UI — so the chrome keeps Word's
spacing and proportions without shipping a licensed font. Where the Microsoft fonts
**are** licensed for the deployment, they can be used directly. Metric compatibility
is the point: the substitute must occupy the same space so the token-driven metrics
in §4 still hold.

## 6. Dialogs — JSDialog JSON to native QML

Engine dialogs are not rendered by the engine. LOK emits its dialogs as **JSDialog
JSON widget trees**, and we render those trees as **native QML dialogs**, themed by
the **same design tokens** as the rest of the chrome. A dialog therefore looks like
part of the Word clone, not like a LibreOffice dialog embedded in it.

This is the one place the engine source is touched: registering a dialog in
`vcl/jsdialog/enabled.cxx` so it emits its JSON tree. That registration is the only
sanctioned engine edit under the **no-core-edits** guardrail — it exposes an existing
dialog, it does not change engine logic.

## 7. Where the token values come from

This doc specifies the **system**; it does not contain the **values**. The concrete
color codes, the measured metrics, the type ramp, and the recolored icon set are the
output of **research stream #4 (UI design-token extraction)**, produced **at build
time, early in the build**, from **real Word and the Fluent specs**. The build phase
extracts those values into the QML singletons described in §4. Until then, the token
system is the contract; #4 fills it.

## 8. Honest parity bar

The target is **indistinguishable at a glance** — scoped parity, consistent with the
fidelity bar used throughout this project: the clone reads as Word within the build
surface, and entry points outside scope are simply absent.

A prior Qt6/QML prototype felt unprofessional. That feel was a matter of
**implementation and metrics discipline** — unmeasured spacing, ad-hoc values, no
token system — **not a ceiling of Qt or QML**. With the measured-token system in §4
and the bespoke controls in §3, the same toolkit reaches the parity bar. The work is
in the discipline, not the toolkit.
