import ids, schemas

TYPE_MAP = {"Button": "button", "CheckBox": "checkbox", "SplitButton": "split",
            "ComboBox": "combo", "Edit": "text-input", "MenuItem": "menu",
            "RadioButton": "toggle", "Slider": "slider"}
KIND_MAP = {"dialog": "opens-dialog", "popup": "opens-dropdown", "pane": "opens-pane",
            "toggles": "toggles", "feature": "feature"}


def derive_type(props):
    # Control-type driven (RELIABLE). The T6 exposure map proved Office ribbon
    # pattern-availability is quirky (Bold reports expand_collapse but is not a dropdown),
    # so we do NOT classify from patterns. Toggle-ness is recovered dynamically from the
    # observed probe class in build_control (button -> toggle when class == 'toggles').
    if props.get("is_gallery"):
        return "gallery"
    return TYPE_MAP.get(props.get("control_type", ""), "button")


def build_control(props, tab, group_seg, probe_result, icon_path, bounds):
    seg = ids.control_segment(props.get("automation_id", ""), props.get("name", ""))
    cid = ids.node_id("ribbon", tab, group_seg, seg)
    cls = probe_result["class"]
    if cls == "boundary":
        b = probe_result["boundary"]
        action = {"kind": b.get("kind", "feature")}
        # Boundary controls always carry the boundary block (documents WHY they were not
        # pressed); for opening kinds this is the ref-XOR-boundary alternative, for 'feature'
        # it is an honest note. They never carry a ref.
        action["boundary"] = {"policy": b["policy"], "decision": b["decision"]}
    else:
        kind = KIND_MAP[cls]
        action = {"kind": kind}
        if kind.startswith("opens-"):
            action["ref"] = probe_result["ref"]
    ctype = derive_type(props)
    if cls == "toggles" and ctype == "button":
        ctype = "toggle"
    c = {"id": cid, "label": props.get("name", ""), "type": ctype,
         "tooltip": props.get("help_text", ""), "keytip": props.get("access_key", ""),
         "action": action, "idMso": props.get("automation_id") or None,
         "capture": {"status": "complete", "probe_mode": probe_result["probe_mode"],
                     "schema_version": 1}}
    shortcut = props.get("accelerator_key")
    if shortcut:
        c["shortcut"] = shortcut
    if icon_path:
        c["icon"] = icon_path
    if bounds:
        c["bounds"] = bounds
    errs = schemas.validate_control(c)
    if errs:
        raise ValueError(f"invalid control {cid}: {errs}")
    return c
