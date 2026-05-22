# lo/ui-improve — UI Improvement Plan & Progress

> Source-of-truth plan + status log for the `lo/ui-improve` branch.
> The **what we want** specs live in:
> - [`lo-ui-improve-tasks.md`](lo-ui-improve-tasks.md) — Word-style unified title strip
> - [`lo-ui-improve-tasks2.md`](lo-ui-improve-tasks2.md) — Word Home ribbon styling
>
> This doc is **what we're doing about it** — task breakdown, decisions
> taken, current status, known blockers, next steps. Update as work
> progresses (per the `keep-docs-in-sync` skill).

Last updated: 2026-05-22 (T4 + T5 parked, branch wrapping)

---

## 1. Branch scope

`lo/ui-improve` is a single short-lived feature branch off cua-bench
`main`. It collects every UI cleanup / Word-parity tweak that comes up
during owner-driven iteration; once shipped, it merges via PR.

Out of scope for this branch:
- Phase 4 V1 work (already merged on `main` per ROADMAP §3.4)
- Calc / Impress UI parity (Phases 5 / 6 scope)
- Win32 / Cocoa CSD — GTK-only, see §2 platform decision

---

## 2. Standing decisions

### 2.1 Platform: GTK only

LO multi-backend (Linux GTK, Windows Win32, macOS Cocoa). Deployment
target is Docker on Linux (ROADMAP §3.6), and the owner runs the build
via WSL2 + WSLg which renders Wayland/X11 windows back to the Windows
desktop. **Win32 native LO build is not on the path.** CSD-style
changes use GTK HeaderBar + GtkCssProvider only.

### 2.2 Title-strip architecture: CSD (single unified strip)

Word renders title + QAT + window controls in a single tight strip via
client-side decoration. LO's default is OS-native title bar + separate
notebook bar — two rows. We pivoted to CSD for visual parity even
though it requires invasive vcl-layer work. See §4 T1 for the GTK
HeaderBar path.

### 2.3 Branding-light variant (no app icon, no Search, no Account)

The Word M365 title bar shows W glyph + AutoSave + QAT + Doc name +
Search + Account + Window controls. Per owner direction (chat
2026-05-22):

| Component | Decision |
|---|---|
| App icon (W glyph) | **Drop** — Microsoft trademark + LO Writer icon renders inconsistently at titlebar sizes; matching Word's M365 minimalist title variant. |
| AutoSave toggle | **Drop** — LO has AutoRecovery, not Word-style cloud autosave. UI stub would mislead. |
| Microsoft Search bar | **Drop** — LO has no command-and-content unified search. Standard Find (Ctrl+F) covers text search. |
| Account avatar | **Drop** — LO has no cloud identity. |
| Ribbon Display Options | **Drop** — Word's auto-hide/show-tabs/show-tabs+commands trichotomy has no LO equivalent. |
| QAT (Save / Undo / Redo / Customize) | **Keep**, relocated to HeaderBar. |
| Window controls (min / max / close) | **Keep**, Windows 11 styling target. |
| Doc name | **Keep**, centered. |

### 2.4 Acrobat tab

Already declined in Phase 4 (LO doesn't ship the Adobe plugin).

---

## 3. Risk / blocker register

### 3.1 BLOCKER: HeaderBar background CSS doesn't apply (T4)

**Symptom:** `headerbar { background-color: #1F1F1F; background-image:
none; }` at `PRIORITY_USER` against the HeaderBar widget context
fails to override Adwaita's default light gray. Verified on both
X11-forced and native Wayland launches. `gtk_widget_override_
background_color` (deprecated) is also a no-op. `gtk-application-
prefer-dark-theme=TRUE` setting also doesn't take.

**What DOES apply** (proven by debug iterations):
- `headerbar { min-height: 50px }` → height visibly changed
- `* { color: red }` → all labels turned red

So screen-level providers reach widgets; the cascade matches `headerbar`
as a selector; but background-color specifically resists override.

**Likely causes** (not yet narrowed):
1. WSLg compositor paints chrome via a path that bypasses GTK CSS
2. LO's own `salnativewidgets-gtk.cxx` paints over the HeaderBar
3. Adwaita uses a `background-image` layer whose source the CSS
   `none` override can't unset
4. The visible HeaderBar bg comes from a wrapper widget that we don't
   tag with our class / name / provider

**Workaround options for future T4 debug sprint:**
- (a) Replace `GtkHeaderBar` with a `GtkBox` we draw ourselves
- (b) Subclass HeaderBar and override the `draw` signal
- (c) Use `GtkInspector` (`GTK_DEBUG=interactive` + Ctrl+Shift+I) to
  inspect the real CSS path GTK uses on the running HeaderBar and
  target THAT exact selector

### 3.2 Autonomous screenshot loop quirk

`xdotool` + `import` (ImageMagick) require X11. WSLg defaults to
Wayland. Forcing `GDK_BACKEND=x11` lets X tools work but changes LO's
theme detection path, so colors render differently from a native
Wayland launch. Owner's normal-env screenshots remain the verification
ground truth.

---

## 4. Task breakdown (CSD title strip)

Each task is one focused commit (with fix-commits as needed). Commits
follow `feat(libreoffice): ...` / `fix(libreoffice): ...` per
`commit-style.md`.

| ID | Subject | Status | Commits |
|---|---|---|---|
| T1 | GTK frame → CSD: `gtk_window_set_titlebar(GtkHeaderBar)` for normal toplevels, dropping the Wayland/RTL gate that previously kept it Wayland-only | ✓ done | `f6b44c632` |
| T2 | HeaderBar contents: force `:minimize,maximize,close` decoration layout, no subtitle, no app icon (branding-light per §2.3) | ✓ done | `9961b201f`, `4e5c379c7`, `972daf000` |
| T3 | Quick Access Toolbar: pack Save / Undo / Redo `GtkButton` widgets into the HeaderBar, wired through `comphelper::dispatchCommand`. Hide the second-row toolbox in `NotebookbarTabControlBase` (`tabctrl.cxx`) | ✓ done | `4f08baf9c` |
| T4 | HeaderBar visual: `#1F1F1F` background, 32 px min-height, Segoe UI font fallback, flat QAT buttons, Windows 11 min/max/close (close-hover red) | ⏭ **skipped** — all 9 T4 commits reverted in a single revert (see below). HeaderBar keeps Adwaita's default chrome on this branch. To be re-attempted in a dedicated debug sprint once the blocker in §3.1 is understood. | (reverted) — see §4.1 |
| T5 | Notebookbar tab strip: `#2B2B2B` bg, active tab 2 px blue underline (`#4A9EFF`), File tab permanent blue button, hover state `rgba(255,255,255,0.05)` — VCL paint customization in `tabctrl.cxx` | ⏭ **skipped** — Paint override in `NotebookbarTabControlBase` never fires on the visible tab strip. Same paint-pipeline blocker as T4 (see §4.2). Reverted; revisit alongside T4. | (reverted) — see §4.2 |
| T6 | Codex review pass + smoke test verification — `superpowers:verification-before-completion` style: build all three apps, smoke-test Writer / Calc / Impress | in progress / final task on this branch | — |

Standalone fix commits on `lo/ui-improve` that don't slot into the
T1-T6 list:

| Commit | Subject | Notes |
|---|---|---|
| `dc6fc97ce` | hide notebookbar tab-strip hamburger menu | pre-CSD cleanup; covers both Writer + Calc / Impress (shared `NotebookbarTabControlBase`) |
| `dbbdafc35` | add libreoffice scope to `commit-style.md` | repo housekeeping |

### 4.1 T4 reverted — what we learned and what to retry

After ~9 iterations against `vcl/unx/gtk3/gtkframe.cxx` (CSS providers
at every GTK priority, per-widget plus per-screen, every selector
specificity tier from bare `headerbar` to `window.csd > headerbar.titlebar`,
plus the deprecated `gtk_widget_override_background_color` API and the
`gtk-application-prefer-dark-theme` settings hook) the HeaderBar
background stayed Adwaita-light in every smoke test. **Min-height and
text color responded to CSS; background-color did not** — a stubborn
asymmetry that points to a non-CSS paint path we haven't identified.

All T4 commits were reverted in a single revert commit. The
`gtkframe.cxx` state matches the T3 endpoint (`4f08baf9c`). T1-T3
functional gains are preserved.

Reverted T4 commits, oldest first (kept here for the future debug
sprint to study without re-deriving):
`1031427b1`, `01650ae2b`, `5a0761848` (debug), `235e82274`,
`b9b6430e2`, `eddf6519b`, `f4078db0f`, `c48bbd6f8`, `c9f9dcadc`.

Recommended next moves when T4 is reopened (do them before writing more
CSS):
1. Run `GTK_DEBUG=interactive` and Ctrl-Shift-I to open `GtkInspector`
   against a live LO window — read the **actual** CSS path the
   running HeaderBar carries (classes, name, parent chain). Half of
   the iterations above guessed at the selector; the inspector tells
   you for sure.
2. While in the inspector, modify CSS rules on the live widget — the
   moment a rule **does** turn the bg dark, you know which selector
   and which property survives the cascade. That is the rule to bake
   into `gtkframe.cxx`.
3. Verify whether `salnativewidgets-gtk.cxx` or `custom-theme.cxx`
   is repainting the HeaderBar after our CSS lands. Both have draw
   hooks; a `printf` in their HeaderBar code path will confirm.
4. As a fallback, replace the GtkHeaderBar with a custom `GtkBox` whose
   `draw` signal we own end-to-end. Loses native window-control
   integration (we'd reimplement min / max / close), but gains
   complete paint control.

### 4.2 T5 reverted — same paint-pipeline blocker as T4

Attempted: override `NotebookbarTabControlBase::Paint` to overlay a
Word-style `#2B5797` blue rectangle plus a white "File" label on the
first tab item's rect. A debug version drew a 6 px red stripe at the
top of `rRect` unconditionally to verify the override fired.

Result: in the owner's normal Wayland launch the **debug stripe was
not visible**, which means the override never runs on the visible
tab strip. `NotebookbarTabControlBase::ImplPlaceTabs` and
`SetToolBox` (touched in the hamburger / QAT-relocate commits)
**do** run — `m_pShortcuts->Hide()` took effect — so the layout
side of the class is exercised. Only the paint side is silent.

Most likely cause: the visible tab strip on Wayland / WSLg is
painted by the GTK side of the widget (gtk_render_extension via
`salnativewidgets-gtk.cxx`, or the `WeldedTabbedNotebookbar`
JSDialog wrapper), not by the VCL `TabControl::Paint` cascade we
overrode. Confirming this needs the same GtkInspector pass that
T4 needs.

All T5 commits were reverted in a single revert commit alongside
this plan update. Reverted T5 commits:
`4bebc3356` (T5a — Paint override + blue File overlay),
`b2ca32a99` (debug — red stripe).

Recommended next moves when T5 is reopened — share the debug sprint
with T4 since both fight the same paint pipeline:

1. **GtkInspector first**, against both the HeaderBar and the tab
   strip. Confirm which side renders each — VCL vs GTK-native vs
   JSDialog wrapper.
2. If the tab strip is GTK-native rendered, the styling hook is
   either:
   - A `gtk_render_*` interception in `salnativewidgets-gtk.cxx`
     (e.g. `tabitem` painter) — invasive but contained.
   - A custom GTK CSS provider scoped to the notebookbar widget tree
     (different from the HeaderBar — separate provider with its own
     selectors).
3. If the tab strip is JSDialog-rendered, the styling lives in the
   JS notebookbar component (LO Online code path); we may need a
   per-platform branch.
4. The File tab "permanently blue button" is intentionally the
   highest-impact visual cue: nail that one first, then tune the
   active-tab underline colour (`#4A9EFF`) and add the hover state.

---

### 4.3 Codex review pass (T6) — findings and dispositions

Codex review of the net diff against `main` flagged five items; two
major, three notes / minor. Dispositions:

| # | File / lines | Severity | Disposition |
|---|---|---|---|
| 1 | `gtkframe.cxx` ~L1743 `eType == GDK_WINDOW_TYPE_HINT_NORMAL` guard | major | **Fixed in branch** — narrowed to also exclude `DIALOG` / `TOOLWINDOW` / `INTRO` / `OWNERDRAWDECORATION` so a parentless dialog can't pick up the document CSD HeaderBar. Code now: `eType == NORMAL && !(nStyle & (DIALOG | TOOLWINDOW | INTRO | OWNERDRAWDECORATION))`. |
| 2 | `tabctrl.cxx` hamburger + shortcuts hide is unconditional | major | **Accepted as known limitation** — see §3.3 below. The hide runs in shared `NotebookbarTabControlBase` code regardless of whether a GTK HeaderBar was installed. For our Linux-only Docker deployment (ROADMAP §3.6) this is a non-issue, but on a hypothetical non-GTK native build (Windows / macOS) the QAT functions would disappear without the HeaderBar replacement. |
| 3 | `gtkframe.cxx` button signal callbacks pass `nullptr` user data | note | No action. `comphelper::dispatchCommand` resolves the active frame at click time which is the intended behaviour — see §3.4. |
| 4 | `comphelper::dispatchCommand` layering | minor | **Accepted** — Section 3.4 captures the focus-targeting semantics. `comphelper` is at the same layer as `vcl`, no inverted dependency; the only behavioural caveat is that command targeting follows the active LO frame, not the GTK window the button physically sits in. Practical effect: identical in the single-window case, possibly surprising with multiple LO windows where focus isn't where the click lands (rare given LO modal-ish window switching). |
| 5 | Hidden hamburger / shortcuts treated as zero-width but still allocated | note | Documented in commit messages and §3.5 below. A future "unhide" path would need to re-trigger `ImplPlaceTabs`; not on this branch's roadmap. |

### 3.3 Known limitation — tab-strip hides are unconditional

`NotebookbarTabControlBase::SetToolBox` calls `pToolBox->Hide()` and
`NotebookbarTabControlBase::ImplPlaceTabs` treats `m_pShortcuts` and the
hamburger `m_pOpenMenu` as zero-width regardless of which platform the
notebookbar is rendering on. On the Linux GTK builds this branch
targets, that's correct: the QAT functions are reachable via the GTK
HeaderBar instead. On a hypothetical native Windows VCL build (not
on the deployment path per ROADMAP §3.6), the QAT functions would
disappear without a replacement — File menu still has Save, and
keyboard shortcuts (Ctrl+S / Ctrl+Z / Ctrl+Y) still work, but the
visible toolbar buttons would be gone.

When / if a native Windows / macOS build re-enters scope, the hides
need to be gated on the platform supplying the HeaderBar replacement.
Easiest fix: add a `static bool s_bHasGtkHeaderBarQat` flag set by the
GTK backend during frame init and checked in `SetToolBox` /
`ImplPlaceTabs`.

### 3.4 Behavioural note — active-frame dispatch from HeaderBar buttons

The QAT buttons (`on_qat_save_clicked` etc.) use
`comphelper::dispatchCommand(u".uno:Save"_ustr, {})` which resolves
the **active LO frame** at click time. They do not capture the
`GtkSalFrame` whose HeaderBar was clicked. With a single open document
window this is identical to "the window I clicked in", and with a
focused window it is the right behaviour. The edge case is clicking
the HeaderBar of an unfocused window: the click activates the window
(GTK gives focus) before the signal fires, so the dispatch still
targets the right frame in normal usage. The only scenario where it
could surprise the user is multi-LO-window setups with manual focus
control via a window manager that suppresses click-to-focus.

### 3.5 Behavioural note — hidden widgets are still in the navigation chain

`NotebookbarTabControl::ArrowStops` walks `m_pShortcuts` and
`m_pOpenMenu` for keyboard focus traversal. Both pointers stay valid
after the hide, so `Hide()` widgets are still reachable via
keyboard, just invisible. In practice the `GrabFocus()` calls on a
hidden widget are silent no-ops in VCL, so the navigation just skips
past them. Documented for any future re-enable path.

---

## 5. Cross-app side effects

| Change | Effect on Calc / Impress |
|---|---|
| GTK CSD HeaderBar (T1) | Calc + Impress also get a HeaderBar (shared `GtkSalFrame::Init`). Empty initially; T2 fills with QAT. |
| Decoration layout force (T2) | All three apps show min/max/close trio regardless of GNOME `button-layout`. |
| QAT in HeaderBar (T3) | All three apps gain HeaderBar QAT; Phase 4 V1.1 Comments / Editing / Share also removed from second-row QAT toolbox. |
| Hamburger menu hide (pre-T1) | Same. |
| T4 visual styling | **Not shipped on this branch** (reverted, §4.1). When eventually applied it'll hit all three apps' HeaderBars; Calc / Impress visual targets will diverge in Phases 5 / 6. |
| T5 tab-strip styling | **Not shipped on this branch** (reverted, §4.2). Same multi-app fan-out as T4 when eventually applied. |

To be appended to
[`../architecture/PHASE4_SIDE_EFFECTS_CALC_IMPRESS.md`](../architecture/PHASE4_SIDE_EFFECTS_CALC_IMPRESS.md)
when this branch lands.

---

## 6. Home ribbon work (queued, post-CSD)

Spec: [`lo-ui-improve-tasks2.md`](lo-ui-improve-tasks2.md). 18 sections,
~96 px ribbon height target, 7 functional groups (Clipboard / Font /
Paragraph / Styles / Editing / Voice / Editor / Add-ins), dialog
launchers, style preview gallery cards with cream backgrounds, etc.

Decision deferred: when to start. Owner direction (chat 2026-05-22):
"finish CSD first, then move to that side." Since T4 and T5 were
parked and only T1-T3 + T6 wrap on this branch, Home ribbon is the
next major piece — it can start as soon as `lo/ui-improve` merges,
without waiting on the T4 / T5 debug sprint (Home ribbon is VCL paint
inside the tab BODY, structurally separate from the GTK chrome that
blocked T4 / T5).

Pre-existing state: Phase 4 V1.1 already restructured the Home tab to
Word's 8 groups (ROADMAP §3.4). The new spec is **pixel-level styling**
on top of that structure: spacing, separators, gallery card visuals,
icon colors. Most of this needs:
- `tabctrl.cxx` paint code edits (VCL)
- StylesPreview C++ widget work (the gallery cards)
- New officecfg color tokens

Cataloguing exactly which spec sections are **doable in lo/ui-improve
scope** vs **need new VCL infrastructure** is a job for after the CSD
chunk lands — we'll create a `lo-ui-improve-ribbon-plan.md` then.

---

## 7. Verification

Default smoke loop per task:

```sh
cd /home/ogutd/cua-bench-lo
git pull origin lo/ui-improve
cd apps/libreoffice/libreoffice-codebase
make vcl    # for vcl-only edits; `make vcl sw sc sd` if higher-level
instdir/program/soffice --writer --norestore
```

Owner's normal-environment screenshots = ground truth for visual
verification. Autonomous (xdotool + ImageMagick + WSLg X11 force) is
unreliable for theme-sensitive output (see §3.2).

T6 final pass: full Writer + Calc + Impress smoke (all three open,
type something, save, undo, redo, close), codex review of every commit
on the branch, then PR.

---

## 8. Branch wrap — what ships in the PR

What this branch delivers (relative to `main`):

**Functional changes** (two `vcl/` files touched):
- `vcl/unx/gtk3/gtkframe.cxx` (+89 / -18): GTK Client-Side Decoration
  for every normal LO document toplevel; `GtkHeaderBar` with forced
  `:minimize,maximize,close` decoration layout, no subtitle slot,
  and a left-packed Save / Undo / Redo Quick Access Toolbar wired
  through `comphelper::dispatchCommand`.
- `vcl/source/control/tabctrl.cxx` (+20 / -x):
  - `NotebookbarTabControlBase::ImplPlaceTabs` ignores the tab-strip
    hamburger (`m_pOpenMenu`) width when hidden, reclaiming the row
    for tabs.
  - The hamburger widget is created hidden (no longer drawn).
  - The in-tab-strip shortcuts ToolBox (`m_pShortcuts`) is hidden on
    `SetToolBox`, its width treated as zero — the QAT functions now
    live in the HeaderBar instead.

**Cross-app side effect**: every change above is in shared
`NotebookbarTabControlBase` / `GtkSalFrame` code so it applies to
Writer + Calc + Impress in lockstep.

**Documentation** (`apps/libreoffice/`):
- New `docs/plan/` directory holding owner-supplied UI specs plus this
  agent-maintained progress + decision log. `CLAUDE.md` "Read this
  first" lists it; `AGENTS.md` §9 / §9.1 catalogs how it differs from
  `docs/architecture/`.
- `commit-style.md` (repo-root `.claude/`) gains the `libreoffice`
  scope tag.

**Parked** for the future T4 / T5 paint-pipeline debug sprint
(captured here, not shipped):
- T4: `HeaderBar` visual styling — Word-dark background, Win11 button
  styling. Reverted; see §3.1 / §4.1.
- T5: Tab-strip visual styling — `#2B2B2B` bg, blue File-tab button,
  hover state. Reverted; see §4.2.

**Next milestones** (owner direction):
1. Combined T4 / T5 debug sprint — run GtkInspector against a live
   LO window first, then unblock both via the route the inspector
   reveals.
2. Home ribbon (`lo-ui-improve-tasks2.md`) — separate sprint, can
   start in parallel since it's VCL paint inside the tab BODY,
   structurally independent from the GTK chrome that blocked T4 / T5.

---

## 9. Cross-references

- [`lo-ui-improve-tasks.md`](lo-ui-improve-tasks.md) — Word title strip spec (owner-supplied)
- [`lo-ui-improve-tasks2.md`](lo-ui-improve-tasks2.md) — Word Home ribbon spec (owner-supplied)
- [`../architecture/PHASE4_WRITER_UI_DESIGN.md`](../architecture/PHASE4_WRITER_UI_DESIGN.md) — Phase 4 V1 design (already-shipped baseline)
- [`../architecture/PHASE4_BLOCKERS.md`](../architecture/PHASE4_BLOCKERS.md) — running blocker log; T4 background-override fight may graduate here if we abandon for V2
- [`../architecture/PHASE4_SIDE_EFFECTS_CALC_IMPRESS.md`](../architecture/PHASE4_SIDE_EFFECTS_CALC_IMPRESS.md) — cross-app side-effect catalogue, gets the §5 entries on PR
- [`../architecture/ROADMAP.md`](../architecture/ROADMAP.md) §3.4 — Phase 4 status the V1 ship line
- [`../../AGENTS.md`](../../AGENTS.md) §8 — conventional commit format
- [`../../CLAUDE.md`](../../CLAUDE.md) — Claude-specific rules (no AI-attribution trailers, build discipline, skill usage)
