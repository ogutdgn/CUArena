#!/usr/bin/env python3
"""Differ reviewer — objective, self-labeling verification that ooxml_diff.py is
correct and its noise list is complete. Run this BEFORE trusting the differ at scale.

Three suites, each catching a DIFFERENT failure mode:
  GOLDEN        hand-labeled docx pairs with a known expected diff   -> differ LOGIC correctness
  WORD-VS-SELF  same real-Word action captured twice; diff MUST be 0 -> NOISE list completeness
  CLONE-VS-SELF same clone action exported twice; diff MUST be 0     -> clone export DETERMINISM

No "right answer" has to be known in advance: identity/self pairs must diff to zero by definition, so any
non-zero diff is, by definition, leaked noise (or a real bug). Emits an actionable report; exit 0 iff all pass.

Self-test pairs are read from parity/fixtures/selftest/<prefix>-<id>-a.docx / -b.docx
  (prefix 'rw' = real Word, 'wc' = clone). Capture them with parity/engines/run.py or the COM/probe scripts.
"""
import os, sys, zipfile, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ooxml_diff

PARITY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SELFTEST = os.path.join(PARITY, "fixtures", "selftest")
GOLDEN_DIR = os.path.join(SELFTEST, "golden")
RESULTS = os.path.join(PARITY, "results")
WNS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
CT = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      '<Default Extension="xml" ContentType="application/xml"/>'
      '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
      '</Types>')


def make_docx(path, body_inner, extra_parts=None):
    doc = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           f'<w:document {WNS}><w:body>{body_inner}</w:body></w:document>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CT)
        z.writestr("word/document.xml", doc)
        for name, content in (extra_parts or {}).items():
            z.writestr(name, content)
    return path


def ftr_part(text):
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:ftr {WNS}><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:ftr>')


def build_golden():
    os.makedirs(GOLDEN_DIR, exist_ok=True)
    cases = []  # (name, expected_missing, expected_extra, a_body, b_body, a_extra, b_extra)
    P = lambda inner: f'<w:p>{inner}</w:p>'
    spec = [
        ("identity", 0, 0, P('<w:r><w:t>Hi</w:t></w:r>'), P('<w:r><w:t>Hi</w:t></w:r>'), None, None),
        ("noise", 0, 0, '<w:p w:rsidR="AAAA"><w:r><w:t>Hi</w:t></w:r></w:p>',
                        '<w:p w:rsidR="BBBB"><w:r><w:t>Hi</w:t></w:r></w:p>', None, None),
        ("extra_bold", 0, 1, P('<w:r><w:rPr/><w:t>Hi</w:t></w:r>'),
                             P('<w:r><w:rPr><w:b/></w:rPr><w:t>Hi</w:t></w:r>'), None, None),
        ("missing_bold", 1, 0, P('<w:r><w:rPr><w:b/></w:rPr><w:t>Hi</w:t></w:r>'),
                               P('<w:r><w:rPr/><w:t>Hi</w:t></w:r>'), None, None),
        ("instr_value", 1, 1, P('<w:r><w:instrText xml:space="preserve"> PAGE \\* MERGEFORMAT </w:instrText></w:r>'),
                              P('<w:r><w:instrText xml:space="preserve">PAGE</w:instrText></w:r>'), None, None),
        ("multiplicity", 1, 0, '<w:tbl><w:tblGrid><w:gridCol w:w="100"/><w:gridCol w:w="100"/><w:gridCol w:w="100"/></w:tblGrid></w:tbl>',
                               '<w:tbl><w:tblGrid><w:gridCol w:w="100"/><w:gridCol w:w="100"/></w:tblGrid></w:tbl>', None, None),
        ("part_collapse", 0, 0, '', '', {"word/footer1.xml": ftr_part("X")}, {"word/footer2.xml": ftr_part("X")}),
    ]
    for name, em, ee, ab, bb, ax, bx in spec:
        pa = os.path.join(GOLDEN_DIR, f"g_{name}_a.docx")
        pb = os.path.join(GOLDEN_DIR, f"g_{name}_b.docx")
        make_docx(pa, ab, ax)
        make_docx(pb, bb, bx)
        cases.append((name, em, ee, pa, pb))
    return cases


def run_golden():
    out = []
    for name, exp_m, exp_e, pa, pb in build_golden():
        d = ooxml_diff.diff(pa, pb, name)
        got_m, got_e = d["counts"]["missing"], d["counts"]["extra"]
        ok = (got_m == exp_m and got_e == exp_e)
        out.append({"name": name, "exp": [exp_m, exp_e], "got": [got_m, got_e], "ok": ok,
                    "detail": (d["missing_nodes"] + d["extra_nodes"]) if not ok else []})
    return out


def run_self(prefix):
    out = []
    for a in sorted(glob.glob(os.path.join(SELFTEST, f"{prefix}-*-a.docx"))):
        b = a[:-len("-a.docx")] + "-b.docx"
        if not os.path.exists(b):
            continue
        tid = os.path.basename(a)[len(prefix) + 1:-len("-a.docx")]
        d = ooxml_diff.diff(a, b, tid)
        leaks = sorted(set(d["missing_nodes"] + d["extra_nodes"]))
        out.append({"id": tid, "missing": d["counts"]["missing"], "extra": d["counts"]["extra"],
                    "ok": (d["counts"]["missing"] == 0 and d["counts"]["extra"] == 0), "leaks": leaks})
    return out


def leaked_attrs(self_results):
    import re
    attrs = set()
    for r in self_results:
        for n in r["leaks"]:
            attrs.update(re.findall(r"'([A-Za-z][\w:]*)',", n))
    return sorted(attrs)


def main():
    os.makedirs(RESULTS, exist_ok=True)
    golden = run_golden()
    word_self = run_self("rw")
    clone_self = run_self("wc")

    g_pass = sum(1 for g in golden if g["ok"])
    g_all = len(golden)
    w_leaks = [r for r in word_self if not r["ok"]]
    c_leaks = [r for r in clone_self if not r["ok"]]

    L = []
    L.append("# Differ Reviewer Report\n")
    L.append("Objective self-validation of `ooxml_diff.py`. Identity/self pairs must diff to ZERO; "
             "any non-zero diff is leaked noise or a bug. Run before trusting the differ at scale.\n")

    L.append("## GOLDEN — differ logic correctness")
    L.append(f"**{g_pass}/{g_all} pass**\n")
    L.append("| case | expected (miss/extra) | got | status |")
    L.append("|---|---|---|---|")
    for g in golden:
        L.append(f"| {g['name']} | {g['exp'][0]}/{g['exp'][1]} | {g['got'][0]}/{g['got'][1]} | "
                 f"{'✅' if g['ok'] else '❌ ' + '; '.join(g['detail'])} |")
    L.append("")

    L.append("## WORD-VS-SELF — noise-list completeness (must be empty)")
    if not word_self:
        L.append("_no rw-*-a/b pairs in fixtures/selftest — capture them first._\n")
    else:
        L.append("| action | missing | extra | status |")
        L.append("|---|--:|--:|---|")
        for r in word_self:
            L.append(f"| {r['id']} | {r['missing']} | {r['extra']} | "
                     f"{'✅ clean' if r['ok'] else '❌ LEAK: ' + '; '.join(r['leaks'])} |")
        L.append("")

    L.append("## CLONE-VS-SELF — clone export determinism (must be empty)")
    if not clone_self:
        L.append("_no wc-*-a/b pairs in fixtures/selftest — capture them first._\n")
    else:
        L.append("| action | missing | extra | status |")
        L.append("|---|--:|--:|---|")
        for r in clone_self:
            L.append(f"| {r['id']} | {r['missing']} | {r['extra']} | "
                     f"{'✅ deterministic' if r['ok'] else '❌ NON-DETERMINISTIC: ' + '; '.join(r['leaks'])} |")
        L.append("")

    # verdict + actions
    L.append("## VERDICT")
    ok_all = (g_pass == g_all) and not w_leaks and not c_leaks
    L.append(f"- **Differ logic (golden):** {'PASS' if g_pass == g_all else 'FAIL — fix differ before scaling'}")
    if word_self:
        if w_leaks:
            L.append(f"- **Noise list:** INCOMPLETE — ACTION: add these attrs to `NOISE_ATTRS` in ooxml_diff.py: "
                     f"`{', '.join(leaked_attrs(w_leaks))}` (seen in {', '.join(r['id'] for r in w_leaks)})")
        else:
            L.append("- **Noise list:** COMPLETE (Word == itself on all captured actions)")
    if clone_self:
        if c_leaks:
            L.append(f"- **Clone determinism:** NON-DETERMINISTIC on {', '.join(r['id'] for r in c_leaks)} "
                     "— ACTION: make clone export stable (random ids/ordering) or add them to noise")
        else:
            L.append("- **Clone determinism:** OK (clone == itself)")
    L.append(f"\n**Overall: {'✅ ALL PASS — differ trustworthy at scale' if ok_all else '❌ FIX issues above before scaling'}**")
    L.append("\n> Note: this reviewer validates differ CORRECTNESS only. Whether a real diff is "
             "'must-match' vs 'fidelity' is a policy call handled by the ledger classification, not here.")

    report = "\n".join(L)
    with open(os.path.join(RESULTS, "DIFFER_REVIEW.md"), "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
