"""Dump measured contextual-tab children (id / type / marker / group) for spec authoring."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

ui = json.loads((common.APP_KB / "ui.json").read_text(encoding="utf-8"))["containers"]
which = sys.argv[1:] or [cid for cid, c in ui.items() if c.get("trigger_condition")]
for cid in which:
    c = ui.get(cid)
    if not c:
        print("MISSING", cid)
        continue
    print()
    print("===", cid, "| cond:", c.get("trigger_condition"))
    for e in c["children"]:
        mk = ("opens:" + e["opens"]) if e.get("opens") else \
             ("T:" + e["triggers"].removeprefix("subfeature:") if e.get("triggers") else "unexp")
        m = re.search(r"group '([^']+)'", e.get("state_notes") or "")
        g = m.group(1) if m else ""
        dis = " DIS" if "disabled" in (e.get("state_notes") or "") else ""
        print("%-18s %-60s %-11s %s%s" % (g[:18], e["id"], e["control_type"], mk[:70], dis))
