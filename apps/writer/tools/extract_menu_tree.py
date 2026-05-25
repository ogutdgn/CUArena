#!/usr/bin/env python3
"""Extract Writer's authoritative menu/command tree from the engine uiconfig.

LibreOffice's `sw/uiconfig/swriter/menubar/menubar.xml` is the canonical map
of *what functionality Writer exposes and how it is organized* (the deep-dive
source our ribbon/menus must mirror — see CLAUDE.md "functionality from LO
workflows"). This parses it into a hierarchical writer-menu-tree.json,
cross-referenced to command-catalog.json, and reports coverage.

Build-independent (parses config XML only).

Usage:
    python3 extract_menu_tree.py [--engine PATH] [--catalog PATH] [--out PATH]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

MENU = "{http://openoffice.org/2001/menu}"


def _id(el: ET.Element) -> str | None:
    return el.get(f"{MENU}id")


def clean_label(label: str | None) -> str | None:
    if not label:
        return None
    return label.replace("~", "").strip()


def walk(container: ET.Element, catalog: dict, stats: dict) -> list:
    """Walk a menubar/menupopup container's direct children into a tree."""
    out = []
    for child in list(container):
        tag = child.tag
        if tag == f"{MENU}menu":
            mid = _id(child)
            popup = child.find(f"{MENU}menupopup")
            entry = catalog.get(mid, {})
            stats["menus"] += 1
            out.append({
                "type": "menu",
                "id": mid,
                "label": clean_label(entry.get("label")),
                "inCatalog": mid in catalog,
                "children": walk(popup, catalog, stats) if popup is not None else [],
            })
        elif tag == f"{MENU}menuitem":
            iid = _id(child)
            entry = catalog.get(iid, {})
            stats["items"] += 1
            in_cat = iid in catalog
            stats["items_in_catalog"] += 1 if in_cat else 0
            if not in_cat:
                stats["missing"].add(iid)
            out.append({
                "type": "item",
                "id": iid,
                "label": clean_label(entry.get("label")),
                "inCatalog": in_cat,
            })
        elif tag == f"{MENU}menuseparator":
            out.append({"type": "separator"})
    return out


def main() -> int:
    here = Path(__file__).resolve()
    repo_root = here.parents[3]
    default_engine = repo_root / "apps/libreoffice/libreoffice-codebase"
    default_catalog = repo_root / "apps/writer/resources/command-catalog.json"
    default_out = repo_root / "apps/writer/resources/writer-menu-tree.json"

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--engine", type=Path, default=default_engine)
    ap.add_argument("--catalog", type=Path, default=default_catalog)
    ap.add_argument("--out", type=Path, default=default_out)
    args = ap.parse_args()

    menubar = args.engine / "sw/uiconfig/swriter/menubar/menubar.xml"
    if not menubar.is_file():
        print(f"ERROR: not found: {menubar}", file=sys.stderr)
        return 2
    if not args.catalog.is_file():
        print(f"ERROR: catalog not found (run gen_command_catalog.py first): "
              f"{args.catalog}", file=sys.stderr)
        return 2

    catalog = json.loads(args.catalog.read_text())["commands"]
    root = ET.parse(menubar).getroot()  # menu:menubar
    stats = {"menus": 0, "items": 0, "items_in_catalog": 0, "missing": set()}
    tree = walk(root, catalog, stats)

    payload = {
        "schemaVersion": 1,
        "source": "sw/uiconfig/swriter/menubar/menubar.xml",
        "topLevelMenus": [t["label"] or t["id"] for t in tree if t["type"] == "menu"],
        "stats": {
            "menus": stats["menus"],
            "items": stats["items"],
            "itemsInCatalog": stats["items_in_catalog"],
            "itemsMissingFromCatalog": len(stats["missing"]),
        },
        "menubar": tree,
        # commands referenced by the menu but absent from command-catalog.json
        # (labels live elsewhere — submenu heads, dynamic lists, other .xcu)
        "missingFromCatalog": sorted(stats["missing"]),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(f"wrote {args.out}")
    print(f"  top-level menus: {payload['topLevelMenus']}")
    print(f"  menus:           {stats['menus']}")
    print(f"  items:           {stats['items']}")
    print(f"  items in catalog:{stats['items_in_catalog']}")
    print(f"  missing from catalog: {len(stats['missing'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
