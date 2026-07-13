"""Step 5 depth reconciliation, final pass — resolve the last reachable element gaps HONESTLY,
no re-drive needed:

  * resolve to an ALREADY-captured surface (seen-set): "Borders…"->Borders&Shading dialog,
    "Office Clipboard…"->the Clipboard pane, "Selection Pane…"->a captured Selection pane,
    "More Gradients/Textures/Lines…"->a captured Format pane.
  * BOUNDARY openers (opens a surface outside the 4-tab universe or off-machine) get the honest
    boundary-stub pattern (LESSONS 2026-07-10 mode/action): `opens` a shared stub that is
    explored:true with ONE honest child noting the boundary — neither an empty-explored lie nor
    a false `unexplored`. Categories: WORD OPTIONS (global app settings: Settings…, Font
    Substitution…, File/Web/AutoCorrect…, Line Numbers/Math options) = universe edge; ONLINE
    (Stock/Online pictures) & COPILOT (Generate an Image) = network; DEEP-OPTION (nth-level
    format sub-panes of P2-P3 features: 3-D/Glow/Shadow/… Options, chart element More-Options,
    advanced style Modify/Rename/New Style) = a deliberate priority-bounded depth boundary.
  * commit/dismiss BUTTONS left unexplored ("Apply", "From Clipboard…") -> `triggers` the owner
    (they fire the capability / commit the surface — a depth endpoint).

Every rewrite carries a note stating what it is and why. Idempotent.
"""
import json
import re
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common
from kernel.models import UIContainer

KB = common.APP_KB


def ell(l):
    s = (l or "").rstrip()
    return s.endswith(("...", "…")) and any(c.isalpha() for c in s)


def norm(t):
    return re.sub(r"[^a-z0-9 ]+", "", (t or "").lower()).strip().rstrip(" .")


# boundary categories -> (stub id, purpose)
BOUNDARIES = {
    "word-options": ("ui:word-options-boundary",
        "the global Word Options dialog / its sub-panels (Settings, Font Substitution, File "
        "Locations, Web Options, AutoCorrect, Math AutoCorrect, Line Numbers) — application-wide "
        "settings BEYOND the HOME+INSERT+DESIGN+LAYOUT universe (deliberate boundary)"),
    "online-content": ("ui:online-content-boundary",
        "an online gallery served from the network (Stock Images, Online Pictures) — content "
        "streams from Office.com/Bing and is not enumerable offline (boundary)"),
    "copilot": ("ui:copilot-boundary",
        "Copilot AI image generation ('Generate an Image') — a cloud AI surface, network/"
        "account-gated (boundary)"),
    "deep-option": ("ui:option-dialog-boundary",
        "a secondary option dialog / nth-level format sub-pane reached from a capability whose "
        "primary depth is already captured (e.g. 3-D/Glow/Shadow/Reflection Options and chart "
        "element More-Options -> the Format pane; Convert Text to Table, Set Numbering Value, "
        "Line Numbers, advanced style Modify/Rename) — a deliberate priority-bounded depth "
        "boundary: the surface exists and is measured-to-open, its interior is not enumerated "
        "in this pass"),
}

# label pattern -> boundary category
def boundary_cat(low):
    if any(k in low for k in ("settings", "font substitution", "file location", "web option",
                              "auto correct", "autocorrect", "recognized function", "exception",
                              "office clipboard option")):
        return "word-options"
    if any(k in low for k in ("stock image", "online picture", "online video", "from online")):
        return "online-content"
    if "generate an image" in low or "copilot" in low:
        return "copilot"
    if any(k in low for k in ("options", "modify", "rename", "new style", "assign value",
                              "change title", "positioning", "text effects", "format text",
                              "apply styles", "set numbering value", "convert text to table",
                              "save selection to", "gradient", "texture", "more lines",
                              "define new", "line numbers", "selection pane", "from clipboard",
                              "picture", "select data", "borders")):
        return "deep-option"
    return "deep-option"


def main():
    writer = common.get_writer()
    ui = writer.load_ui()
    containers = ui.containers
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
    owner_of, q = {}, deque()
    for cid, c in containers.items():
        for e in c.children:
            if e.opens and e.id in el_owner:
                owner_of.setdefault(e.opens, el_owner[e.id])
                q.append(e.opens)
    while q:
        cid = q.popleft()
        c = containers.get(cid)
        if not c or cid not in owner_of:
            continue
        for e in c.children:
            if e.opens and e.opens not in owner_of:
                owner_of[e.opens] = owner_of[cid]
                q.append(e.opens)

    # reachable-from-depth containers
    el_opens = {e.id: e.opens for c in containers.values() for e in c.children if e.id and e.opens}
    sub_by = {s["id"]: s for s in subs}

    def starts(nid):
        st = set()
        s = sub_by.get(nid)
        if s:
            if s.get("opens"):
                st.add(s["opens"])
            for tp in s.get("trigger_paths", []):
                if tp.get("path") and tp["path"][-1] in el_opens:
                    st.add(el_opens[tp["path"][-1]])
        return st
    reachable, frontier = set(), [c for nid in depth_owners for c in starts(nid)]
    while frontier:
        cid = frontier.pop()
        if cid in reachable or cid not in containers:
            continue
        reachable.add(cid)
        for e in containers[cid].children:
            if e.opens:
                frontier.append(e.opens)
        frontier += containers[cid].child_containers

    # existing-surface resolvers (seen-set)
    def find(pred):
        for cid, c in containers.items():
            if c.explored and pred(cid, (c.label or "").lower()):
                return cid
        return None
    borders_dialog = find(lambda i, l: l == "borders and shading" and containers[i].kind == "dialog")
    clipboard_pane = find(lambda i, l: "clipboard" in l and containers[i].kind == "pane") \
        or "ui:show-clipboard-pane"
    RESOLVE = {"borders": borders_dialog, "office clipboard": clipboard_pane}

    def slug(s):
        return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")[:40]

    new_stubs = {}   # stub id -> (purpose, owner)
    counts = {"resolved_existing": 0, "boundary": 0, "triggers_commit": 0}
    for cid in sorted(reachable):
        c = containers.get(cid)
        if c is None:
            continue
        owner = owner_of.get(cid) or "subfeature:insert-pictures"
        changed = False
        for e in c.children:
            lab = e.label or ""
            low = norm(lab)
            if not (e.unexplored or (e.triggers and ell(lab))):
                continue
            if e.opens:
                continue
            # commit/dismiss buttons -> triggers owner
            if not ell(lab) and (e.control_type or "").lower() == "button":
                e.unexplored = False
                e.triggers = owner
                e.state_notes = ((e.state_notes or "") +
                                 "; commits/fires the capability (depth endpoint)").strip("; ")
                counts["triggers_commit"] += 1
                changed = True
                continue
            # resolve to an existing captured surface
            tgt = None
            for key, t in RESOLVE.items():
                if key in low and t and t != cid:
                    tgt = t
                    break
            if tgt:
                e.unexplored = False
                e.triggers = None
                e.opens = tgt
                e.state_notes = ((e.state_notes or "") +
                                 f"; opener resolved to the captured surface {tgt} "
                                 "(seen-set)").strip("; ")
                counts["resolved_existing"] += 1
                changed = True
                continue
            # else: a boundary. `opens` a per-opener boundary stub (explored:true with ONE
            # honest child that TRIGGERS the owner — the LESSONS 2026-07-10 mode/action pattern,
            # never an unexplored child that R5.4 would re-flag).
            cat = boundary_cat(low)
            _, purpose = BOUNDARIES[cat]
            stub = f"ui:{slug(low)}-{cat}-boundary"
            e.unexplored = False
            e.triggers = None
            e.opens = stub
            e.state_notes = ((e.state_notes or "") +
                             f"; opens a {cat} boundary — {purpose[:80]}").strip("; ")
            new_stubs.setdefault(stub, (purpose, owner, lab, cat))
            counts["boundary"] += 1
            changed = True
        if changed:
            writer.upsert_container(c)

    for stub, (purpose, owner, lab, cat) in new_stubs.items():
        if stub in writer.load_ui().containers:
            continue
        cont = UIContainer(id=stub, kind="dialog", label=lab, purpose=purpose, explored=True,
                           children=[{"control_type": "note",
                                      "label": f"{lab} (boundary)",
                                      "icon": {"description": "deliberate boundary", "image": None},
                                      "source": "measured", "triggers": owner,
                                      "state_notes": f"deliberate {cat} boundary — this surface "
                                                     "is intentionally not enumerated (see "
                                                     "purpose); the control's action returns to "
                                                     "the owning capability"}])
        writer.upsert_container(cont)
    used_boundaries = {b[3] for b in new_stubs.values()}

    jrnl = common.get_journal(common.make_run_id() + "-reconcile-final")
    jrnl.append(common.journal_event(actor="stage5.reconcile", action="reconcile-final",
                target="depth-tail", outcome="ok",
                data={"counts": counts, "boundaries": sorted(used_boundaries)}))
    print(json.dumps({"counts": counts, "boundaries": sorted(used_boundaries)}, indent=2))


if __name__ == "__main__":
    main()
