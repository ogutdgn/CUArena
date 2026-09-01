"""Step 3 addendum — measure the Layout tab's ARRANGE group with an object selected.

The Layout > Arrange controls (Position, Wrap Text, Bring Forward, Send Backward, Align,
Group, Rotate, Selection Pane) read DISABLED on a bare-text fixture, so Step 2 left them
`unexplored` (honest, R2.2). They are the SHARED object-arrange machinery (feature:object-arrange,
measured on the object-format contextual tabs). This pass inserts a floating shape, selects it,
activates the LAYOUT tab (Arrange now enabled), press-observe-classifies each Arrange control,
and SURGICALLY replaces just those element records inside ui:ribbon-layout (every other Layout
child untouched). dl_spec.LAYOUT_ARRANGE_HOSTS then folds them into the object-arrange subs as
extra trigger paths — so the Layout tab is a real door into object-arrange, not a dead group.

Reuses the contextual probe machinery (object-context reset). Idempotent: re-running re-measures
and re-merges the same 8 element ids.
"""
import json
import sys
import time
from pathlib import Path

import win32api

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common
from session import WordSession
import uia_attach as ua
import enumerator as en
import driver as drv
import capture as cap
import run_step2 as r2
import run_step3_contextual as r3c

KB = common.APP_KB
TAB = "Layout"
CID = "ui:ribbon-layout"
ARRANGE_GROUP = "Arrange"


def main():
    run_id = common.make_run_id() + "-step3-layout-arrange"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    screen_w = win32api.GetSystemMetrics(0)
    pinned = json.loads((KB / "version.json").read_text(encoding="utf-8"))
    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    jrnl.append(common.journal_event(actor="stage3.layout-arrange", action="launch",
                target=f"pid={sess.pid}", outcome="ok", data={"run_id": run_id}))
    merged = {}
    try:
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
        sess.select_paragraph(1)

        def ins_shape():
            sess.doc.Shapes.AddShape(1, 100, 100, 120, 80)
            return True

        def sel_shape():
            sess.doc.Shapes(1).Select()
            return True

        ins_shape()
        time.sleep(0.6)
        sel_shape()
        drv.ensure_frame_foreground(sess.frame)
        time.sleep(1.0)
        win = ua.attach(sess.frame)
        time.sleep(0.4)
        en.select_tab(win, TAB)
        time.sleep(0.5)
        drv.ensure_frame_foreground(sess.frame)
        time.sleep(0.3)
        frame_img, frame_rect = cap.grab_window(sess.frame)

        ctx = {"sess": sess, "jrnl": jrnl, "writer": writer, "win": win, "cid": CID,
               "tab_label": TAB, "family": "shape", "fingerprint": r3c.fp_shape,
               "reselect": sel_shape, "reinsert": ins_shape, "screen_w": screen_w,
               "frame_img": frame_img, "frame_rect": frame_rect,
               "seen_surfaces": set(writer.load_ui().containers.keys()),
               "stub_containers": {},
               "base_doc_hash": sess.doc_hash(), "base_family": r3c.fp_shape(sess),
               "base_objects": sess.object_fingerprint(),
               "base_stable_hwnds": r3c._stable_hwnds(sess.pid)}

        # enumerate the Arrange group live (with the shape selected)
        arrange_leaves = None
        for gname, gkeytip, leaves in en.live_leaves(win, TAB):
            if gname == ARRANGE_GROUP:
                arrange_leaves = leaves
                break
        assert arrange_leaves is not None, "Arrange group not found on Layout tab"

        for el, props in arrange_leaves:
            label = props.name or props.automation_id or "?"
            ct = props.control_type
            slug = r2.slugify(props.automation_id, label)   # SAME slug as Step 2 -> same el id
            if not props.is_enabled:
                # still disabled even with a shape selected (e.g. Group needs 2+ objects) —
                # keep it honest unexplored, but note the measured precondition
                jrnl.append(common.journal_event(actor="stage3.layout-arrange",
                            action="press-skipped", target=slug, outcome="disabled-with-object",
                            data={"label": label, "note": "still disabled with one shape "
                                  "selected (needs a stronger precondition, e.g. 2+ objects)"}))
                icon = r2.make_icon(frame_img, frame_rect, tuple(props.rect), writer, CID,
                                    slug, label)
                merged[f"el:{slug}"] = {"id": f"el:{slug}", "control_type": ct.lower(),
                    "label": label, "icon": icon, "tooltip": props.tooltip or None,
                    "shortcut": props.accelerator_key or None,
                    "location": f"ui:main-window > {CID}", "bounds": list(props.rect),
                    "source": "uia", "unexplored": True,
                    "state_notes": "object-gated: still disabled with a single shape selected "
                                   "(measured); needs a stronger precondition"}
                continue
            presses = []
            if ct == "SplitButton":
                primary, dropdown = drv.split_zone_rects(el)
                presses.append((primary or drv.zone_point(props.rect, "primary"),
                                slug, label, False))
                presses.append((dropdown or drv.zone_point(props.rect, "dropdown"),
                                slug + "-dropdown", f"{label} (dropdown)", True))
            else:
                presses.append((tuple(props.rect), slug, label, False))
            for click_rect, pslug, plabel, dz in presses:
                e, ok, k = r3c.probe_contextual_control(ctx, props, click_rect, pslug,
                                                        plabel, dropdown_zone=dz)
                e["state_notes"] = ((e.get("state_notes") or "")
                    + "; measured on the Layout tab with a shape selected (object-arrange, "
                      "shared with the object-format contextual tabs)").strip("; ")
                merged[e["id"]] = e

        # ---- surgical merge into ui:ribbon-layout ----
        ui = writer.load_ui()
        layout = ui.containers[CID].model_dump()
        new_children = []
        for child in layout["children"]:
            new_children.append(merged.pop(child["id"], child))
        # any measured element not already present (e.g. a split dropdown) is appended
        for eid, e in merged.items():
            new_children.append(e)
        layout["children"] = new_children
        # register any newly opened stub containers
        for sid, c in ctx["stub_containers"].items():
            if sid not in ui.containers:
                writer.upsert_container(c)
        writer.upsert_container(layout)
        jrnl.append(common.journal_event(actor="stage3.layout-arrange", action="write-containers",
                    target=CID, outcome="ok",
                    data={"arrange_elements_measured": sorted(merged.keys()) or "merged-in-place",
                          "stub_containers": sorted(ctx["stub_containers"].keys())}))

        from collections import Counter
        mk = Counter("opens" if c.get("opens") else "triggers" if c.get("triggers")
                     else "unexplored" for c in new_children)
        print(json.dumps({"layout_children": len(new_children), "markers": dict(mk),
                          "arrange_stubs": sorted(ctx["stub_containers"].keys())}, indent=2))
    finally:
        sess.close()
        jrnl.append(common.journal_event(actor="stage3.layout-arrange", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed", data={}))


if __name__ == "__main__":
    main()
