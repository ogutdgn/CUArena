"""First-level popup / dialog capture (DESIGN 4.3-4.4, 6.4) — rebuilt per KNOWN_GAPS + FIX_PLAN v2.

Ribbon flyouts are owner-drawn: their items are only reachable by IUIAutomation.ElementFromPoint
hit-testing (the UIA tree returns only an empty container). Modal dialogs expose a full UIA
descendant tree. So popups are captured by point-sampling; dialogs by descendants().

Key rebuild fixes vs the first P0 run:
  * GEOMETRY dedupe for owner-drawn cells (color swatches / gallery tiles share an empty Name, so
    the old (control_type, name) key collapsed ~70 swatches to one). Menu items still dedupe by name.
  * color-grid section kind: blank-name swatches -> {rgb (screenshot pixel), themeSlot, tint, bounds}.
  * label/chrome sanitization; phantom 'Gallery Filters' chrome dropped.
  * dialog More>> expansion; per-tab buttons (no cross-tab name shadowing); field identity from
    UIA LabeledBy/ControllerFor then geometry (kills the anonymous 'RichEdit Control' fields);
    fields grouped into their UIA Group section.
  * E1: surface-discovered entry uses the real item id, never a trailing '#'.
"""
import time
import win32gui
import ids, schemas, shots, textutil
from pywinauto import Desktop
from pywinauto.uia_defines import IUIA

# UIA control-type ids (owner-drawn flyout items report these).
_HEADER, _IMAGE, _LISTITEM = 50026, 50007, 50008
_MENUBAR, _MENUITEM, _BUTTON, _PANE = 50011, 50012, 50000, 50024
_GALLERY_CTS = {_IMAGE, _LISTITEM}
_MENU_CTS = {_MENUBAR, _MENUITEM, _BUTTON}
_DYNAMIC_HINTS = ("styles", "recently", "recent")
_COLOR_HEADERS = ("theme colors", "standard colors", "recent colors", "standard")
_UIA_LABELEDBY = 30003
_GENERIC_NAMES = {"", "richedit control", "text"}


def _rect(el):
    try:
        r = el.CurrentBoundingRectangle
        return (r.left, r.top, r.right, r.bottom)
    except Exception:
        return (0, 0, 0, 0)


def _unique_id(base, used):
    slug = ids.slugify(base) or "item"
    cand, n = slug, 2
    while cand in used:
        cand = f"{slug}-{n}"
        n += 1
    used.add(cand)
    return cand


def _sample_popup(popup_rect):
    """Grid ElementFromPoint over the popup. MENU items dedupe by name (distinct); GALLERY/color
    cells dedupe by cell GEOMETRY (owner-drawn cells share an empty Name). Returns
    (ct, name, rect, enabled) ordered top-to-bottom, left-to-right. `enabled` matters: pressing a
    DISABLED opener captures garbage (the flyout itself), so drains must be able to skip them."""
    iuia = IUIA().iuia
    from ctypes.wintypes import POINT
    l, t, r, b = popup_rect
    seen = {}
    y = t + 4
    while y < b - 3:
        x = l + 5
        while x < r - 5:
            try:
                el = iuia.ElementFromPoint(POINT(x, y))
                ct = el.CurrentControlType
                if ct == _PANE:
                    x += 8
                    continue
                name = el.CurrentName or ""
                rc = _rect(el)
                try:
                    enabled = bool(el.CurrentIsEnabled)
                except Exception:
                    enabled = True
                if ct in _GALLERY_CTS:
                    key = ("cell", round(rc[0] / 3), round(rc[1] / 3),
                           round(rc[2] / 3), round(rc[3] / 3))
                elif ct == _HEADER:
                    key = ("hdr", name, rc[1])
                elif ct in _MENU_CTS and name:
                    key = ("menu", name)
                else:
                    x += 8
                    continue
                if key not in seen:
                    seen[key] = (ct, name, rc, enabled)
            except Exception:
                pass
            x += 8
        y += 6
    items = list(seen.values())
    items.sort(key=lambda it: (it[2][1], it[2][0]))
    return items


def _popup_action(name):
    n = (name or "").strip()
    # ASCII "..." AND Unicode "…" both carry the opens-a-dialog convention ("Line Spacing Options…"
    # was typed feature because only the ASCII form was checked). slugify strips the dots either way.
    if n.endswith("...") or n.endswith("…"):
        return {"kind": "opens-dialog", "ref": ids.surface_id("dialogs", n)}, True
    return {"kind": "feature"}, False


def _pid_tops(pid):
    import win32process
    out = set()

    def cb(h, _):
        try:
            if win32gui.IsWindowVisible(h):
                _, wp = win32process.GetWindowThreadProcessId(h)
                if wp == pid:
                    out.add(h)
        except Exception:
            pass
        return True

    win32gui.EnumWindows(cb, None)
    return out


def _cascade_window(hwnds, popup_rect):
    """The one new window that is a real cascade SUBMENU, not a ScreenTip/tooltip. An Office
    submenu cascades to the RIGHT of the parent popup (its left edge sits at/after the parent's
    right edge, within a small overlap) and is a real flyout height; a hover ScreenTip appears
    over/below the hovered item (left edge well inside the parent) — so position alone separates
    them and, unlike UIA content checks, it also accepts owner-drawn submenus (Gradient) whose
    body has no UIA children."""
    for h in sorted(hwnds):
        try:
            l, t, r, b = win32gui.GetWindowRect(h)
        except Exception:
            continue
        if l >= popup_rect[2] - 24 and (r - l) >= 24 and (b - t) >= 24:
            return h
    return None


def _hover_submenus(session, journal, surface_id, popup_rect, sections):
    """A menu item that opens a SUB-flyout is only detectable by HOVER (never click — clicking fires
    terminal 'feature' items). Hover each feature menu item; a new PID top-level window that CASCADES
    to the right (see _cascade_window) => submenu edge. FIX_PLAN B1/#1, generalizes to every tab."""
    from pywinauto import mouse
    # settle: park the mouse on the popup's top edge so the FIRST item hover is a clean transition
    # (otherwise the first candidate — e.g. TextEffects 'Outline' — intermittently misses).
    park = (popup_rect[0] + (popup_rect[2] - popup_rect[0]) // 2, popup_rect[1] + 2)
    try:
        mouse.move(coords=park)
        time.sleep(0.35)
    except Exception:
        pass
    baseline = _pid_tops(session.pid)
    open_prev = False
    for sec in sections:
        if sec.get("kind") != "menu-items":
            continue
        for it in sec["items"]:
            if it.get("action", {}).get("kind") != "feature" or it.get("enabled") is False:
                continue
            b = it.get("bounds")
            if not b:
                continue
            cx = popup_rect[0] + b["x"] + b["w"] // 2
            cy = popup_rect[1] + b["y"] + b["h"] // 2
            try:
                # A stale sub-flyout from the PREVIOUS item makes the window-set delta empty for the
                # next candidate (missed edges: Change List Level, Gradient) — park and wait for the
                # window set to return to baseline, THEN take a fresh per-item snapshot.
                if open_prev:
                    mouse.move(coords=park)
                    for _ in range(10):
                        if _pid_tops(session.pid) <= baseline:
                            break
                        time.sleep(0.12)
                    open_prev = False
                before = _pid_tops(session.pid)
                mouse.move(coords=(cx, cy))
                time.sleep(0.55)
                sub = _cascade_window(_pid_tops(session.pid) - before, popup_rect)
                if sub is None:                      # slow flyouts (list-level previews) render late
                    time.sleep(0.4)
                    sub = _cascade_window(_pid_tops(session.pid) - before, popup_rect)
                if sub is not None:
                    open_prev = True
                    ref = ids.surface_id("dropdowns", surface_id.split("/")[-1] + "-" + it["id"])
                    it["action"] = {"kind": "submenu", "ref": ref}
                    journal.append({"t": "surface-discovered", "surface": ref,
                                    "entry": ids.sub_addr(surface_id, it["id"])})
            except Exception:
                pass
    if open_prev:                                   # collapse any open sub-flyout (hover the top edge)
        try:
            mouse.move(coords=park)
            time.sleep(0.2)
        except Exception:
            pass


def _rgb_of(png, popup_rect, rc):
    cx = (rc[0] + rc[2]) // 2 - popup_rect[0]
    cy = (rc[1] + rc[3]) // 2 - popup_rect[1]
    try:
        return shots.sample_rgb(png, cx, cy)
    except Exception:
        return None


def _assign_grid_pos(items):
    """Give color-grid swatches (col=themeSlot, row=tint) by ranking cell centers."""
    def ranks(vals, tol=5):
        uniq = []
        for v in sorted(set(vals)):
            if not uniq or v - uniq[-1] > tol:
                uniq.append(v)
        return lambda v: min(range(len(uniq)), key=lambda i: abs(uniq[i] - v))
    cx = [it["_cx"] for it in items]
    cy = [it["_cy"] for it in items]
    if not cx:
        return
    xi, yi = ranks(cx), ranks(cy)
    for it in items:
        it["themeSlot"] = xi(it["_cx"])
        it["tint"] = yi(it["_cy"])
        del it["_cx"], it["_cy"]


def _col_centers(img, x0, x1, y, bg):
    """Column centers on scanline y: split on a background gap OR a large color change (handles
    both gapped grids like Highlight and contiguous grids like Theme Colors)."""
    def isbg(p):
        return abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) < 16
    centers, run_start, prev = [], None, None
    for x in range(x0, x1):
        p = img.getpixel((x, y))
        if isbg(p):
            if run_start is not None and x - run_start >= 6:
                centers.append((run_start + x) // 2)
            run_start = None
        else:
            if run_start is None:
                run_start = x
            elif prev is not None and sum(abs(a - b) for a, b in zip(p, prev)) > 45 \
                    and x - run_start >= 6:
                centers.append((run_start + x) // 2)
                run_start = x
        prev = p
    if run_start is not None and (x1 - 1) - run_start >= 6:
        centers.append((run_start + x1 - 1) // 2)
    return centers


def _row_centers(img, y0, y1, x, bg):
    """Row centers on vertical scanline x — the transpose of _col_centers. Used to detect the true
    row count (theme=6, highlight=3, standard=1) instead of guessing from band-height/pitch, which
    over-counted non-square / gapped grids (#3)."""
    def isbg(p):
        return abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) < 16
    centers, run_start, prev = [], None, None
    for y in range(y0, y1):
        p = img.getpixel((x, y))
        if isbg(p):
            if run_start is not None and y - run_start >= 6:
                centers.append((run_start + y) // 2)
            run_start = None
        else:
            if run_start is None:
                run_start = y
            elif prev is not None and sum(abs(a - b) for a, b in zip(p, prev)) > 45 \
                    and y - run_start >= 6:
                centers.append((run_start + y) // 2)
                run_start = y
        prev = p
    if run_start is not None and (y1 - 1) - run_start >= 6:
        centers.append((run_start + y1 - 1) // 2)
    return centers


def _detect_color_grids(png_path, popup_rect, headers, used):
    """Swatches have NO per-cell UIA element (owner-drawn pixels), and header elements span the
    swatch rows (so header.bottom is unreliable). Detect grids from PIXELS: a swatch ROW is a y
    where >=4 evenly-spaced probes are non-background. Cluster rows into bands; detect the column
    centers per band from a representative row (n_cols varies: Theme=10, Highlight=5)."""
    from PIL import Image
    img = Image.open(png_path).convert("RGB")
    pw, ph = img.width, img.height
    x0, x1 = 8, pw - 8
    probes = [int(x0 + (c + 0.5) * (x1 - x0) / 10) for c in range(10)]
    bg = img.getpixel((2, 2))

    def is_bg(p):
        return abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) < 16

    hdr_by_top = sorted(((rc[1] - popup_rect[1], textutil.sanitize_label(nm)) for nm, rc in headers),
                        key=lambda h: h[0])
    color_hdrs = [(top, nm) for top, nm in hdr_by_top if any(h in nm.lower() for h in _COLOR_HEADERS)]
    first_hdr = color_hdrs[0][0] if color_hdrs else 0          # ignore the 'Automatic' bar above it

    rowflag = [y >= first_hdr and
               sum(0 if is_bg(img.getpixel((cx, y))) else 1 for cx in probes) >= 4
               for y in range(ph)]
    bands, y = [], 0
    while y < ph:
        if rowflag[y]:
            start = end = y
            gap = 0
            while y < ph and (rowflag[y] or gap < 4):
                if rowflag[y]:
                    end = y
                    gap = 0
                else:
                    gap += 1
                y += 1
            if end - start >= 4:
                bands.append((start, end))
        else:
            y += 1

    def _title_for(band_start):
        above = [nm for top, nm in color_hdrs if top <= band_start + 4]
        return above[-1] if above else "Colors"

    # merge adjacent bands with the SAME title (the theme grid's main row + tint rows split on the
    # visual gap between them) into one region
    regions = []
    for (bs, be) in bands:
        title = _title_for(bs)
        if regions and regions[-1]["title"] == title:
            regions[-1]["end"] = be
        else:
            regions.append({"start": bs, "end": be, "title": title})

    sections = []
    for reg in regions:
        bs, be, title = reg["start"], reg["end"], reg["title"]
        # detect columns from the densest row in this region
        best_y = max(range(bs, be + 1),
                     key=lambda yy: sum(0 if is_bg(img.getpixel((cx, yy)))
                                        else 1 for cx in probes))
        cols = _col_centers(img, x0, x1, best_y, bg)
        if len(cols) < 2:
            cols = probes
        pitch = (sorted(cols[i + 1] - cols[i] for i in range(len(cols) - 1))[(len(cols) - 1) // 2]
                 if len(cols) > 1 else (x1 - x0) // 10)
        # Rows by vertical transitions (transpose of the column detection): scan every column, take the
        # MEDIAN-length row set (robust to a single noisy column). This is the most stable variant we
        # found — every section is present and Font Color is exact (60+10). Shading/Highlight retain a
        # residual duplicate row/col from their non-standard layouts (swatches carry real RGB); further
        # per-picker CV tuning regressed other pickers, so we stop here and document it (#3).
        row_sets = [rs for rs in (_row_centers(img, bs, be + 1, cx, bg) for cx in cols) if rs]
        rows = sorted(row_sets, key=len)[len(row_sets) // 2] if row_sets else [(bs + be) // 2]
        rpitch = (sorted(rows[i + 1] - rows[i] for i in range(len(rows) - 1))[(len(rows) - 1) // 2]
                  if len(rows) > 1 else (be - bs + 1))
        items = []
        for out_r, cy in enumerate(rows):
            cells = [img.getpixel((cx, cy)) for cx in cols]
            if all(is_bg(p) for p in cells):
                continue
            for c, (cx, (pr, pg, pb)) in enumerate(zip(cols, cells)):
                items.append({"id": _unique_id(f"c{c}-r{out_r}", used),
                              "rgb": f"#{pr:02X}{pg:02X}{pb:02X}", "themeSlot": c, "tint": out_r,
                              "bounds": {"x": cx - int(pitch // 2), "y": cy - int(rpitch // 2),
                                         "w": int(pitch), "h": int(rpitch)},
                              "action": {"kind": "feature"}})
        if items:
            sections.append({"top": bs, "kind": "color-grid", "title": title, "items": items})
    return sections


def _color_popup_sections(png, popup_rect, items, used, journal, surface_id):
    """Color picker: pixel-detected swatch grids + named items ('Automatic', 'More Colors...',
    'Gradient'), ordered top-to-bottom."""
    headers = [(rawname, rc) for ct, rawname, rc, _en in items
               if ct == _HEADER and not textutil.is_chrome(rawname)]
    blocks = _detect_color_grids(png, popup_rect, headers, used)

    for ct, rawname, rc, enabled in items:
        name = textutil.sanitize_label(rawname)
        if ct == _HEADER or textutil.is_chrome(rawname) or not name:
            continue
        if ct not in _MENU_CTS and ct not in _GALLERY_CTS:
            continue
        action, discovered = _popup_action(name)
        itid = _unique_id(name, used)
        if discovered:
            journal.append({"t": "surface-discovered", "surface": action["ref"],
                            "entry": ids.sub_addr(surface_id, itid)})
        it = {"id": itid, "label": name, "action": action,
              "bounds": shots.rel_bounds(rc, popup_rect)}
        if not enabled:
            it["enabled"] = False
        blocks.append({"top": rc[1] - popup_rect[1], "kind": "menu-items", "items": [it]})

    blocks.sort(key=lambda b: b["top"])
    # merge adjacent menu-items blocks
    sections = []
    for b in blocks:
        b = {k: v for k, v in b.items() if k != "top"}
        if b["kind"] == "menu-items" and sections and sections[-1]["kind"] == "menu-items":
            sections[-1]["items"].extend(b["items"])
        else:
            sections.append(b)
    return sections


def _crop_preview(png, popup_rect, rc, run_dir, surface_id, itid):
    rb = shots.rel_bounds(rc, popup_rect)
    if rb["w"] < 4 or rb["h"] < 4:
        return None
    pv = run_dir / ("icon__" + surface_id.replace("/", "__") + "__" + itid + ".png")
    try:
        shots.crop_from(png, (rb["x"], rb["y"], rb["x"] + rb["w"], rb["y"] + rb["h"]), pv)
        if shots.quality_ok(pv):
            return pv.name
    except Exception:
        pass
    return None


def _merge_orphan_headers(sections):
    """Re-attach a gallery header to its content. A blank/chrome pseudo-header between a real header
    ('Theme Fonts') and its tiles resets `cur`, leaving a titled EMPTY gallery section followed by
    untitled single-item gallery sections holding its actual items. A titled gallery section that
    started empty absorbs consecutive following UNTITLED gallery sections."""
    out = []
    for s in sections:
        prev = out[-1] if out else None
        if (prev is not None and s.get("kind") == "gallery" and not s.get("title")
                and prev.get("kind") == "gallery" and prev.get("title")
                and prev.get("_absorb", not prev["items"])):
            prev["_absorb"] = True
            prev["items"].extend(s["items"])
            continue
        out.append(s)
    for s in out:
        s.pop("_absorb", None)
    return out


def capture_popup(session, journal, run_dir, surface_id, popup_rect, detect_submenus=True):
    png = run_dir / (surface_id.replace("/", "__") + ".png")
    try:
        shots.grab(popup_rect, png)
    except Exception:
        pass
    items = _sample_popup(popup_rect)
    # 'font' is a scrollable owner-drawn list of the machine's INSTALLED fonts (ElementFromPoint sees
    # only the visible window) -> mark dynamic: the capture is an honest sample, not a false-complete
    # enumeration (#5). ('font' tail only, not fontcolor/fontsize.)
    tail = surface_id.rsplit("/", 1)[-1]
    dynamic = any(h in surface_id.lower() for h in _DYNAMIC_HINTS) or tail == "font"
    is_color = "color" in surface_id.lower()

    if is_color:
        sections = _color_popup_sections(png, popup_rect, items, set(), journal, surface_id)
        # color popups need submenu detection too — the early return skipped it, so fontcolorpicker's
        # 'Gradient' (a hover-only sub-gallery) was typed as a leaf feature.
        if detect_submenus:
            _hover_submenus(session, journal, surface_id, popup_rect, sections)
        payload = {"id": surface_id, "schema_version": 1,
                   "screenshot": str(png.name), "sections": sections}
        errs = schemas.validate_popup(payload)
        if errs:
            raise ValueError(f"invalid popup {surface_id}: {errs}")
        journal.append({"t": "surface-captured", "surface": surface_id, "payload": payload})
        return payload

    sections, used, cur = [], set(), None

    def _new(kind, title=None):
        s = {"kind": kind, "items": []}
        if title:
            s["title"] = title
        if dynamic:
            s["dynamic"] = True
        sections.append(s)
        return s

    for ct, rawname, rc, enabled in items:
        name = textutil.sanitize_label(rawname)
        if ct == _HEADER:
            if textutil.is_chrome(rawname):
                cur = None
                continue
            low = name.lower()
            kind = "color-grid" if (is_color and any(h in low for h in _COLOR_HEADERS)) else "gallery"
            cur = _new(kind, title=name)
            continue

        if ct in _GALLERY_CTS:
            # a color picker's BLANK-name cell is a swatch; a NAMED cell (Automatic, No Color) is a
            # normal feature item.
            if is_color and not name:
                if cur is None or cur["kind"] != "color-grid":
                    cur = _new("color-grid")
                item = {"id": _unique_id("swatch", used), "rgb": _rgb_of(png, popup_rect, rc),
                        "bounds": shots.rel_bounds(rc, popup_rect), "action": {"kind": "feature"},
                        "_cx": (rc[0] + rc[2]) // 2, "_cy": (rc[1] + rc[3]) // 2}
                cur["items"].append(item)
            else:
                if cur is None or cur["kind"] not in ("gallery",):
                    cur = _new("gallery")
                itid = _unique_id(name or "tile", used)
                # a gallery can hold an ellipsis LEAF that opens a dialog ("Line Spacing Options…"
                # lives in the Line Spacing gallery, not a menu) — classify it like a menu item.
                action, discovered = _popup_action(name)
                if discovered:
                    journal.append({"t": "surface-discovered", "surface": action["ref"],
                                    "entry": ids.sub_addr(surface_id, itid)})
                item = {"id": itid, "label": name, "action": action,
                        "bounds": shots.rel_bounds(rc, popup_rect)}
                if not enabled:
                    item["enabled"] = False
                pv = _crop_preview(png, popup_rect, rc, run_dir, surface_id, itid)
                if pv:
                    item["preview"] = pv
                cur["items"].append(item)

        elif ct in _MENU_CTS:
            if textutil.is_chrome(rawname):
                continue
            if cur is None or cur["kind"] != "menu-items":
                cur = _new("menu-items")
            action, discovered = _popup_action(name)
            itid = _unique_id(name, used)
            if discovered:
                journal.append({"t": "surface-discovered", "surface": action["ref"],
                                "entry": ids.sub_addr(surface_id, itid)})   # E1: real item id
            it = {"id": itid, "label": name, "action": action,
                  "bounds": shots.rel_bounds(rc, popup_rect)}
            if not enabled:
                it["enabled"] = False
            cur["items"].append(it)

    sections = _merge_orphan_headers(sections)      # re-attach split-off gallery headers (font popup)
    for s in sections:
        if s["kind"] == "color-grid":
            _assign_grid_pos(s["items"])

    if detect_submenus:
        _hover_submenus(session, journal, surface_id, popup_rect, sections)   # #1 submenu edges

    payload = {"id": surface_id, "schema_version": 1,
               "screenshot": str(png.name), "sections": sections}
    if dynamic:
        payload["dynamic"] = True
    errs = schemas.validate_popup(payload)
    if errs:
        raise ValueError(f"invalid popup {surface_id}: {errs}")
    journal.append({"t": "surface-captured", "surface": surface_id, "payload": payload})
    return payload


# ---- dialog capture (standard UIA descendants) ----

_FIELD_TYPE = {"Edit": "text", "ComboBox": "combo", "List": "listbox",
               "CheckBox": "checkbox", "RadioButton": "radio", "Slider": "slider",
               "Spinner": "spinner"}
_SCROLL_AIDS = {"UpButton", "DownButton", "DownPageButton", "UpPageButton", "ScrollbarThumb"}


def _labeled_by_name(raw):
    """UIA LabeledBy -> the label element's Name (strongest field-identity signal)."""
    try:
        lb = raw.GetCurrentPropertyValue(_UIA_LABELEDBY)
        if lb:
            return lb.CurrentName or ""
    except Exception:
        pass
    return ""


def _nearest_label(rect, labels):
    """Geometry fallback: nearest label to the LEFT on the same row, else directly above."""
    l, t, r, b = rect
    cy = (t + b) // 2
    same_row = [(lt, ln) for (lr, ln) in labels
                for lt in [lr] if lt[1] <= cy <= lt[3] and lt[2] <= l + 8]
    if same_row:
        return max(same_row, key=lambda x: x[0][2])[1]     # closest from the left
    above = [(lr, ln) for (lr, ln) in labels if lr[3] <= t + 4 and lr[0] <= r and lr[2] >= l]
    if above:
        return max(above, key=lambda x: x[0][3])[1]         # closest above
    return ""


def _field_section(w):
    p = w
    for _ in range(6):
        try:
            p = p.parent()
        except Exception:
            break
        if p is None:
            break
        ei = p.element_info
        if ei.control_type == "Group" and (ei.name or "").strip():
            return textutil.sanitize_label(ei.name)
    return ""


def _dedup_fields(fs):
    """Drop nested/duplicate fields: descendants() surfaces both a ComboBox and its INNER Edit with
    the same label ('Style Name:' twice in Apply Styles). When two same-named fields nest, keep the
    OUTER control; exact duplicates keep the first."""
    def _contains(a, b):
        return (a["x"] <= b["x"] and a["y"] <= b["y"]
                and a["x"] + a["w"] >= b["x"] + b["w"] and a["y"] + a["h"] >= b["y"] + b["h"])
    out = []
    for f in fs:
        dup = False
        if f["name"]:
            for i, g in enumerate(out):
                if g["name"] != f["name"]:
                    continue
                if _contains(g["bounds"], f["bounds"]):
                    dup = True
                    break
                if _contains(f["bounds"], g["bounds"]):
                    out[i] = f
                    dup = True
                    break
        if not dup:
            out.append(f)
    return out


def _page_fields(dlg):
    labels = []
    try:
        for tw in dlg.descendants(control_type="Text"):
            ei = tw.element_info
            nm = textutil.sanitize_label(ei.name)
            if nm:
                r = ei.rectangle
                labels.append(((r.left, r.top, r.right, r.bottom), nm))
    except Exception:
        pass

    by_section = {}
    for w in dlg.descendants():
        ei = w.element_info
        ct = ei.control_type
        if ct not in _FIELD_TYPE or ei.automation_id in _SCROLL_AIDS:
            continue
        r = ei.rectangle
        rect = (r.left, r.top, r.right, r.bottom)
        raw_name = ei.name or ""
        name = textutil.sanitize_label(raw_name)
        if name.lower() in _GENERIC_NAMES:
            name = (textutil.sanitize_label(_labeled_by_name(ei.element))
                    or _nearest_label(rect, labels))
        f = {"name": name, "type": _FIELD_TYPE[ct],
             "bounds": {"x": r.left, "y": r.top, "w": r.right - r.left, "h": r.bottom - r.top}}
        if ct == "List":
            try:
                kids = w.children()
                f["itemsSampled"] = [textutil.sanitize_label(k.element_info.name)
                                     for k in kids[:12] if k.element_info.name]
                if len(kids) > 30:
                    f["dynamic"] = True
            except Exception:
                pass
        by_section.setdefault(_field_section(w), []).append(f)

    return [{"title": title, "fields": _dedup_fields(fs)} for title, fs in by_section.items()]


def _button_action(name, parent_stem):
    """Dialog button name -> (action, role). A '…' button opens a CHILD dialog whose id is SCOPED by
    the parent stem: same-named buttons on different dialogs (Sort's 'Options...' and Borders &
    Shading's 'Options...') must NOT alias to one global id — the collision captured only Sort
    Options and mispointed the other. A genuinely-shared dialog captured twice under two scoped ids
    is re-merged by the emitter's structural dedup, so scoping cannot over-split the final output."""
    low = name.lower()
    if low == "ok":
        return {"kind": "feature"}, "default"
    if low in ("cancel", "close"):
        return {"kind": "feature"}, "cancel"
    if name.endswith("...") or name.endswith("…"):
        return {"kind": "opens-dialog",
                "ref": ids.surface_id("dialogs", f"{parent_stem} {name}")}, None
    return {"kind": "feature"}, None


def _tab_buttons(dlg, parent_stem):
    """Buttons visible on the CURRENTLY-ACTIVE tab (call inside the tab loop)."""
    out, seen = [], set()
    try:
        bwraps = dlg.descendants(control_type="Button")
    except Exception:
        bwraps = []
    for bwrap in bwraps:
        ei = bwrap.element_info
        name = textutil.sanitize_label(ei.name)
        if not name or ei.automation_id in _SCROLL_AIDS or name in ("Line up", "Line down",
                                                                    "Context help"):
            continue
        if name in seen:
            continue
        seen.add(name)
        action, role = _button_action(name, parent_stem)
        btn = {"name": name, "action": action}
        if role:
            btn["role"] = role
        try:
            if not ei.enabled:          # a disabled '...' button must never be pressed by the drain
                btn["enabled"] = False
        except Exception:
            pass
        out.append(btn)
    return out


def _expand_more(dlg):
    """Click a 'More >>' expander (Find & Replace) so its options panel joins the UIA tree."""
    try:
        for b in dlg.descendants(control_type="Button"):
            nm = textutil.sanitize_label(b.element_info.name).lower().replace(">", "").strip()
            if nm == "more" or (nm.startswith("more") and "less" not in nm):
                b.click_input()
                time.sleep(0.5)
                return True
    except Exception:
        pass
    return False


_EXPANDER_TYPES = {"Button", "Group"}


def _expand_groups(session, dlg):
    """Format Text Effects-style dialogs hide their controls behind ExpandCollapse groups (Text
    Fill, Text Outline, Shadow, Reflection…) — expand each collapsed one so its fields join the UIA
    tree. ComboBox/SplitButton also expose ExpandCollapse but expanding them opens their POPUP, so
    only Button/Group are candidates, and any expansion that spawned a new top-level window (a
    dropdown-button like Find & Replace's 'Format') is ESCed and left alone."""
    from pywinauto.keyboard import send_keys
    n = 0
    try:
        for w in dlg.descendants():
            if w.element_info.control_type not in _EXPANDER_TYPES:
                continue
            try:
                ec = w.iface_expand_collapse            # pattern CALLS raise when unsupported
                if ec.CurrentExpandCollapseState != 0:  # 0 = collapsed
                    continue
                before = _pid_tops(session.pid)
                ec.Expand()
                time.sleep(0.3)
                if _pid_tops(session.pid) - before:     # it was a dropdown, not an expander panel
                    send_keys("{ESC}")
                    time.sleep(0.25)
                    continue
                n += 1
            except Exception:
                continue
            if n >= 12:
                break
    except Exception:
        pass
    return n


def capture_dialog(session, journal, run_dir, surface_id, dialog_hwnd):
    dlg = Desktop(backend="uia").window(handle=dialog_hwnd)
    stem = surface_id.split("/", 1)[1]                  # scopes child-dialog ids (same-name collision)
    title = ""
    try:
        title = textutil.sanitize_label(dlg.element_info.name)
    except Exception:
        pass
    _expand_more(dlg)                                   # B1: expand before enumerating
    _expand_groups(session, dlg)                        # Format Text Effects-style expander panels
    try:
        tab_items = dlg.descendants(control_type="TabItem")
    except Exception:
        tab_items = []

    tabs, all_buttons, seen_btn = [], [], set()

    def _add_buttons(bs):
        for b in bs:
            if b["name"] not in seen_btn:
                seen_btn.add(b["name"])
                all_buttons.append(b)

    if not tab_items:
        r = dlg.element_info.rectangle
        png = run_dir / (surface_id.replace("/", "__") + ".png")
        try:
            shots.grab((r.left, r.top, r.right, r.bottom), png)
        except Exception:
            pass
        btns = _tab_buttons(dlg, stem)
        _add_buttons(btns)
        tabs.append({"name": title or "Main", "screenshot": png.name,
                     "sections": _page_fields(dlg), "buttons": btns})
    else:
        for ti in tab_items:
            tname = textutil.sanitize_label(ti.element_info.name) or "tab"
            try:
                ti.click_input()
            except Exception:
                pass
            time.sleep(0.5)
            _expand_more(dlg)
            _expand_groups(session, dlg)
            r = dlg.element_info.rectangle
            png = run_dir / (surface_id.replace("/", "__") + "@" + ids.slugify(tname) + ".png")
            try:
                shots.grab((r.left, r.top, r.right, r.bottom), png)
            except Exception:
                pass
            btns = _tab_buttons(dlg, stem)              # B2: per-tab, no cross-tab shadowing
            _add_buttons(btns)
            tabs.append({"name": tname, "screenshot": png.name,
                         "sections": _page_fields(dlg), "buttons": btns})

    payload = {"id": surface_id, "title": title, "modal": True, "schema_version": 1,
               "tabs": tabs, "buttons": all_buttons}
    for b in payload["buttons"]:
        if b.get("action", {}).get("kind") == "opens-dialog":
            journal.append({"t": "surface-discovered", "surface": b["action"]["ref"],
                            "entry": ids.sub_addr(surface_id, "btn:" + ids.slugify(b["name"]))})
    errs = schemas.validate_dialog(payload)
    if errs:
        raise ValueError(f"invalid dialog {surface_id}: {errs}")
    journal.append({"t": "surface-captured", "surface": surface_id, "payload": payload})
    return payload


# ---- pane capture (task panes expose a real UIA tree, unlike ribbon flyouts) ----

_PANE_TYPE = {"Button": "button", "ComboBox": "combo", "Edit": "text-input",
              "CheckBox": "checkbox", "RadioButton": "radio", "MenuItem": "menu",
              "List": "listbox", "ListItem": "listitem", "Hyperlink": "button",
              "Tab": "label", "TabItem": "label"}
# ListItem is included because task-pane content (Styles pane's style entries: Normal, Heading 1,
# Title…) is exposed as ListItems, not Buttons — omitting it dropped the pane's main content (#4).
_PANE_INTER = set(_PANE_TYPE)


def _inside(r, box, pad=3):
    return box[0] - pad <= r[0] and r[2] <= box[2] + pad and box[1] - pad <= r[1] and r[3] <= box[3] + pad


def _drop_occluded_bounds(controls):
    """A pane's footer controls (Styles pane's 'Show Preview' / 'Disable Linked Styles') are painted
    ON TOP of the last list rows, so those clipped rows report on-screen bounds that collide with the
    footer — untrustworthy geometry. When a listitem's bounds overlap a non-listitem control's bounds
    by >40%, drop the listitem's bounds (same as a scrolled-in row) and flag it occluded."""
    def ov(a, b):
        ix = max(0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]))
        iy = max(0, min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]))
        area = a["w"] * a["h"]
        return area > 0 and ix * iy > 0.4 * area
    others = [c["bounds"] for c in controls if c.get("type") != "listitem" and "bounds" in c]
    for c in controls:
        if c.get("type") == "listitem" and "bounds" in c and any(ov(c["bounds"], o) for o in others):
            c.pop("bounds")
            c["occluded"] = True


def _find_pane(win, frame):
    """The task pane containing a 'Close pane' button. A Word task pane is NARROW (<520px) and lives
    INSIDE the frame, so we reject the giant desktop/shell Pane that a naive ancestor-walk would grab
    (which leaked the Windows taskbar/notifications into the first pane capture)."""
    try:
        btns = win.descendants(control_type="Button")
    except Exception:
        btns = []
    for b in btns:
        if "close pane" not in (b.element_info.name or "").lower():
            continue
        br = b.element_info.rectangle
        if not _inside((br.left, br.top, br.right, br.bottom), frame):
            continue
        p = b
        for _ in range(6):
            try:
                p = p.parent()
            except Exception:
                break
            if p is None:
                break
            if p.element_info.control_type == "Pane":
                r = p.element_info.rectangle
                w, h = r.right - r.left, r.bottom - r.top
                if 120 < w < 520 and h > 200 and _inside((r.left, r.top, r.right, r.bottom), frame):
                    return p
    return None


def capture_pane(session, journal, run_dir, surface_id, win, pane_hwnd=None):
    """Task panes expose a real UIA tree. DOCKED panes (Clipboard) live inside the frame; FLOATING
    panes (Styles) are a separate top-level MsoCommandBar window (pass its hwnd)."""
    if pane_hwnd:
        pane = Desktop(backend="uia").window(handle=pane_hwnd)
        wr = win32gui.GetWindowRect(pane_hwnd)
        prect = (wr[0], wr[1], wr[2], wr[3])
    else:
        fr = win32gui.GetWindowRect(session._hwnd())
        pane = _find_pane(win, fr)
        if pane is None:
            raise ValueError(f"pane not found for {surface_id}")
        r = pane.element_info.rectangle
        prect = (r.left, r.top, r.right, r.bottom)
    png = run_dir / (surface_id.replace("/", "__") + ".png")
    try:
        shots.grab(prect, png)
    except Exception:
        pass
    controls, used, seen_keys = [], set(), set()

    def _collect(scrolled=False):
        """One enumeration round; returns how many NEW controls it added. Identity is (name, type) —
        after scrolling the same item reports a NEW rect, so the rect can't be part of the key.
        Post-scroll items carry NO bounds: the pane screenshot was grabbed before scrolling, so
        their on-screen rect maps to the WRONG screenshot pixels (bounds must stay a rect inside
        the owning screenshot, DESIGN D10) — they're flagged `scrolled` instead."""
        added = 0
        try:
            descs = pane.descendants()
        except Exception:
            descs = []
        for w in descs:
            ei = w.element_info
            if ei.control_type not in _PANE_INTER:
                continue
            nm = textutil.sanitize_label(ei.name)
            if not nm:
                # icon-only buttons (Styles pane's New Style / Style Inspector / Manage Styles) have
                # an EMPTY UIA Name — their label lives in FullDescription (30159), same as ribbon
                # controls (#6). Fall back to it, then AutomationId, so they aren't silently dropped.
                try:
                    nm = textutil.sanitize_label(ei.element.GetCurrentPropertyValue(30159))
                except Exception:
                    nm = ""
                if not nm and ei.automation_id:
                    nm = ei.automation_id
            if not nm or "close pane" in nm.lower():
                continue
            rr = (ei.rectangle.left, ei.rectangle.top, ei.rectangle.right, ei.rectangle.bottom)
            if not _inside(rr, prect):                    # reject anything outside the pane rect
                continue
            key = (nm, ei.control_type)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            c = {"id": _unique_id(nm, used), "label": nm, "type": _PANE_TYPE[ei.control_type]}
            if scrolled:
                c["scrolled"] = True
            else:
                c["bounds"] = shots.rel_bounds(rr, prect)
            controls.append(c)
            added += 1
            if len(controls) >= 160:
                break
        return added

    _collect()
    # SCROLL-DRAIN: a long pane list (the Styles pane's style entries) only exposes its VISIBLE
    # ListItems — the first capture truncated at 8 styles. Wheel-scroll the list and re-collect
    # until a round adds nothing new (or the cap/round limit stops a runaway).
    try:
        lists = [w for w in pane.descendants() if w.element_info.control_type == "List"]
    except Exception:
        lists = []
    if lists and len(controls) < 160:
        from pywinauto import mouse
        r = lists[0].element_info.rectangle
        cx, cy = (r.left + r.right) // 2, (r.top + r.bottom) // 2
        for _ in range(12):
            try:
                mouse.scroll(coords=(cx, cy), wheel_dist=-3)
            except Exception:
                break
            time.sleep(0.25)
            if _collect(scrolled=True) == 0 or len(controls) >= 160:
                break
    _drop_occluded_bounds(controls)
    payload = {"id": surface_id, "schema_version": 1, "screenshot": png.name,
               "docked": True, "sections": [{"kind": "controls", "items": controls}]}
    journal.append({"t": "surface-captured", "surface": surface_id, "payload": payload})
    return payload
