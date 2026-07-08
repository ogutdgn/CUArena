from pathlib import Path
from tools.models import Icon, JournalEvent, UIContainer, UIElement
from tools.kb_writer import KBWriter
from tools.journal import Journal
from tools.winapp.uia import ElemInfo
from tools.winapp import capture

# Evidence from a diagnostic run against a real Win11 store-app UIA tree:
# depth=3 (37 nodes) never surfaces the menu-bar items; depth=4 (42 nodes)
# is the first depth where they appear; depth=5 (50 nodes) still finds them
# with one level of margin. This is a general knob -- not app-specific
# logic. The default is raised from the original depth=3 to depth=5 so the
# surface scan reaches menu-bar items on modern deep UIA trees.
DEFAULT_SCAN_DEPTH = 5

def build_surface(window_info: ElemInfo, children: list[ElemInfo], app: str,
                   exclude_labels: tuple = ()) -> UIContainer:
    elements = [
        UIElement(control_type=k.control_type.lower(), label=k.name,
                  icon=Icon(description="not captured", image=None),
                  bounds=k.rect, source="uia", unexplored=True)
        for k in children if k.name.strip() and k.name not in exclude_labels
    ]
    return UIContainer(id="ui:main-window", kind="window", label=window_info.name or app,
                       children=elements)

def scan_surface(session, writer: KBWriter, journal: Journal, max_containers: int = 50) -> list[Path]:
    win_info = session.ui.info()
    children = session.ui.children(depth=DEFAULT_SCAN_DEPTH)
    exclude_labels = tuple(session.config.boundaries.exclude_labels)
    container = build_surface(win_info, children, app=session.config.name,
                               exclude_labels=exclude_labels)
    img = capture.grab_region(win_info.rect)
    container.screenshot = writer.save_screenshot(img, container.id, "full")
    path = writer.write_container(container)
    journal.append(JournalEvent(actor="stage1.surface", action="scan-container", target=container.id,
                                outcome="ok", data={"elements": len(container.children)}))
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
