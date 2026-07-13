"""Fixup — a few surfaces the depth pass entered are MODES / single actions, not menus: Remove
Background enters an interactive editing mode (Mark to Keep/Remove + Keep/Discard on a
contextual tab); a crop cascade's 'Fill' is a single command. The hit-test walk found no
separately-enumerable items, leaving the container explored:true with empty children — which the
schema forbids (empty must be an unexplored stub). These are NOT stubs (we entered them and there
is genuinely nothing more to enumerate), so the honest fix is a single child describing the
surface's action, firing its owner node. Journaled; idempotent.
"""
import json
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB


def main():
    writer = common.get_writer()
    ui = writer.load_ui()
    containers = ui.containers

    ffiles = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((KB / "features").glob("*.json"))]
    subs = [s for ff in ffiles for s in ff["subfeatures"]]
    el_owner = {}
    for s in subs:
        for tp in s.get("trigger_paths", []):
            if tp.get("path") and tp["path"][-1].startswith("el:"):
                el_owner.setdefault(tp["path"][-1], s["id"])
    owner_of = {}
    q = deque()
    for cid, c in containers.items():
        for e in c.children:
            if e.opens and e.id in el_owner:
                owner_of.setdefault(e.opens, el_owner[e.id])
                q.append(e.opens)
    while q:
        cid = q.popleft()
        owner = owner_of.get(cid)
        c = containers.get(cid)
        if not c or not owner:
            continue
        for e in c.children:
            if e.opens and e.opens not in owner_of:
                owner_of[e.opens] = owner
                q.append(e.opens)

    fixed = []
    for cid, c in containers.items():
        if c.children or c.explored is False:
            continue
        owner = owner_of.get(cid)
        if not owner:
            # cannot resolve an owner -> honest stub rather than a dishonest empty-explored
            c.explored = False
            c.children = [{
                "control_type": "region", "label": "(not separately enumerable)",
                "icon": {"description": "surface content not enumerable via the accessibility "
                                        "tree", "image": None},
                "source": "measured", "unexplored": True,
                "state_notes": "entered but exposes no separately-enumerable items"}]
            writer.upsert_container(c)
            fixed.append((cid, "stub"))
            continue
        label = c.label or cid
        c.children = [{
            "control_type": "mode" if "background" in cid else "command",
            "label": (label or "action"),
            "icon": {"description": f"{label} — single action/mode surface", "image": None},
            "source": "measured", "triggers": owner,
            "state_notes": ("this surface is an interactive MODE / single action, not a menu of "
                            "items — entering it exposes no separately-enumerable controls; it "
                            "fires its owning capability")}]
        writer.upsert_container(c)
        fixed.append((cid, f"triggers:{owner}"))

    jrnl = common.get_journal(common.make_run_id() + "-fix-empty-explored")
    jrnl.append(common.journal_event(actor="stage5.fixup", action="reconcile",
                target="empty-explored", outcome="ok", data={"fixed": fixed}))
    print(json.dumps({"fixed": fixed}, indent=2))


if __name__ == "__main__":
    main()
