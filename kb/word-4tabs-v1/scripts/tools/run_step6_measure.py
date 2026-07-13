"""Step 6 measurement (GUI/COM) — measure the SEMANTICS of every depth-set sub-feature through
the app's strongest offline channels (behavior-channels.json), writing raw measurements to
behavior/measurements.json + the journal. step6_author.py turns these into BehaviorRecords.

Channels used (toolbox/behavior.md):
  * UI-metadata: CommandBars.GetEnabledMso(idMso) across STAGED CONTEXTS (bare caret / formatted
    selection / in-table / picture / shape / chart / equation / header-edit) — the enablement
    matrix = state_rules ("enabled when …") AND the Step-3 `requires` precondition evidence, in
    ONE hang-free sweep. GetPressedMso = toggle/selected state.
  * Object model + file: for a COMMAND endpoint (the sub's element `triggers`, not `opens`), run
    the ribbon button's REAL code headlessly via CommandBars.ExecuteMso(idMso) in the right
    context, and read the delta on doc_hash / format_sig / object_fingerprint / layout_fingerprint
    (session fingerprints) — the measured EFFECT. Toggle test: ExecuteMso twice, compare.
Gesture recorded = executeMso(idMso) (the button's real code path); build pinned. Openers/modal
launchers are NOT ExecuteMso'd (deadlock risk, toolbox/behavior.md) — their effect is "opens the
measured surface" (structural, from Step 5).

idMso map is built LIVE: enumerate the four ribbon faces + each contextual family tab, reading
automation_id (== idMso) per control, keyed by the same el-id slug the KB uses.
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
import run_step2 as r2
import run_step3_contextual as r3c

KB = common.APP_KB
OUT = KB / "behavior"


def load_depth_set():
    pri = json.loads((KB / "priority.json").read_text(encoding="utf-8"))
    whole = {f for f, d in pri.get("derived_features", {}).items() if d.get("scope") == "whole"}
    layers = pri["layers"]
    lay = {}
    for L, ids in layers.items():
        for i in ids:
            lay[i] = L
    ffiles = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((KB / "features").glob("*.json"))]
    subs = [s for ff in ffiles for s in ff["subfeatures"]]
    ui = json.loads((KB / "ui.json").read_text(encoding="utf-8"))["containers"]
    el_marker = {}
    for c in ui.values():
        for e in c.get("children", []):
            if e.get("id"):
                if e.get("triggers"):
                    el_marker[e["id"]] = ("triggers", e["triggers"])
                elif e.get("opens"):
                    el_marker[e["id"]] = ("opens", e["opens"])
                else:
                    el_marker[e["id"]] = ("unexplored", None)
    depth = []
    for s in subs:
        L = lay.get(s["id"])
        in_set = (L in ("P0", "P1", "P2", "P3")) or (s.get("parent") in whole)
        if not in_set:
            continue
        # primary element = first mouse trigger-path leaf that is a real ribbon/contextual el
        prim = None
        for tp in s.get("trigger_paths", []):
            if tp.get("kind") == "mouse" and tp.get("path"):
                leaf = tp["path"][-1]
                if leaf.startswith("el:"):
                    prim = leaf
                    if el_marker.get(leaf, ("", ))[0] == "triggers":
                        break     # prefer a command element for effect measurement
        depth.append({"id": s["id"], "layer": L or "whole-child", "primary_el": prim,
                      "marker": el_marker.get(prim, ("", None))[0] if prim else "",
                      "opens": s.get("opens")})
    return depth


CONTEXTS = ["bare", "text-selected", "in-table", "picture-selected", "svg-selected",
            "shape-selected", "smartart-selected", "chart-selected", "equation", "header-edit"]

# context -> [(live tab label to activate, el-id prefix == that tab's container id stem)]
CTX_TABS = {
    "in-table": [("Table Design", "ribbon-table-design-"),
                 ("Table Layout", "ribbon-table-layout-")],
    "picture-selected": [("Picture Format", "ribbon-picture-format-")],
    "svg-selected": [("Graphics Format", "ribbon-graphics-format-")],
    "shape-selected": [("Shape Format", "ribbon-shape-format-")],
    "smartart-selected": [("SmartArt Design", "ribbon-smart-art-design-"),
                          ("Format", "ribbon-smart-art-format-")],
    "chart-selected": [("Chart Design", "ribbon-chart-design-"),
                       ("Format", "ribbon-chart-format-")],
    "equation": [("Equation", "ribbon-equation-")],
    "header-edit": [("Header & Footer", "ribbon-header-footer-")],
}
CTX_PROBE = {"in-table": "table", "picture-selected": "picture", "svg-selected": "svg-graphic",
             "shape-selected": "shape", "smartart-selected": "smartart",
             "chart-selected": "chart", "equation": "equation", "header-edit": "header"}


def build_idmso_map(sess, win):
    """el-id slug -> idMso, live from the four ribbon faces + each contextual family tab."""
    idmso = {}

    def harvest(tab_title, prefix=""):
        try:
            for gname, kt, leaves in en.live_leaves(win, tab_title):
                for el, props in leaves:
                    slug = (prefix + r2.slugify(props.automation_id, props.name))[:100]
                    if props.automation_id:
                        idmso[f"el:{slug}"] = props.automation_id
        except Exception as e:
            print(f"  harvest {tab_title} failed: {e}")

    for t in ("Home", "Insert", "Design", "Layout"):
        en.select_tab(win, t)
        time.sleep(0.3)
        harvest(t)
    return idmso, harvest


def snap(sess):
    return {"doc": sess.doc_hash(), "fmt": sess.format_sig(),
            "obj": sess.object_fingerprint(), "lay": sess.layout_fingerprint()}


def delta(a, b):
    d = []
    if a["doc"] != b["doc"] and "<com-busy>" not in (a["doc"], b["doc"]):
        d.append("doc-text")
    if a["fmt"] != b["fmt"] and None not in (a["fmt"], b["fmt"]):
        d.append("selection-format")
    ao, bo = a["obj"] or {}, b["obj"] or {}
    for k in bo:
        if ao.get(k) != bo.get(k):
            d.append(f"obj:{k}:{ao.get(k)}->{bo.get(k)}")
    al, bl = a["lay"] or {}, b["lay"] or {}
    for k in bl:
        if al.get(k) != bl.get(k):
            d.append(f"layout:{k}:{al.get(k)}->{bl.get(k)}")
    return d


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    run_id = common.make_run_id() + "-step6-measure"
    jrnl = common.get_journal(run_id)
    screen_w = win32api.GetSystemMetrics(0)
    pinned = json.loads((KB / "version.json").read_text(encoding="utf-8"))
    depth = load_depth_set()
    png, svg = r3c.make_probe_png(), r3c.make_probe_svg()
    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    jrnl.append(common.journal_event(actor="stage6", action="launch", target=f"pid={sess.pid}",
                outcome="ok", data={"depth_set": len(depth)}))
    cb = sess.app.CommandBars
    measurements = {"build": sess.build, "contexts": CONTEXTS, "nodes": {}}
    try:
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog. "
                                     "Second sentence for context.")
        sess.select_paragraph(1)
        win = ua.attach(sess.frame)
        time.sleep(0.4)
        idmso, harvest = build_idmso_map(sess, win)

        # ---- stage each context, harvest contextual idMso, read the enablement matrix ----
        probes = {name: (ins, sel, fp) for name, ins, sel, fp, cond, ownr
                  in r3c.object_probes(sess, png, svg)}
        # map context -> (setup fn, contextual tab to harvest)
        def ctx_setup(ctx):
            try:
                sess.app.ActiveWindow.View.SeekView = 0
            except Exception:
                pass
            # clear objects
            sess.select_paragraph(1)
            for _ in range(12):
                drv.send_keys("^z")
                time.sleep(0.15)
                of = sess.object_fingerprint()
                if all(of.get(k, 0) in (0, -1) for k in ("tables", "inline_shapes", "shapes")):
                    break
            sess.select_paragraph(1)
            if ctx == "bare":
                sess.doc.Range(0, 0).Select()
            elif ctx == "text-selected":
                sess.select_paragraph(1)
                try:
                    f = sess.app.Selection.Font
                    f.Bold = True; f.Italic = True; f.Size = 14
                except Exception:
                    pass
            elif ctx == "header-edit":
                sess.app.ActiveWindow.View.SeekView = 9
            elif ctx in CTX_PROBE:
                fam = CTX_PROBE[ctx]
                probes[fam][0](); time.sleep(0.5); probes[fam][1]()
            time.sleep(0.5)

        enabled_matrix = {}   # idMso -> {ctx: bool}
        pressed_ctx = {}      # idMso -> {ctx: bool}
        for ctx in CONTEXTS:
            try:
                ctx_setup(ctx)
                win = ua.attach(sess.frame)
                # harvest contextual-tab idMso once, in this object's context (right tab active)
                for tab_label, prefix in CTX_TABS.get(ctx, []):
                    try:
                        harvest(tab_label, prefix=prefix)
                    except Exception:
                        pass
                all_idmsos = sorted(set(idmso.values()))
                for mso in all_idmsos:
                    try:
                        enabled_matrix.setdefault(mso, {})[ctx] = bool(cb.GetEnabledMso(mso))
                    except Exception:
                        enabled_matrix.setdefault(mso, {})[ctx] = None
                    try:
                        pressed_ctx.setdefault(mso, {})[ctx] = bool(cb.GetPressedMso(mso))
                    except Exception:
                        pass
                jrnl.append(common.journal_event(actor="stage6", action="enablement-context",
                            target=ctx, outcome="ok", data={"idmsos": len(all_idmsos)}))
            except Exception as e:
                jrnl.append(common.journal_event(actor="stage6", action="enablement-context",
                            target=ctx, outcome=f"error: {type(e).__name__}: {e}", data={}))

        measurements["idmso_map"] = idmso
        measurements["enabled_matrix"] = enabled_matrix
        measurements["pressed"] = pressed_ctx

        # ---- effect + toggle via ExecuteMso for COMMAND endpoints ----
        # choose the measurement context per node from where its idMso is enabled
        def ctx_for(mso):
            row = enabled_matrix.get(mso, {})
            for c in ("text-selected", "in-table", "picture-selected", "svg-selected",
                      "shape-selected", "smartart-selected", "chart-selected", "equation",
                      "header-edit", "bare"):
                if row.get(c):
                    return c
            return None

        effects = {}
        cur_ctx = None
        for node in depth:
            prim = node["primary_el"]
            mso = idmso.get(prim) if prim else None
            node_out = {"idmso": mso, "marker": node["marker"], "layer": node["layer"]}
            if mso:
                node_out["enabled"] = enabled_matrix.get(mso, {})
                node_out["pressed"] = pressed_ctx.get(mso, {})
            # effect only for command endpoints (marker triggers) with a resolvable idMso
            if mso and node["marker"] == "triggers":
                c = ctx_for(mso)
                if c:
                    if c != cur_ctx:
                        try:
                            ctx_setup(c); cur_ctx = c
                        except Exception:
                            pass
                    try:
                        before = snap(sess)
                        cb.ExecuteMso(mso)
                        time.sleep(0.3)
                        after = snap(sess)
                        d1 = delta(before, after)
                        # toggle test: run again, see if it reverts
                        cb.ExecuteMso(mso)
                        time.sleep(0.3)
                        after2 = snap(sess)
                        d2 = delta(after, after2)
                        reverts = (after2["fmt"] == before["fmt"] and after2["doc"] == before["doc"]
                                   and after2["obj"] == before["obj"])
                        node_out["effect_delta"] = d1
                        node_out["second_press_delta"] = d2
                        node_out["toggle"] = bool(d1) and reverts
                        node_out["gesture"] = f"executeMso({mso})"
                        node_out["measure_context"] = c
                        # restore
                        for _ in range(4):
                            drv.send_keys("^z"); time.sleep(0.15)
                        jrnl.append(common.journal_event(actor="stage6", action="effect",
                                    target=node["id"], outcome="measured",
                                    data={"idmso": mso, "delta": d1, "toggle": node_out["toggle"],
                                          "context": c}))
                    except Exception as e:
                        node_out["effect_error"] = str(e)[:100]
                        jrnl.append(common.journal_event(actor="stage6", action="effect",
                                    target=node["id"], outcome=f"error: {type(e).__name__}",
                                    data={"idmso": mso}))
            measurements["nodes"][node["id"]] = node_out

        (OUT / "measurements.json").write_text(
            json.dumps(measurements, indent=2, ensure_ascii=False), encoding="utf-8")
        got_effect = sum(1 for n in measurements["nodes"].values() if n.get("effect_delta"))
        got_mso = sum(1 for n in measurements["nodes"].values() if n.get("idmso"))
        print(json.dumps({"depth_set": len(depth), "idmso_resolved": got_mso,
                          "effects_measured": got_effect,
                          "matrix_idmsos": len(enabled_matrix)}, indent=2))
    finally:
        sess.close()
        jrnl.append(common.journal_event(actor="stage6", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed", data={}))


if __name__ == "__main__":
    main()
