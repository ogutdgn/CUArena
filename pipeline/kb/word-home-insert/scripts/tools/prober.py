"""prober — press-observe-classify-reset a single control, measured not assumed.

The classification precedence and the reset discipline are the hard-won core (toolbox/win32.md,
input.md, com.md, journal.md):
  1. new dialog-class window       -> opens a dialog
  2. new flyout-class window       -> opens a dropdown/menu
  3. docked-pane count grew        -> opens a pane
  4. doc/format/app-state changed  -> triggers a feature (opened no UI)
  5. nothing observable            -> no-effect / ambiguous (journaled honestly)
Markers come ONLY from a measured outcome. Restore is action-specific; every control is
reset-verified back to baseline before the next one, or one stuck surface corrupts the rest.
"""
import sys
import time
from pathlib import Path

import win32gui

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import driver as drv
import windows as wins


def snapshot(sess, screen_w):
    return {
        "hwnds": wins.snapshot_hwnds(sess.pid),
        "doc_hash": sess.doc_hash(),
        "format_sig": sess.format_sig(),
        "app_fp": sess.app_fingerprint(),
        "objects": sess.object_fingerprint(),
        "panes": wins.count_docked_panes(sess.frame, screen_w)[0],
    }


def observe(sess, before_hwnds, kind_hint=None, min_wait=0.8, max_wait=5.0):
    """Poll new top-level windows until the set is stable across two reads (windows appear late)."""
    t0 = time.time()
    prev = None
    stable = []
    while time.time() - t0 < max_wait:
        time.sleep(0.25)
        cur = [w for w in wins.new_windows(sess.pid, before_hwnds)]
        cur_ids = tuple(sorted(w[0] for w in cur))
        if cur_ids == prev and (time.time() - t0) >= min_wait:
            stable = cur
            break
        prev = cur_ids
        stable = cur
    return stable


def _real_new_windows(new_win_list):
    """Filter out tiny tooltip/screentip popups by area; keep dialogs and real flyouts."""
    out = []
    for h, cls, title, r in new_win_list:
        k = wins.classify_window(cls, title, r)
        if k == "tooltip":
            continue
        out.append((h, cls, title, r, k))
    return out


def _state_changes(before, after):
    changed = []
    if before["doc_hash"] != after["doc_hash"] and "<com-busy>" not in (before["doc_hash"], after["doc_hash"]):
        changed.append("doc")
    if before["format_sig"] != after["format_sig"] and None not in (before["format_sig"], after["format_sig"]):
        changed.append("format")
    if before["app_fp"] != after["app_fp"] and before["app_fp"] and after["app_fp"]:
        changed.append("app:" + ",".join(k for k in after["app_fp"]
                                          if before["app_fp"].get(k) != after["app_fp"].get(k)))
    bo, ao = before.get("objects") or {}, after.get("objects") or {}
    if bo and ao and bo != ao:
        changed.append("objects:" + ",".join(f"{k}{bo.get(k)}->{ao.get(k)}"
                                             for k in ao if bo.get(k) != ao.get(k)))
    return changed


def classify(before, after, new_windows):
    """Return (kind, detail). kind in {dialog, flyout, pane, feature, no-effect}.

    Precedence (toolbox/win32.md): dialog first (a modal is unambiguous and blocks COM). Then a
    committed doc/format/app STATE change beats a coincident flyout — transient live-preview /
    screentip popups of flyout class intermittently appear and would otherwise mask real
    formatting features (e.g. Justify). Then real flyouts, then panes, then unclassified windows."""
    real = _real_new_windows(new_windows)
    dialogs = [w for w in real if w[4] == "dialog"]
    flyouts = [w for w in real if w[4] == "flyout"]
    others = [w for w in real if w[4] == "other"]

    if dialogs:
        h, cls, title, r, _ = max(dialogs, key=lambda w: wins._area(w[3]))
        return "dialog", {"hwnd": h, "class": cls, "title": title, "rect": list(r)}
    changed = _state_changes(before, after)
    if changed:
        return "feature", {"state_changed": changed}
    if flyouts:
        h, cls, title, r, _ = max(flyouts, key=lambda w: wins._area(w[3]))
        return "flyout", {"hwnd": h, "class": cls, "title": title, "rect": list(r)}
    if after["panes"] > before["panes"]:
        return "pane", {"panes_before": before["panes"], "panes_after": after["panes"]}
    # a non-classified 'other' top-level window that persisted counts as a dialog-like surface
    if others:
        h, cls, title, r, _ = max(others, key=lambda w: wins._area(w[3]))
        return "dialog", {"hwnd": h, "class": cls, "title": title, "rect": list(r),
                          "note": "unclassified top-level accepted as dialog"}
    return "no-effect", {}


def restore(sess, kind, detail, click_pt, baseline, screen_w):
    """Action-specific restore, then verify baseline. Returns (reset_ok, notes)."""
    notes = []
    if kind in ("dialog", "flyout"):
        h = detail.get("hwnd")
        # close by Cancel/Close button first, then ESC, verify gone
        _close_window(sess, h, notes)
    elif kind == "pane":
        if detail.get("floating") and detail.get("hwnd"):
            _close_pane_window(sess, detail["hwnd"], notes)   # floating pane: its own window
        _close_panes(sess, notes)                              # docked panes: frame header button
    elif kind == "feature":
        sc = detail.get("state_changed", [])
        doc_or_fmt = any(x.startswith(("doc", "format", "objects")) for x in sc)
        app_only = (not doc_or_fmt) and any(x.startswith("app") for x in sc)
        if doc_or_fmt:
            # Ctrl+Z is the universal undo for document AND formatting AND object insertions.
            # Re-press does NOT undo a non-toggle apply (font color), so never use it for resets.
            for _ in range(6):
                drv.send_keys("^z")
                time.sleep(0.25)
                sess.select_paragraph(1)
                if (sess.doc_hash() == baseline["doc_hash"]
                        and sess.format_sig() == baseline["format_sig"]
                        and sess.object_fingerprint() == baseline.get("objects")):
                    break
            notes.append("ctrl+z")
        elif app_only:
            # a view toggle (Show All) — Ctrl+Z won't undo it; re-press to toggle back
            drv.ensure_frame_foreground(sess.frame)
            drv.click_point(*click_pt)
            time.sleep(0.2)
            notes.append("re-press view-toggle")
    elif kind == "no-effect":
        # a press that showed nothing may have armed a mode (Format Painter) — ESC to cancel
        drv.ensure_frame_foreground(sess.frame)
        drv.press_escape(1)
        notes.append("esc(no-effect)")
    # final verify — always compare the full baseline on the same selection
    sess.select_paragraph(1)
    after = snapshot(sess, screen_w)

    def _match(a, b):
        return (a["hwnds"] == b["hwnds"] and a["panes"] == b["panes"]
                and a["doc_hash"] == b["doc_hash"] and a["format_sig"] == b["format_sig"]
                and a["app_fp"] == b["app_fp"] and a.get("objects") == b.get("objects"))
    ok = _match(after, baseline)
    if not ok:
        notes.append(f"reset-mismatch hwnds={after['hwnds']==baseline['hwnds']} "
                     f"panes={after['panes']==baseline['panes']} "
                     f"doc={after['doc_hash']==baseline['doc_hash']} "
                     f"fmt={after['format_sig']==baseline['format_sig']} "
                     f"app={after['app_fp']==baseline['app_fp']}")
        # last-resort: ESC + close panes to unstick surfaces; only undo if the DOCUMENT drifted
        # (blind Ctrl+Z here could roll back the pre-formatting baseline and cascade).
        drv.press_escape(3)
        _close_panes(sess, notes)
        doc_drift = (after["doc_hash"] != baseline["doc_hash"]
                     and "<com-busy>" not in (after["doc_hash"], baseline["doc_hash"]))
        obj_drift = after.get("objects") != baseline.get("objects")
        if doc_drift or obj_drift:
            for _ in range(4):
                drv.send_keys("^z")
                time.sleep(0.2)
                if (sess.doc_hash() == baseline["doc_hash"]
                        and sess.object_fingerprint() == baseline.get("objects")):
                    break
        sess.select_paragraph(1)
        after = snapshot(sess, screen_w)
        ok = _match(after, baseline)
    return ok, notes


def _close_window(sess, hwnd, notes):
    if not hwnd:
        drv.press_escape(2)
        notes.append("esc(no-hwnd)")
        return
    try:
        from pywinauto import Desktop
        dlg = Desktop(backend="uia").window(handle=hwnd)
        for btn in ("Cancel", "Close", "No"):
            try:
                b = dlg.child_window(title=btn, control_type="Button")
                if b.exists(timeout=0.6):
                    b.click_input()
                    time.sleep(0.35)
                    notes.append(f"clicked {btn}")
                    break
            except Exception:
                continue
    except Exception:
        pass
    for _ in range(4):
        if not (win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)):
            return
        drv.press_escape(1)
        time.sleep(0.2)
    notes.append("window may be stuck")


def _close_pane_window(sess, hwnd, notes):
    """Close a FLOATING task pane by the 'Close pane' button on its own window."""
    try:
        from pywinauto import Desktop
        w = Desktop(backend="uia").window(handle=hwnd)
        btn = w.child_window(title="Close pane", control_type="Button")
        if btn.exists(timeout=0.6):
            btn.click_input()
            time.sleep(0.3)
            notes.append("closed floating pane")
            return
    except Exception:
        pass
    notes.append("floating pane close: button not found")


def _close_panes(sess, notes):
    """Close docked task panes via their 'Close pane' header button (ESC does not close panes)."""
    try:
        from pywinauto import Desktop
        win = Desktop(backend="uia").window(handle=sess.frame)
        for _ in range(4):
            try:
                btn = win.child_window(title="Close pane", control_type="Button")
                if btn.exists(timeout=0.5):
                    btn.click_input()
                    time.sleep(0.3)
                    notes.append("closed pane")
                    continue
            except Exception:
                pass
            break
    except Exception:
        pass
