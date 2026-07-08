from dataclasses import dataclass
from pywinauto import Desktop


@dataclass
class ElemInfo:
    control_type: str
    name: str
    rect: tuple[int, int, int, int]
    auto_id: str


def _info(w) -> ElemInfo:
    r = w.rectangle()
    return ElemInfo(control_type=w.element_info.control_type or "unknown",
                    name=w.element_info.name or "",
                    rect=(r.left, r.top, r.right, r.bottom),
                    auto_id=w.element_info.automation_id or "")


class UIASession:
    def __init__(self, window):
        self._win = window

    @classmethod
    def attach(cls, title_re: str) -> "UIASession":
        win = Desktop(backend="uia").window(title_re=title_re)
        win.wait("exists ready", timeout=10)
        return cls(win)

    @classmethod
    def attach_by_handle(cls, hwnd: int) -> "UIASession":
        # Some windows (observed: Win11 Notepad's menu, a
        # Microsoft.UI.Content.PopupWindowSiteBridge host titled generically
        # "PopupHost") aren't reliably found by Desktop(...).window(title_re=...)
        # -- the title-based search can time out even though the window is
        # live and enumerable by top_windows(). Attaching directly by hwnd,
        # which we already have from wait_new_window, is a general and more
        # robust alternative that sidesteps title matching entirely.
        win = Desktop(backend="uia").window(handle=hwnd)
        # Evidence (live Win11 Notepad popup menu, captured via probe_element
        # under both bare-script and pytest invocation): waiting only for
        # "exists" lets a WinUI/UWP popup's window handle be enumerable and
        # attachable before its internal UIA content tree has finished
        # populating, so an immediate children() scan intermittently returns
        # 0 named elements even though the same popup, scanned a beat later,
        # reliably yields the full menu (observed both empty and 14-element
        # results from back-to-back runs with no code change). "ready" (the
        # same condition attach() already waits for) additionally requires
        # visible+enabled, which is a strictly safe superset for any popup
        # window in general, not just Notepad's.
        win.wait("exists ready", timeout=10)
        return cls(win)

    def info(self) -> ElemInfo:
        return _info(self._win)

    def window_rect(self):
        return self.info().rect

    def children(self, depth: int = 1) -> list[ElemInfo]:
        out, frontier = [], [(self._win, 0)]
        while frontier:
            node, d = frontier.pop(0)
            for ch in node.children():
                out.append(_info(ch))
                if d + 1 < depth:
                    frontier.append((ch, d + 1))
        return out
