"""Step 5 (driving, v2) — enter stub surfaces TRANSITIVELY for P0-P2 owners; one level for P3.

Depth-endpoint rule (playbook 05): a branch continues while pressing reveals more UI, and ends
when an element fires an action. In data: openers get `opens` + recursion; option-setting
controls / menu commands are endpoints -> `triggers` the owning node; OK/Cancel/Apply are
commit/dismiss endpoints; disabled or network-gated elements stay `unexplored` WITH a reason
(journaled boundary). DONE for P0-P2 = no explored:false container reachable via ANY opens
chain (the DoD checker computes that reachability).

v2 additions over the v1 walker:
  * consolidated IO — everything reads/writes the single ui.json through the kernel writer;
  * CONTEXTUAL TARGETS — stubs opened from contextual ribbons are entered too: targets are
    grouped by object family (table/picture/shape/.../header), the family's object is
    COM-inserted + selected first (same state setup as the step-3 probes), the contextual tab
    activated, then the opener pressed and the surface walked exactly like a Home/Insert one.

Mechanics (unchanged, proven in v1):
  * dialogs are modal — recursion presses a '…' opener while the parent stays open;
  * flyouts die on item-click — each opener item costs a route replay (reopen());
  * menu items without '…' may own cascade submenus — hover-probed with the position rule;
  * a discovered sub-dialog whose title matches an ALREADY-KNOWN container resolves to that
    container id (seen-set); OS file dialogs enumerated one level; network-content surfaces
    enumerated as far as offline UIA shows, interior unexplored + boundary journaled.

Usage: run_step5_enter.py            -> all targets (plain first, then per-family)
       run_step5_enter.py ui:<id>    -> one surface
       run_step5_enter.py <fam>      -> only one family's contextual targets (or 'plain')
"""
import json
import re
import sys
import time
from pathlib import Path

import win32api
import win32gui

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common
from session import WordSession
import uia_attach as ua
import enumerator as en
import driver as drv
import windows as wins
import capture as cap
import depth_capture as dc
import run_step2 as r2
import run_step3_contextual as r3c

KB = common.APP_KB
MAX_DEPTH = 5
FILE_DIALOG_TITLES = {"insert picture", "insert file", "browse", "insert video",
                      "insert object", "open", "select texture", "choose a smartart graphic"}
NETWORK_SURFACE_HINTS = ("stock", "online pictures", "online video", "icons", "3d models",
                         "office.com", "onedrive", "generate an image", "copilot", "designer")
EDGE_DIALOG_TITLES = {"word options"}


def _center(rect):
    return ((rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2)


def _norm_title(t):
    return re.sub(r"[^a-z0-9 ]+", "", (t or "").lower()).strip()


def _is_opener_label(label):
    l = (label or "").strip()
    return l.endswith("...") or l.endswith("…")


def _chrome(label):
    return (label or "").strip().lower() in (
        "ok", "cancel", "close", "apply", "help", "insert", "set as default",
        "set as default...", "text effects...", "")


CHROME_COMMIT = {"ok", "insert", "apply"}


def sub_id_for(parent_id, label):
    s = "".join(ch if ch.isalnum() else "-" for ch in label).strip("-").lower()
    s = re.sub(r"-+", "-", s)[:28].strip("-")
    return f"ui:{parent_id.removeprefix('ui:')}-{s}"


class DepthWalker:
    def __init__(self, sess, win, writer, jrnl, screen_w):
        self.sess, self.win, self.writer, self.jrnl = sess, win, writer, jrnl
        self.screen_w = screen_w
        self.iuia = ua.get_iuia()
        self.explored = set()
        self.title_to_id = {}
        self.written = {}
        # seed from the consolidated ui.json — resumed runs skip entered surfaces
        for cid, c in writer.load_ui().containers.items():
            d = c.model_dump()
            self.written[cid] = d
            if d.get("explored", True):
                self.explored.add(cid)
            t = _norm_title(d.get("label"))
            if t and d["kind"] == "dialog":
                self.title_to_id.setdefault(t, cid)

    def j(self, action, target, outcome, **data):
        self.jrnl.append(common.journal_event(actor="stage5.depth", action=action,
                         target=target, outcome=outcome, data=data))

    def save(self, cont):
        self.writer.upsert_container(cont)
        self.explored.add(cont["id"])
        self.written[cont["id"]] = cont

    def mk(self, control, owner, marker, target=None, note=None, source="uia"):
        el = {"control_type": (control.get("control_type") or "control").lower(),
              "label": control.get("label") or "(unlabeled)",
              "icon": {"description": f"{control.get('label')} (in-dialog control)",
                       "image": None},
              "bounds": control.get("bounds"), "source": source,
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

    def observe_new(self, before, exclude=None, floor=2500):
        for _ in range(12):
            time.sleep(0.25)
            neww = [w for w in wins.new_windows(self.sess.pid, before)
                    if wins._area(w[3]) >= floor and w[0] != exclude]
            if neww:
                return max(neww, key=lambda w: wins._area(w[3]))
        return None

    def close_window(self, hwnd):
        if not hwnd or not win32gui.IsWindow(hwnd):
            return
        try:
            from pywinauto import Desktop
            d = Desktop(backend="uia").window(handle=hwnd)
            for b in ("Cancel", "Close", "No"):
                try:
                    bt = d.child_window(title=b, control_type="Button")
                    if bt.exists(timeout=0.4):
                        bt.click_input()
                        time.sleep(0.35)
                        break
                except Exception:
                    continue
        except Exception:
            pass
        for _ in range(4):
            if not (win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)):
                return
            drv.press_escape(1)
            time.sleep(0.25)

    def close_all(self):
        drv.press_escape(2)
        try:
            from pywinauto import Desktop
            w = Desktop(backend="uia").window(handle=self.sess.frame)
            btn = w.child_window(title="Close pane", control_type="Button")
            if btn.exists(timeout=0.4):
                btn.click_input()
                time.sleep(0.3)
        except Exception:
            pass

    def resolve_known(self, title):
        return self.title_to_id.get(_norm_title(title))

    # ================= dialog =================
    def explore_dialog(self, hwnd, surf_id, owner, recurse, depth=0):
        if surf_id in self.explored:
            return self.written.get(surf_id)
        title = win32gui.GetWindowText(hwnd)
        ntitle = _norm_title(title)
        is_file_dlg = any(k in ntitle for k in FILE_DIALOG_TITLES) or \
            win32gui.GetClassName(hwnd) == "#32770"
        is_network = any(k in ntitle for k in NETWORK_SURFACE_HINTS)
        if any(k in ntitle for k in EDGE_DIALOG_TITLES):
            is_network = True
            self.j("boundary", surf_id, "universe-edge",
                   note="global app-settings dialog beyond the Home+Insert universe; "
                        "enumerated one level only", title=title)
        data = dc.enumerate_dialog(hwnd, self.writer, surf_id.removeprefix("ui:"))
        flat = {}
        for tab in data["tabs"]:
            for c in tab["controls"]:
                key = (c["label"], tuple(round(b / 4) for b in (c.get("bounds") or [0]*4)))
                flat.setdefault(key, c)
        children, child_conts = [], []
        pressed = set()
        for c in list(flat.values()):
            label = c["label"]
            if (recurse and depth < MAX_DEPTH and not is_file_dlg and not is_network
                    and _is_opener_label(label) and c.get("control_type") == "button"
                    and label not in pressed and c.get("enabled", True)):
                pressed.add(label)
                before = wins.snapshot_hwnds(self.sess.pid)
                self.j("press-attempted", f"{surf_id}/{label}", "", depth=depth)
                drv.click_rect(tuple(c["bounds"]))
                new = self.observe_new(before, exclude=hwnd)
                if new:
                    h2, cls2, t2, r2_ = new
                    known = self.resolve_known(t2)
                    sub = known or sub_id_for(surf_id, label)
                    self.j("press-outcome", f"{surf_id}/{label}",
                           "opened", title=t2, cls=cls2, sub_id=sub, known=bool(known))
                    if known and known in self.explored:
                        pass
                    else:
                        self.explore_dialog(h2, sub, owner, recurse, depth + 1)
                    self.close_window(h2)
                    children.append(self.mk(c, owner, "opens", sub,
                                            "opens a sub-dialog (measured)"))
                    if sub not in child_conts:
                        child_conts.append(sub)
                    continue
                else:
                    self.j("press-outcome", f"{surf_id}/{label}", "no-window",
                           note="opener label but nothing appeared")
            if not c.get("enabled", True):
                children.append(self.mk(c, owner, "unexplored",
                                        note="disabled in this document state"))
            elif _chrome(label):
                kindnote = "commits the dialog" if label.strip().lower() in CHROME_COMMIT \
                    else "dismisses/help (dialog chrome)"
                children.append(self.mk(c, owner, "triggers", owner, kindnote))
            elif _is_opener_label(label) and (is_file_dlg or is_network or not recurse):
                children.append(self.mk(c, owner, "unexplored",
                                        note="opener not descended: " +
                                        ("OS/network interior (boundary)" if
                                         (is_file_dlg or is_network) else "P3 one-level rule")))
            else:
                children.append(self.mk(c, owner, "triggers", owner,
                                        "sets an option (depth endpoint)"))
        purpose = f"the {title or owner} dialog"
        if is_file_dlg:
            purpose += " — OS common file dialog; interior is OS chrome (one level, endpoint)"
        if is_network:
            purpose += " — content area streams from the network (boundary; offline UI only)"
            self.j("boundary", surf_id, "network-interior", title=title)
        prev = self.written.get(surf_id, {})
        cont = {"id": surf_id, "kind": "dialog", "label": title or prev.get("label", owner),
                "screenshot": data["tabs"][0]["screenshot"] if data["tabs"] else
                prev.get("screenshot"),
                "children": children, "child_containers": child_conts, "explored": True,
                "trigger_condition": prev.get("trigger_condition"),
                "purpose": purpose + f"; enumerated across {len(data['tabs'])} tab(s)"}
        self.save(cont)
        if _norm_title(title):
            self.title_to_id.setdefault(_norm_title(title), surf_id)
        self.j("surface-captured", surf_id, "explored", children=len(children),
               sub_containers=child_conts, depth=depth)
        return cont

    # ================= flyout =================
    def hover_probe_cascade(self, item_bounds, flyout_hwnd):
        l, t, r, b = win32gui.GetWindowRect(flyout_hwnd)
        drv.move_park((l + r) // 2, t + 2)
        before = wins.snapshot_hwnds(self.sess.pid)
        x, y = _center(tuple(item_bounds))
        from pywinauto import mouse
        mouse.move(coords=(x, y))
        time.sleep(0.65)
        neww = [w for w in wins.new_windows(self.sess.pid, before)
                if wins._area(w[3]) >= 2500]
        if not neww:
            time.sleep(0.45)
            neww = [w for w in wins.new_windows(self.sess.pid, before)
                    if wins._area(w[3]) >= 2500]
        for h, cls, ti, rc in neww:
            if rc[0] >= r - 30:
                return h
        return None

    def explore_flyout(self, hwnd, surf_id, owner, reopen, recurse, depth=0):
        if surf_id in self.explored:
            return self.written.get(surf_id)
        time.sleep(0.2)
        data = dc.enumerate_flyout(self.iuia, hwnd)
        img = cap.grab_rect(win32gui.GetWindowRect(hwnd))
        shot = self.writer.save_screenshot(img, surf_id, "surface")
        wl = win32gui.GetWindowRect(hwnd)
        children, child_conts = [], []
        if data["swatches"]:
            rgbs = []
            for sw in data["swatches"][:6]:
                b = sw["bounds"]
                rgbs.append(cap.sample_rgb(img, (b[0] + b[2]) // 2 - wl[0],
                                           (b[1] + b[3]) // 2 - wl[1]))
            children.append({"control_type": "swatch-grid", "label": "Color swatches",
                "icon": {"description": "grid of theme/standard color swatches", "image": shot},
                "source": "pixel", "triggers": owner,
                "state_notes": f"{len(data['swatches'])} owner-drawn color cells "
                               f"(endpoint: applies the color); sample RGB {rgbs}"})
        cascade_candidates, openers = [], []
        for it in data["items"]:
            if not it.get("enabled", True):
                children.append(self.mk(it, owner, "unexplored",
                                        note="disabled in this document state",
                                        source="hit-test"))
            elif _is_opener_label(it["label"]):
                openers.append(it)
            elif it["control_type"] == "menuitem" and recurse and depth < MAX_DEPTH:
                cascade_candidates.append(it)
            else:
                children.append(self.mk(it, owner, "triggers", owner,
                                        "menu/gallery command (endpoint)", source="hit-test"))
        for it in cascade_candidates:
            if "office.com" in it["label"].lower():
                children.append(self.mk(it, owner, "unexplored",
                                        note="network gallery (boundary)", source="hit-test"))
                self.j("boundary", f"{surf_id}/{it['label']}", "network-gallery")
                continue
            if not win32gui.IsWindowVisible(hwnd):
                hwnd = reopen()
                if not hwnd:
                    children.append(self.mk(it, owner, "triggers", owner,
                                            "menu command (endpoint; cascade probe skipped — "
                                            "flyout could not be reopened)", source="hit-test"))
                    continue
            sub_h = self.hover_probe_cascade(it["bounds"], hwnd)
            if sub_h:
                sub = sub_id_for(surf_id, it["label"])
                self.j("surface-discovered", sub, "cascade", via=it["label"])
                self.explore_flyout(sub_h, sub, owner,
                                    reopen=lambda it=it: self._reopen_cascade(reopen, it),
                                    recurse=recurse, depth=depth + 1)
                children.append(self.mk(it, owner, "opens", sub,
                                        "opens a cascade submenu (measured by hover)",
                                        source="hit-test"))
                if sub not in child_conts:
                    child_conts.append(sub)
                drv.press_escape(1)
                time.sleep(0.2)
            else:
                children.append(self.mk(it, owner, "triggers", owner,
                                        "menu command (endpoint; no cascade on hover)",
                                        source="hit-test"))
        for it in openers:
            if not recurse or depth >= MAX_DEPTH:
                children.append(self.mk(it, owner, "unexplored",
                                        note="opener not descended (P3 one-level rule)",
                                        source="hit-test"))
                continue
            if not win32gui.IsWindowVisible(hwnd):
                hwnd = reopen()
                if not hwnd:
                    children.append(self.mk(it, owner, "unexplored",
                                            note="flyout could not be reopened for this opener",
                                            source="hit-test"))
                    continue
            before = wins.snapshot_hwnds(self.sess.pid)
            self.j("press-attempted", f"{surf_id}/{it['label']}", "", depth=depth)
            drv.click_rect(tuple(it["bounds"]))
            new = self.observe_new(before)
            if not new:
                self.j("press-outcome", f"{surf_id}/{it['label']}", "no-window")
                children.append(self.mk(it, owner, "triggers", owner,
                                        "menu command (endpoint — no surface appeared on "
                                        "press)", source="hit-test"))
                continue
            h2, cls2, t2, rr = new
            kind2 = wins.classify_window(cls2, t2, rr)
            known = self.resolve_known(t2) if kind2 == "dialog" else None
            sub = known or sub_id_for(surf_id, it["label"])
            self.j("press-outcome", f"{surf_id}/{it['label']}", kind2,
                   title=t2, sub_id=sub, known=bool(known))
            if kind2 == "dialog":
                if not (known and known in self.explored):
                    self.explore_dialog(h2, sub, owner, recurse, depth + 1)
                self.close_window(h2)
            else:
                self.explore_flyout(h2, sub, owner,
                                    reopen=lambda: None, recurse=recurse, depth=depth + 1)
                drv.press_escape(2)
            children.append(self.mk(it, owner, "opens", sub,
                                    f"opens a {kind2} (measured)", source="hit-test"))
            if sub not in child_conts:
                child_conts.append(sub)
            time.sleep(0.3)
        secs = ("; sections: " + ", ".join(data.get("sections", []))) \
            if data.get("sections") else ""
        prev = self.written.get(surf_id, {})
        cont = {"id": surf_id, "kind": prev.get("kind", "dropdown"),
                "label": prev.get("label", owner),
                "screenshot": shot, "children": children, "child_containers": child_conts,
                "explored": True,
                "trigger_condition": prev.get("trigger_condition"),
                "purpose": f"flyout of {owner} — commands/tiles are endpoints; openers "
                           f"descended per the depth-endpoint rule{secs}"}
        self.save(cont)
        self.j("surface-captured", surf_id, "explored", children=len(children),
               sub_containers=child_conts, depth=depth)
        return cont

    def _reopen_cascade(self, reopen_parent, item):
        h = reopen_parent()
        if not h:
            return None
        return self.hover_probe_cascade(item["bounds"], h)

    # ================= pane =================
    def explore_pane(self, surf_id, owner, recurse):
        if surf_id in self.explored:
            return self.written.get(surf_id)
        win = ua.attach(self.sess.frame)
        time.sleep(0.4)
        img, _ = cap.grab_window(self.sess.frame)
        shot = self.writer.save_screenshot(img, surf_id, "surface")
        children = []
        try:
            for ct in ("Edit", "Button", "TabItem", "CheckBox"):
                for el in win.descendants(control_type=ct):
                    nm = (el.element_info.name or "").strip()
                    r = el.element_info.rectangle
                    if nm and 0 <= r.left < 460:
                        children.append({"control_type": ct.lower(), "label": nm,
                            "icon": {"description": f"{nm} (in {owner})", "image": None},
                            "source": "uia", "triggers": owner,
                            "bounds": [r.left, r.top, r.right, r.bottom]})
        except Exception:
            pass
        seen, uniq = set(), []
        for c in children:
            if c["label"] in seen:
                continue
            seen.add(c["label"])
            uniq.append(c)
        prev = self.written.get(surf_id, {})
        cont = {"id": surf_id, "kind": "pane",
                "label": prev.get("label", owner),
                "screenshot": shot, "children": uniq[:30], "child_containers": [],
                "explored": True,
                "trigger_condition": prev.get("trigger_condition"),
                "purpose": f"the {owner} pane (docked/floating), enumerated one level — "
                           f"pane controls act on the pane's function (endpoints)"}
        self.save(cont)
        self.j("surface-captured", surf_id, "explored", children=len(uniq))
        return cont


# ================= orchestration =================

def build_open_points_tab(win, tab_title, container, prefix=""):
    """Live click points for every element on the given (possibly contextual) tab that opens
    a surface — split dropdown ZONES, combo open arrows, plain rects."""
    pts = {}
    for gname, kt, leaves in en.live_leaves(win, tab_title):
        for el, props in leaves:
            base = r2.slugify(props.automation_id, props.name)
            # EXACTLY the crawl's id scheme: slug=(prefix+base)[:100]; dropdown adds suffix
            slug = (prefix + base)[:100] if prefix else base
            eid = f"el:{slug}"
            ct = props.control_type
            if ct == "SplitButton":
                primary, dropdown = drv.split_zone_rects(el)
                pts[eid] = _center(primary) if primary else \
                    drv.zone_point(props.rect, "primary")
                dz = _center(dropdown) if dropdown else drv.zone_point(props.rect, "dropdown")
                pts[f"el:{slug}-dropdown"] = dz
            elif ct == "ComboBox":
                orct = en.combo_open_rect(el)
                pts[eid] = _center(orct) if orct else drv.zone_point(props.rect, "dropdown")
            elif props.automation_id in ("QuickStylesGallery", "QuickStylesSets"):
                # R2.5 in-ribbon gallery: center hits a tile (applies a style). Open the FULL
                # flyout via the expand-arrow child, exactly as Step 2 measured it. The element
                # id in ui.json is keyed by the SURFACE slug (Step 2 INRIBBON_GALLERY_SURFACE),
                # not the idMso slug — map explicitly or the open-point never resolves.
                geid = {"QuickStylesGallery": "el:quick-styles-gallery",
                        "QuickStylesSets": "el:style-set-gallery"}[props.automation_id]
                exp = r2.gallery_expand_rect(el)
                pts[geid] = _center(exp) if exp else drv.zone_point(props.rect, "dropdown")
            else:
                pts[eid] = _center(tuple(props.rect))
            if gname == "Styles" and ct == "Button" and props.name == "Styles":
                pts["el:styles-more"] = _center(tuple(props.rect))
    return pts


def load_layers():
    pri = json.loads((KB / "priority.json").read_text(encoding="utf-8"))
    return pri["layers"]


def _depth_set_owners():
    """The depth set the kernel checks: P0-P3 nodes + ALL children of whole-scope features
    (R5.5). Every one gets TRANSITIVE depth (the kernel requires P0-P3 to reach no stub, not
    just P0-P2). Closure pulls are NOT here — they get outline/'enough to work', not entering."""
    pri = json.loads((KB / "priority.json").read_text(encoding="utf-8"))
    layers = pri["layers"]
    whole = {f for f, d in pri.get("derived_features", {}).items()
             if d.get("scope") == "whole"}
    p03 = set(layers.get("P0", []) + layers.get("P1", []) + layers.get("P2", [])
              + layers.get("P3", []))
    ffiles = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((KB / "features").glob("*.json"))]
    subs = [s for ff in ffiles for s in ff["subfeatures"]]
    owners = set(i for i in p03 if i.startswith("subfeature:"))
    for s in subs:
        if s.get("parent") in whole:
            owners.add(s["id"])          # whole-scope children, whatever their own layer
    return owners, subs


# Layout Arrange controls are object-gated: their stubs (Position/Wrap/Rotate dropdowns, the
# Align/Group menus, Selection pane, z-order menus) only open with a drawing object selected.
# Force the 'shape' family for openers on the Layout tab whose owner is an object-arrange sub.
LAYOUT_ARRANGE_OWNERS = {
    "subfeature:object-position", "subfeature:object-text-wrap", "subfeature:object-reorder",
    "subfeature:object-align", "subfeature:object-group", "subfeature:object-rotate",
    "subfeature:object-selection-pane",
}


def collect_targets(writer):
    """[(surf_id, opener_el_id, host_container, family, owner_node, recurse=True)] for every
    ribbon-opened stub whose owning node is in the depth set (P0-P3 + whole children). ALL get
    transitive depth. family=None for Home/Insert/Design/Layout plain controls; else the object
    family needed to summon the host (contextual tab, OR Layout Arrange which needs a shape)."""
    depth_owners, subs = _depth_set_owners()
    el_owner = {}
    for s in subs:
        for tp in s.get("trigger_paths", []):
            if tp.get("path") and tp["path"][-1].startswith("el:"):
                el_owner.setdefault(tp["path"][-1], s["id"])

    # host container -> family via its trigger_condition (measured in step 3)
    COND_FAMILY = [("table", "table"), ("picture is selected", "picture"),
                   ("svg/icon", "svg-graphic"), ("drawn shape", "shape"),
                   ("text box", "shape"), ("wordart", "wordart"),
                   ("smartart", "smartart"), ("chart", "chart"),
                   ("equation", "equation"), ("math zone", "equation"),
                   ("header or footer", "header"), ("header/footer", "header")]

    def family_of(cont):
        cond = (cont.get("trigger_condition") or "").lower()
        if not cond:
            return None
        for key, fam in COND_FAMILY:
            if key in cond:
                return fam
        return None

    ui = writer.load_ui()
    containers = {cid: c.model_dump() for cid, c in ui.containers.items()}
    targets, seen = [], set()
    ribbons = [(cid, c) for cid, c in containers.items()
               if cid in ("ui:ribbon-home", "ui:ribbon-insert", "ui:ribbon-design",
                          "ui:ribbon-layout") or c.get("trigger_condition")]
    for cid, c in ribbons:
        fam = family_of(c)
        for e in c["children"]:
            surf = e.get("opens")
            if not surf or surf in seen:
                continue
            if not containers.get(surf, {}).get("explored", True) is False:
                continue          # only stubs need entering
            owner = el_owner.get(e.get("id"))
            if owner not in depth_owners:
                continue
            fam_here = fam
            if cid == "ui:ribbon-layout" and owner in LAYOUT_ARRANGE_OWNERS:
                fam_here = "shape"     # Layout Arrange opener needs a selected object
            seen.add(surf)
            targets.append((surf, e["id"], cid, fam_here, owner, True))
    return targets


def enter_styles_gallery(walker, surf_id, owner):
    sess, writer = walker.sess, walker.writer
    win = ua.attach(sess.frame)
    time.sleep(0.3)
    children, shot, rects = [], None, []
    try:
        dg = win.child_window(title="Styles", control_type="DataGrid")
        for li in dg.descendants(control_type="ListItem"):
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
        img, frect = cap.grab_window(sess.frame)
        if rects:
            x0 = min(r[0] for r in rects); y0 = min(r[1] for r in rects)
            x1 = max(r[2] for r in rects); y1 = max(r[3] for r in rects)
            shot = writer.save_screenshot(cap.crop_from(img, (x0, y0, x1, y1), frect),
                                          surf_id, "surface")
    except Exception:
        pass
    cont = {"id": surf_id, "kind": "dropdown", "label": "Quick Styles gallery",
            "screenshot": shot, "children": children, "child_containers": [],
            "explored": True,
            "purpose": "the Quick Styles gallery — named style tiles (each applies a style)"}
    walker.save(cont)
    walker.j("surface-captured", surf_id, "explored", children=len(children))
    return cont


TAB_TITLE = {  # host container id -> live tab title to activate
    "ui:ribbon-home": "Home", "ui:ribbon-insert": "Insert",
    "ui:ribbon-design": "Design", "ui:ribbon-layout": "Layout",
}


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    run_id = common.make_run_id() + "-step5-enter"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    screen_w = win32api.GetSystemMetrics(0)
    pinned = json.loads((KB / "version.json").read_text(encoding="utf-8"))
    targets = collect_targets(writer)
    if only and only.startswith("ui:"):
        targets = [t for t in targets if t[0] == only]
    elif only == "plain":
        targets = [t for t in targets if t[3] is None]
    elif only:
        targets = [t for t in targets if t[3] == only]

    # group: plain targets first, then per family (one object setup per family)
    order = {None: 0, "table": 1, "picture": 2, "svg-graphic": 3, "shape": 4, "wordart": 5,
             "smartart": 6, "chart": 7, "equation": 8, "header": 9}
    targets.sort(key=lambda t: (order.get(t[3], 99), t[0]))

    png, svg = r3c.make_probe_png(), r3c.make_probe_svg()
    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    jrnl.append(common.journal_event(actor="stage5.depth", action="launch",
                target=f"pid={sess.pid}", outcome="ok",
                data={"targets": [(t[0], t[3] or "plain", "deep" if t[5] else "P3")
                                  for t in targets]}))
    results = []
    try:
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
        sess.select_paragraph(1)
        try:
            sess.doc.Paragraphs(1).Range.Copy()
        except Exception:
            pass
        win = ua.attach(sess.frame)
        time.sleep(0.4)
        walker = DepthWalker(sess, win, writer, jrnl, screen_w)
        probes = {name: (ins, sel) for name, ins, sel, fp, cond, ownr
                  in r3c.object_probes(sess, png, svg)}
        cur_family = "<start>"
        open_points = {}

        for surf_id, el_id, host, fam, owner, recurse in targets:
            if surf_id in walker.explored:
                walker.j("enter", surf_id, "seen-already")
                continue
            # ---- context setup on family change ----
            if fam != cur_family:
                # tear down previous object state
                try:
                    sess.doc.Paragraphs(1).Range.Select()
                except Exception:
                    pass
                for _ in range(12):
                    drv.send_keys("^z")
                    time.sleep(0.25)
                    if sess.object_fingerprint().get("tables", 0) in (0, -1) and \
                       sess.object_fingerprint().get("inline_shapes", 0) in (0, -1) and \
                       sess.object_fingerprint().get("shapes", 0) in (0, -1):
                        break
                sess.select_paragraph(1)
                if fam is not None:
                    ins, sel = probes[fam]
                    try:
                        ins()
                        time.sleep(0.6)
                        sel()
                        time.sleep(1.0)
                        walker.j("context-setup", fam, "ok")
                    except Exception as e:
                        walker.j("context-setup", fam, f"error: {e}")
                        cur_family = fam
                        continue
                cur_family = fam
                open_points = {}
            # ---- activate host tab, resolve opener point live ----
            tab_title = TAB_TITLE.get(host)
            if tab_title is None:
                cont = walker.written.get(host, {})
                tab_title = (cont.get("label") or "").replace(" (contextual tab)", "")
            if fam is not None:
                try:
                    probes[fam][1]()      # re-select the object (tab needs the selection)
                    time.sleep(0.4)
                except Exception:
                    pass
            # activate the host tab; the cached UIA `win` wrapper goes stale after heavy
            # interaction (esp. an OS file dialog), so re-attach the frame and retry before
            # giving up (measured: plain depth pass, tab-activate-failed cascade).
            activated = False
            for attempt in range(3):
                try:
                    en.select_tab(win, tab_title)
                    time.sleep(0.35)
                    activated = True
                    break
                except Exception as e:
                    walker.j("enter", surf_id, f"tab-activate-retry{attempt}: {type(e).__name__}")
                    # HARD reset: a prior opener may have left an OS file dialog / Copilot pane /
                    # stuck modal blocking the ribbon so every later tab-activate fails (measured:
                    # Insert Pictures 'This Device…' / 'Generate an Image…'). Close every non-frame
                    # top-level window win32-only (no COM), wait for COM to free, re-attach.
                    r3c._force_close_nonframe(sess, set())
                    drv.press_escape(2)
                    walker.close_all()
                    drv.ensure_frame_foreground(sess.frame)
                    time.sleep(0.5)
                    # the frame hwnd can change if Word re-created its window; re-resolve it
                    from session import frame_hwnd as _fh
                    fh = _fh(sess.pid)
                    if fh:
                        sess.frame = fh
                    win = ua.attach(sess.frame)
                    walker.win = win
                    open_points.pop(host, None)     # rects may have shifted; recompute
                    time.sleep(0.4)
            if not activated:
                walker.j("enter", surf_id, "tab-activate-failed")
                continue
            if host not in open_points:
                prefix = host.removeprefix("ui:") + "-" if host not in TAB_TITLE else ""
                open_points[host] = build_open_points_tab(win, tab_title, None, prefix)
            point = open_points[host].get(el_id)
            if not point:
                walker.j("enter", surf_id, "no-open-point", opener=el_id)
                continue
            if surf_id == "ui:styles-gallery":
                enter_styles_gallery(walker, surf_id, owner)
                results.append({"surf": surf_id, "kind": "gallery"})
                continue

            def reopen(tab_title=tab_title, point=point, fam=fam):
                walker.close_all()
                if fam is not None:
                    try:
                        probes[fam][1]()
                        time.sleep(0.3)
                    except Exception:
                        pass
                try:
                    en.select_tab(win, tab_title)
                except Exception:
                    return None
                time.sleep(0.35)
                drv.ensure_frame_foreground(sess.frame)
                before = wins.snapshot_hwnds(sess.pid)
                drv.click_point(*point)
                new = walker.observe_new(before, floor=2500)
                return new[0] if new else None

            walker.j("press-attempted", surf_id, "", opener=el_id, point=list(point))
            drv.ensure_frame_foreground(sess.frame)
            before_hwnds = wins.snapshot_hwnds(sess.pid)
            panes_before = wins.count_docked_panes(sess.frame, screen_w)[0]
            drv.click_point(*point)
            new = walker.observe_new(before_hwnds, floor=2500)
            kind = hwnd = None
            if new:
                hwnd, cls, title, r = new
                kind = wins.classify_window(cls, title, r)
                # a floating task pane (Styles pane) is a top-level window whose class is not in
                # the dialog set -> reads as 'other'/'dialog'; the 'Close pane' button identifies
                # it. Reclassify BEFORE the dispatch or explore_pane never runs.
                if kind in ("dialog", "other") and wins.is_task_pane_window(hwnd):
                    kind = "pane"
            elif wins.count_docked_panes(sess.frame, screen_w)[0] > panes_before:
                kind = "pane"
            walker.j("press-outcome", surf_id, kind or "none")
            try:
                if kind == "dialog":
                    walker.explore_dialog(hwnd, surf_id, owner, recurse)
                    walker.close_window(hwnd)
                elif kind in ("flyout", "tooltip"):
                    walker.explore_flyout(hwnd, surf_id, owner, reopen, recurse)
                    drv.press_escape(2)
                elif kind == "pane":
                    walker.explore_pane(surf_id, owner, recurse)
                    walker.close_all()
                else:
                    walker.j("enter", surf_id, "no-surface-appeared")
            except Exception as e:
                walker.j("enter", surf_id, f"error: {type(e).__name__}: {e}")
                walker.close_all()
            walker.close_all()
            if fam is None:
                sess.select_paragraph(1)
            results.append({"surf": surf_id, "kind": kind,
                            "explored": surf_id in walker.explored})
        print(json.dumps({"targets": len(targets), "entered": results},
                         indent=2, ensure_ascii=False))
    finally:
        sess.close()
        jrnl.append(common.journal_event(actor="stage5.depth", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed", data={}))


if __name__ == "__main__":
    main()
