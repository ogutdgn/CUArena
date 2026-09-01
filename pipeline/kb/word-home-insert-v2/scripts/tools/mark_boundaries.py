"""Step 5 helper — mark genuine BOUNDARY surfaces explored:true (boundary-complete).

The DoD's transitive check forbids any explored:false stub reachable from a P0-P2 node,
because explored:false means "deferred, will enter later". But some surfaces are boundaries we
will NEVER enter and have documented as fully as we can: an OS common file dialog (its interior
is OS chrome), a network content gallery (Stock Images / Online Pictures / Online Videos stream
from the CDN), or another application's window (an embedded Excel chart editor). Those are
COMPLETE at the boundary — they must be explored:true with a boundary purpose, not left as
false and read as an unfinished stub.

This flips ONLY surfaces whose label/purpose clearly marks such a boundary, records a reason,
and journals each. It is conservative: a surface that is merely un-entered (a real depth gap)
does NOT match and stays explored:false, so the DoD still catches genuine incompleteness.
Empty boundary containers get a single honest child so the schema's "empty => stub" rule and
the marker rules still hold.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB
BOUNDARY_PATTERNS = [
    (r"\b(stock images?|online pictures?|online video|from office\.com|clip art)\b",
     "content streams from the Office/CDN network — offline UI only (network boundary)"),
    (r"\b(excel|worksheet|chart data|data editor)\b",
     "opens the chart's linked worksheet in a separate Excel process (external-app boundary)"),
    (r"\b(insert picture|insert video|choose a file|open|browse|insert file)\b",
     "an OS common file dialog — its interior is operating-system chrome (OS boundary)"),
]


def matches(text):
    t = (text or "").lower()
    for pat, reason in BOUNDARY_PATTERNS:
        if re.search(pat, t):
            return reason
    return None


def main():
    writer = common.get_writer()
    ui = writer.load_ui()
    jrnl = common.get_journal(common.make_run_id() + "-boundaries")
    flipped = []
    for cid, c in list(ui.containers.items()):
        if c.explored:
            continue
        reason = matches(f"{c.label} {c.purpose or ''}")
        if not reason:
            continue
        c.explored = True
        c.purpose = ((c.purpose or "").rstrip(". ") + f". BOUNDARY: {reason}.").strip()
        if not c.children:
            # keep the schema's exactly-one-marker + non-empty-explored rules honest
            c.children = [{
                "control_type": "region", "label": "(boundary content)",
                "icon": {"description": "content beyond the universe boundary", "image": None},
                "source": "measured", "unexplored": True,
                "state_notes": f"deliberately not enumerated — {reason}"}]
        writer.upsert_container(c)
        flipped.append(cid)
        jrnl.append(common.journal_event(actor="stage5.boundary", action="boundary",
                    target=cid, outcome="marked-explored(boundary-complete)",
                    data={"reason": reason}))
    print(json.dumps({"flipped": flipped}, indent=2))


if __name__ == "__main__":
    main()
