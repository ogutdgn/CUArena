import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import config
from launcher import WordSession


def _compact_walk(el, fh, depth=0, max_depth=14, budget=None):
    """Compact one-line-per-node UIA dump: depth | control_type | name | aid | rect."""
    if budget is not None:
        budget[0] -= 1
        if budget[0] < 0:
            return
    try:
        ei = el.element_info
        r = ei.rectangle
        fh.write(f"{depth:2d} {'  ' * depth}ct={ei.control_type!r} "
                 f"name={ (ei.name or '')[:60]!r} aid={ei.automation_id or ''!r} "
                 f"rect=({r.left},{r.top},{r.right},{r.bottom})\n")
    except Exception as e:
        fh.write(f"{depth:2d} {'  ' * depth}<props error: {e}>\n")
        return
    if depth >= max_depth:
        return
    try:
        kids = el.children()
    except Exception:
        kids = []
    for k in kids:
        _compact_walk(k, fh, depth + 1, max_depth, budget)


def dump_tree():
    from pywinauto import Desktop
    s = WordSession.start(config.FIXTURES / "p0-blank.docx")
    rd = config.new_run_dir()
    try:
        win = Desktop(backend="uia").window(process=s.pid, top_level_only=True)
        win.dump_tree(depth=5, filename=str(rd / "tree-top.txt"))       # find the ribbon pane
        with open(rd / "tree-compact.txt", "w", encoding="utf-8") as fh:
            _compact_walk(win.wrapper_object(), fh, budget=[60000])
        print(f"stage-1 dump: {rd/'tree-top.txt'}")
        print(f"compact dump: {rd/'tree-compact.txt'}")
        print(f"RUN_DIR={rd}")
    finally:
        s.close()


def enumerate_home():
    import json, uia, exposure
    s = WordSession.start(config.FIXTURES / "p0-text.docx")
    rd = config.new_run_dir()
    try:
        win = uia.attach(s)
        print("foreground after attach:", s.assert_foreground())
        dump = uia.enumerate_tab(win, "Home")
        out = rd / "home-enum.json"
        out.write_text(json.dumps(dump, indent=1, ensure_ascii=False), encoding="utf-8")
        exp = exposure.dump([out], rd / "exposure-map.json")
        per = {g["name"]: len(g["controls"]) for g in dump["groups"]}
        total = sum(per.values())
        print(f"groups={len(dump['groups'])} total={total} per-group={per}")
        # AutomationId==idMso spot-check
        bold = next((c for g in dump["groups"] for c in g["controls"] if c["name"] == "Bold"), None)
        print("Bold:", None if bold is None else
              {"aid": bold["automation_id"], "type": bold["control_type"],
               "patterns": bold["patterns"], "keytip": bold["access_key"],
               "shortcut": bold["accelerator_key"]})
        print("exposure flags:", exp["flags"])
        print(f"RUN_DIR={rd}")
    finally:
        s.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump-tree", action="store_true")
    ap.add_argument("--enumerate-home", action="store_true")
    a = ap.parse_args()
    if a.dump_tree:
        dump_tree()
    if a.enumerate_home:
        enumerate_home()
