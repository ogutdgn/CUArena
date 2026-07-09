"""Validate the prober classifier on a handful of representative Home controls before the
full crawl. Not a KB producer — a sanity check I read with my own eyes + the journal."""
import json
import sys
import time
from pathlib import Path

import win32api

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import common
from session import WordSession
import uia_attach as ua
import enumerator as en
import driver as drv
import prober as pb

# idMso -> expected kind (my hypothesis; the run measures the truth)
EXPECT = [
    ("Bold", "feature"),
    ("AlignCenter", "feature"),
    ("ParagraphMarks", "feature"),   # Show All -> app:show_all toggle
    ("FontDialog", "dialog"),
    ("ChangeCaseGallery", "flyout"),
    ("NavigationPaneFind", "pane"),  # Find primary opens the Navigation pane
    ("ReplaceDialog", "dialog"),
]


def _find(groups, idmso):
    for g in groups:
        for c in g["controls"]:
            if c["automation_id"] == idmso:
                return c
    return None


def main():
    run_id = common.make_run_id() + "-test-prober"
    jrnl = common.get_journal(run_id)
    screen_w = win32api.GetSystemMetrics(0)
    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build="16.0.20131")
    try:
        # prepare a real selection + armed clipboard
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
        sess.select_paragraph(1)
        try:
            sess.doc.Paragraphs(1).Range.Copy()
        except Exception:
            pass
        win = ua.attach(sess.frame)
        time.sleep(0.5)
        enum = en.enumerate_tab(win, "Home")
        results = []
        for idmso, expected in EXPECT:
            c = _find(enum["groups"], idmso)
            if not c:
                results.append({"id": idmso, "found": False})
                continue
            rect = tuple(c["rect"])
            sess.select_paragraph(1)
            baseline = pb.snapshot(sess, screen_w)
            jrnl.append(common.journal_event(actor="test.prober", action="press-attempted",
                        target=idmso, outcome="", data={"rect": list(rect)}))
            drv.ensure_frame_foreground(sess.frame)
            pt = drv.click_rect(rect)
            neww = pb.observe(sess, baseline["hwnds"])
            sess.select_paragraph(1)
            after = pb.snapshot(sess, screen_w)
            kind, detail = pb.classify(baseline, after, neww)
            reset_ok, notes = pb.restore(sess, kind, detail, pt, baseline, screen_w)
            jrnl.append(common.journal_event(actor="test.prober", action="press-outcome",
                        target=idmso, outcome=kind,
                        data={"expected": expected, "detail": detail,
                              "reset_ok": reset_ok, "notes": notes}))
            results.append({"id": idmso, "expected": expected, "measured": kind,
                            "match": kind == expected, "reset_ok": reset_ok,
                            "detail": {k: detail.get(k) for k in ("class", "title", "state_changed", "panes_after") if k in detail},
                            "notes": notes})
        print(json.dumps(results, indent=2, ensure_ascii=False))
    finally:
        sess.close()
        jrnl.append(common.journal_event(actor="test.prober", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed", data={}))


if __name__ == "__main__":
    main()
