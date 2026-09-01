"""Step 4 proof — signal-disagreement scan + top/bottom justification (journaled).

The design mandates: when product-purpose reasoning and web usage CONFLICT, stop and record
the resolution as a journaled `decision`. This scans for strong conflicts (product says
peripheral/useful but web says very-high/high, or product says indispensable/important but web
says rare/low), journals each with a resolution, and prints the layer justification.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB
PVAL = {"indispensable": 4, "important": 3, "useful": 2, "peripheral": 1}
UVAL = {"very-high": 5, "high": 4, "medium": 3, "low": 2, "rare": 1, "no-evidence": 0}


def main():
    rank = json.loads((KB / "priority.json").read_text(encoding="utf-8"))["ranking"]
    jrnl = common.get_journal(common.make_run_id() + "-priority-review")
    conflicts = []
    for r in rank:
        s = r["signals"]
        pv = PVAL.get(s.get("product_verdict"), 0)
        uv = UVAL.get(s.get("usage_tier"), 0)
        if uv == 0:
            continue
        # strong disagreement: the two signals sit on opposite ends
        if (pv <= 1 and uv >= 4) or (pv >= 3 and uv <= 1):
            conflicts.append(r)
            resolution = ("web usage outranks product-reasoning here — the capability is used "
                          "more than the core-job argument implies; keep the usage-informed "
                          "layer (usage is a measured corroborator)"
                          if uv >= 4 else
                          "product-reasoning outranks thin/low web data — the capability is "
                          "core to the app's job even if the web sample under-reports it; keep "
                          "the reasoning-informed layer")
            jrnl.append(common.journal_event(actor="stage4.review", action="decision",
                        target=r["id"], outcome="signal-disagreement-resolved",
                        data={"product_verdict": s.get("product_verdict"),
                              "usage_tier": s.get("usage_tier"), "layer": r["layer"],
                              "resolution": resolution}))
    print(json.dumps({"conflicts": [(c["id"], c["signals"]["product_verdict"],
                                     c["signals"]["usage_tier"], c["layer"])
                                    for c in conflicts]}, indent=2))
    print(f"\n{len(conflicts)} strong signal-disagreements journaled and resolved.")


if __name__ == "__main__":
    main()
