import hashlib, subprocess, time
import psutil, win32com.client, win32gui, win32api, win32con, win32process
import config


def _winword_pids():
    return {p.pid for p in psutil.process_iter(["name"])
            if (p.info["name"] or "").lower() == "winword.exe"}


class WordSession:
    @classmethod
    def start(cls, fixture=None):
        self = cls()
        pre = _winword_pids()
        self.app = win32com.client.DispatchEx("Word.Application")   # NEW instance
        for _ in range(50):
            new = _winword_pids() - pre
            if new:
                break
            time.sleep(0.1)
        assert len(new) == 1, f"expected 1 new WINWORD, got {new}"
        self.pid = new.pop()
        try:
            self.app.Visible = True
            self.doc = (self.app.Documents.Open(str(fixture), ReadOnly=False)
                        if fixture else self.app.Documents.Add())
            assert self.app.Build.startswith(config.BUILD_PREFIX), f"build drift: {self.app.Build}"
            self._disconnect_addins()
            self.app.ActiveWindow.WindowState = 1        # wdWindowStateMaximize
            self.app.ActiveWindow.View.Type = 3          # wdPrintView
            self._assert_primary_monitor()
        except Exception:
            self.close()
            raise
        return self

    def _disconnect_addins(self):
        for i in range(1, self.app.COMAddIns.Count + 1):
            try:
                self.app.COMAddIns.Item(i).Connect = False
            except Exception:
                pass

    def _hwnd(self):
        return self.app.ActiveWindow.Hwnd

    def _assert_primary_monitor(self):
        mon = win32api.MonitorFromWindow(self._hwnd(), win32con.MONITOR_DEFAULTTONEAREST)
        info = win32api.GetMonitorInfo(mon)
        assert info["Flags"] & 1, "Word is not on the PRIMARY monitor — move it and rerun"

    def doc_hash(self):
        return hashlib.sha256(self.doc.Content.Text.encode("utf-8", "replace")).hexdigest()

    def format_sig(self):
        """Formatting fingerprint of the current selection. doc_hash (text only) misses
        FORMATTING features (Grow Font, Clear Formatting, indent, color) -- this catches them
        as a COM app-state delta (DESIGN section 4.2 positive evidence). None on COM-busy."""
        try:
            sel = self.app.Selection
            f, p = sel.Font, sel.ParagraphFormat
            sig = (int(f.Bold), int(f.Italic), int(f.Underline),
                   float(f.Size) if f.Size not in (None, "") else -1.0, str(f.Name),
                   int(f.Color), int(f.StrikeThrough), int(f.Subscript), int(f.Superscript),
                   int(p.Alignment), float(p.LeftIndent), float(p.FirstLineIndent))
            return hashlib.sha1(repr(sig).encode("utf-8", "replace")).hexdigest()[:16]
        except Exception:
            return None

    def _addins_connected(self):
        return sum(1 for i in range(1, self.app.COMAddIns.Count + 1)
                   if self.app.COMAddIns.Item(i).Connect)

    def app_fingerprint(self):
        v = self.app.ActiveWindow.View
        return {"track_revisions": bool(self.doc.TrackRevisions),
                "view_type": int(v.Type), "zoom": int(v.Zoom.Percentage),
                "rulers": bool(self.app.ActiveWindow.DisplayRulers),
                "show_all": bool(v.ShowAll), "addins_connected": self._addins_connected()}

    def select_paragraph(self, n):
        self.doc.Paragraphs(n).Range.Select()

    def copy_fixture_text(self):
        rng = self.doc.Paragraphs(1).Range
        rng.Copy()
        return rng.Text

    def assert_foreground(self):
        return win32gui.GetForegroundWindow() == self._hwnd()

    def close(self):
        # Each COM step is independent: a stuck modal dialog makes doc.Close() report
        # 'application is busy', but taskkill (below) is the guaranteed PID-safe cleanup.
        try:
            if getattr(self, "doc", None):
                self.doc.Close(SaveChanges=0)
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
