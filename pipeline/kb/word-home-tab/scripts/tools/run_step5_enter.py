"""Step 5 (driving) — enter the P0-P2 (and P3 mid-level) stub surfaces and enumerate them.

Depth-endpoint rule in the data: an option-setting control (checkbox, edit, combo, list item,
swatch) FIRES an action -> endpoint -> triggers its owning subfeature. A '...' button that opens
another surface -> descend -> opens + recurse one level (P0-P2). OK/Apply/Cancel are commit/
dismiss endpoints on the owner. Every container we enter is flipped explored:true with real
children[] + screenshots. P3 surfaces are entered one level (mid-level), no recursion.
"""
import json
import sys
import time
from pathlib import Path

import win32api
import win32gui

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import common
from session import WordSession
import uia_attach as ua
import driver as drv
import windows as wins
import capture as cap
import depth_capture as dc
import enumerator as en
import run_step2 as r2   # reuse slugify / surface_id / container_kind for click-point resolution

KB = common.APP_KB


def _center(rect):
    return ((rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2)


def build_open_points(win):
    """Live click points for surfaces whose opener is a split-button DROPDOWN zone, a combo's
    open arrow, or the QuickStyles More button — the element's stored full-rect center would hit
    the primary (apply) zone instead. Keyed by the surface id the zone opens."""
    pts = {}
    for gname, kt, leaves in en.live_leaves(win, "Home"):
        for el, props in leaves:
            base = r2.slugify(props.automation_id, props.name)
            ct = props.control_type
            if ct == "SplitButton":
                primary, dropdown = drv.split_zone_rects(el)
                ck = r2.container_kind("flyout", props.automation_id)
                surf = r2.surface_id(base, "flyout", ck)
                pts[surf] = _center(dropdown or drv.zone_point(props.rect, "dropdown"))
            elif ct == "ComboBox":
                surf = r2.surface_id(base, "flyout", "dropdown")
                pts[surf] = _center(en.combo_open_rect(el) or drv.zone_point(props.rect, "dropdown"))
            elif gname == "Styles" and ct == "Button" and props.name == "Styles":
                pts["ui:styles-gallery"] = _center(tuple(props.rect))
    return pts


def load_layers():
    return json.loads((KB / "priority" / "layers.json").read_text(encoding="utf-8"))["layers"]


def load_container(cid):
    p = KB / "ui" / (cid.removeprefix("ui:") + ".json")
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def owner_of_surface(surf_id, subs):
    for s in subs:
        if s.get("opens") == surf_id:
            return s["id"]
    return None


def opener_bounds(ribbon, surf_id):
    for e in ribbon["children"]:
        if e.get("opens") == surf_id:
            return e["id"], tuple(e["bounds"])
    return None, None


def _mk_elem(control, owner, marker="triggers", target=None, note=None):
    icon = {"description": f"{control['label']} (in {owner})", "image": None}
    el = {"control_type": (control.get("control_type") or "control"), "label": control["label"],
          "icon": icon, "bounds": control.get("bounds"), "source": "uia",
          "tooltip": control.get("tooltip"), "shortcut": control.get("shortcut")}
    if marker == "opens":
        el["opens"] = target
    elif marker == "unexplored":
        el["unexplored"] = True
    else:
        el["triggers"] = target or owner
    if note:
        el["state_notes"] = note
    return el


def _is_opener_label(label):
    l = (label or "").strip()
    return l.endswith("...") or l.endswith("…")


def _chrome(label):
    return (label or "").strip().lower() in ("ok", "cancel", "close", "apply", "help",
                                             "set as default", "set as default...")


def press_subsurface(sess, parent_hwnd, bounds, writer, jrnl, sub_id, owner=None):
    """Press a '...' opener inside a surface, measure the new window, enumerate it one level.
    `owner` is the owning NODE id (subfeature:...) — child triggers must point at it, never at
    the container id."""
    owner = owner or sub_id
    before = wins.snapshot_hwnds(sess.pid)
    drv.click_rect(bounds)
    neww = []
    for _ in range(12):
        time.sleep(0.25)
        neww = [w for w in wins.new_windows(sess.pid, before)
                if wins._area(w[3]) >= 8000 and w[0] != parent_hwnd]
        if neww:
            break
    if not neww:
        return None
    h, cls, title, r = max(neww, key=lambda w: wins._area(w[3]))
    kind = wins.classify_window(cls, title, r)
    cont = None
    try:
        if kind == "dialog":
            data = dc.enumerate_dialog(h, writer, sub_id.removeprefix("ui:"))
            children = [_mk_elem(c, owner, note="option/field") for tab in data["tabs"]
                        for c in tab["controls"] if not _is_opener_label(c["label"])]
            cont = {"id": sub_id, "kind": "dialog", "label": title or "sub-dialog",
                    "screenshot": data["tabs"][0]["screenshot"] if data["tabs"] else None,
                    "children": children, "child_containers": [], "explored": True,
                    "purpose": "sub-dialog reached from a parent surface (one level, depth-endpoint)"}
        else:
            img = cap.grab_rect(r)
            shot = writer.save_screenshot(img, sub_id, "surface")
            cont = {"id": sub_id, "kind": "dropdown" if kind == "flyout" else "dialog",
                    "label": title or "sub-surface", "screenshot": shot,
                    "children": [], "child_containers": [], "explored": False,
                    "purpose": "sub-surface reached from a parent; interior deferred (deep)"}
    finally:
        # close the sub-window
        try:
            from pywinauto import Desktop
            d = Desktop(backend="uia").window(handle=h)
            for b in ("Cancel", "Close", "OK"):
                bt = d.child_window(title=b, control_type="Button")
                if bt.exists(timeout=0.5):
                    bt.click_input(); time.sleep(0.3); break
            else:
                drv.press_escape(2)
        except Exception:
            drv.press_escape(2)
    return cont


def enter_dialog(sess, hwnd, surf_id, owner, writer, jrnl, recurse):
    data = dc.enumerate_dialog(hwnd, writer, surf_id.removeprefix("ui:"))
    # UIA descendants are NOT tab-scoped: dialog-bottom buttons (OK, Text Effects...) appear under
    # every tab. Flatten + dedup globally by (label, rounded bounds), and press each opener once.
    flat = {}
    for tab in data["tabs"]:
        for c in tab["controls"]:
            key = (c["label"], tuple(round(b / 4) for b in (c.get("bounds") or [0, 0, 0, 0])))
            flat.setdefault(key, c)
    children, child_conts, pressed = [], [], set()
    for c in flat.values():
        label = c["label"]
        if (recurse and _is_opener_label(label) and c.get("control_type") == "button"
                and label not in pressed):
            pressed.add(label)
            sub_id = "ui:" + surf_id.removeprefix("ui:") + "-" + \
                "".join(ch if ch.isalnum() else "-" for ch in label).strip("-").lower()[:26].strip("-")
            sub = press_subsurface(sess, hwnd, tuple(c["bounds"]), writer, jrnl, sub_id, owner)
            if sub:
                writer.write_container(sub)
                if sub_id not in child_conts:
                    child_conts.append(sub_id)
                children.append(_mk_elem(c, owner, "opens", sub_id, "opens a sub-dialog"))
                jrnl.append(common.journal_event(actor="stage5.depth", action="recurse",
                            target=sub_id, outcome="entered", data={"via": label}))
                continue
        note = "commit/dismiss" if _chrome(label) else "sets an option (endpoint)"
        children.append(_mk_elem(c, owner, "triggers", owner, note))
    cont = {"id": surf_id, "kind": "dialog", "label": data.get("title") or owner,
            "screenshot": data["tabs"][0]["screenshot"] if data["tabs"] else None,
            "children": children, "child_containers": child_conts, "explored": True,
            "purpose": f"the {owner} dialog — fully enumerated across "
                       f"{len(data['tabs'])} tab(s); option controls are endpoints"}
    return cont


def enter_flyout(sess, hwnd, surf_id, owner, writer, jrnl, recurse):
    iuia = ua.get_iuia()
    time.sleep(0.2)
    data = dc.enumerate_flyout(iuia, hwnd)
    img = cap.grab_rect(win32gui.GetWindowRect(hwnd))
    shot = writer.save_screenshot(img, surf_id, "surface")
    children, child_conts = [], []
    for it in data["items"]:
        label = it["label"]
        if _is_opener_label(label) and recurse:
            sub_id = "ui:" + surf_id.removeprefix("ui:") + "-" + \
                "".join(ch if ch.isalnum() else "-" for ch in label).strip("-").lower()[:30]
            # re-open the flyout is needed after pressing an item; handled by caller retry — here
            # we just record it as opens with a stub (deep), to avoid destabilizing the flyout.
            children.append(_mk_elem(it, owner, "opens", sub_id, "opens a sub-surface (deep)"))
            child_conts.append(sub_id)
            writer.write_container({"id": sub_id, "kind": "dialog", "label": label,
                "screenshot": None, "children": [], "child_containers": [], "explored": False,
                "purpose": "sub-surface of a menu; interior deferred"})
        else:
            children.append(_mk_elem(it, owner, "triggers", owner, "menu command (endpoint)"))
    if data["swatches"]:
        # sample a few RGBs from the screenshot for evidence
        rgbs = []
        for sw in data["swatches"][:6]:
            b = sw["bounds"]
            wl = win32gui.GetWindowRect(hwnd)
            cx = (b[0] + b[2]) // 2 - wl[0]
            cy = (b[1] + b[3]) // 2 - wl[1]
            rgbs.append(cap.sample_rgb(img, cx, cy))
        children.append({"control_type": "swatch-grid", "label": "Color swatches",
            "icon": {"description": "grid of theme/standard color swatches", "image": shot},
            "source": "pixel", "triggers": owner,
            "state_notes": f"{len(data['swatches'])} owner-drawn color cells; sample RGB {rgbs}"})
    secs = ("; sections: " + ", ".join(data.get("sections", []))) if data.get("sections") else ""
    cont = {"id": surf_id, "kind": "dropdown", "label": owner, "screenshot": shot,
            "children": children, "child_containers": child_conts, "explored": True,
            "purpose": f"the {owner} flyout — items are endpoints; swatches pixel-sampled{secs}"}
    return cont


def enter_styles_gallery(sess, surf_id, owner, writer):
    """The Quick Styles inline gallery IS exposed in the UIA tree (DataGrid 'Styles' > ListItems),
    unlike owner-drawn flyouts — enumerate it directly rather than via the flaky More button."""
    win = ua.attach(sess.frame)
    time.sleep(0.3)
    children = []
    shot = None
    try:
        dg = win.child_window(title="Styles", control_type="DataGrid")
        items = dg.descendants(control_type="ListItem")
        rects = []
        for li in items:
            nm = (li.element_info.name or "").strip()
            r = li.element_info.rectangle
            if not nm:
                continue
            rects.append((r.left, r.top, r.right, r.bottom))
            children.append({"control_type": "listitem", "label": nm,
                "icon": {"description": f"'{nm}' style preview tile", "image": None},
                "source": "uia", "triggers": owner,
                "bounds": [r.left, r.top, r.right, r.bottom],
                "state_notes": "applies the named style (endpoint)"})
        # screenshot: crop the gallery region from the frame
        img, frect = cap.grab_window(sess.frame)
        if rects:
            x0 = min(r[0] for r in rects); y0 = min(r[1] for r in rects)
            x1 = max(r[2] for r in rects); y1 = max(r[3] for r in rects)
            crop = cap.crop_from(img, (x0, y0, x1, y1), frect)
            shot = writer.save_screenshot(crop, surf_id, "surface")
    except Exception:
        pass
    return {"id": surf_id, "kind": "dropdown", "label": "Quick Styles gallery",
            "screenshot": shot, "children": children, "child_containers": [], "explored": True,
            "purpose": "the Quick Styles gallery — named style tiles (each applies a style)"}


def enter_pane(sess, surf_id, owner, writer, jrnl):
    """Light enumeration of a docked pane: screenshot the frame + list top UIA controls."""
    win = ua.attach(sess.frame)
    time.sleep(0.3)
    img, _ = cap.grab_window(sess.frame)
    shot = writer.save_screenshot(img, surf_id, "surface")
    children = []
    try:
        # the Navigation pane hosts a search Edit + result tabs; enumerate visible buttons/edits/tabs
        for ct in ("Edit", "Button", "TabItem"):
            for el in win.descendants(control_type=ct):
                nm = (el.element_info.name or "").strip()
                r = el.element_info.rectangle
                # only controls in the left docked region (x < 420)
                if nm and r.left < 420 and r.left >= 0:
                    children.append({"control_type": ct.lower(), "label": nm,
                        "icon": {"description": f"{nm} (in {owner})", "image": None},
                        "source": "uia", "triggers": owner, "bounds": [r.left, r.top, r.right, r.bottom]})
    except Exception:
        pass
    # dedupe
    seen, uniq = set(), []
    for c in children:
        k = c["label"]
        if k in seen:
            continue
        seen.add(k); uniq.append(c)
    cont = {"id": surf_id, "kind": "pane", "label": owner, "screenshot": shot,
            "children": uniq[:25], "child_containers": [], "explored": True,
            "purpose": f"the {owner} docked pane (enumerated one level)"}
    return cont


def open_surface(sess, point):
    before = wins.snapshot_hwnds(sess.pid)
    panes_before = wins.count_docked_panes(sess.frame, win32api.GetSystemMetrics(0))[0]
    drv.ensure_frame_foreground(sess.frame)
    drv.click_point(*point)
    for _ in range(14):
        time.sleep(0.25)
        neww = [w for w in wins.new_windows(sess.pid, before) if wins._area(w[3]) >= 6000]
        if neww:
            h, cls, title, r = max(neww, key=lambda w: wins._area(w[3]))
            k = wins.classify_window(cls, title, r)
            if k == "dialog" and wins.is_task_pane_window(h):
                return "pane", None
            return k, h
        panes_now = wins.count_docked_panes(sess.frame, win32api.GetSystemMetrics(0))[0]
        if panes_now > panes_before:
            return "pane", None
    return "none", None


def close_any(sess, hwnd):
    if hwnd:
        try:
            from pywinauto import Desktop
            d = Desktop(backend="uia").window(handle=hwnd)
            for b in ("Cancel", "Close", "OK"):
                bt = d.child_window(title=b, control_type="Button")
                if bt.exists(timeout=0.4):
                    bt.click_input(); time.sleep(0.3); return
        except Exception:
            pass
    drv.press_escape(2)
    # close any docked pane
    try:
        from pywinauto import Desktop
        w = Desktop(backend="uia").window(handle=sess.frame)
        btn = w.child_window(title="Close pane", control_type="Button")
        if btn.exists(timeout=0.4):
            btn.click_input(); time.sleep(0.3)
    except Exception:
        pass


def main():
    run_id = common.make_run_id() + "-step5-enter"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    layers = load_layers()
    p0p2 = set(layers.get("P0", []) + layers.get("P1", []) + layers.get("P2", []))
    p3 = set(layers.get("P3", []))
    subs = [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(KB.glob("subfeatures/**/*.json"))]
    ribbon = load_container("ui:ribbon-home")

    # Element-driven targets: any ribbon element that OPENS a surface, whose owning subfeature is
    # P0-P2 (recurse) or P3 (mid-level). Catches split-dropdown surfaces (Find menu) that are not
    # a subfeature's own `opens` but still belong to a high-priority owner.
    el_owner = {}
    for s in subs:
        for tp in s.get("trigger_paths", []):
            if tp.get("path") and tp["path"][-1].startswith("el:"):
                el_owner[tp["path"][-1]] = s["id"]
    sub_layer = {s["id"]: ("P0P2" if s["id"] in p0p2 else ("P3" if s["id"] in p3 else None))
                 for s in subs}
    targets, seen = [], set()
    for e in ribbon["children"]:
        surf = e.get("opens")
        if not surf or surf in seen:
            continue
        owner = el_owner.get(e.get("id"))
        lay = sub_layer.get(owner) if owner else None
        if not lay:
            continue
        seen.add(surf)
        targets.append((surf, owner, lay == "P0P2"))

    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build="16.0.20131")
    jrnl.append(common.journal_event(actor="stage5.depth", action="launch",
                target=f"pid={sess.pid}", outcome="ok", data={"targets": len(targets)}))
    results = []
    try:
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
        sess.select_paragraph(1)
        win = ua.attach(sess.frame)
        time.sleep(0.4)
        open_points = build_open_points(win)     # exact click points for split/combo/gallery
        for surf_id, owner, recurse in targets:
            oid, bounds = opener_bounds(ribbon, surf_id)
            if not bounds:
                jrnl.append(common.journal_event(actor="stage5.depth", action="enter",
                            target=surf_id, outcome="no-opener", data={}))
                continue
            # the Quick Styles gallery is enumerated from the UIA tree, not by opening a flyout
            if surf_id == "ui:styles-gallery":
                cont = enter_styles_gallery(sess, surf_id, owner, writer)
                writer.write_container(cont)
                results.append({"surf": surf_id, "kind": "gallery",
                                "children": len(cont["children"]), "recursed": []})
                jrnl.append(common.journal_event(actor="stage5.depth", action="enter",
                            target=surf_id, outcome="explored",
                            data={"kind": "gallery", "children": len(cont["children"])}))
                continue
            point = open_points.get(surf_id) or _center(bounds)
            jrnl.append(common.journal_event(actor="stage5.depth", action="press-attempted",
                        target=surf_id, outcome="", data={"opener": oid, "point": list(point)}))
            kind, hwnd = open_surface(sess, point)
            cont = None
            try:
                if kind == "dialog":
                    cont = enter_dialog(sess, hwnd, surf_id, owner, writer, jrnl, recurse)
                elif kind == "flyout":
                    cont = enter_flyout(sess, hwnd, surf_id, owner, writer, jrnl, recurse)
                elif kind == "pane":
                    cont = enter_pane(sess, surf_id, owner, writer, jrnl)
                else:
                    jrnl.append(common.journal_event(actor="stage5.depth", action="enter",
                                target=surf_id, outcome=f"no-surface({kind})", data={}))
            except Exception as e:
                jrnl.append(common.journal_event(actor="stage5.depth", action="enter",
                            target=surf_id, outcome=f"error: {e}", data={}))
            if cont:
                writer.write_container(cont)
                results.append({"surf": surf_id, "kind": kind, "children": len(cont["children"]),
                                "recursed": cont.get("child_containers", [])})
                jrnl.append(common.journal_event(actor="stage5.depth", action="enter",
                            target=surf_id, outcome="explored",
                            data={"kind": kind, "children": len(cont["children"]),
                                  "child_containers": cont.get("child_containers", [])}))
            close_any(sess, hwnd)
            time.sleep(0.3)
            drv.press_escape(1)
            sess.select_paragraph(1)
        print(json.dumps({"entered": len(results), "surfaces": results}, indent=2, ensure_ascii=False))
    finally:
        sess.close()
        jrnl.append(common.journal_event(actor="stage5.depth", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed", data={}))


if __name__ == "__main__":
    main()
