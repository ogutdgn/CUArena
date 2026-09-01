"""Step 5 (authoring) — enrich nodes to their layer's rubric depth and flip explored flags.

P0-P2 subfeatures: behavior (options/states/defaults harvested from the entered surfaces),
icon crop + surface screenshots, short visual description, explored:true — but ONLY if no
explored:false container is reachable from the node via any opens chain (the TRANSITIVE rule;
a shallow direct-surface check falsely reports done). P3: full rubric + one-level surface.
P4: breadth, explored stays false, honestly labeled. Re-runnable; reads the entered
containers, never re-drives the app.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB

VISUAL = {
    "subfeature:bold": "a bold capital 'B'",
    "subfeature:italic": "a slanted capital 'I'",
    "subfeature:underline-gallery": "a capital 'U' with an underline, plus a dropdown chevron",
    "subfeature:strikethrough": "'abc' with a line struck through it",
    "subfeature:subscript": "an 'x' with a small subscript '2'",
    "subfeature:superscript": "an 'x' with a small superscript '2'",
    "subfeature:font": "the font-name box showing the current typeface (e.g. 'Aptos (Body)')",
    "subfeature:font-size": "the point-size box showing the current size (e.g. 12)",
    "subfeature:font-size-increase": "a large 'A' beside a small 'A' with an up arrow",
    "subfeature:font-size-decrease": "a large 'A' beside a small 'A' with a down arrow",
    "subfeature:font-color-picker": "a capital 'A' with a red bar beneath it and a chevron",
    "subfeature:text-highlight-color-picker": "a highlighter pen over text with a yellow bar",
    "subfeature:font-dialog": "the small dialog-launcher arrow in the Font group's corner",
    "subfeature:copy": "two overlapping document pages",
    "subfeature:cut": "a pair of scissors",
    "subfeature:paste": "a clipboard with a document; a large split button with a dropdown",
    "subfeature:format-painter": "a paintbrush (Format Painter)",
    "subfeature:align-left": "four horizontal lines aligned to the left",
    "subfeature:align-center": "four horizontal lines centered",
    "subfeature:align-right": "four horizontal lines aligned to the right",
    "subfeature:align-justify": "four horizontal lines flush to both margins",
    "subfeature:bullets-gallery": "a bulleted list (dots beside lines) with a chevron",
    "subfeature:numbering-gallery": "a numbered list (1,2,3 beside lines) with a chevron",
    "subfeature:line-spacing": "stacked lines with up/down arrows and a chevron",
    "subfeature:find": "a magnifying glass labelled 'Find'",
    "subfeature:replace": "'abc' with a replacement arrow labelled 'Replace'",
    "subfeature:quick-styles": "a gallery of style previews (Normal, Heading 1, Title…)",
    "subfeature:paragraph-dialog": "the small dialog-launcher arrow in the Paragraph group",
    "subfeature:shading-color-picker": "a paint bucket tilted over a square with a chevron",
    "subfeature:change-case": "'Aa' with a dropdown chevron",
    "subfeature:clear-formatting": "an 'A' with a pink eraser in front of it",
    "subfeature:table-insert": "a 4x4 grid labelled 'Table' with a dropdown chevron",
    "subfeature:insert-pictures": "a photo of mountains and sun, labelled 'Pictures'",
    "subfeature:shapes-insert": "overlapping circle/square/triangle outlines",
    "subfeature:icon-insert": "a simple pictogram figure, labelled 'Icons'",
    "subfeature:insert-3d-models": "a 3D cube in perspective",
    "subfeature:smart-art-insert": "a green diagram of connected boxes, labelled 'SmartArt'",
    "subfeature:chart-insert": "a column chart with colored bars, labelled 'Chart'",
    "subfeature:screenshot-insert": "a camera over a window frame with a dashed border",
    "subfeature:page-break-insert": "a page split by a dashed line, labelled 'Page Break'",
    "subfeature:blank-page-insert": "an empty page outline, labelled 'Blank Page'",
    "subfeature:cover-page-insert": "a page with a title band, labelled 'Cover Page'",
    "subfeature:insert-link": "two chain links, labelled 'Link', with a dropdown",
    "subfeature:bookmark-insert": "a ribbon bookmark over a page, labelled 'Bookmark'",
    "subfeature:cross-reference-insert": "a page with an arrow pointing into it",
    "subfeature:insert-new-comment": "a speech bubble with a plus sign, labelled 'Comment'",
    "subfeature:header-insert": "a page with its top band highlighted, labelled 'Header'",
    "subfeature:footer-insert": "a page with its bottom band highlighted, labelled 'Footer'",
    "subfeature:page-number-insert": "a page with '#' marks, labelled 'Page Number'",
    "subfeature:text-box-insert": "an 'A' inside a rectangle, labelled 'Text Box'",
    "subfeature:quick-parts-insert": "a document with a puzzle-like insert, 'Quick Parts'",
    "subfeature:word-art-insert": "a large ornate tilted 'A', labelled 'WordArt'",
    "subfeature:drop-cap-insert": "a large 'A' dropped beside two lines of text",
    "subfeature:signature-line-insert": "a pen signing on a line",
    "subfeature:date-and-time-insert": "a calendar page with a clock",
    "subfeature:object-insert": "a boxed component icon, labelled 'Object'",
    "subfeature:equation-insert-gallery": "a pi symbol, labelled 'Equation', with a chevron",
    "subfeature:symbol-insert": "an omega symbol, labelled 'Symbol', with a chevron",
}


def load_container(cid, cache={}):
    if cid in cache:
        return cache[cid]
    p = KB / "ui" / (cid.removeprefix("ui:") + ".json")
    c = json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    cache[cid] = c
    return c


def all_containers():
    return {c["id"]: c for c in
            (json.loads(p.read_text(encoding="utf-8")) for p in KB.glob("ui/*.json"))}


def reachable(start_ids, cont_by_id):
    seen, stack = set(), list(start_ids)
    while stack:
        cid = stack.pop()
        if cid in seen:
            continue
        seen.add(cid)
        c = cont_by_id.get(cid)
        if not c:
            continue
        for e in c.get("children", []):
            if e.get("opens"):
                stack.append(e["opens"])
        stack.extend(c.get("child_containers", []))
    return seen


def ribbon_icon(ribbons, sub):
    els = [tp["path"][-1] for tp in sub.get("trigger_paths", []) if tp.get("path")]
    for ribbon in ribbons:
        for e in ribbon["children"]:
            if e.get("id") in els and e.get("icon", {}).get("image"):
                return e["icon"]["image"]
    return None


def behavior_from_surface(sub, cont_by_id):
    if not sub.get("opens"):
        return (f"Direct action: {sub['what_it_does']} Applied immediately to "
                f"{sub['affects']}; toggle state (where applicable) is reflected by the "
                f"button's highlighted look.")
    cont = cont_by_id.get(sub["opens"])
    if not cont:
        return None
    labels = [c["label"] for c in cont.get("children", []) if c.get("label")][:16]
    subsurf = cont.get("child_containers", [])
    txt = (f"Opens {cont.get('label', sub['opens'])} ({cont['kind']}). "
           f"Contents ({len(cont.get('children', []))} controls): {', '.join(labels)}.")
    if subsurf:
        txt += f" Sub-surfaces: {', '.join(subsurf)}."
    if cont.get("purpose"):
        txt += f" [{cont['purpose']}]"
    return txt


def node_start_surfaces(n, el_opens):
    starts = set()
    if n.get("opens"):
        starts.add(n["opens"])
    for tp in n.get("trigger_paths", []):
        leaf = tp["path"][-1] if tp.get("path") else None
        if leaf and leaf in el_opens:
            starts.add(el_opens[leaf])
    return starts


def main():
    layers = json.loads((KB / "priority" / "layers.json").read_text(encoding="utf-8"))["layers"]
    p0p2 = set(layers.get("P0", []) + layers.get("P1", []) + layers.get("P2", []))
    p3 = set(layers.get("P3", []))
    writer = common.get_writer()
    run_id = common.make_run_id() + "-step5-final"
    jrnl = common.get_journal(run_id)
    cont_by_id = all_containers()
    ribbons = [cont_by_id["ui:ribbon-home"], cont_by_id["ui:ribbon-insert"]]
    el_opens = {}
    for c in cont_by_id.values():
        for e in c.get("children", []):
            if e.get("id") and e.get("opens"):
                el_opens[e["id"]] = e["opens"]

    enriched = {"P0P2": 0, "P3": 0, "P4": 0, "blocked": []}
    for p in sorted(KB.glob("subfeatures/**/*.json")):
        s = json.loads(p.read_text(encoding="utf-8"))
        sid = s["id"]
        icon = ribbon_icon(ribbons, s)
        shots = [x for x in [icon] if x]
        if s.get("opens"):
            cont = cont_by_id.get(s["opens"])
            if cont and cont.get("screenshot"):
                shots.append(cont["screenshot"])
        if sid in p0p2 or sid in p3:
            s["behavior"] = behavior_from_surface(s, cont_by_id)
            if sid in VISUAL:
                s["behavior"] = (s["behavior"] or "") + f" Appears as {VISUAL[sid]}."
            s["screenshot"] = icon
            s["screenshots"] = shots
            if sid in p0p2:
                # TRANSITIVE: explored only if NO stub is reachable through any opens chain
                reach = reachable(node_start_surfaces(s, el_opens), cont_by_id)
                stubs = [cid for cid in reach
                         if cont_by_id.get(cid, {}).get("explored", True) is False]
                s["explored"] = not stubs
                if stubs:
                    enriched["blocked"].append({sid: stubs})
            else:
                s["explored"] = False       # P3 = mid-level, not full depth
            enriched["P0P2" if sid in p0p2 else "P3"] += 1
        else:
            s["explored"] = False
            s["screenshots"] = shots
            enriched["P4"] += 1
        writer.write_subfeature(s)

    for p in sorted(KB.glob("features/*.json")):
        f = json.loads(p.read_text(encoding="utf-8"))
        if f["id"] in p0p2:
            f["explored"] = True
            f["behavior"] = (f["what_it_does"] + " Group controls: " +
                             ", ".join(f.get("subfeatures", [])))
        elif f["id"] in p3:
            f["explored"] = True
            f["behavior"] = f["what_it_does"]
        else:
            f["explored"] = False
        writer.write_feature(f)

    jrnl.append(common.journal_event(actor="stage5.finalize", action="enrich-rubric",
                target="features+subfeatures", outcome="ok", data=enriched))
    print(json.dumps({"enriched": enriched}, indent=2))


if __name__ == "__main__":
    main()
