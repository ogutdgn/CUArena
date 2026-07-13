"""UIA attach + property reading, shared by every reader/driver tool.

Pinned to the toolbox lessons (toolbox/uia.md): read properties through the raw
IUIAutomationElement (wrapper attrs lie); the ribbon ScreenTip lives in FullDescription
(30159), NOT HelpText; pattern availability comes from Is<Pattern>AvailablePropertyId, not
from pywinauto iface_* attrs; AutomationId carries Office's idMso (Bold -> 'Bold',
Font launcher -> 'FontDialog') — record it always.
"""
import sys
from dataclasses import dataclass, field
from pathlib import Path

import win32gui

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
from session import force_foreground   # reuse the AttachThreadInput dance

# IUIAutomationElement Is<Pattern>AvailablePropertyId ids
_PATTERN_PROP = {
    "invoke": 30031, "toggle": 30086, "expand_collapse": 30070,
    "selection_item": 30096, "value": 30045, "range_value": 30052,
    "scroll": 30056, "legacy_i_accessible": 30090,
}
_FULL_DESCRIPTION = 30159   # ribbon ScreenTip text
INTERACTIVE = {"Button", "SplitButton", "CheckBox", "RadioButton",
               "ComboBox", "Edit", "MenuItem", "ListItem", "TabItem",
               "Spinner"}   # Spinner: Layout tab's Paragraph group (Indent/Spacing value
                            # fields) — childless leaves in the live dump (word-4tabs-v1
                            # uia_tree_layout.json); without this the whole group vanishes
ATOMIC = {"SplitButton", "ComboBox"}   # captured whole; child zones handled by the driver


def get_iuia():
    """Raw IUIAutomation singleton (for ElementFromPoint hit-testing of owner-drawn surfaces)."""
    from pywinauto.uia_defines import IUIA
    return IUIA().iuia


def attach(frame_hwnd):
    """pywinauto uia window wrapper for the frame, forced foreground."""
    from pywinauto import Desktop
    win = Desktop(backend="uia").window(handle=frame_hwnd)
    try:
        win.set_focus()
    except Exception:
        pass
    force_foreground(frame_hwnd)
    return win


@dataclass
class ControlProps:
    name: str
    automation_id: str                 # == idMso on Office ribbon controls
    control_type: str
    rect: tuple                        # (left, top, right, bottom) screen px
    patterns: list = field(default_factory=list)
    tooltip: str = ""                  # FullDescription (30159)
    access_key: str = ""               # keytip, e.g. "H, 1" (Alt overlay)
    accelerator_key: str = ""          # shortcut display, e.g. "Ctrl+B"
    is_enabled: bool = True
    is_gallery: bool = False


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


def is_gallery(el):
    """In-ribbon gallery strip: a DataGrid/List of tiles under the control (QuickStyles)."""
    return _has_descendant_type(el, {"DataGrid", "List"})


def has_interactive_descendant(el):
    try:
        kids = el.children()
    except Exception:
        return False
    for k in kids:
        if k.element_info.control_type in INTERACTIVE or has_interactive_descendant(k):
            return True
    return False


def read_props(el) -> ControlProps:
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

    try:
        enabled = bool(raw.CurrentIsEnabled)
    except Exception:
        enabled = True

    return ControlProps(
        name=ei.name or "",
        automation_id=ei.automation_id or "",
        control_type=ei.control_type or "",
        rect=(r.left, r.top, r.right, r.bottom),
        patterns=_available_patterns(raw),
        tooltip=(_p(_FULL_DESCRIPTION) or _s("CurrentHelpText")),
        access_key=_s("CurrentAccessKey"),
        accelerator_key=_s("CurrentAcceleratorKey"),
        is_enabled=enabled,
        is_gallery=is_gallery(el),
    )
