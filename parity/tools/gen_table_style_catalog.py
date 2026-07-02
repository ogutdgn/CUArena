#!/usr/bin/env python3
"""gen_table_style_catalog.py — turn the real-Word styles.xml dump (from
_extract_table_styles.ps1) into the clone's table-style gallery catalog.

The clone's Table Styles gallery ships only ~2 styles; Word has ~113 modern built-in table
styles. This parses each <w:style w:type="table"> definition Word wrote and emits a compact
JSON catalog (styleId, name, basedOn, the tblPr/tblStylePr conditional-format blocks) that the
clone gallery can enumerate + apply. Byte-faithful rendering of every conditional format is a
follow-up; this gives the NAMES + structure so the gallery is populated and the tblStyle ref
round-trips.

Usage: python parity/tools/gen_table_style_catalog.py
  in:  parity/oracle/word-tablestyles.xml   (real Word styles.xml)
  out: parity/oracle/table_style_catalog.json
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PAR = os.path.join(ROOT, "parity")
XML = os.path.join(PAR, "oracle", "word-tablestyles.xml")
NAMES = os.path.join(PAR, "oracle", "word-tablestyle-names.txt")
OUT = os.path.join(PAR, "oracle", "table_style_catalog.json")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# Word display name -> styleId (the OOXML w:styleId is the name with spaces/hyphens stripped).
MODERN_RE = re.compile(r"^(Grid Table|List Table|Plain Table|Table Grid)")


def style_id(name):
    return re.sub(r"[^A-Za-z0-9]", "", name)


def from_names():
    """Fallback catalog from the NAMES dump (no styles.xml). NAMES + basedOn structure is enough
    for the gallery: applying a tblStyle ref gives FUNCTIONAL parity — Word recomputes the
    conditional formatting from tblStyle+tblLook on open (per the archived Tables finding).
    Byte-faithful conditional-format defs are a follow-up (batched XML extraction)."""
    names = [n.strip() for n in open(NAMES, encoding="utf-8-sig").read().splitlines() if n.strip()]
    styles = []
    for n in names:
        styles.append({
            "styleId": style_id(n),
            "name": n,
            "modern": bool(MODERN_RE.match(n)),
            "source": "names",
        })
    return styles


def attr(el, name):
    return el.get(W + name) if el is not None else None


def from_xml():
    raw = open(XML, encoding="utf-8-sig").read()
    root = ET.fromstring(raw)
    styles = []
    for st in root.findall(f"{W}style"):
        if attr(st, "type") != "table":
            continue
        sid = attr(st, "styleId")
        name_el = st.find(f"{W}name")
        based_el = st.find(f"{W}basedOn")
        # conditional-format regions present (firstRow, band1Horz, etc.)
        conds = [attr(c, "type") for c in st.findall(f"{W}tblStylePr")]
        name = attr(name_el, "val") if name_el is not None else sid
        styles.append({
            "styleId": sid,
            "name": name,
            "modern": bool(MODERN_RE.match(name)),
            "basedOn": attr(based_el, "val") if based_el is not None else None,
            "customStyle": attr(st, "customStyle") == "1",
            "conditionalFormats": [c for c in conds if c],
            "hasWholeTablePr": st.find(f"{W}tblPr") is not None,
            "source": "xml",
        })
    return styles


def main():
    if os.path.exists(XML):
        styles, src = from_xml(), "styles.xml (full defs)"
    elif os.path.exists(NAMES):
        styles, src = from_names(), "names dump (SaveAs2 hung on the 113-table doc; names + " \
            "structure suffice for functional parity — Word recomputes cnf from tblStyle+tblLook)"
    else:
        print(f"gen_table_style_catalog: neither {XML} nor {NAMES} present")
        return 2
    modern = [s for s in styles if s.get("modern")]
    meta = {
        "source": f"real Word build 16.0.20026 — {src}",
        "generated_by": "parity/tools/gen_table_style_catalog.py",
        "count": len(styles),
        "modernCount": len(modern),
        "note": "The clone gallery ships ~2 styles; this is Word's full catalog. `modern`=the "
                "Grid/List/Plain Table + Table Grid gallery set. Applying a tblStyle ref gives "
                "FUNCTIONAL parity (Word recomputes conditional formatting on open); byte-faithful "
                "cnf defs = a follow-up via batched XML extraction (single-doc SaveAs2 hangs here).",
    }
    json.dump({"meta": meta, "styles": styles}, open(OUT, "w", encoding="utf-8"), indent=1)
    print(f"wrote {len(styles)} table styles ({len(modern)} modern) -> {os.path.relpath(OUT, ROOT)}")
    for s in [x for x in styles if x.get("modern")][:6]:
        print(f"  {s['styleId']:26s} {s['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
