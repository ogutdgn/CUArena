"""Fixup — the straggler re-drive (run_step5_stragglers) passed the CONTAINER id as the depth
walker's `owner`, so endpoint elements in the re-driven color/crop dropdowns got
`triggers: <container-id>` instead of `triggers: <sub-feature-id>`. An endpoint must fire a
NODE, never a container. This reconciles them: compute each container's owning sub-feature by
propagating ownership down the opens-chain from the ribbon opener element, then rewrite any
`triggers` that points at a container to that owner node. Journaled; idempotent.
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
    cont_ids = set(containers)

    ffiles = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((KB / "features").glob("*.json"))]
    subs = [s for ff in ffiles for s in ff["subfeatures"]]
    node_ids = {s["id"] for s in subs} | {ff["feature"]["id"] for ff in ffiles}

    # el id -> owning sub-feature (from trigger paths)
    el_owner = {}
    for s in subs:
        for tp in s.get("trigger_paths", []):
            if tp.get("path") and tp["path"][-1].startswith("el:"):
                el_owner.setdefault(tp["path"][-1], s["id"])

    # container -> owner sub-feature: seed from ribbon-face elements (opens X, owner known),
    # then propagate down each container's children opens to sub-containers.
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

    rewrites = 0
    for cid, c in containers.items():
        owner = owner_of.get(cid)
        changed = False
        for e in c.children:
            if e.triggers and e.triggers in cont_ids and e.triggers not in node_ids:
                # an endpoint wrongly firing a container — repoint at the surface's owner node
                e.triggers = owner or e.triggers
                if owner:
                    e.state_notes = ((e.state_notes or "") +
                                     "; endpoint retargeted to owning sub-feature").strip("; ")
                    changed = True
                    rewrites += 1
        if changed:
            writer.upsert_container(c)

    jrnl = common.get_journal(common.make_run_id() + "-fix-straggler-triggers")
    jrnl.append(common.journal_event(actor="stage5.fixup", action="reconcile",
                target="straggler-triggers", outcome="ok", data={"rewrites": rewrites}))
    print(json.dumps({"triggers_rewritten": rewrites}, indent=2))


if __name__ == "__main__":
    main()
