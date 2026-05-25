#!/usr/bin/env python3
"""Generate the Writer command catalog from LibreOffice's *Commands.xcu.

Reads WriterCommands.xcu + GenericCommands.xcu (the engine's canonical .uno:
command definitions) and emits a single command-catalog.json that the app's
UI (ribbon labels/tooltips), dispatch layer (valid command set), logger
(semantic names) and MCP surface (tool list) all consume.

Build-independent: parses config XML only — no engine build required.

Usage:
    python3 gen_command_catalog.py \
        [--engine <path to libreoffice-codebase>] \
        [--out <path to command-catalog.json>]

Defaults assume this lives at apps/writer/tools/ inside the cua-bench repo.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

OOR = "{http://openoffice.org/2001/registry}"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
LANG = "en-US"


def _value(prop: ET.Element) -> str | None:
    """Return the en-US value (or the first/only value) of a <prop>.

    Elements (<prop>, <value>, <node>) are in NO namespace in these XCU
    files; only attributes (oor:name, xml:lang) are namespaced.
    """
    values = prop.findall("value")
    if not values:
        return None
    for val in values:
        if val.get(XML_LANG) in (LANG, None):
            return (val.text or "").strip() or None
    return (values[0].text or "").strip() or None


def _text_prop(node: ET.Element, name: str) -> str | None:
    for prop in node.findall("prop"):
        if prop.get(f"{OOR}name") == name:
            return _value(prop)
    return None


def _int_prop(node: ET.Element, name: str) -> int | None:
    for prop in node.findall("prop"):
        if prop.get(f"{OOR}name") == name:
            raw = _value(prop)
            if raw is not None:
                try:
                    return int(raw)
                except ValueError:
                    return None
    return None


def semantic_name(uno: str) -> str:
    """'.uno:InsertTable' -> 'insert_table' (RL-friendly logger/MCP name)."""
    base = uno.split(":", 1)[1] if ":" in uno else uno
    # split CamelCase / acronym boundaries, then lowercase
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", base)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", s)
    return s.lower()


def parse_commands(path: Path, source: str) -> dict[str, dict]:
    root = ET.parse(path).getroot()
    out: dict[str, dict] = {}
    for node in root.iter("node"):
        name = node.get(f"{OOR}name")
        if not name or not name.startswith(".uno:"):
            continue
        label = _text_prop(node, "Label")
        popup = _text_prop(node, "PopupLabel")
        # a real command/popup definition has at least a Label or PopupLabel
        if label is None and popup is None:
            continue
        out[name] = {
            "command": name,
            "semanticName": semantic_name(name),
            "label": label,
            "contextLabel": _text_prop(node, "ContextLabel"),
            "tooltip": _text_prop(node, "TooltipLabel"),
            "popupLabel": popup,
            "targetURL": _text_prop(node, "TargetURL"),
            # NOTE: Properties is an int bitmask whose exact bit meanings we
            # have NOT yet verified against the engine schema. Stored raw;
            # decode in W3 (ribbon wiring) after confirming bits in
            # officecfg .xcs. Do not invent bit semantics here.
            "propertiesRaw": _int_prop(node, "Properties"),
            "source": source,
        }
    return out


def main() -> int:
    here = Path(__file__).resolve()
    repo_root = here.parents[3]  # apps/writer/tools/<this> -> repo root
    default_engine = repo_root / "apps/libreoffice/libreoffice-codebase"
    default_out = repo_root / "apps/writer/resources/command-catalog.json"

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--engine", type=Path, default=default_engine,
                    help="path to libreoffice-codebase (engine source)")
    ap.add_argument("--out", type=Path, default=default_out,
                    help="output JSON catalog path")
    args = ap.parse_args()

    ui = args.engine / "officecfg/registry/data/org/openoffice/Office/UI"
    writer_xcu = ui / "WriterCommands.xcu"
    generic_xcu = ui / "GenericCommands.xcu"
    for f in (writer_xcu, generic_xcu):
        if not f.is_file():
            print(f"ERROR: not found: {f}", file=sys.stderr)
            return 2

    # generic first, then writer overrides on overlap (writer is more specific)
    catalog = parse_commands(generic_xcu, "generic")
    writer = parse_commands(writer_xcu, "writer")
    overlap = sorted(set(catalog) & set(writer))
    catalog.update(writer)

    catalog = dict(sorted(catalog.items()))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": 1,
        "generatedFrom": ["WriterCommands.xcu", "GenericCommands.xcu"],
        "commandCount": len(catalog),
        "commands": catalog,
    }
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    # summary
    with_label = sum(1 for c in catalog.values() if c["label"])
    with_tooltip = sum(1 for c in catalog.values() if c["tooltip"])
    by_source = {}
    for c in catalog.values():
        by_source[c["source"]] = by_source.get(c["source"], 0) + 1
    print(f"wrote {args.out}")
    print(f"  commands:     {len(catalog)}")
    print(f"  by source:    {by_source}")
    print(f"  with label:   {with_label}")
    print(f"  with tooltip: {with_tooltip}")
    print(f"  overlap (writer overrode generic): {len(overlap)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
