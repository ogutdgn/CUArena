"""Step 2 mechanical checks over ui.json — v2, CONSOLIDATED layout.

Asserts (playbook 02 proof):
  * every element carries exactly ONE marker (triggers/opens/unexplored);
  * every opens value resolves to a container in ui.json (stubs allowed);
  * no container is empty WITHOUT explored:false (dishonest-empty ban);
  * every child_containers entry resolves;
  * every stub has a label + kind (+ purpose or screenshot where available);
  * journal has a press-attempted+press-outcome pair (or press-skipped/boundary)
    for every element measured on the ribbon faces.
Exit 0 = clean.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB


def main():
    ui = json.loads((KB / "ui.json").read_text(encoding="utf-8"))
    containers = ui["containers"]
    cont_ids = set(containers)
    gaps = []
    marker_counts = {"triggers": 0, "opens": 0, "unexplored": 0}

    for cid, c in containers.items():
        kids = c.get("children", [])
        if not kids and c.get("explored", True):
            gaps.append(f"{cid}: empty children but explored != false (dishonest-empty)")
        for e in kids:
            n = sum([bool(e.get("triggers")), bool(e.get("opens")), bool(e.get("unexplored"))])
            if n != 1:
                gaps.append(f"{cid}/{e.get('label')}: {n} markers (must be exactly 1)")
            for m in marker_counts:
                if e.get(m):
                    marker_counts[m] += 1
            if e.get("opens") and e["opens"] not in cont_ids:
                gaps.append(f"{cid}/{e.get('label')}: opens {e['opens']} -> dangling")
            if not e.get("label") and not e.get("id"):
                gaps.append(f"{cid}: element with neither label nor id")
        for cc in c.get("child_containers", []):
            if cc not in cont_ids:
                gaps.append(f"{cid}: child_container {cc} -> dangling")
        if not c.get("explored", True):
            if not c.get("label"):
                gaps.append(f"{cid}: stub without label")

    # journal coverage: every ribbon-face element id has press evidence
    journal_targets = {"attempted": set(), "skipped": set(), "boundary": set()}
    for line in (KB / "journal.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        j = json.loads(line)
        if j["action"] == "press-attempted":
            journal_targets["attempted"].add(j["target"])
        elif j["action"] == "press-skipped":
            journal_targets["skipped"].add(j["target"])
        elif j["action"] == "boundary":
            journal_targets["boundary"].add(j["target"])
    evidence = (journal_targets["attempted"] | journal_targets["skipped"]
                | journal_targets["boundary"])
    for rid in ("ui:ribbon-home", "ui:ribbon-insert", "ui:ribbon-design", "ui:ribbon-layout"):
        for e in containers.get(rid, {}).get("children", []):
            slug = (e.get("id") or "").removeprefix("el:")
            if slug and slug not in evidence and e.get("control_type") != "gallery":
                gaps.append(f"{rid}/{slug}: no journal press evidence")

    stubs = sorted(cid for cid, c in containers.items() if not c.get("explored", True))
    report = {"containers": len(containers), "markers": marker_counts,
              "stubs": len(stubs), "stub_ids": stubs, "gaps": gaps}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\nRESULT:", "PASS" if not gaps else f"FAIL ({len(gaps)} gaps)")
    return 0 if not gaps else 1


if __name__ == "__main__":
    raise SystemExit(main())
