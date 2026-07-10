"""Debug: why does the tab strip show no contextual tabs after COM table insert+select?"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common
from session import WordSession, force_foreground
import uia_attach as ua

pinned = json.loads((common.APP_KB / "version.json").read_text(encoding="utf-8"))
fixture = common.fresh_scratch_fixture()
sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
try:
    sess.doc.Content.InsertAfter("Probe text.")
    t = sess.doc.Tables.Add(sess.doc.Paragraphs(1).Range, 3, 3)
    t.Cell(1, 1).Range.Select()
    force_foreground(sess.frame)
    time.sleep(2.0)

    from pywinauto import Desktop
    win = Desktop(backend="uia").window(handle=sess.frame)

    # 1) all TabItems anywhere under the frame (fresh walk)
    items = win.descendants(control_type="TabItem")
    print("ALL TabItems:", [(i.element_info.name, i.element_info.automation_id)
                            for i in items])

    # 2) children of the 'Ribbon Tabs' Tab strip specifically
    strip = win.child_window(title="Ribbon Tabs", control_type="Tab")
    print("strip children:", [(c.element_info.control_type, c.element_info.name)
                              for c in strip.children()])

    # 3) selection really in table?
    print("selection in table:", bool(sess.app.Selection.Information(12)))  # wdWithInTable
finally:
    sess.close()
