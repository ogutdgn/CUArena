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
