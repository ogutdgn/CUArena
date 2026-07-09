"""Mechanical completeness check over the UI containers (design's three-state check).

Walks kb/word/ui/*.json and asserts:
  * every element carries exactly one marker (triggers / opens / unexplored) — kernel enforces
    this on write, re-checked here on the assembled set;
  * every `opens` resolves to an existing container file (no dangling containers);
  * every container that is empty (children == []) is an honest stub (explored == false) — an
    empty container claiming explored:true is a dishonest 'done';
  * every element has the mandatory control_type + label + icon.
Reports triggers targets too, so Step 3 can confirm each resolves to a node.
Exit 0 = clean; prints GAPS otherwise.
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import common

UI = common.APP_KB / "ui"


def main():
    files = sorted(UI.glob("*.json"))
    ids = {json.loads(f.read_text(encoding="utf-8"))["id"] for f in files}
    gaps = []
    marker = Counter()
    trigger_targets = set()
    opens_targets = set()
    empties = []
    containers = 0
    elements = 0
    for f in files:
        c = json.loads(f.read_text(encoding="utf-8"))
        containers += 1
        kids = c.get("children", [])
        if not kids and c.get("explored", True):
            empties.append(f"{c['id']}: empty children but explored != false (dishonest done)")
        for e in kids:
            elements += 1
            n = sum([bool(e.get("triggers")), bool(e.get("opens")), bool(e.get("unexplored"))])
            if n != 1:
                gaps.append(f"{c['id']} / {e.get('label')}: {n} markers (must be 1)")
            if e.get("triggers"):
                marker["triggers"] += 1
                trigger_targets.add(e["triggers"])
            if e.get("opens"):
                marker["opens"] += 1
                opens_targets.add(e["opens"])
                if e["opens"] not in ids:
                    gaps.append(f"{c['id']} / {e.get('label')}: opens {e['opens']} -> NO container file")
            if e.get("unexplored"):
                marker["unexplored"] += 1
            # mandatory fields
            if not e.get("control_type") or not e.get("label"):
                gaps.append(f"{c['id']} / {e.get('label')}: missing control_type/label")
            if not e.get("icon") or not e["icon"].get("description"):
                gaps.append(f"{c['id']} / {e.get('label')}: missing icon.description")
    # child_containers must resolve too
    for f in files:
        c = json.loads(f.read_text(encoding="utf-8"))
        for cc in c.get("child_containers", []):
            if cc not in ids:
                gaps.append(f"{c['id']}: child_container {cc} -> NO file")

    report = {
        "containers": containers, "elements": elements,
        "markers": dict(marker),
        "opens_resolve": all(t in ids for t in opens_targets),
        "empty_nonstub": empties,
        "gaps": gaps,
        "trigger_targets": sorted(trigger_targets),
        "opens_targets": sorted(opens_targets),
        "stub_containers": sorted(json.loads(f.read_text(encoding="utf-8"))["id"]
                                  for f in files
                                  if json.loads(f.read_text(encoding="utf-8")).get("explored", True) is False),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    ok = not gaps and not empties
    print("\nRESULT:", "PASS ✓" if ok else f"FAIL ✗ ({len(gaps)} gaps, {len(empties)} dishonest-empties)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
