"""WordSession — an isolated Word instance we fully own, by PID.

Pattern proven by references/word-crawler/launcher.py; re-implemented here (not copied)
and pinned to THIS machine. Three jobs only (see toolbox/com.md): (1) launch a NEW
instance and own its pid via a process-set delta, (2) open a scratch fixture and reach a
deterministic workspace, (3) expose state fingerprints (doc hash + selection format sig +
app fingerprint) so later steps can measure what a press changed. We never drive the UI
through COM — that would measure the API, not the UI.
"""
import ctypes
import hashlib
import subprocess
import time

import psutil
import win32api
import win32com.client
import win32con
import win32gui
import win32process


def _winword_pids():
    return {p.pid for p in psutil.process_iter(["name"])
            if (p.info["name"] or "").lower() == "winword.exe"}


def frame_hwnd(pid):
    """The process's top-level 'OpusApp' frame — the window hosting the ribbon. Word can own
    several top-level windows at startup and ActiveWindow.Hwnd is not always the frame, so
    target the OpusApp class explicitly (there is exactly one)."""
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


def force_foreground(hwnd):
    """SetForegroundWindow is refused unless our thread's input queue is attached to the
    current foreground thread first (the AttachThreadInput dance)."""
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


class WordSession:
    @classmethod
    def start(cls, fixture, expected_build=None):
        self = cls()
        pre = _winword_pids()
        self.app = win32com.client.DispatchEx("Word.Application")   # DispatchEx = NEW instance
        new = set()
        for _ in range(80):
            new = _winword_pids() - pre
            if new:
                break
            time.sleep(0.1)
        assert len(new) == 1, f"expected exactly 1 new WINWORD pid, got {new}"
        self.pid = new.pop()
        try:
            self.app.Visible = True
            self.doc = self.app.Documents.Open(str(fixture), ReadOnly=False)
            self.build = str(self.app.Build)
            self.version = str(self.app.Version)
            if expected_build:
                assert self.build.startswith(expected_build), \
                    f"build drift: running {self.build}, pinned {expected_build}"
            self._disconnect_addins()
            self._move_to_primary()
            self.app.ActiveWindow.WindowState = 1        # wdWindowStateMaximize
            self.app.ActiveWindow.View.Type = 3          # wdPrintView
            self._assert_primary_monitor()
            self.frame = frame_hwnd(self.pid) or self.app.ActiveWindow.Hwnd
            assert self.frame, "no OpusApp frame window found"
        except Exception:
            self.close()
            raise
        return self

    def _disconnect_addins(self):
        try:
            for i in range(1, self.app.COMAddIns.Count + 1):
                try:
                    self.app.COMAddIns.Item(i).Connect = False
                except Exception:
                    pass
        except Exception:
            pass

    def _hwnd(self):
        return self.app.ActiveWindow.Hwnd

    def _move_to_primary(self):
        """Word may open on a secondary monitor. The primary monitor's origin is (0,0) in
        virtual coords, so restore + move to (0,0), then maximize snaps to it."""
        hwnd = self._hwnd()
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0,
                                  win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
        except Exception:
            pass

    def _assert_primary_monitor(self):
        mon = win32api.MonitorFromWindow(self._hwnd(), win32con.MONITOR_DEFAULTTONEAREST)
        info = win32api.GetMonitorInfo(mon)
        assert info["Flags"] & 1, "Word is not on the PRIMARY monitor"

    # --- state fingerprints (the truth oracle for 'did the press change anything?') -----
    def doc_hash(self):
        try:
            return hashlib.sha256(self.doc.Content.Text.encode("utf-8", "replace")).hexdigest()
        except Exception:
            return "<com-busy>"

    def format_sig(self):
        """Selection formatting fingerprint — catches formatting-only presses (Bold, Grow
        Font, indent, color, highlight, shading, borders) that leave Content.Text unchanged.
        None when COM is busy. Highlight/shading/borders were added after Step 2 measured
        those primary-applies as false 'no-effect' — they live outside Font/ParagraphFormat."""
        try:
            sel = self.app.Selection
            f, p = sel.Font, sel.ParagraphFormat

            def _try(fn, default=-1):
                try:
                    return fn()
                except Exception:
                    return default
            hl = _try(lambda: int(sel.Range.HighlightColorIndex))
            sh = _try(lambda: int(p.Shading.BackgroundPatternColor))
            borders = tuple(_try(lambda i=i: int(sel.Range.Borders(i).LineStyle))
                            for i in (-1, -2, -3, -4))   # top/left/bottom/right
            sig = (int(f.Bold), int(f.Italic), int(f.Underline),
                   float(f.Size) if f.Size not in (None, "") else -1.0, str(f.Name),
                   int(f.Color), int(f.StrikeThrough), int(f.Subscript), int(f.Superscript),
                   int(p.Alignment), float(p.LeftIndent), float(p.FirstLineIndent),
                   hl, sh, borders)
            return hashlib.sha1(repr(sig).encode("utf-8", "replace")).hexdigest()[:16]
        except Exception:
            return None

    def app_fingerprint(self):
        try:
            v = self.app.ActiveWindow.View
            return {"track_revisions": bool(self.doc.TrackRevisions),
                    "view_type": int(v.Type), "zoom": int(v.Zoom.Percentage),
                    "rulers": bool(self.app.ActiveWindow.DisplayRulers),
                    "show_all": bool(v.ShowAll)}
        except Exception:
            return {}

    def object_fingerprint(self):
        """Object-count fingerprint — the Insert tab's effects live here, NOT in Content.Text
        or the format signature: tables, pictures (InlineShapes), text boxes/WordArt (Shapes),
        comments, bookmarks, equations (OMaths), fields, sections. Without these counts,
        object-inserting presses measure as false 'no-effect' (com.md lesson, widened)."""
        def _c(fn):
            try:
                return int(fn())
            except Exception:
                return -1
        try:
            d = self.doc
            return {"tables": _c(lambda: d.Tables.Count),
                    "inline_shapes": _c(lambda: d.InlineShapes.Count),
                    "shapes": _c(lambda: d.Shapes.Count),
                    "comments": _c(lambda: d.Comments.Count),
                    "bookmarks": _c(lambda: d.Bookmarks.Count),
                    "omaths": _c(lambda: d.OMaths.Count),
                    "fields": _c(lambda: d.Fields.Count),
                    "sections": _c(lambda: d.Sections.Count),
                    "hyperlinks": _c(lambda: d.Hyperlinks.Count)}
        except Exception:
            return {}

    def select_paragraph(self, n=1):
        """Select paragraph n. No-op when COM is busy (a modal dialog is up) — the caller
        relies on window-delta, not format_sig, in that case. Returns True on success."""
        try:
            self.doc.Paragraphs(n).Range.Select()
            return True
        except Exception:
            return False

    def top_level_windows(self):
        """Visible top-level windows owned by our pid: (hwnd, class, title, rect)."""
        out = []

        def cb(h, _):
            try:
                _, wp = win32process.GetWindowThreadProcessId(h)
                if wp == self.pid and win32gui.IsWindowVisible(h):
                    out.append((h, win32gui.GetClassName(h),
                                win32gui.GetWindowText(h), win32gui.GetWindowRect(h)))
            except Exception:
                pass
            return True

        win32gui.EnumWindows(cb, None)
        return out

    def frame_rect(self):
        return win32gui.GetWindowRect(self.frame)

    def close(self):
        """Independent teardown steps: a stuck modal makes doc.Close()/Quit() report busy, so
        the PID-targeted taskkill is the guaranteed cleanup. NEVER kill by name — that would
        murder the user's own Word instance."""
        try:
            if getattr(self, "doc", None):
                self.doc.Close(SaveChanges=0)          # 0 = wdDoNotSaveChanges
        except Exception:
            pass
        try:
            if getattr(self, "app", None):
                self.app.Quit()
        except Exception:
            pass
        time.sleep(1)
        if getattr(self, "pid", None):
            subprocess.run(["taskkill", "/PID", str(self.pid), "/F"], capture_output=True)
