"""First-level popup / dialog capture (DESIGN section 4.3-4.4, 6.4).

KEY LIVE FINDING (Word 16.0.20131): ribbon flyouts (menus, galleries, color grids) are
owner-drawn -- their items are NOT reachable by UIA tree-walk (control OR raw view returns
only the empty top container). They ARE recoverable via IUIAutomation.ElementFromPoint
hit-testing across the popup rect. Modal dialogs, by contrast, expose a full UIA descendant
tree. So popups are captured by point-sampling; dialogs by descendants().

These functions capture an ALREADY-OPEN surface (they do not open or close it) so the caller
(prober visit / T12 orchestrator) controls the surface lifecycle -- flyouts die on focus loss.
"""
import ids, schemas, shots
from pywinauto import Desktop
from pywinauto.uia_defines import IUIA

# UIA control-type ids (owner-drawn flyout items report these).
_HEADER, _IMAGE, _LISTITEM = 50026, 50007, 50008
_MENUBAR, _MENUITEM, _BUTTON, _TEXT, _PANE = 50011, 50012, 50000, 50023, 50024
_GALLERY_CTS = {_IMAGE, _LISTITEM}
_MENU_CTS = {_MENUBAR, _MENUITEM, _BUTTON}
_DYNAMIC_HINTS = ("styles", "recently", "recent")


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
    """Grid ElementFromPoint over the popup; dedupe by (ct, name); return items ordered
    top-to-bottom, left-to-right with real bounding rects."""
    iuia = IUIA().iuia
    from ctypes.wintypes import POINT
    l, t, r, b = popup_rect
    seen = {}
    y = t + 5
    while y < b - 3:
        x = l + 8
        while x < r - 8:
            try:
                el = iuia.ElementFromPoint(POINT(x, y))
                ct = el.CurrentControlType
                name = el.CurrentName or ""
                key = (ct, name)
                if key not in seen and ct not in (_PANE,) and (name or ct in _GALLERY_CTS):
                    seen[key] = (ct, name, _rect(el))
            except Exception:
                pass
            x += 24
        y += 7
    items = list(seen.values())
    items.sort(key=lambda it: (it[2][1], it[2][0]))     # (top, left)
    return items


def _popup_action(name):
    n = (name or "").strip()
    if n.endswith("..."):
        return {"kind": "opens-dialog", "ref": ids.surface_id("dialogs", n.rstrip(". "))}, True
    return {"kind": "feature"}, False


def capture_popup(session, journal, run_dir, surface_id, popup_rect):
    png = run_dir / (surface_id.replace("/", "__") + ".png")
    try:
        shots.grab(popup_rect, png)
    except Exception:
        pass
    items = _sample_popup(popup_rect)
    dynamic = any(h in surface_id.lower() for h in _DYNAMIC_HINTS)

    sections, used, cur = [], set(), None

    def _new(kind, title=None):
        s = {"kind": kind, "items": []}
        if title:
            s["title"] = title
        if dynamic:
            s["dynamic"] = True
        sections.append(s)
        return s

    for ct, name, rect in items:
        if ct == _HEADER:
            cur = _new("gallery", title=name)
            continue
        if ct in _GALLERY_CTS:
            if cur is None or cur["kind"] != "gallery":
                cur = _new("gallery")
            item = {"id": _unique_id(name or "tile", used), "label": name,
                    "action": {"kind": "feature"},
                    "bounds": shots.rel_bounds(rect, popup_rect)}
            cur["items"].append(item)
        elif ct in _MENU_CTS and name:
            if cur is None or cur["kind"] != "menu-items":
                cur = _new("menu-items")
            action, discovered = _popup_action(name)
            if discovered:
                journal.append({"t": "surface-discovered", "surface": action["ref"],
                                "entry": ids.sub_addr(surface_id, "")})
            cur["items"].append({"id": _unique_id(name, used), "label": name,
                                 "action": action, "bounds": shots.rel_bounds(rect, popup_rect)})

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
               "CheckBox": "checkbox", "RadioButton": "radio", "Slider": "slider"}
_SCROLL_AIDS = {"UpButton", "DownButton", "DownPageButton", "UpPageButton", "ScrollbarThumb"}


def _dialog_buttons(dlg):
    buttons = []
    for bwrap in dlg.descendants(control_type="Button"):
        ei = bwrap.element_info
        name = (ei.name or "").strip()
        if not name or ei.automation_id in _SCROLL_AIDS or name in ("Line up", "Line down"):
            continue
        if name in ("Context help",):
            continue
        low = name.lower()
        if low == "ok":
            action = {"kind": "feature"}
            buttons.append({"name": name, "role": "default", "action": action})
        elif low in ("cancel", "close"):
            buttons.append({"name": name, "role": "cancel", "action": {"kind": "feature"}})
        elif name.endswith("..."):
            action = {"kind": "opens-dialog", "ref": ids.surface_id("dialogs", name.rstrip(". "))}
            buttons.append({"name": name, "action": action})
        else:
            buttons.append({"name": name, "action": {"kind": "feature"}})
    # dedupe by name preserving order
    out, seen = [], set()
    for b in buttons:
        if b["name"] in seen:
            continue
        seen.add(b["name"])
        out.append(b)
    return out


def _page_fields(dlg):
    fields = []
    for w in dlg.descendants():
        ei = w.element_info
        ct = ei.control_type
        if ct not in _FIELD_TYPE:
            continue
        if ei.automation_id in _SCROLL_AIDS:
            continue
        name = ei.name or ""
        r = ei.rectangle
        f = {"name": name, "type": _FIELD_TYPE[ct],
             "bounds": {"x": r.left, "y": r.top, "w": r.right - r.left, "h": r.bottom - r.top}}
        if ct == "List":
            try:
                kids = w.children()
                f["itemsSampled"] = [k.element_info.name for k in kids[:12] if k.element_info.name]
                if len(kids) > 30:
                    f["dynamic"] = True
            except Exception:
                pass
        fields.append(f)
    return fields


def capture_dialog(session, journal, run_dir, surface_id, dialog_hwnd):
    dlg = Desktop(backend="uia").window(handle=dialog_hwnd)
    title = ""
    try:
        title = dlg.element_info.name or ""
    except Exception:
        pass
    try:
        tab_items = dlg.descendants(control_type="TabItem")
    except Exception:
        tab_items = []

    tabs = []
    if not tab_items:
        r = dlg.element_info.rectangle
        png = run_dir / (surface_id.replace("/", "__") + ".png")
        try:
            shots.grab((r.left, r.top, r.right, r.bottom), png)
        except Exception:
            pass
        tabs.append({"name": title or "Main", "screenshot": png.name,
                     "sections": [{"title": "", "fields": _page_fields(dlg)}]})
    else:
        for ti in tab_items:
            tname = ti.element_info.name or "tab"
            try:
                ti.click_input()
            except Exception:
                pass
            import time
            time.sleep(0.5)
            r = dlg.element_info.rectangle
            png = run_dir / (surface_id.replace("/", "__") + "@" + ids.slugify(tname) + ".png")
            try:
                shots.grab((r.left, r.top, r.right, r.bottom), png)
            except Exception:
                pass
            tabs.append({"name": tname, "screenshot": png.name,
                         "sections": [{"title": "", "fields": _page_fields(dlg)}]})

    payload = {"id": surface_id, "title": title, "modal": True, "schema_version": 1,
               "tabs": tabs, "buttons": _dialog_buttons(dlg)}
    for b in payload["buttons"]:
        if b.get("action", {}).get("kind") == "opens-dialog":
            journal.append({"t": "surface-discovered", "surface": b["action"]["ref"],
                            "entry": ids.sub_addr(surface_id, "btn:" + ids.slugify(b["name"]))})
    errs = schemas.validate_dialog(payload)
    if errs:
        raise ValueError(f"invalid dialog {surface_id}: {errs}")
    journal.append({"t": "surface-captured", "surface": surface_id, "payload": payload})
    return payload
