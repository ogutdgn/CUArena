import time
from dataclasses import dataclass, field
from tools.models import JournalEvent, UIElement
from tools.winapp.uia import ElemInfo, UIASession
from tools.winapp.windows import WinInfo, top_windows, wait_new_window, classify
from tools.winapp import inputs

EXPANSION_THRESHOLD = 3   # named children appearing in-tree = a menu/dropdown expanded

@dataclass
class ProbeObservation:
    new_window: WinInfo | None
    child_delta: int
    before_windows: list[WinInfo]
    after_windows: list[WinInfo]

@dataclass
class ProbeResult:
    kind: str
    new_window: WinInfo | None = None
    expanded: list[ElemInfo] = field(default_factory=list)
    restored: bool = True

def classify_probe(obs: ProbeObservation, dialog_classes, flyout_classes) -> str:
    if obs.new_window is not None:
        k = classify(obs.new_window.cls, dialog_classes, flyout_classes)
        return "opens-flyout" if k == "flyout" else "opens-dialog"
    if obs.child_delta >= EXPANSION_THRESHOLD:
        return "expands-inline"
    return "no-effect"

def _named_children(session, depth):
    return [k for k in session.ui.children(depth=depth) if k.name.strip()]

def probe_element(session, elem: UIElement, journal, scan_depth: int = 9) -> ProbeResult:
    from pipeline.stage1_surface import DEFAULT_SCAN_DEPTH
    scan_depth = scan_depth or DEFAULT_SCAN_DEPTH
    if elem.bounds is None or (elem.bounds[2] - elem.bounds[0]) <= 0:
        journal.append(JournalEvent(actor="prober", action="probe", target=elem.id or elem.label,
                                    outcome="skipped-disabled"))
        return ProbeResult(kind="skipped")
    before_w = top_windows()
    before_c = _named_children(session, scan_depth)
    inputs.ensure_foreground(session.hwnd)
    inputs.click_rect(elem.bounds)
    new_win = wait_new_window(before_w, timeout=2.5)
    time.sleep(0.3)
    after_c = _named_children(session, scan_depth)
    obs = ProbeObservation(new_window=new_win, child_delta=len(after_c) - len(before_c),
                           before_windows=before_w, after_windows=top_windows())
    kind = classify_probe(obs, session.config.dialog_classes, session.config.flyout_classes)
    result = ProbeResult(kind=kind, new_window=new_win)
    if kind == "expands-inline":
        before_keys = {(k.name, k.rect) for k in before_c}
        result.expanded = [k for k in after_c if (k.name, k.rect) not in before_keys]
    elif kind in ("opens-dialog", "opens-flyout") and new_win is not None:
        try:
            # Attach by hwnd, not title regex: live evidence against Win11
            # Notepad's menu popup (class Microsoft.UI.Content.PopupWindowSiteBridge,
            # title literally "PopupHost") showed UIASession.attach(title_re)
            # timing out even though the window is real and enumerable --
            # Desktop(...).window(title_re=...) doesn't reliably resolve it.
            # attach_by_handle sidesteps title matching entirely using the
            # hwnd wait_new_window already gave us. General fix (tools/winapp),
            # not app-specific.
            popup = UIASession.attach_by_handle(new_win.hwnd)
            result.expanded = [k for k in popup.children(depth=4) if k.name.strip()] if popup else []
        except Exception:
            result.expanded = []
    # restore
    if kind in ("opens-dialog", "opens-flyout", "expands-inline"):
        inputs.press("{ESC}")
        time.sleep(0.3)
        if new_win is not None and any(w.hwnd == new_win.hwnd for w in top_windows()):
            import win32con, win32gui
            win32gui.PostMessage(new_win.hwnd, win32con.WM_CLOSE, 0, 0)
            time.sleep(0.4)
        result.restored = {w.hwnd for w in top_windows()} == {w.hwnd for w in before_w}
    journal.append(JournalEvent(actor="prober", action="probe", target=elem.id or elem.label,
                                outcome=kind if result.restored else f"{kind}; failed: unrestored",
                                data={"expanded": len(result.expanded)}))
    return result
