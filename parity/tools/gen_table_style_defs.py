#!/usr/bin/env python3
"""Collect the REAL Word table-style definitions (FIX 1 ground truth).

Input : C:/tmp/wc-styledefs/def-*.docx — one per style, captured by
        parity/oracle/_extract_style_defs.ps1 logic (fresh doc + apply style + save;
        113 modern styles in 26s once run INLINE — the archive's "bulk extraction
        hangs" lesson was a nested-powershell launch artifact, not COM).
Output: parity/oracle/table_style_defs.json — {styleId: {name, xml, themeRefs, basedOn}}
        The `xml` is the verbatim <w:style> subtree from Word's styles.xml (the
        byte-accurate definition the clone must register), rsid bookkeeping stripped.

Run:  python parity/tools/gen_table_style_defs.py [--src C:/tmp/wc-styledefs]
"""
import argparse
import glob
import json
import os
import re
import zipfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
PARITY = os.path.dirname(TOOLS)
OUT = os.path.join(PARITY, "oracle", "table_style_defs.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="C:/tmp/wc-styledefs")
    a = ap.parse_args()

    defs = {}
    files = sorted(glob.glob(os.path.join(a.src, "def-*.docx")))
    for path in files:
        try:
            styles = zipfile.ZipFile(path).read("word/styles.xml").decode("utf-8")
        except Exception as e:
            print(f"SKIP {os.path.basename(path)}: {e}")
            continue
        # every table style present beyond the stock defaults (TableNormal/TableGrid ship in
        # every doc; the APPLIED style is the one whose def we came for — but grab all
        # non-default table styles so basedOn chains are never dangling)
        for m in re.finditer(r'<w:style [^>]*w:type="table"[^>]*>.*?</w:style>', styles, re.S):
            xml = m.group(0)
            sid = re.search(r'w:styleId="([^"]+)"', xml).group(1)
            if sid in ("TableNormal",) or sid in defs:
                continue
            xml = re.sub(r"<w:rsid [^/]*/>", "", xml)   # per-save bookkeeping, not definition
            name = re.search(r'<w:name w:val="([^"]+)"/>', xml)
            based = re.search(r'<w:basedOn w:val="([^"]+)"/>', xml)
            theme_refs = sorted(set(re.findall(r'w:themeColor="([^"]+)"|w:themeFill="([^"]+)"', xml)))
            theme_refs = sorted({x for pair in theme_refs for x in pair if x})
            defs[sid] = {
                "name": name.group(1) if name else sid,
                "basedOn": based.group(1) if based else None,
                "themeRefs": theme_refs,
                "xml": xml,
            }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"meta": {
            "source": "real Word 16.0 locked build — per-style COM captures (def-*.docx)",
            "count": len(defs),
            "note": "xml = verbatim <w:style> subtree (rsid stripped). Theme palette lives in "
                    "the doc theme (theme1.xml accent1=#156082 etc. on this build) — defs "
                    "reference it via themeColor/themeFill, so the clone theme must match.",
        }, "styles": defs}, f, indent=1, ensure_ascii=False)
    themed = sum(1 for d in defs.values() if d["themeRefs"])
    print(f"collected {len(defs)} table-style definitions -> {os.path.relpath(OUT, PARITY)}")
    print(f"theme-linked: {themed} / {len(defs)}  (palette fidelity is load-bearing)")


if __name__ == "__main__":
    main()
