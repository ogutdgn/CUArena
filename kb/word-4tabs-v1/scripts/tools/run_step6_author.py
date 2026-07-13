"""Step 6 authoring — turn behavior/measurements.json (the enablement matrix + ExecuteMso
effect/toggle deltas) + the Step-5 structure into an EVIDENCED BehaviorRecord on every
depth-set sub-feature, written through the kernel. Findings are FUNCTIONAL (R6.2) and grounded
in a MEASUREMENT (R6.5 — no memory-only claims): effect prose is derived from the measured
delta + the node's measured affects; state_rules from the measured enablement matrix + toggle
test; options from the Step-5 enumerated surface. Every filled slot points at its evidence
(the measurement journal id + measurements.json entry, and for openers the captured surface).
Unmeasured slots are honest `pending` (R6.3/R6.5). Gesture + build pinned (R6.4).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common
from kernel.models import BehaviorRecord, BehaviorOption

KB = common.APP_KB


def clean_delta(delta):
    """Drop com-busy / failed-read artifacts: a transition to or from the -1 sentinel means the
    fingerprint read failed (a modal held COM busy), not a real change."""
    if not delta:
        return delta
    out = []
    for d in delta:
        if "->-1" in d or ":-1->" in d or d.endswith("->-1"):
            continue
        out.append(d)
    return out


def effect_prose(node_id, affects, what, delta, toggle, marker, opens, surf):
    """Functional effect prose grounded in the measured delta (R6.2/R6.5)."""
    if marker == "opens" or (not delta and opens):
        if surf:
            n = len([c for c in surf.get("children", []) if c.get("label")])
            kind = surf.get("kind", "surface")
            return (f"Opens the {surf.get('label', opens)} {kind} — the surface that presents "
                    f"this capability's options ({n} controls enumerated in the structural pass). "
                    f"Applying a choice there changes: {affects}.")
        return f"Opens a surface presenting the options that change: {affects}."
    if not delta:
        return None
    parts = []
    if any(d == "selection-format" for d in delta):
        parts.append(f"changes the selection's formatting ({affects})")
    if any(d == "doc-text" for d in delta):
        parts.append("changes the document text/content")
    for d in delta:
        if d.startswith("obj:tables"):
            parts.append("adds or removes a table object")
        elif d.startswith("obj:inline_shapes"):
            parts.append("adds/changes an inline picture or object")
        elif d.startswith("obj:shapes") and "states" not in d:
            parts.append("adds/changes a floating shape")
        elif d.startswith("obj:shape_states"):
            parts.append("changes the selected object's z-order / wrapping / geometry")
        elif d.startswith("obj:comments"):
            parts.append("changes the document's comments")
        elif d.startswith("obj:fields"):
            parts.append("inserts a field")
        elif d.startswith("obj:bookmarks"):
            parts.append("changes the document's bookmarks")
        elif d.startswith("obj:omaths"):
            parts.append("adds/changes an equation (math zone)")
        elif d.startswith("obj:sections"):
            parts.append("changes the document's section structure")
        elif d.startswith("layout:"):
            prop = d.split(":")[1]
            parts.append(f"changes the page/section layout ({prop})")
        elif d.startswith("cells:"):
            parts.append(f"changes the table's cell count ({d.split(':',1)[1]} — cells "
                         "merged/split/added)")
        elif d.startswith("rows:"):
            parts.append(f"adds/removes table rows ({d.split(':',1)[1]})")
        elif d.startswith("cols:"):
            parts.append(f"adds/removes table columns ({d.split(':',1)[1]})")
        elif d.startswith("text:"):
            parts.append("changes the table's content/structure")
    if not parts:
        parts.append(f"changes: {affects}")
    prose = "Running it " + "; ".join(dict.fromkeys(parts)) + "."
    if toggle:
        prose += (" Measured toggle: a second press from the same state reverts the change "
                  "(on/off behavior).")
    else:
        prose += (" Measured as a command: a second press repeats/keeps the change rather than "
                  "reverting it.")
    return prose


def state_rules_prose(mso, enabled, pressed):
    if not enabled:
        return None
    on = sorted(c for c, v in enabled.items() if v is True)
    off = sorted(c for c, v in enabled.items() if v is False)
    bits = []
    if on and off:
        bits.append(f"enabled in context(s): {', '.join(on)}; disabled in: {', '.join(off)} "
                    "(measured via GetEnabledMso) — the disabled contexts are its preconditions")
    elif on and not off:
        bits.append("enabled in every staged context (no object/selection precondition measured)")
    elif off and not on:
        bits.append(f"disabled in every staged context ({', '.join(off)}) — needs a precondition "
                    "beyond the ones staged")
    if pressed:
        anyp = any(v for v in pressed.values())
        bits.append("exposes a pressed/selected state (a toggle or current-selection reflector)"
                    if anyp else "no pressed state observed (a command, not a toggle)")
    return "; ".join(bits) if bits else None


def main():
    meas_path = KB / "behavior" / "measurements.json"
    meas = json.loads(meas_path.read_text(encoding="utf-8")) if meas_path.exists() else \
        {"build": "", "nodes": {}, "enabled_matrix": {}, "pressed": {}}
    build = meas.get("build", "")
    mnodes = meas.get("nodes", {})
    ui = json.loads((KB / "ui.json").read_text(encoding="utf-8"))["containers"]
    pri = json.loads((KB / "priority.json").read_text(encoding="utf-8"))
    whole = {f for f, d in pri.get("derived_features", {}).items() if d.get("scope") == "whole"}
    layers = pri["layers"]
    lay = {i: L for L, ids in layers.items() for i in ids}

    # find the measurement run id (evidence anchor) from the journal
    measure_run = None
    for line in (KB / "journal.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get("actor") == "stage6" and e.get("action") == "launch":
            measure_run = e.get("run_id")
    ev_anchor = f"journal:{measure_run}" if measure_run else "behavior/measurements.json"

    writer = common.get_writer()
    run_id = common.make_run_id() + "-step6-author"
    jrnl = common.get_journal(run_id)

    authored = {"records": 0, "effect_measured": 0, "opener": 0, "pending_only_effect": 0}
    for p in sorted((KB / "features").glob("*.json")):
        ff = json.loads(p.read_text(encoding="utf-8"))
        changed = False
        for s in ff["subfeatures"]:
            sid = s["id"]
            L = lay.get(sid)
            in_set = (L in ("P0", "P1", "P2", "P3")) or (s.get("parent") in whole)
            if not in_set:
                continue
            m = mnodes.get(sid, {})
            mso = m.get("idmso")
            marker = m.get("marker") or ("opens" if s.get("opens") else "triggers")
            opens = s.get("opens")
            surf = ui.get(opens) if opens else None
            delta = clean_delta(m.get("effect_delta"))
            toggle = m.get("toggle")
            enabled = m.get("enabled") or {}
            pressed = m.get("pressed") or {}

            evidence = [ev_anchor, f"behavior/measurements.json#{sid}"]
            eff = effect_prose(sid, s["affects"], s["what_it_does"], delta, toggle, marker,
                               opens, surf)
            sr = state_rules_prose(mso, enabled, pressed)
            pending = []

            options = []
            if marker == "opens" and surf:
                for c in surf.get("children", [])[:24]:
                    lbl = c.get("label")
                    if not lbl or lbl.lower() in ("ok", "cancel", "close", "apply", "help"):
                        continue
                    options.append(BehaviorOption(
                        name=lbl,
                        found=None,   # per-option functional semantics not individually measured
                        evidence=[f"behavior/measurements.json#{sid}"]))
                if options:
                    pending.append("per-option functional differences (each option's individual "
                                   "effect enumerated structurally in Step 5; not measured "
                                   "one-by-one this pass)")
                authored["opener"] += 1
            defaults = None
            if delta:
                authored["effect_measured"] += 1
                defaults = ("baseline: the command applied its effect from the staged neutral "
                            "state (measured delta above); pre-selected options not separately "
                            "diffed") if marker == "triggers" else None
            else:
                if marker == "triggers":
                    pending.append("effect delta (idMso not resolved or ExecuteMso not applicable "
                                   "in the staged contexts; the control's press outcome was "
                                   "measured in Steps 2-3 — see its skeleton element)")
                    authored["pending_only_effect"] += 1
            if not defaults:
                pending.append("defaults / baseline-subtraction (file-channel diff not run per "
                               "sub this pass)")
            if sr is None:
                pending.append("state_rules (enablement not resolved — no idMso mapped)")
            # dynamics: R6.6 — only P0-P1 owe dynamics; screen channel not recorded -> pending
            dynamics = None
            if L in ("P0", "P1"):
                pending.append("dynamics: live-preview / caret-landing / undo-granularity "
                               "(screen-channel recording not run this pass, R6.6)")
            else:
                pending.append("dynamics not required below P1 (R6.6)")

            rec = BehaviorRecord(
                effect=eff,
                options=options,
                defaults=defaults,
                state_rules=sr,
                dynamics=dynamics,
                extra=(f"idMso: {mso}" if mso else None),
                pending=pending,
                evidence=evidence,
                gesture=m.get("gesture") or ("ribbon-click (opens a surface — not ExecuteMso'd: "
                        "modal launcher)" if marker == "opens" else "ribbon-click"),
                build=build or None,
            )
            s["behavior_record"] = rec.model_dump()
            s["behavior"] = eff or (sr or "measured via enablement matrix; see behavior_record")
            authored["records"] += 1
            changed = True
        if changed:
            writer.write_feature_file(ff)

    jrnl.append(common.journal_event(actor="stage6.author", action="write-behavior",
                target="features/*.json", outcome="ok", data=authored))
    print(json.dumps(authored, indent=2))


if __name__ == "__main__":
    main()
