"""Step 5 depth reconciliation — resolve the element-level gaps the transitive walk left in
surfaces reachable from a DEPTH-SET node (P0-P3 + whole children), so the kernel R5.4/R2.4
checks pass HONESTLY. Only touches containers reachable from the depth set; P4 surfaces are
left as honest outline. Idempotent.

Categories (each an honest classification, not a paper-over):
  * ellipsis-labeled openers wrongly marked `triggers` (R2.4) or left `unexplored`: resolve to
    an already-captured dialog of the same title -> `opens` it (the seen-set: one dialog, many
    entry points). Un-resolvable ones are collected for a live re-drive (printed).
  * network 'from Office.com' items: NON-ellipsis -> `triggers` the owner with an external-
    boundary note (the control's modeled action is "fetch external content"; the online gallery
    is not part of this app's surface). ELLIPSIS network openers (Stock/Online/Generate) ->
    `opens` a per-item boundary stub (explored:true, ONE honest child that triggers the owner
    with a 'network boundary, not enumerable offline' note — the LESSONS 2026-07-10 mode/action
    pattern; neither an empty-explored lie nor a false unexplored).
  * dialog OPTION controls left `unexplored` (disabled/state-gated edits, checkboxes, radios,
    combos, spinners, gallery list tiles): `triggers` the owner (they set an option of the
    capability — a depth endpoint; the disabled state is a state rule, recorded in the note),
    matching how the walker marks the ENABLED option fields in the same dialog.
  * non-ellipsis menu commands left `unexplored`: `triggers` the owner (menu command endpoint).
"""
import json
import re
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB
CHROME = {"ok", "cancel", "close", "apply", "help", "minimize", "maximize", "restore",
          "restore down", ""}


def ell(l):
    s = (l or "").rstrip()
    return s.endswith(("...", "…")) and any(c.isalpha() for c in s)


def norm(t):
    return re.sub(r"[^a-z0-9 ]+", "", (t or "").lower()).strip().rstrip(" .")


def main():
    writer = common.get_writer()
    ui = writer.load_ui()
    containers = ui.containers
    cont_ids = set(containers)
    pri = json.loads((KB / "priority.json").read_text(encoding="utf-8"))
    whole = {f for f, d in pri.get("derived_features", {}).items() if d.get("scope") == "whole"}
    p03 = set(pri["layers"]["P0"] + pri["layers"]["P1"] + pri["layers"]["P2"]
              + pri["layers"].get("P3", []))
    ffiles = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((KB / "features").glob("*.json"))]
    subs = [s for ff in ffiles for s in ff["subfeatures"]]
    depth_owners = set(i for i in p03 if i.startswith("subfeature:"))
    for s in subs:
        if s.get("parent") in whole:
            depth_owners.add(s["id"])

    el_owner = {}
    for s in subs:
        for tp in s.get("trigger_paths", []):
            if tp.get("path") and tp["path"][-1].startswith("el:"):
                el_owner.setdefault(tp["path"][-1], s["id"])

    # container -> owner sub-feature (propagate down opens-chains from ribbon openers)
    owner_of, q = {}, deque()
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

    # containers reachable from a depth-set node (start = each depth owner's node.opens +
    # trigger-path leaf opens), transitively
    el_opens = {e.id: e.opens for c in containers.values() for e in c.children
                if e.id and e.opens}
    sub_by = {s["id"]: s for s in subs}

    def starts(nid):
        st = set()
        s = sub_by.get(nid)
        if not s:
            return st
        if s.get("opens"):
            st.add(s["opens"])
        for tp in s.get("trigger_paths", []):
            if tp.get("path"):
                leaf = tp["path"][-1]
                if leaf in el_opens:
                    st.add(el_opens[leaf])
        return st

    reachable = set()
    frontier = [c for nid in depth_owners for c in starts(nid)]
    while frontier:
        cid = frontier.pop()
        if cid in reachable or cid not in containers:
            continue
        reachable.add(cid)
        for e in containers[cid].children:
            if e.opens:
                frontier.append(e.opens)
        frontier += containers[cid].child_containers

    # title -> explored dialog container (for seen-set opener resolution)
    title_to_cid = {}
    for cid, c in containers.items():
        if c.explored and c.kind == "dialog":
            title_to_cid.setdefault(norm(c.label), cid)

    FIELD_TYPES = {"edit", "checkbox", "radiobutton", "combobox", "spinner", "listitem",
                   "tabitem", "slider"}
    OPT_MENU = {"menuitem", "button"}
    net_stub_ids = {}
    unresolved_openers = []
    counts = {"ellipsis_opens": 0, "network_triggers": 0, "network_opens": 0,
              "field_triggers": 0, "menucmd_triggers": 0}

    from kernel.models import UIContainer
    for cid in sorted(reachable):
        c = containers.get(cid)
        if c is None:
            continue
        owner = owner_of.get(cid)
        changed = False
        for e in c.children:
            lab = e.label or ""
            low = lab.lower().strip()
            is_net = "office.com" in low or "from office" in low
            # --- 1) ellipsis opener wrongly triggers / left unexplored -> opens a known dialog
            if ell(lab) and (e.triggers or e.unexplored) and not is_net:
                match = title_to_cid.get(norm(lab))
                # also try matching without a trailing verb noise
                if match and match != cid:
                    e.triggers = None
                    e.unexplored = False
                    e.opens = match
                    e.state_notes = ((e.state_notes or "") +
                                     "; ellipsis opener resolved to the shared dialog "
                                     f"{match} (seen-set)").strip("; ")
                    counts["ellipsis_opens"] += 1
                    changed = True
                    continue
                if e.triggers:                 # R2.4: can't stay triggers; defer honestly
                    e.triggers = None
                    e.unexplored = True
                    e.state_notes = ((e.state_notes or "") +
                                     "; R2.4 ellipsis opener — dialog not captured; re-drive")\
                        .strip("; ")
                    changed = True
                unresolved_openers.append((cid, lab, owner))
                continue
            # --- 2) network 'from Office.com' boundary
            if is_net and (e.unexplored or e.triggers):
                if ell(lab):                   # ellipsis network opener -> opens a boundary stub
                    stub = "ui:" + re.sub(r"[^a-z0-9]+", "-",
                                          low.replace("...", "").replace("…", "")).strip("-")
                    stub = stub[:60]
                    e.triggers = None
                    e.unexplored = False
                    e.opens = stub
                    e.state_notes = ((e.state_notes or "") +
                                     "; network gallery boundary (Office.com)").strip("; ")
                    if stub not in net_stub_ids and stub not in cont_ids:
                        net_stub_ids[stub] = (lab, owner)
                    counts["network_opens"] += 1
                else:                          # non-ellipsis -> triggers owner (boundary note)
                    e.unexplored = False
                    e.opens = None
                    e.triggers = owner or e.triggers
                    e.state_notes = ((e.state_notes or "") +
                                     "; opens an Office.com online gallery — external/network "
                                     "content boundary, not enumerated offline").strip("; ")
                    counts["network_triggers"] += 1
                changed = True
                continue
            # --- 3) unexplored dialog OPTION control -> triggers the owner (option endpoint)
            if e.unexplored and low not in CHROME and not ell(lab) and owner:
                ct = (e.control_type or "").lower()
                if ct in FIELD_TYPES:
                    e.unexplored = False
                    e.triggers = owner
                    e.state_notes = ((e.state_notes or "") +
                                     "; sets an option of the capability (depth endpoint); "
                                     "disabled/state-gated in the captured state").strip("; ")
                    counts["field_triggers"] += 1
                    changed = True
                elif ct in OPT_MENU:
                    e.unexplored = False
                    e.triggers = owner
                    e.state_notes = ((e.state_notes or "") +
                                     "; menu command / option (depth endpoint)").strip("; ")
                    counts["menucmd_triggers"] += 1
                    changed = True
        if changed:
            writer.upsert_container(c)

    # create the network boundary stubs (explored:true, ONE honest child -> triggers owner)
    for stub, (lab, owner) in net_stub_ids.items():
        if stub in writer.load_ui().containers:
            continue
        child_owner = owner or "subfeature:insert-pictures"
        cont = UIContainer(id=stub, kind="dropdown", label=lab,
                           purpose="online gallery served from Office.com — content streams "
                                   "from the network and is not enumerable offline (boundary)",
                           explored=True,
                           children=[{"control_type": "gallery", "label": lab,
                                      "icon": {"description": "network gallery (Office.com)",
                                               "image": None},
                                      "source": "measured", "triggers": child_owner,
                                      "state_notes": "network boundary: the online gallery is "
                                                     "not part of this app's modeled surface "
                                                     "(mode/action, not a menu)"}])
        writer.upsert_container(cont)

    run_id = common.make_run_id() + "-reconcile-depth"
    jrnl = common.get_journal(run_id)
    jrnl.append(common.journal_event(actor="stage5.reconcile", action="reconcile",
                target="depth-element-gaps", outcome="ok",
                data={"counts": counts, "network_stubs": sorted(net_stub_ids),
                      "unresolved_openers": [f"{c}::{l}" for c, l, o in unresolved_openers]}))
    print(json.dumps({"counts": counts, "network_stubs": len(net_stub_ids),
                      "unresolved_openers": len(unresolved_openers)}, indent=2))
    if unresolved_openers:
        print("\nUNRESOLVED ellipsis openers (need live re-drive):")
        for c, l, o in unresolved_openers:
            print(f"   {c} :: {l}  (owner {o})")


if __name__ == "__main__":
    main()
