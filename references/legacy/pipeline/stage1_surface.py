from pathlib import Path
from tools.models import Icon, JournalEvent, UIContainer, UIElement
from tools.kb_writer import KBWriter
from tools.journal import Journal
from tools.winapp.uia import ElemInfo
from tools.winapp import capture
from tools.ids import slug, element_id

# Evidence from a diagnostic run against a real Win11 store-app UIA tree:
# depth=3 (37 nodes) never surfaces the menu-bar items; depth=4 (42 nodes)
# is the first depth where they appear; depth=5 (50 nodes) still finds them
# with one level of margin. This is a general knob -- not app-specific
# logic. The default is raised from the original depth=3 to depth=5 so the
# surface scan reaches menu-bar items on modern deep UIA trees.
#
# Plan A addendum evidence (ready-state Word, launched directly into the
# workspace via fixture document, live diagnostic walk of the attached
# window's UIA tree depth by depth): depth=7 (54 nodes, 42 named) still has
# zero ribbon-tab hits; depth=8 (78 nodes, 66 named) is the first depth
# where all ribbon tab names appear (Home/Insert/Design/Layout/References/
# Mailings/Review/View/Help/Acrobat, or localized equivalents e.g. Giris/
# Ekle on Turkish-locale Office); depth=9 additionally surfaces the ribbon
# command groups within the active tab (Clipboard/Font/Paragraph/Styles/
# Editing/...), which is the feature-bearing content stage1_agent needs.
# Raised again from 5 to 9 (first-appear depth 8 + one level of margin,
# same margin policy as the original depth=3->5 decision) so the workspace
# scan reaches ribbon commands, not just ribbon tab chrome.
DEFAULT_SCAN_DEPTH = 9

def assign_ids(container_id: str, infos: list[ElemInfo], exclude_labels: tuple = ()) -> list[UIElement]:
    counts: dict[str, int] = {}
    elements = []
    for k in infos:
        if not k.name.strip() or k.name in exclude_labels:
            continue
        s = slug(k.name)
        elements.append(UIElement(
            id=element_id(container_id, k.name, counts.get(s, 0)),
            control_type=k.control_type.lower(), label=k.name,
            icon=Icon(description="not captured", image=None),
            bounds=k.rect, source="uia", unexplored=True))
        counts[s] = counts.get(s, 0) + 1
    return elements

def build_surface(window_info: ElemInfo, children: list[ElemInfo], app: str,
                   exclude_labels: tuple = ()) -> UIContainer:
    elements = assign_ids("ui:main-window", children, exclude_labels)
    return UIContainer(id="ui:main-window", kind="window", label=window_info.name or app,
                       children=elements)

def scan_surface(session, writer: KBWriter, journal: Journal, max_containers: int = 50) -> list[Path]:
    win_info = session.ui.info()
    children = session.ui.children(depth=DEFAULT_SCAN_DEPTH)
    exclude_labels = tuple(session.config.boundaries.exclude_labels)
    container = build_surface(win_info, children, app=session.config.name,
                               exclude_labels=exclude_labels)
    img, method = capture.grab_window(session.hwnd)
    container.screenshot = writer.save_screenshot(img, container.id, "full")
    path = writer.write_container(container)
    journal.append(JournalEvent(actor="stage1.surface", action="scan-container", target=container.id,
                                outcome="ok",
                                data={"elements": len(container.children), "capture_method": method}))
    skipped = [k.name for k in children if not k.name.strip()]
    if skipped:
        journal.append(JournalEvent(actor="stage1.surface", action="scan-container", target=container.id,
                                    outcome="skipped-unnamed", data={"count": len(skipped)}))
    excluded = [k.name for k in children if k.name.strip() and k.name in exclude_labels]
    if excluded:
        journal.append(JournalEvent(actor="stage1.surface", action="scan-container", target=container.id,
                                    outcome="skipped-excluded",
                                    data={"count": len(excluded), "labels": excluded}))
    return [path]
