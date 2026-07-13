"""Dump the live UIA tree of the Word workspace — evidence to pin locators against.

Playbook Step 1: look FIRST, then code. This launches a session, selects the requested
ribbon tab (default Home; pass 'Insert' etc. as argv[1]), walks the frame's UIA tree,
and records every element's control_type / name / automation_id(idMso) / rect /
patterns / tooltip / keytip / shortcut into a JSON + a readable outline under
tools/dumps/. Nothing is assumed; the enumerator is written against what this shows.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word-home-insert/scripts
import common
from session import WordSession
import uia_attach as ua

DUMP_DIR = Path(__file__).resolve().parent / "dumps"
MAX_DEPTH = 40
MAX_NODES = 8000


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
    tab_name = sys.argv[1] if len(sys.argv) > 1 else "Home"
    slug = tab_name.lower().replace(" ", "-")
    DUMP_DIR.mkdir(parents=True, exist_ok=True)
    run_id = common.make_run_id() + f"-dumptree-{slug}"
    jrnl = common.get_journal(run_id)
    pinned = json.loads((common.APP_KB / "version.json").read_text(encoding="utf-8"))
    fixture = common.fresh_scratch_fixture()
    jrnl.append(common.journal_event(actor="stage1.dump", action="launch",
                target="Word", outcome="attempting", data={"tab": tab_name}))
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    jrnl.append(common.journal_event(actor="stage1.dump", action="launch",
                target=f"pid={sess.pid}", outcome="ok",
                data={"build": sess.build, "frame": sess.frame}))
    try:
        win = ua.attach(sess.frame)
        time.sleep(0.5)
        if tab_name != "Home":     # Home is active at launch
            tab = win.child_window(title=tab_name, control_type="TabItem")
            tab.click_input()
            time.sleep(0.6)
        counter = [0]
        tree = walk(win, 0, counter)
        (DUMP_DIR / f"uia_tree_{slug}.json").write_text(
            json.dumps(tree, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = []
        outline(tree, 0, lines)
        (DUMP_DIR / f"uia_tree_{slug}.txt").write_text("\n".join(lines), encoding="utf-8")
        jrnl.append(common.journal_event(actor="stage1.dump", action="dump-tree",
                    target=tab_name, outcome="ok",
                    data={"nodes": counter[0], "json": f"tools/dumps/uia_tree_{slug}.json",
                          "txt": f"tools/dumps/uia_tree_{slug}.txt"}))
        print(json.dumps({"tab": tab_name, "nodes": counter[0],
                          "outline_lines": len(lines)}, indent=2))
    finally:
        sess.close()
        jrnl.append(common.journal_event(actor="stage1.dump", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed", data={}))


if __name__ == "__main__":
    main()
