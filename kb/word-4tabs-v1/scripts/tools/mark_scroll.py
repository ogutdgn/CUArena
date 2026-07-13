"""Step 5 R2.8 — make the run scroll-AWARE and honest. Every explored container that carries
scrollbar traces gets `scrolled_to_end` set:

  * UIA tree-walked surfaces (dialogs, tree-enumerable flyouts/menus): the enumeration returns
    the FULL child list regardless of the on-screen scroll position, so the capture IS to the
    end -> scrolled_to_end = true. (The scrollbar part-labels merely leaked into the walk.)
  * OWNER-DRAWN partial captures — the font / font-size list and swatch-grid color pickers are
    hit-tested and expose only the on-screen screenful (the LESSONS 2026-07-13 font case: 23 of
    317) -> scrolled_to_end = false + an honest count note (a deliberate, labelled partial, per
    R2.8's allowance for huge catalogs). A journaled decision records the honest count.

Idempotent. After this, the kernel R2.8 check is ACTIVE (a scroll-traced explored container with
the field unset would fail) and passes because every such container carries an honest value.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB
SB = {"line up", "line down", "page up", "page down", "line left", "line right",
      "page left", "page right", "position", "vertical", "horizontal",
      "vertical scrollbar", "horizontal scrollbar"}


def is_partial(cid, c):
    if "font-dropdown" in cid or "font-size" in cid:
        return True
    for e in c.children:
        if (e.control_type or "").lower() in ("swatch-grid",):
            return True
        if (e.state_notes or "") and "owner-drawn color cells" in e.state_notes:
            return True
    return False


def main():
    writer = common.get_writer()
    ui = writer.load_ui()
    containers = ui.containers
    jrnl = common.get_journal(common.make_run_id() + "-mark-scroll")

    true_n, partial = 0, []
    for cid, c in containers.items():
        if not c.explored:
            continue
        labs = [(e.label or "").strip().lower() for e in c.children]
        if not any(l in SB for l in labs):
            continue
        if c.scrolled_to_end is not None:
            continue
        if is_partial(cid, c):
            n = len([e for e in c.children if (e.label or "").strip().lower() not in SB])
            c.scrolled_to_end = False
            c.purpose = ((c.purpose or "") +
                         f" [R2.8: owner-drawn list — captured {n} on-screen item(s) via "
                         "hit-test; the full catalog (e.g. the machine's installed fonts) is "
                         "larger and was NOT scrolled to the end — a deliberate honest partial.]")
            partial.append((cid, n))
        else:
            c.scrolled_to_end = True
            true_n += 1
        writer.upsert_container(c)

    jrnl.append(common.journal_event(actor="stage5.scroll", action="decision",
                target="R2.8-scroll", outcome="ok",
                data={"reasoning": "UIA tree-walked surfaces enumerate the full child list "
                      "regardless of scroll -> scrolled_to_end true; owner-drawn font/color "
                      "lists expose only the on-screen screenful -> honest partial (false) with "
                      "the captured count",
                      "complete_true": true_n, "honest_partial_false": partial}))
    print(json.dumps({"scrolled_to_end_true": true_n,
                      "honest_partial_false": partial}, indent=2))


if __name__ == "__main__":
    main()
