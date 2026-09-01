"""UIA attach + focus-force + pinned LOCATORS + recursive leaf enumeration.

LOCATORS and the leaf/atomic/gallery rules below were PINNED from a live UIA tree dump
of Word 16.0.20131 (T6 Step 1: run_p0.py --dump-tree), not guessed. Key live findings:
  * Ribbon nesting: Pane 'Ribbon' > Tab 'Ribbon Tabs' (TabItems) + Pane 'Lower Ribbon';
    Lower Ribbon > Group '<active tab>' (wrapper) > Group '<group label>' (real groups).
  * Leaf controls expose AutomationId == idMso (Bold->'Bold', Font...->'FontDialog').
  * Split buttons expose BOTH zones as children (Button primary + MenuItem '*_Dropdown').
  * pywinauto 'iface_*' attributes are ALWAYS present on every wrapper -> useless for
    pattern detection. Reliable method = IUIAutomationElement.GetCurrentPropertyValue on
    the Is<Pattern>AvailablePropertyId ids below.
  * Office ribbon pattern availability is quirky (Bold exposes SelectionItem not Toggle),
    so patterns are recorded for the exposure map, NOT trusted to classify at press time.
"""
import ctypes
from dataclasses import dataclass, asdict
import win32gui, win32process, win32api
from pywinauto import Desktop

LOCATORS = {                                             # verified from --dump-tree (T6 Step 1)
    "tab_strip":    {"title": "Ribbon Tabs", "control_type": "Tab"},
    "tab_item":     {"control_type": "TabItem"},         # + title=<tab label>
    "lower_ribbon": {"title": "Lower Ribbon", "control_type": "Pane"},
    "group":        {"control_type": "Group"},
}
INTERACTIVE = {"Button", "SplitButton", "CheckBox", "RadioButton",
               "ComboBox", "Edit", "MenuItem"}
# Composite controls captured as ONE atomic leaf (their child zones handled by the prober).
ATOMIC = {"SplitButton", "ComboBox"}

# IUIAutomationElement Is<Pattern>AvailablePropertyId ids (UIA_* property ids).
_PATTERN_PROP = {
    "invoke": 30031, "toggle": 30086, "expand_collapse": 30070,
    "selection_item": 30096, "value": 30045, "range_value": 30052,
    "scroll": 30056, "legacy_i_accessible": 30090,
}


@dataclass
class ControlProps:
    name: str
    automation_id: str
    control_type: str
    patterns: list
    rect: tuple
    help_text: str
    access_key: str          # keytip (Alt overlay), e.g. "Alt, H, 1"
    accelerator_key: str     # shortcut, e.g. "Ctrl+B"
    is_gallery: bool


def _force_foreground(hwnd):
    if win32gui.GetForegroundWindow() == hwnd:
        return
    fg = win32gui.GetForegroundWindow()
    t1, _ = win32process.GetWindowThreadProcessId(fg)
    t2 = win32api.GetCurrentThreadId()
    ctypes.windll.user32.AttachThreadInput(t1, t2, True)
    try:
        win32gui.SetForegroundWindow(hwnd)
    finally:
        ctypes.windll.user32.AttachThreadInput(t1, t2, False)


def _frame_hwnd(pid):
    """The process's top-level 'OpusApp' frame -- the window that hosts the ribbon. Word can
    own >1 top-level window (startup panes) and ActiveWindow.Hwnd is not always the frame, so
    target OpusApp explicitly (there is exactly one)."""
    found = []

    def cb(h, _):
        try:
            _, wp = win32process.GetWindowThreadProcessId(h)
            if wp == pid and win32gui.IsWindowVisible(h) and win32gui.GetClassName(h) == "OpusApp":
                found.append(h)
        except Exception:
            pass
        return True

    win32gui.EnumWindows(cb, None)
    return found[0] if found else None


def attach(session):
    hwnd = _frame_hwnd(session.pid) or session._hwnd()
    win = Desktop(backend="uia").window(handle=hwnd)
    win.set_focus()
    _force_foreground(hwnd)
    return win


def _available_patterns(raw):
    out = []
    for name, pid in _PATTERN_PROP.items():
        try:
            if raw.GetCurrentPropertyValue(pid):
                out.append(name)
        except Exception:
            pass
    return out


def _has_descendant_type(el, types, _depth=0):
    if _depth > 6:
        return False
    try:
        kids = el.children()
    except Exception:
        return False
    for k in kids:
        if k.element_info.control_type in types:
            return True
        if _has_descendant_type(k, types, _depth + 1):
            return True
    return False


def _is_gallery(el):
    # In-ribbon gallery strip: a DataGrid/List of tiles under the control (e.g. QuickStyles).
    return _has_descendant_type(el, {"DataGrid", "List"})


def _has_interactive_descendant(el):
    try:
        kids = el.children()
    except Exception:
        return False
    for k in kids:
        if k.element_info.control_type in INTERACTIVE or _has_interactive_descendant(k):
            return True
    return False


def _props(el):
    ei = el.element_info
    raw = ei.element
    r = ei.rectangle

    def _s(attr):
        try:
            return getattr(raw, attr, "") or ""
        except Exception:
            return ""

    def _p(pid):
        try:
            return raw.GetCurrentPropertyValue(pid) or ""
        except Exception:
            return ""

    # Ribbon ScreenTip text lives in UIA FullDescription (30159), NOT HelpText (which is empty even
    # on hover) — e.g. Bold's FullDescription is "Make your text bold." (bug #6).
    tooltip = _p(30159) or _s("CurrentHelpText")
    return ControlProps(
        name=ei.name or "", automation_id=ei.automation_id or "",
        control_type=ei.control_type or "", patterns=_available_patterns(raw),
        rect=(r.left, r.top, r.right, r.bottom),
        help_text=tooltip, access_key=_s("CurrentAccessKey"),
        accelerator_key=_s("CurrentAcceleratorKey"), is_gallery=_is_gallery(el))


def _leaves(el, acc):
    """Collect interactive leaves. Composite controls (SplitButton/ComboBox) and in-ribbon
    galleries are ATOMIC (kept whole); other interactive nodes with interactive descendants
    are descended into."""
    ct = el.element_info.control_type
    if ct in INTERACTIVE:
        if ct in ATOMIC or _is_gallery(el) or not _has_interactive_descendant(el):
            acc.append(el)
            return
    try:
        kids = el.children()
    except Exception:
        kids = []
    for k in kids:
        _leaves(k, acc)


def select_tab(win, tab_name):
    tab = win.child_window(title=tab_name, **LOCATORS["tab_item"])
    tab.click_input()


def _real_groups(win, tab_name):
    lower = win.child_window(**LOCATORS["lower_ribbon"])
    wrapper = lower.child_window(title=tab_name, control_type="Group")
    return [g for g in wrapper.children() if g.element_info.control_type == "Group"]


def enumerate_tab(win, tab_name):
    select_tab(win, tab_name)
    groups = []
    for g in _real_groups(win, tab_name):
        acc = []
        for child in g.children():
            _leaves(child, acc)
        seen, controls = set(), []
        for c in acc:
            rid = c.element_info.runtime_id
            key = tuple(rid) if rid else id(c)
            if key in seen:
                continue
            seen.add(key)
            controls.append(asdict(_props(c)))
        groups.append({"name": g.element_info.name, "controls": controls})
    return {"tab": tab_name, "groups": groups}
