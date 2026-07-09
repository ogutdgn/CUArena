"""Step 0 — Stage: launch Word and reach its editing workspace, provably and repeatably.

Usage:
    python kb/word/scripts/drive/stage.py record   # launch, write route+version+screenshot
    python kb/word/scripts/drive/stage.py replay    # cold launch replaying the route (the proof)

Both do a genuine cold launch (own new pid, open a fresh scratch fixture copy, reach the
workspace, screenshot window-true, journal, tear down). 'replay' additionally asserts the
pinned build and requires ready_route.json to already exist — it proves the route is
mechanically replayable with no judgment calls.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import win32api
import win32gui
import win32process
from PIL import ImageGrab

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts on path
import common
from session import WordSession, force_foreground

DRIVE_DIR = common.APP_KB / "scripts" / "drive"
ROUTE_PATH = DRIVE_DIR / "ready_route.json"
VERSION_PATH = common.APP_KB / "version.json"


def _find_child_class(frame_hwnd, target_class):
    """Depth-first search for a child window of the given class under the frame."""
    hit = []

    def walk(h):
        try:
            children = []
            win32gui.EnumChildWindows(h, lambda c, _: (children.append(c) or True), None)
        except Exception:
            children = []
        for c in children:
            try:
                if win32gui.GetClassName(c) == target_class:
                    hit.append(c)
                    return
            except Exception:
                pass
        # EnumChildWindows already recurses through the whole tree, so one pass is enough
    walk(frame_hwnd)
    return hit[0] if hit else None


def _ribbon_present(frame_hwnd):
    """Confirm the ribbon command surface is up via UIA (Pane named 'Ribbon' / 'Ribbon Tabs')."""
    try:
        from pywinauto import Desktop
        win = Desktop(backend="uia").window(handle=frame_hwnd)
        for title in ("Ribbon Tabs", "Ribbon"):
            try:
                if win.child_window(title=title).exists(timeout=2):
                    return True
            except Exception:
                continue
        return False
    except Exception:
        return False


def _dismiss_nags(sess, jrnl, cfg):
    """Close any top-level window whose title matches the config's dismiss regexes."""
    import re
    pats = [re.compile(p) for p in cfg.get("boundaries", {}).get("dismiss_title_res", [])]
    dismissed = []
    for h, cls, title, rect in sess.top_level_windows():
        if h == sess.frame:
            continue
        if any(p.search(title or "") for p in pats):
            try:
                win32gui.PostMessage(h, 0x0010, 0, 0)   # WM_CLOSE
                dismissed.append({"hwnd": h, "class": cls, "title": title})
            except Exception:
                pass
    jrnl.append(common.journal_event(
        actor="stage0", action="dismiss-nags", target="toplevel-windows",
        outcome=f"dismissed={len(dismissed)}", data={"dismissed": dismissed}))
    return dismissed


def _launch_to_workspace(mode, run_id, jrnl, cfg, expected_build=None):
    fixture = common.fresh_scratch_fixture()
    jrnl.append(common.journal_event(
        actor="stage0", action="scratch-copy", target=str(fixture),
        outcome="ok", data={"source": cfg["fixture"], "mode": mode}))

    jrnl.append(common.journal_event(
        actor="stage0", action="launch", target="Word.Application (DispatchEx)",
        outcome="attempting", data={"expected_build": expected_build, "mode": mode}))
    sess = WordSession.start(fixture, expected_build=expected_build)
    jrnl.append(common.journal_event(
        actor="stage0", action="launch", target=f"pid={sess.pid}",
        outcome="ok", data={"build": sess.build, "version": sess.version,
                            "frame_hwnd": sess.frame}))

    _dismiss_nags(sess, jrnl, cfg)

    # --- verify we are actually in the editing workspace, not a launcher/gallery ---
    doc_canvas = _find_child_class(sess.frame, "_WwG")   # Word document editing surface
    ribbon = _ribbon_present(sess.frame)
    toplevels = [{"class": c, "title": t} for (_h, c, t, _r) in sess.top_level_windows()]
    workspace_ok = bool(doc_canvas) and bool(ribbon)
    jrnl.append(common.journal_event(
        actor="stage0", action="verify-workspace", target=f"pid={sess.pid}",
        outcome="workspace" if workspace_ok else "NOT-workspace",
        data={"doc_canvas__WwG": doc_canvas, "ribbon_present": ribbon,
              "toplevel_windows": toplevels}))

    # --- window-true screenshot (grab exactly the frame rect, not a screen region) ---
    force_foreground(sess.frame)
    import time
    time.sleep(0.6)
    rect = sess.frame_rect()
    img = ImageGrab.grab(bbox=rect, all_screens=True)
    writer = common.get_writer()
    shot_name = "reached" if mode == "record" else "reached-replay"
    shot_rel = writer.save_screenshot(img, "app:workspace", shot_name)
    jrnl.append(common.journal_event(
        actor="stage0", action="screenshot", target="app:workspace",
        outcome="ok", data={"path": shot_rel, "frame_rect": rect,
                            "size": [img.width, img.height]}))

    result = {"pid": sess.pid, "build": sess.build, "version": sess.version,
              "frame_rect": rect, "workspace_ok": workspace_ok,
              "screenshot": shot_rel, "doc_canvas": doc_canvas, "ribbon": ribbon}
    sess.close()
    jrnl.append(common.journal_event(
        actor="stage0", action="teardown", target=f"pid={sess.pid}",
        outcome="closed (SaveChanges=0, taskkill by pid)", data={}))
    return result


def do_record(jrnl, cfg):
    run_id = jrnl.run_id
    res = _launch_to_workspace("record", run_id, jrnl, cfg, expected_build=None)
    if not res["workspace_ok"]:
        jrnl.append(common.journal_event(
            actor="stage0", action="record", target="workspace",
            outcome="FAILED: workspace not reached", data=res))
        raise SystemExit("record failed: workspace not reached")

    # Pin the version discovered on THIS machine.
    exe = cfg["exe"]
    try:
        info = win32api.GetFileVersionInfo(exe, "\\")
        ms, ls = info["FileVersionMS"], info["FileVersionLS"]
        exe_file_version = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
    except Exception:
        exe_file_version = None
    version_doc = {
        "name": "Microsoft Word",
        "version": res["version"],          # e.g. "16.0"
        "build": res["build"],              # e.g. "16.0.20xxx.yyyyy" — the pinned truth
        "build_prefix_pinned": ".".join(res["build"].split(".")[:3]),
        "exe": exe,
        "exe_file_version": exe_file_version,
        "platform": "desktop",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "launch_method": "com-dispatchex",
    }
    VERSION_PATH.write_text(json.dumps(version_doc, indent=2), encoding="utf-8")

    route = {
        "app": "word",
        "goal": "reach the editing workspace (document canvas + ribbon visible)",
        "method": "com-dispatchex",
        "steps": [
            {"op": "copy-fixture", "from": cfg["fixture"],
             "to": "OS temp (never the original — cloud AutoSave mutates it)"},
            {"op": "com-new-instance", "progid": "Word.Application",
             "note": "DispatchEx = new instance; own the one new winword.exe pid"},
            {"op": "open-doc", "arg": "<scratch fixture copy>", "read_only": False},
            {"op": "assert-build-prefix", "value": version_doc["build_prefix_pinned"]},
            {"op": "disconnect-addins"},
            {"op": "move-to-primary-monitor"},
            {"op": "maximize", "com": "ActiveWindow.WindowState = 1"},
            {"op": "print-view", "com": "ActiveWindow.View.Type = 3"},
            {"op": "verify-workspace",
             "checks": ["OpusApp frame present", "_WwG document canvas present",
                        "Ribbon pane present"]},
        ],
        "no_judgment_calls": True,
        "teardown": "doc.Close(SaveChanges=0); app.Quit(); taskkill /PID <owned> /F",
    }
    ROUTE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ROUTE_PATH.write_text(json.dumps(route, indent=2), encoding="utf-8")
    jrnl.append(common.journal_event(
        actor="stage0", action="record", target="ready_route.json + version.json",
        outcome="ok", data={"route": str(ROUTE_PATH), "version": str(VERSION_PATH),
                            "pinned_build": version_doc["build_prefix_pinned"]}))
    print(json.dumps({"mode": "record", **res, "pinned_build":
                      version_doc["build_prefix_pinned"]}, indent=2))


def do_replay(jrnl, cfg):
    if not ROUTE_PATH.exists() or not VERSION_PATH.exists():
        raise SystemExit("replay requires ready_route.json + version.json (run record first)")
    route = json.loads(ROUTE_PATH.read_text(encoding="utf-8"))
    version_doc = json.loads(VERSION_PATH.read_text(encoding="utf-8"))
    pinned = version_doc["build_prefix_pinned"]
    jrnl.append(common.journal_event(
        actor="stage0", action="replay", target="ready_route.json",
        outcome="start", data={"pinned_build": pinned, "steps": len(route["steps"])}))
    res = _launch_to_workspace("replay", jrnl.run_id, jrnl, cfg, expected_build=pinned)
    passed = res["workspace_ok"] and res["build"].startswith(pinned)
    jrnl.append(common.journal_event(
        actor="stage0", action="replay", target="workspace",
        outcome="PASS" if passed else "FAIL",
        data={"workspace_ok": res["workspace_ok"], "build": res["build"],
              "pinned": pinned}))
    print(json.dumps({"mode": "replay", "passed": passed, **res}, indent=2))
    if not passed:
        raise SystemExit("replay failed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["record", "replay"])
    args = ap.parse_args()
    cfg = common.load_config()
    run_id = common.make_run_id() + f"-stage0-{args.mode}"
    jrnl = common.get_journal(run_id)
    jrnl.append(common.journal_event(
        actor="stage0", action="run-begin", target="stage.py",
        outcome=args.mode, data={"run_id": run_id}))
    if args.mode == "record":
        do_record(jrnl, cfg)
    else:
        do_replay(jrnl, cfg)
    jrnl.append(common.journal_event(
        actor="stage0", action="run-end", target="stage.py", outcome="ok", data={}))


if __name__ == "__main__":
    main()
