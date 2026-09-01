"""Step 6 effect re-measure — the first sweep's generic fingerprints (tables.Count etc.) do NOT
capture table STRUCTURE changes (rows/cols/cells) or clipboard/selection effects, so a few
core P1 commands (Merge Cells, Insert Rows/Columns, Cut, Highlight) measured no effect_delta.
This re-measures exactly those, with a structure-aware fingerprint and the correct selection
staged per command, then patches behavior/measurements.json. (Copy = clipboard-only and
InsertNewComment = a non-fingerprintable draft stay honestly pending — genuinely not
observable on any offline channel; the Step-2/3 measurement records that.)
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common
from session import WordSession
import driver as drv

KB = common.APP_KB


def _g(fn, d=None):
    try:
        return fn()
    except Exception:
        return d


def tbl_fp(sess):
    d = sess.doc
    t = _g(lambda: d.Tables(1))
    if t is None:
        return {"present": False}
    return {"rows": _g(lambda: t.Rows.Count), "cols": _g(lambda: t.Columns.Count),
            "cells": _g(lambda: t.Range.Cells.Count),
            "text": _g(lambda: hash(t.Range.Text) % 10_000_000)}


def main():
    run_id = common.make_run_id() + "-step6-remeasure"
    jrnl = common.get_journal(run_id)
    pinned = json.loads((KB / "version.json").read_text(encoding="utf-8"))
    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    cb = sess.app.CommandBars
    patched = {}
    try:
        doc = sess.doc
        # --- table structure commands ---
        def fresh_table():
            for _ in range(15):
                drv.send_keys("^z"); time.sleep(0.1)
                if _g(lambda: doc.Tables.Count, 0) == 0:
                    break
            t = doc.Tables.Add(doc.Paragraphs(1).Range, 3, 3)
            for i, cell in enumerate(t.Range.Cells):
                cell.Range.Text = f"c{i}"
            return t

        def measure(mso, select_fn, label, structure=True):
            t = fresh_table()
            select_fn(t)
            time.sleep(0.2)
            before = tbl_fp(sess) if structure else {"doc": sess.doc_hash()}
            try:
                cb.ExecuteMso(mso)
            except Exception as e:
                jrnl.append(common.journal_event(actor="stage6.remeasure", action="effect",
                            target=mso, outcome=f"error: {e}", data={}))
                return None
            time.sleep(0.3)
            after = tbl_fp(sess) if structure else {"doc": sess.doc_hash()}
            d = [f"{k}:{before.get(k)}->{after.get(k)}" for k in after
                 if before.get(k) != after.get(k)]
            jrnl.append(common.journal_event(actor="stage6.remeasure", action="effect",
                        target=mso, outcome="measured", data={"delta": d, "label": label}))
            return d

        # Merge Cells: select two adjacent cells in row 1
        def sel_two(t):
            doc.Range(t.Cell(1, 1).Range.Start, t.Cell(1, 2).Range.End).Select()
        patched["subfeature:table-merge-cells"] = measure(
            "MergeCells", sel_two, "merge two selected cells into one")
        # Insert Rows Above: cursor in a cell
        def sel_cell(t):
            t.Cell(1, 1).Range.Select()
        patched["subfeature:table-insert-rows"] = measure(
            "TableRowsInsertAboveWord", sel_cell, "insert a row above the current row")
        patched["subfeature:table-insert-columns"] = measure(
            "TableColumnsInsertLeft", sel_cell, "insert a column left of the current column")

        # --- selection/clipboard commands (doc-text channel) ---
        for _ in range(15):
            drv.send_keys("^z"); time.sleep(0.1)
            if _g(lambda: doc.Tables.Count, 0) == 0:
                break
        doc.Content.Delete()
        doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")

        def sel_words():
            doc.Range(doc.Paragraphs(1).Range.Start, doc.Paragraphs(1).Range.Start + 9).Select()
        # Cut: removes the selection -> doc text changes
        sel_words(); time.sleep(0.2)
        b = sess.doc_hash()
        try:
            cb.ExecuteMso("Cut"); time.sleep(0.3)
            a = sess.doc_hash()
            patched["subfeature:cut"] = ["doc-text"] if a != b else []
            drv.send_keys("^z"); time.sleep(0.2)
            jrnl.append(common.journal_event(actor="stage6.remeasure", action="effect",
                        target="Cut", outcome="measured", data={"changed": a != b}))
        except Exception:
            pass
        # Highlight: applies a highlight color -> selection format changes
        sel_words(); time.sleep(0.2)
        bf = sess.format_sig()
        try:
            cb.ExecuteMso("TextHighlightColorPicker"); time.sleep(0.3)
            af = sess.format_sig()
            patched["subfeature:text-highlight-color-picker"] = \
                ["selection-format"] if af != bf else []
            drv.send_keys("^z"); time.sleep(0.2)
            jrnl.append(common.journal_event(actor="stage6.remeasure", action="effect",
                        target="TextHighlightColorPicker", outcome="measured",
                        data={"changed": af != bf}))
        except Exception:
            pass

        # patch measurements.json
        mp = KB / "behavior" / "measurements.json"
        meas = json.loads(mp.read_text(encoding="utf-8"))
        applied = {}
        for sid, d in patched.items():
            if d:
                meas["nodes"].setdefault(sid, {})["effect_delta"] = d
                meas["nodes"][sid]["gesture"] = f"executeMso (re-measure, structure-aware)"
                meas["nodes"][sid]["remeasured"] = True
                applied[sid] = d
        mp.write_text(json.dumps(meas, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({"remeasured": applied}, indent=2))
    finally:
        sess.close()
        jrnl.append(common.journal_event(actor="stage6.remeasure", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed", data={"patched": list(patched)}))


if __name__ == "__main__":
    main()
