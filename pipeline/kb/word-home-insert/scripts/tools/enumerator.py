"""enumerator — read a Word command surface into structured controls.

LOCATORS below were PINNED from a live UIA tree dump of Word 16.0.20131 on this machine
(tools/dumps/uia_tree_home.*), not guessed. Live findings that shaped them:
  * Ribbon: Pane 'Lower Ribbon' > Group '<tab>' (wrapper) > Group '<group label>' (real groups).
  * Leaf controls expose AutomationId == idMso (Bold->'Bold', Font...->'FontDialog').
  * SplitButton/ComboBox are ATOMIC composites; in-ribbon galleries (DataGrid/List) are atomic too.
  * ScreenTip text is FullDescription (30159); shortcut is AcceleratorKey; keytip is AccessKey.
"""
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import uia_attach as ua

LOCATORS = {
    "tab_strip":    {"title": "Ribbon Tabs", "control_type": "Tab"},
    "tab_item":     {"control_type": "TabItem"},           # + title=<tab label>
    "lower_ribbon": {"title": "Lower Ribbon", "control_type": "Pane"},
    "qat":          {"title": "Quick Access Toolbar", "control_type": "ToolBar"},
}


def select_tab(win, tab_name):
    tab = win.child_window(title=tab_name, **LOCATORS["tab_item"])
    tab.click_input()
    import time
    time.sleep(0.4)


def real_groups(win, tab_name):
    """The real ribbon groups: Group children of the active-tab wrapper Group under Lower Ribbon.
    Contextual tabs may name their wrapper differently — fall back to the single Group child of
    Lower Ribbon (there is exactly one wrapper: the active tab's)."""
    lower = win.child_window(**LOCATORS["lower_ribbon"])
    try:
        wrapper = lower.child_window(title=tab_name, control_type="Group")
        return [g for g in wrapper.children() if g.element_info.control_type == "Group"]
    except Exception:
        wrappers = [g for g in lower.children() if g.element_info.control_type == "Group"]
        if len(wrappers) == 1:
            return [g for g in wrappers[0].children()
                    if g.element_info.control_type == "Group"]
        raise


def _leaves(el, acc):
    """Interactive leaves. SplitButton/ComboBox and in-ribbon galleries are atomic; other
    interactive nodes with interactive descendants are descended into."""
    ct = el.element_info.control_type
    if ct in ua.INTERACTIVE:
        if ct in ua.ATOMIC or ua.is_gallery(el) or not ua.has_interactive_descendant(el):
            acc.append(el)
            return
    try:
        kids = el.children()
    except Exception:
        kids = []
    for k in kids:
        _leaves(k, acc)


def _dedupe(leaves):
    seen, out = set(), []
    for c in leaves:
        rid = c.element_info.runtime_id
        key = tuple(rid) if rid else id(c)
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


def _backfill_id(el, props):
    """A SplitButton's own AutomationId can be empty (e.g. Paste) while its primary child carries
    the idMso — pull it from the primary Button child (not the '*_Dropdown' MenuItem)."""
    if props.automation_id or props.control_type not in ua.ATOMIC:
        return props
    try:
        for k in el.children():
            ei = k.element_info
            if ei.control_type == "Button" and ei.automation_id:
                props.automation_id = ei.automation_id
                break
    except Exception:
        pass
    return props


def enumerate_group(g):
    acc = []
    for child in g.children():
        _leaves(child, acc)
    controls = []
    for c in _dedupe(acc):
        p = _backfill_id(c, ua.read_props(c))
        controls.append(asdict(p))
    return {"group": g.element_info.name,
            "group_keytip": (ua.read_props(g).access_key),
            "controls": controls}


def enumerate_tab(win, tab_name):
    """Full enumeration of one ribbon tab: every group, every interactive leaf control."""
    select_tab(win, tab_name)
    groups = [enumerate_group(g) for g in real_groups(win, tab_name)]
    total = sum(len(g["controls"]) for g in groups)
    return {"tab": tab_name, "groups": groups, "control_count": total}


def live_leaves(win, tab_name):
    """Like enumerate_tab but keeps the LIVE element handle per control (needed to read exact
    split-button / combo zone rects at press time). Returns [(group_name, keytip, [(el, props)])]."""
    select_tab(win, tab_name)
    out = []
    for g in real_groups(win, tab_name):
        acc = []
        for child in g.children():
            _leaves(child, acc)
        leaves = []
        for c in _dedupe(acc):
            leaves.append((c, _backfill_id(c, ua.read_props(c))))
        out.append((g.element_info.name, ua.read_props(g).access_key, leaves))
    return out


def combo_open_rect(el):
    """The dropdown 'Open' button rect of a ComboBox (Font / Font Size)."""
    try:
        for k in el.children():
            ei = k.element_info
            if ei.control_type == "Button":
                r = ei.rectangle
                return (r.left, r.top, r.right, r.bottom)
    except Exception:
        pass
    return None


def enumerate_container_leaves(container_el):
    """Generic: interactive leaves of any container (dialog/pane/menu) — reused by Step 2/5."""
    acc = []
    for child in container_el.children():
        _leaves(child, acc)
    return [asdict(ua.read_props(c)) for c in _dedupe(acc)]
