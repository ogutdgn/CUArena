"""Step 5 (authoring) — enrich P0-P2 nodes to full depth and flip explored.

For each P0-P2 subfeature: write the depth rubric (behavior = options/states/defaults harvested
from the surface it opens), attach the icon crop + surface screenshot, add a short visual
description, and flip explored:true. P3 nodes get the same rubric + their one-level surface
(mid-level). P4 stays breadth (explored stays false, honestly labeled). Features in P0-P2 flip
explored:true too. Re-runnable; reads the entered containers, never re-drives the app.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import common

KB = common.APP_KB

# short visual descriptions for P0-P2 controls, grounded in the ribbon screenshots examined
VISUAL = {
    "subfeature:bold": "a bold capital 'B'",
    "subfeature:italic": "a slanted capital 'I'",
    "subfeature:underline-gallery": "a capital 'U' with an underline beneath it, plus a dropdown chevron",
    "subfeature:strikethrough": "'abc' with a line struck through it",
    "subfeature:subscript": "an 'x' with a small subscript '2'",
    "subfeature:superscript": "an 'x' with a small superscript '2'",
    "subfeature:font": "the font-name box showing the current typeface (e.g. 'Aptos (Body)')",
    "subfeature:font-size": "the point-size box showing the current size (e.g. 12)",
    "subfeature:font-size-increase": "a large 'A' beside a small 'A' with an up arrow (Grow Font)",
    "subfeature:font-size-decrease": "a large 'A' beside a small 'A' with a down arrow (Shrink Font)",
    "subfeature:font-color-picker": "a capital 'A' with a red bar beneath it and a dropdown chevron",
    "subfeature:text-highlight-color-picker": "a highlighter pen over text with a yellow bar and dropdown",
    "subfeature:font-dialog": "the small dialog-launcher arrow in the Font group's corner",
    "subfeature:copy": "two overlapping document pages",
    "subfeature:cut": "a pair of scissors",
    "subfeature:paste": "a clipboard with a document; a large split button with a dropdown",
    "subfeature:format-painter": "a paintbrush (Format Painter)",
    "subfeature:align-left": "four horizontal lines aligned to the left",
    "subfeature:align-center": "four horizontal lines centered",
    "subfeature:align-right": "four horizontal lines aligned to the right",
    "subfeature:align-justify": "four horizontal lines flush to both margins",
    "subfeature:bullets-gallery": "a bulleted list (dots beside lines) with a dropdown chevron",
    "subfeature:numbering-gallery": "a numbered list (1,2,3 beside lines) with a dropdown chevron",
    "subfeature:line-spacing": "stacked lines with up/down arrows and a dropdown chevron",
    "subfeature:find": "a magnifying glass labelled 'Find'",
    "subfeature:replace": "'abc' with a replacement arrow labelled 'Replace'",
    "subfeature:quick-styles": "a gallery of style previews (Normal, No Spacing, Heading, Title…)",
    "subfeature:paragraph-dialog": "the small dialog-launcher arrow in the Paragraph group's corner",
    "subfeature:shading-color-picker": "a paint-bucket tilted over a square (shading) with a dropdown",
}


def load_container(cid):
    p = KB / "ui" / (cid.removeprefix("ui:") + ".json")
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def ribbon_icon(ribbon, sub):
    """The icon crop path for a subfeature, from its primary skeleton element."""
    els = [tp["path"][-1] for tp in sub.get("trigger_paths", []) if tp.get("path")]
    for e in ribbon["children"]:
        if e.get("id") in els and e.get("icon", {}).get("image"):
            return e["icon"]["image"]
    return None


def behavior_from_surface(sub):
    if not sub.get("opens"):
        return (f"Direct action: {sub['what_it_does']} Applied immediately to {sub['affects']}; "
                f"toggle state (where applicable) is reflected by the button's highlighted look.")
    cont = load_container(sub["opens"])
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


def main():
    layers = json.loads((KB / "priority" / "layers.json").read_text(encoding="utf-8"))["layers"]
    p0p2 = set(layers.get("P0", []) + layers.get("P1", []) + layers.get("P2", []))
    p3 = set(layers.get("P3", []))
    writer = common.get_writer()
    run_id = common.make_run_id() + "-step5-final"
    jrnl = common.get_journal(run_id)
    ribbon = load_container("ui:ribbon-home")

    enriched = {"P0P2": 0, "P3": 0, "P4": 0}
    for p in sorted(KB.glob("subfeatures/**/*.json")):
        s = json.loads(p.read_text(encoding="utf-8"))
        sid = s["id"]
        icon = ribbon_icon(ribbon, s)
        shots = [x for x in [icon] if x]
        if s.get("opens"):
            cont = load_container(s["opens"])
            if cont and cont.get("screenshot"):
                shots.append(cont["screenshot"])
        if sid in p0p2 or sid in p3:
            s["behavior"] = behavior_from_surface(s)
            if sid in VISUAL:
                s["behavior"] = (s["behavior"] or "") + f" Appears as {VISUAL[sid]}."
            s["screenshot"] = icon
            s["screenshots"] = shots
            # explored only if it has no unentered stub it opens
            unresolved = False
            if s.get("opens"):
                c = load_container(s["opens"])
                unresolved = (c is None) or (c.get("explored") is False)
            s["explored"] = (sid in p0p2) and not unresolved
            enriched["P0P2" if sid in p0p2 else "P3"] += 1
        else:
            s["explored"] = False
            s["screenshots"] = shots
            enriched["P4"] += 1
        writer.write_subfeature(s)

    # features
    for p in sorted(KB.glob("features/*.json")):
        f = json.loads(p.read_text(encoding="utf-8"))
        if f["id"] in p0p2:
            f["explored"] = True
            f["behavior"] = (f["what_it_does"] + " Group controls: " +
                             ", ".join(f.get("subfeatures", [])))
        elif f["id"] in p3:
            f["explored"] = True
        else:
            f["explored"] = False
        writer.write_feature(f)

    jrnl.append(common.journal_event(actor="stage5.finalize", action="enrich-rubric",
                target="features+subfeatures", outcome="ok", data=enriched))
    print(json.dumps({"enriched": enriched}, indent=2))


if __name__ == "__main__":
    main()
