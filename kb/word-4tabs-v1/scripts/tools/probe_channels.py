"""Step 1 §6 — probe which behavior-measurement channels THIS app offers (playbook 06 prep).

Confirms each channel LIVE (toolbox/behavior.md: file / object-model / UI-metadata / screen)
and records the map in kb/word-4tabs-v1/behavior-channels.json. SaveAs2 targets live in the
OS temp scratch dir only — the scratch copy is itself throwaway (CR3-safe; journaled).
"""
import json
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common
from session import WordSession

OUT = common.APP_KB / "behavior-channels.json"


def main():
    run_id = common.make_run_id() + "-channels"
    jrnl = common.get_journal(run_id)
    pinned = json.loads((common.APP_KB / "version.json").read_text(encoding="utf-8"))
    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    jrnl.append(common.journal_event(actor="stage1.channels", action="launch",
                target=f"pid={sess.pid}", outcome="ok", data={"build": sess.build}))
    channels = {}
    try:
        # --- 1) saved-file channel: SaveAs2 to a scratch temp path, read the zip-XML ---
        out_path = common.SCRATCH_DIR / f"channel-probe-{time.strftime('%H%M%S')}.docx"
        sess.doc.Content.InsertAfter("channel probe text")
        sess.doc.SaveAs2(str(out_path), 16)   # 16 = wdFormatXMLDocument (.docx)
        names = []
        with zipfile.ZipFile(out_path) as z:
            names = z.namelist()
            doc_xml = z.read("word/document.xml").decode("utf-8", "replace")
        ok_file = "channel probe text" in doc_xml
        channels["file"] = {
            "available": ok_file,
            "how": "doc.SaveAs2(<OS-temp scratch path>, 16) -> zip-XML (.docx); diff "
                   "word/*.xml between experiments (option-dimension, baseline-subtraction, "
                   "noise self-diff recipes)",
            "confirmed_by": f"saved {out_path.name}; word/document.xml contains the probe "
                            f"text; {len(names)} zip members",
            "safety": "SaveAs2 targets only the OS-temp scratch dir; fixture itself never saved"}
        jrnl.append(common.journal_event(actor="stage1.channels", action="probe-channel",
                    target="file", outcome="ok" if ok_file else "FAILED",
                    data=channels["file"]))

        # --- 2) object-model channel: COM property reads (already the run's truth oracle) ---
        f = sess.app.Selection.Font
        ps = sess.doc.Sections(1).PageSetup
        ok_com = (sess.doc_hash() != "<com-busy>" and float(ps.TopMargin) > 0)
        channels["object_model"] = {
            "available": ok_com,
            "how": "Word COM (win32com DispatchEx): doc_hash/format_sig/object_fingerprint/"
                   "layout_fingerprint (session.py) + targeted property reads at the "
                   "granularity the feature operates on",
            "confirmed_by": f"TopMargin={float(ps.TopMargin)}, Bold={int(f.Bold)}, "
                            f"doc_hash readable",
            "caveats": "busy while a modal is up (<com-busy> sentinel); paragraph-level reads "
                       "collapse mixed runs to sentinels (behavior.md)"}
        jrnl.append(common.journal_event(actor="stage1.channels", action="probe-channel",
                    target="object_model", outcome="ok" if ok_com else "FAILED",
                    data=channels["object_model"]))

        # --- 3) UI-metadata channel: GetEnabledMso / GetPressedMso over idMso inventory ---
        cb = sess.app.CommandBars
        probe = {}
        for idmso in ("Bold", "Paste", "TableColumnsGallery", "ObjectBringForward",
                      "PageMarginsGallery"):
            try:
                probe[idmso] = {"enabled": bool(cb.GetEnabledMso(idmso))}
            except Exception as e:
                probe[idmso] = {"error": str(e)[:80]}
        try:
            probe["Bold"]["pressed"] = bool(cb.GetPressedMso("Bold"))
        except Exception as e:
            probe["Bold"]["pressed_error"] = str(e)[:80]
        ok_meta = all("enabled" in v for v in probe.values())
        # expectation: ObjectBringForward disabled at bare caret (object-arrange precondition)
        channels["ui_metadata"] = {
            "available": ok_meta,
            "how": "CommandBars.GetEnabledMso(idMso) / GetPressedMso(idMso) — enablement "
                   "matrix per staged context (bare caret / selection / in-table / object "
                   "selected); the same sweep yields Step 3 `requires` precondition evidence",
            "confirmed_by": probe,
            "caveats": "idMso inventory comes from the step-1 enum dumps (automation_id)"}
        jrnl.append(common.journal_event(actor="stage1.channels", action="probe-channel",
                    target="ui_metadata", outcome="ok" if ok_meta else "FAILED",
                    data=channels["ui_metadata"]))

        # --- 4) screen channel: proven in this step's capture checks ---
        channels["screen"] = {
            "available": True,
            "how": "window-true PrintWindow-style grabs (capture.py) + real input injection "
                   "(driver.py); reserve for live previews / caret / undo granularity "
                   "(P0-P1 dynamics only, R6.6)",
            "confirmed_by": "step-1 tool-check captures verified by eye (4 target types)"}

        channels["strongest_order"] = ["file", "object_model", "ui_metadata", "screen"]
        channels["build"] = sess.build
        OUT.write_text(json.dumps(channels, indent=2, ensure_ascii=False), encoding="utf-8")
        jrnl.append(common.journal_event(actor="stage1.channels", action="write",
                    target=str(OUT), outcome="ok",
                    data={"channels": list(channels)}))
        print(json.dumps({k: v.get("available") if isinstance(v, dict) else v
                          for k, v in channels.items()}, indent=2))
    finally:
        sess.close()
        jrnl.append(common.journal_event(actor="stage1.channels", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed", data={}))


if __name__ == "__main__":
    main()
