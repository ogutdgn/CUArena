TYPES = {"button","toggle","split","dropdown","menu","gallery","combo","spinner",
         "checkbox","launcher","label","slider","text-input","group-overflow"}
KINDS = {"feature","toggles","opens-dropdown","opens-menu","submenu","opens-dialog",
         "opens-pane","opens-group-flyout","activates-tab","cycles-state",
         "switches-view-mode","opens-backstage"}
PROBE_MODES = {"pressed-observed","pattern-inferred","boundary-declared"}
_OPENING = {k for k in KINDS if k.startswith("opens-") or k == "submenu"}


def _check_action(a, errs, where):
    if a["kind"] not in KINDS:
        errs.append(f"{where}: bad kind {a['kind']}")
    if a["kind"] in _OPENING and a["kind"] != "opens-backstage":
        if bool(a.get("ref")) == bool(a.get("boundary")):
            errs.append(f"{where}: ref XOR boundary violated")
    if a["kind"] == "opens-backstage" and not a.get("boundary"):
        errs.append(f"{where}: ref XOR boundary violated (backstage needs boundary)")


def validate_control(d):
    errs = []
    if d.get("type") not in TYPES:
        errs.append(f"bad type {d.get('type')}")
    for zone in ("primary", "flyout"):
        if zone in d and d[zone]:
            _check_action(d[zone]["action"], errs, f"{d['id']}.{zone}")
    if "action" in d:
        _check_action(d["action"], errs, d["id"])
    cap = d.get("capture", {})
    if cap.get("probe_mode") not in PROBE_MODES:
        errs.append("bad probe_mode")
    if cap.get("schema_version") != 1:
        errs.append("bad schema_version")
    return errs


def validate_popup(d):
    errs = [] if d.get("schema_version") == 1 else ["bad schema_version"]
    for s in d.get("sections", []):
        for it in s.get("items", []):
            if not it.get("id"):
                errs.append(f"{d['id']}: item id missing ({it.get('label')})")
            if "action" in it:
                _check_action(it["action"], errs, d["id"])
    return errs


def validate_dialog(d):
    errs = [] if d.get("schema_version") == 1 else ["bad schema_version"]
    for b in d.get("buttons", []):
        if "action" in b:
            _check_action(b["action"], errs, d["id"])
    return errs


def validate_tab_file(d):
    errs = [] if d.get("schema_version") == 1 else ["bad schema_version"]
    for g in d.get("groups", []):
        for c in g.get("controls", []):
            errs += validate_control(c)
    return errs
