"""depth_capture — perception primitives for Step 5 (entering stub surfaces).

Two hard cases (toolbox/uia.md, pixel.md):
  * DIALOGS expose a full UIA tree — walk descendants per TabItem; identify anonymous fields by
    LabeledBy (30003) then nearest-label geometry (same row left, else above).
  * FLYOUTS/menus/color pickers are owner-drawn — the tree walk returns an empty container, so
    items are recovered by ElementFromPoint grid sampling (menu items by NAME, swatch cells by
    rounded GEOMETRY) plus pixel RGB from the screenshot.
Read-only perception: this enumerates and screenshots; it does not press option controls (that
would apply formatting). Sub-surface recursion (a '...' button that opens another dialog) is
driven by the Step 5 orchestrator, which presses only measured openers.
"""
import sys
import time
from pathlib import Path

import win32gui

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import uia_attach as ua
import capture as cap

_LABELED_BY = 30003
_INTERACTIVE = {"Button", "SplitButton", "CheckBox", "RadioButton", "ComboBox", "Edit",
                "MenuItem", "ListItem", "Slider", "Spinner", "TabItem", "Hyperlink"}


def _rect(el):
    r = el.element_info.rectangle
    return (r.left, r.top, r.right, r.bottom)


def _nearest_label(field_rect, labels):
    """Nearest Text label to an anonymous field: same row to the left, else directly above.
    labels = list of (x, y_top, y_bottom, text)."""
    fl, ft, fr, fb = field_rect
    fcy = (ft + fb) // 2
    best, best_d = None, 1e9
    for (lx, lt, lb, ltext) in labels:                    # same row, to the left
        lcy = (lt + lb) // 2
        if abs(lcy - fcy) < 12 and lx < fl:
            d = fl - lx
            if d < best_d:
                best, best_d = ltext, d
    if best:
        return best
    best, best_d = None, 1e9
    for (lx, lt, lb, ltext) in labels:                    # else nearest above
        if lb <= ft + 4 and abs(lx - fl) < 160:
            d = ft - lb
            if 0 <= d < best_d:
                best, best_d = ltext, d
    return best


def _collect_labels(container):
    labels = []
    try:
        for el in container.descendants(control_type="Text"):
            t = (el.element_info.name or "").strip()
            if t:
                x, y0, x1, y1 = _rect(el)
                labels.append((x, y0, y1, t))
    except Exception:
        pass
    return labels


def _control_label(el, labels):
    ei = el.element_info
    name = (ei.name or "").strip()
    if name:
        return name
    raw = ei.element
    try:
        lb = raw.GetCurrentPropertyValue(_LABELED_BY)
        if lb:
            nm = (lb.CurrentName or "").strip()
            if nm:
                return nm
    except Exception:
        pass
    nl = _nearest_label(_rect(el), labels)
    if nl:
        return nl
    try:
        fd = raw.GetCurrentPropertyValue(ua._FULL_DESCRIPTION)
        if fd:
            return str(fd)
    except Exception:
        pass
    return ei.automation_id or "(unlabeled)"


def dialog_tabs(dlg):
    try:
        tabs = [t for t in dlg.descendants(control_type="TabItem")]
        return tabs
    except Exception:
        return []


def enumerate_dialog(hwnd, writer, node_slug):
    """Enumerate a dialog window: per-tab controls (labelled) + per-tab screenshots.
    Returns {tabs: [{tab, screenshot, controls:[...]}], combobox_values:{...}}."""
    from pywinauto import Desktop
    dlg = Desktop(backend="uia").window(handle=hwnd)
    out = {"tabs": [], "title": win32gui.GetWindowText(hwnd)}
    tabs = dialog_tabs(dlg)
    tab_names = [t.element_info.name for t in tabs] or ["(single)"]

    for i, tname in enumerate(tab_names):
        if tabs:
            try:
                tabs[i].click_input()
                time.sleep(0.3)
                # re-fetch after tab switch
                dlg = Desktop(backend="uia").window(handle=hwnd)
            except Exception:
                pass
        labels = _collect_labels(dlg)
        controls = []
        try:
            for el in dlg.descendants():
                ct = el.element_info.control_type
                if ct not in _INTERACTIVE:
                    continue
                if ct == "TabItem":
                    continue
                r = _rect(el)
                if r[2] <= r[0] or r[3] <= r[1]:
                    continue
                p = ua.read_props(el)
                controls.append({
                    "control_type": ct.lower(), "label": _control_label(el, labels),
                    "automation_id": p.automation_id, "bounds": list(r),
                    "enabled": p.is_enabled, "patterns": p.patterns,
                    "tooltip": p.tooltip or None, "shortcut": p.accelerator_key or None,
                })
        except Exception:
            pass
        # dedupe by (label, bounds)
        seen, uniq = set(), []
        for c in controls:
            k = (c["label"], tuple(c["bounds"]))
            if k in seen:
                continue
            seen.add(k)
            uniq.append(c)
        # per-tab screenshot (window-true)
        img, rect = cap.grab_window(hwnd)
        safe_tab = "".join(ch if ch.isalnum() else "-" for ch in tname).strip("-").lower() or "main"
        shot = writer.save_screenshot(img, f"ui:{node_slug}", f"tab-{safe_tab}")
        out["tabs"].append({"tab": tname, "screenshot": shot, "controls": uniq,
                            "control_count": len(uniq)})
    return out


def enumerate_flyout(iuia, hwnd):
    """ElementFromPoint grid-sample an owner-drawn flyout. Returns items (named commands),
    sections (named Group headers), and swatches (anonymous painted cells, keyed by geometry).
    NOTE: the POINT MUST be ctypes.wintypes.POINT — a hand-rolled ctypes.Structure fails to
    marshal into IUIAutomation.ElementFromPoint and every call silently raises (0 items bug)."""
    from ctypes.wintypes import POINT
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    items, sections, swatches = {}, set(), {}
    y = t + 4
    while y < b - 3:
        x = l + 5
        while x < r - 5:
            try:
                el = iuia.ElementFromPoint(POINT(x, y))
                ct = el.CurrentControlType
                name = (el.CurrentName or "").strip()
                rc = el.CurrentBoundingRectangle
                rect = (rc.left, rc.top, rc.right, rc.bottom)
                if ct in (50033, 50020, 50032):            # Pane / Text / Window container -> skip
                    pass
                elif name:
                    if ct == 50026:                        # a NAMED Group is a section header
                        sections.add(name)
                    elif name not in items:
                        items[name] = {"control_type": _ct_name(ct), "label": name,
                                       "bounds": list(rect), "enabled": bool(el.CurrentIsEnabled)}
                else:                                       # anonymous painted cell -> swatch
                    if rect[2] > rect[0] and rect[3] > rect[1]:
                        gk = (round(rect[0] / 6) * 6, round(rect[1] / 6) * 6)
                        swatches.setdefault(gk, {"bounds": list(rect)})
            except Exception:
                pass
            x += 8
        y += 6
    return {"items": sorted(items.values(), key=lambda c: (c["bounds"][1], c["bounds"][0])),
            "sections": sorted(sections),
            "swatches": sorted(swatches.values(), key=lambda c: (c["bounds"][1], c["bounds"][0]))}


_CT_NAMES = {50000: "button", 50002: "checkbox", 50003: "combobox", 50004: "edit",
             50005: "hyperlink", 50007: "listitem", 50011: "menuitem", 50013: "radiobutton",
             50015: "slider", 50019: "tabitem", 50024: "treeitem", 50025: "custom"}


def _ct_name(ct):
    return _CT_NAMES.get(ct, f"ct{ct}")
