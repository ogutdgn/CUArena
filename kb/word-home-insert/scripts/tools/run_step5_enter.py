"""Step 5 (driving) — enter stub surfaces TRANSITIVELY for P0-P2 owners; one level for P3.

Depth-endpoint rule (playbook 05): a branch continues while pressing reveals more UI, and ends
when an element fires an action. In data: openers get `opens` + recursion; option-setting
controls / menu commands are endpoints -> `triggers` the owning node; OK/Cancel/Apply are
commit/dismiss endpoints; disabled or network-gated elements stay `unexplored` WITH a reason
(journaled boundary). DONE for P0-P2 = no explored:false container reachable via ANY opens
chain (the DoD checker computes that reachability).

Mechanics:
  * dialogs are modal — recursion presses a '…' opener while the parent stays open, explores
    the child, closes it, and continues with the next opener (no reopen needed);
  * flyouts die on item-click — each opener item costs: click -> explore what opened -> close
    -> REOPEN the flyout via its ribbon zone (route replay) for the next opener;
  * menu items without '…' may own cascade submenus — hover-probed (park-settle first);
  * a discovered sub-dialog whose title matches an ALREADY-KNOWN container resolves to that
    container id (seen-set: shared dialogs referenced, never re-crawled); if the known one is
    a stub, it is explored now under its own id;
  * OS common file dialogs are enumerated one level (their interior is OS chrome, endpoint by
    nature); network-content dialogs (Stock Images, Online Pictures/Videos, icons, 3D stock)
    are enumerated as far as offline UIA shows, the network interior marked unexplored with the
    boundary journaled.
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

KB = common.APP_KB
MAX_DEPTH = 5
FILE_DIALOG_TITLES = {"insert picture", "insert file", "browse", "insert video",
                      "insert object", "open"}
NETWORK_SURFACE_HINTS = ("stock", "online pictures", "online video", "icons", "3d models",
                         "office.com")
# dialogs at the UNIVERSE EDGE: reachable from Home/Insert machinery but belonging to the
# whole app (global settings). Enumerated one level, never recursed (journaled boundary).
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
        "set as default...", "text effects...", "" )


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
        self.explored = set()          # container ids fully handled this run
        self.title_to_id = {}          # normalized dialog title -> container id
        self.written = {}              # id -> container dict
        # seed the title map + explored set from disk — makes chunked/resumed runs skip
        # surfaces an earlier session already entered (the run is resumable by design)
        for p in KB.glob("ui/*.json"):
            c = json.loads(p.read_text(encoding="utf-8"))
            self.written[c["id"]] = c
            if c.get("explored", True):
                self.explored.add(c["id"])
            t = _norm_title(c.get("label"))
            if t and c["kind"] == "dialog":
                self.title_to_id.setdefault(t, c["id"])

    # ---------- journal helpers ----------
    def j(self, action, target, outcome, **data):
        self.jrnl.append(common.journal_event(actor="stage5.depth", action=action,
                         target=target, outcome=outcome, data=data))

    # ---------- element factory ----------
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

    # ---------- window helpers ----------
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

    # ---------- identity / dedupe ----------
    def resolve_known(self, title):
        """If this dialog title matches a known container, return its id (seen-set)."""
        return self.title_to_id.get(_norm_title(title))

    # ================= dialog =================
    def explore_dialog(self, hwnd, surf_id, owner, recurse, depth=0):
        """Enumerate a (modal) dialog; press its '…' openers and recurse while modal parent
        stays open. Writes + returns the container."""
        if surf_id in self.explored:
            return self.written.get(surf_id)
        title = win32gui.GetWindowText(hwnd)
        ntitle = _norm_title(title)
        is_file_dlg = any(k in ntitle for k in FILE_DIALOG_TITLES) or \
            win32gui.GetClassName(hwnd) == "#32770"
        is_network = any(k in ntitle for k in NETWORK_SURFACE_HINTS)
        if any(k in ntitle for k in EDGE_DIALOG_TITLES):
            is_network = True     # same treatment: one level, no recursion, boundary journaled
            self.j("boundary", surf_id, "universe-edge",
                   note="global app-settings dialog beyond the Home+Insert universe; "
                        "enumerated one level only", title=title)
        data = dc.enumerate_dialog(hwnd, self.writer, surf_id.removeprefix("ui:"))
        # flatten across tabs; dedupe by (label, rounded bounds) — bottom buttons repeat per tab
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
                        pass                      # shared dialog, already explored
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
            # endpoints / chrome / disabled
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
        cont = {"id": surf_id, "kind": "dialog", "label": title or owner,
                "screenshot": data["tabs"][0]["screenshot"] if data["tabs"] else None,
                "children": children, "child_containers": child_conts, "explored": True,
                "purpose": purpose + f"; enumerated across {len(data['tabs'])} tab(s)"}
        self.writer.write_container(cont)
        self.explored.add(surf_id)
        self.written[surf_id] = cont
        if _norm_title(title):
            self.title_to_id.setdefault(_norm_title(title), surf_id)
        self.j("surface-captured", surf_id, "explored", children=len(children),
               sub_containers=child_conts, depth=depth)
        return cont

    # ================= flyout =================
    def hover_probe_cascade(self, item_bounds, flyout_hwnd):
        """Hover a menu item; return hwnd of a cascade submenu if one appears."""
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
            # a real cascade's left edge sits at/after the parent's right edge (win32.md);
            # allow overlap tolerance of 30px
            if rc[0] >= r - 30:
                return h
        return None

    def explore_flyout(self, hwnd, surf_id, owner, reopen, recurse, depth=0):
        """Enumerate a flyout; explore items that open dialogs / cascades. `reopen()` must
        bring THIS flyout back (returns new hwnd) after an item press killed it."""
        if surf_id in self.explored:
            return self.written.get(surf_id)
        time.sleep(0.2)
        data = dc.enumerate_flyout(self.iuia, hwnd)
        img = cap.grab_rect(win32gui.GetWindowRect(hwnd))
        shot = self.writer.save_screenshot(img, surf_id, "surface")
        wl = win32gui.GetWindowRect(hwnd)
        children, child_conts = [], []
        # --- swatches (owner-drawn color cells) ---
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
        # --- named items ---
        cascade_candidates = []
        openers = []
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
        # --- hover-probe potential cascades (menuitems without '…') ---
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
                drv.press_escape(1)     # collapse cascade, keep parent
                time.sleep(0.2)
            else:
                children.append(self.mk(it, owner, "triggers", owner,
                                        "menu command (endpoint; no cascade on hover)",
                                        source="hit-test"))
        # --- openers: click -> explore -> close -> reopen parent ---
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
        cont = {"id": surf_id, "kind": self.written.get(surf_id, {}).get("kind", "dropdown"),
                "label": self.written.get(surf_id, {}).get("label", owner),
                "screenshot": shot, "children": children, "child_containers": child_conts,
                "explored": True,
                "purpose": f"flyout of {owner} — commands/tiles are endpoints; openers "
                           f"descended per the depth-endpoint rule{secs}"}
        self.writer.write_container(cont)
        self.explored.add(surf_id)
        self.written[surf_id] = cont
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
        cont = {"id": surf_id, "kind": "pane",
                "label": self.written.get(surf_id, {}).get("label", owner),
                "screenshot": shot, "children": uniq[:30], "child_containers": [],
                "explored": True,
                "purpose": f"the {owner} pane (docked/floating), enumerated one level — "
                           f"pane controls act on the pane's function (endpoints)"}
        self.writer.write_container(cont)
        self.explored.add(surf_id)
        self.written[surf_id] = cont
        self.j("surface-captured", surf_id, "explored", children=len(uniq))
        return cont


# ================= orchestration =================

def build_open_points(win, tab):
    """Live click points for every ribbon element that opens a surface on `tab` — split
    dropdown ZONES, combo open arrows, and plain button/menuitem rects (uia.md lesson: a
    stored split-button rect center hits the primary zone)."""
    pts = {}
    for gname, kt, leaves in en.live_leaves(win, tab):
        for el, props in leaves:
            base = r2.slugify(props.automation_id, props.name)
            ct = props.control_type
            if ct == "SplitButton":
                primary, dropdown = drv.split_zone_rects(el)
                pts[f"el:{base}"] = _center(primary or drv.zone_point(props.rect, "primary"))
                pts[f"el:{base}-dropdown"] = _center(dropdown or
                                                     drv.zone_point(props.rect, "dropdown"))
            elif ct == "ComboBox":
                pts[f"el:{base}"] = _center(en.combo_open_rect(el) or
                                            drv.zone_point(props.rect, "dropdown"))
            else:
                pts[f"el:{base}"] = _center(tuple(props.rect))
            if gname == "Styles" and ct == "Button" and props.name == "Styles":
                pts["el:styles-more"] = _center(tuple(props.rect))
    return pts


def load_layers():
    return json.loads((KB / "priority" / "layers.json").read_text(encoding="utf-8"))["layers"]


def collect_targets():
    """(surf_id, opener_el_id, tab, owner_node, recurse) for every ribbon-opened stub whose
    owning node is P0-P2 (recurse) or P3 (one level)."""
    layers = load_layers()
    p0p2 = set(layers.get("P0", []) + layers.get("P1", []) + layers.get("P2", []))
    p3 = set(layers.get("P3", []))
    subs = [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(KB.glob("subfeatures/**/*.json"))]
    el_owner = {}
    for s in subs:
        for tp in s.get("trigger_paths", []):
            if tp.get("path") and tp["path"][-1].startswith("el:"):
                el_owner[tp["path"][-1]] = s["id"]
    targets, seen = [], set()
    for tab, rid in (("Home", "ui:ribbon-home"), ("Insert", "ui:ribbon-insert")):
        ribbon = json.loads((KB / "ui" / (rid.removeprefix("ui:") + ".json"))
                            .read_text(encoding="utf-8"))
        for e in ribbon["children"]:
            surf = e.get("opens")
            if not surf or surf in seen:
                continue
            owner = el_owner.get(e.get("id"))
            if not owner:
                continue
            lay = "P0P2" if owner in p0p2 else ("P3" if owner in p3 else None)
            if not lay:
                continue
            seen.add(surf)
            targets.append((surf, e["id"], tab, owner, lay == "P0P2"))
    return targets


def enter_styles_gallery(walker, surf_id, owner):
    """Quick Styles gallery IS in the UIA tree (DataGrid 'Styles') — enumerate directly."""
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
    walker.writer.write_container(cont)
    walker.explored.add(surf_id)
    walker.written[surf_id] = cont
    walker.j("surface-captured", surf_id, "explored", children=len(children))
    return cont


def main():
    # arg: nothing = all targets; "ui:x" = one surface; "i:j" = index slice of the target list
    only = sys.argv[1] if len(sys.argv) > 1 else None
    run_id = common.make_run_id() + "-step5-enter"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    screen_w = win32api.GetSystemMetrics(0)
    pinned = json.loads((KB / "version.json").read_text(encoding="utf-8"))
    targets = collect_targets()
    if only and only.startswith("ui:"):
        targets = [t for t in targets if t[0] == only]
    elif only and ":" in only:
        i, j = only.split(":")
        targets = targets[int(i):int(j)]
    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    jrnl.append(common.journal_event(actor="stage5.depth", action="launch",
                target=f"pid={sess.pid}", outcome="ok",
                data={"targets": [(t[0], "deep" if t[4] else "P3") for t in targets]}))
    results = []
    try:
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
        sess.select_paragraph(1)
        try:
            sess.doc.Paragraphs(1).Range.Copy()     # arm clipboard (paste menu needs content)
        except Exception:
            pass
        win = ua.attach(sess.frame)
        time.sleep(0.4)
        walker = DepthWalker(sess, win, writer, jrnl, screen_w)
        open_points = {}
        for tab in ("Home", "Insert"):
            en.select_tab(win, tab)
            time.sleep(0.3)
            open_points[tab] = build_open_points(win, tab)

        for surf_id, el_id, tab, owner, recurse in targets:
            if surf_id in walker.explored:
                walker.j("enter", surf_id, "seen-already")
                continue
            if surf_id == "ui:styles-gallery":
                en.select_tab(win, "Home")
                time.sleep(0.3)
                enter_styles_gallery(walker, surf_id, owner)
                results.append({"surf": surf_id, "kind": "gallery"})
                continue
            en.select_tab(win, tab)
            time.sleep(0.35)
            point = open_points[tab].get(el_id)
            if not point:
                walker.j("enter", surf_id, "no-open-point", opener=el_id)
                continue

            def reopen(tab=tab, point=point, surf_id=surf_id):
                walker.close_all()
                en.select_tab(win, tab)
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
                if kind == "dialog" and wins.is_task_pane_window(hwnd):
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


def _unused_explore_pane_moved_to_class(self, surf_id, owner, recurse):
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
        cont = {"id": surf_id, "kind": "pane",
                "label": self.written.get(surf_id, {}).get("label", owner),
                "screenshot": shot, "children": uniq[:30], "child_containers": [],
                "explored": True,
                "purpose": f"the {owner} pane (docked/floating), enumerated one level — "
                           f"pane controls act on the pane's function (endpoints)"}
        self.writer.write_container(cont)
        self.explored.add(surf_id)
        self.written[surf_id] = cont
        self.j("surface-captured", surf_id, "explored", children=len(uniq))
        return cont
