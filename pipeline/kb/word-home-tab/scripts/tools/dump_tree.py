"""Dump the live UIA tree of the Word workspace — evidence to pin locators against.

Playbook Step 1: look FIRST, then code. This launches a session, walks the frame's UIA
tree, and records every element's control_type / name / automation_id(idMso) / rect /
patterns / tooltip / keytip / shortcut into a JSON + a readable outline under
tools/dumps/. Nothing is assumed; the enumerator is written against what this shows.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import common
from session import WordSession
import uia_attach as ua

DUMP_DIR = Path(__file__).resolve().parent / "dumps"
MAX_DEPTH = 40
MAX_NODES = 6000


def walk(el, depth, counter, interactive_only_props=True):
    if counter[0] >= MAX_NODES or depth > MAX_DEPTH:
        return None
    counter[0] += 1
    ei = el.element_info
    r = ei.rectangle
    ct = ei.control_type or ""
    node = {
        "control_type": ct,
        "name": ei.name or "",
        "automation_id": ei.automation_id or "",
        "rect": [r.left, r.top, r.right, r.bottom],
    }
    # Read the richer props (tooltip/keytip/shortcut/patterns/enabled) for interactive nodes.
    if (not interactive_only_props) or ct in ua.INTERACTIVE or ct in ("Tab", "Group", "Pane"):
        raw = ei.element

        def _p(pid):
            try:
                return raw.GetCurrentPropertyValue(pid) or ""
            except Exception:
                return ""

        def _s(attr):
            try:
                return getattr(raw, attr, "") or ""
            except Exception:
                return ""
        node["tooltip"] = _p(ua._FULL_DESCRIPTION)
        node["access_key"] = _s("CurrentAccessKey")
        node["accelerator_key"] = _s("CurrentAcceleratorKey")
        try:
            node["enabled"] = bool(raw.CurrentIsEnabled)
        except Exception:
            node["enabled"] = None
        node["patterns"] = ua._available_patterns(raw)
    try:
        kids = el.children()
    except Exception:
        kids = []
    children = []
    for k in kids:
        c = walk(k, depth + 1, counter, interactive_only_props)
        if c is not None:
            children.append(c)
    if children:
        node["children"] = children
    return node


def outline(node, depth, lines):
    ind = "  " * depth
    aid = f" [{node['automation_id']}]" if node.get("automation_id") else ""
    nm = node.get("name", "")
    nm = (nm[:40] + "…") if len(nm) > 41 else nm
    acc = node.get("accelerator_key") or ""
    key = node.get("access_key") or ""
    extra = []
    if acc:
        extra.append(f"acc={acc}")
    if key:
        extra.append(f"keytip={key}")
    if node.get("enabled") is False:
        extra.append("DISABLED")
    tail = ("  {" + ", ".join(extra) + "}") if extra else ""
    lines.append(f"{ind}{node['control_type']:<12} '{nm}'{aid}{tail}")
    for c in node.get("children", []):
        outline(c, depth + 1, lines)


def main():
    DUMP_DIR.mkdir(parents=True, exist_ok=True)
    run_id = common.make_run_id() + "-dumptree"
    jrnl = common.get_journal(run_id)
    cfg = common.load_config()
    fixture = common.fresh_scratch_fixture()
    jrnl.append(common.journal_event(actor="stage1.dump", action="launch",
                target="Word", outcome="attempting", data={}))
    sess = WordSession.start(fixture, expected_build="16.0.20131")
    jrnl.append(common.journal_event(actor="stage1.dump", action="launch",
                target=f"pid={sess.pid}", outcome="ok",
                data={"build": sess.build, "frame": sess.frame}))
    try:
        win = ua.attach(sess.frame)
        import time
        time.sleep(0.5)
        root = win.element_info  # top window element
        # Build a wrapper for walking: use the pywinauto window wrapper directly.
        counter = [0]
        tree = walk(win, 0, counter)
        (DUMP_DIR / "uia_tree_home.json").write_text(
            json.dumps(tree, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = []
        outline(tree, 0, lines)
        (DUMP_DIR / "uia_tree_home.txt").write_text("\n".join(lines), encoding="utf-8")
        jrnl.append(common.journal_event(actor="stage1.dump", action="dump-tree",
                    target="frame", outcome="ok",
                    data={"nodes": counter[0], "json": "tools/dumps/uia_tree_home.json",
                          "txt": "tools/dumps/uia_tree_home.txt"}))
        print(json.dumps({"nodes": counter[0],
                          "outline_lines": len(lines)}, indent=2))
    finally:
        sess.close()
        jrnl.append(common.journal_event(actor="stage1.dump", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed", data={}))


if __name__ == "__main__":
    main()
