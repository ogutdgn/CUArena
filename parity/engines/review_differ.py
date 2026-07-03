#!/usr/bin/env python3
"""Differ reviewer — objective, self-labeling verification that ooxml_diff.py is
correct and its noise list is complete. Run this BEFORE trusting the differ at scale.

Three suites, each catching a DIFFERENT failure mode:
  GOLDEN        hand-labeled docx pairs with a known expected diff   -> differ LOGIC correctness
  WORD-VS-SELF  same real-Word action captured twice; diff MUST be 0 -> NOISE list completeness
  CLONE-VS-SELF same clone action exported twice; diff MUST be 0     -> clone export DETERMINISM

No "right answer" has to be known in advance: identity/self pairs must diff to zero by definition, so any
non-zero diff is, by definition, leaked noise (or a real bug). Emits an actionable report; exit 0 iff all pass.

Self-test pairs are read from parity/selftest/<prefix>-<id>-a.docx / -b.docx
  (prefix 'rw' = real Word, 'wc' = clone). Capture them with parity/engines/run.py or the COM/probe scripts.
"""
import os, sys, zipfile, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ooxml_diff

# The report contains ✅/❌; the Windows console defaults to cp1252 and crashes on
# print(). Force UTF-8 so the reviewer runs to completion everywhere (no-op on POSIX).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PARITY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SELFTEST = os.path.join(PARITY, "selftest")
GOLDEN_DIR = SELFTEST  # golden pairs (g_*/gb_*) regenerated directly here — no 'golden' subfolder
RESULTS = os.path.join(PARITY, "results")
WNS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
RNS = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
CT = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      '<Default Extension="xml" ContentType="application/xml"/>'
      '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
      '</Types>')


def make_docx(path, body_inner, extra_parts=None):
    doc = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           f'<w:document {WNS} {RNS}><w:body>{body_inner}</w:body></w:document>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CT)
        z.writestr("word/document.xml", doc)
        for name, content in (extra_parts or {}).items():
            z.writestr(name, content)
    return path


def ftr_part(text):
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:ftr {WNS}><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:ftr>')


def num_part(inner):
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:numbering {WNS}>{inner}</w:numbering>')


def styles_part(inner):
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:styles {WNS}>{inner}</w:styles>')


def build_golden():
    os.makedirs(GOLDEN_DIR, exist_ok=True)
    cases = []  # (name, expected_missing, expected_extra, a_body, b_body, a_extra, b_extra)
    P = lambda inner: f'<w:p>{inner}</w:p>'
    # styles.xml is diffed by styleId presence/content scoped to REFERENCED styleIds (preloaded-vs-lazy safe).
    REF = P('<w:r><w:rPr><w:rStyle w:val="Foo"/></w:rPr><w:t>Hi</w:t></w:r>')   # body references style 'Foo'
    PLAIN_P = P('<w:r><w:t>Hi</w:t></w:r>')                                     # body references NO style
    STY = lambda inner='': {"word/styles.xml": styles_part(f'<w:style w:styleId="Foo" w:type="character">{inner}</w:style>')}
    STY_EMPTY = {"word/styles.xml": styles_part('')}
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
        # numbering.xml is now in scope: a numbering definition node present on one side must be caught.
        ("numbering_part", 1, 0, '', '', {"word/numbering.xml": num_part('<w:abstractNum w:abstractNumId="0"/>')},
                                          {"word/numbering.xml": num_part('')}),
        # numbering.xml per-def opaque ids (nsid/tmpl elements + durableId attr) are per-save noise — two defs that
        # differ ONLY in those must diff to 0/0 (the ribbon oracle mints fresh ones every capture).
        ("numbering_noise", 0, 0, '', '',
         {"word/numbering.xml": num_part('<w:abstractNum w:abstractNumId="0"><w:nsid w:val="AAAA"/><w:tmpl w:val="1111"/></w:abstractNum><w:num w:numId="1" w:durableId="99"><w:abstractNumId w:val="0"/></w:num>')},
         {"word/numbering.xml": num_part('<w:abstractNum w:abstractNumId="0"><w:nsid w:val="BBBB"/><w:tmpl w:val="2222"/></w:abstractNum><w:num w:numId="1" w:durableId="88"><w:abstractNumId w:val="0"/></w:num>')}),
        # styles.xml: diffed by styleId presence/content, scoped to REFERENCED styleIds (preloaded-vs-lazy safe).
        # A referenced style Word has + the clone lacks -> missing (real gap).
        ("styles_referenced_missing", 1, 0, REF, REF, STY(), STY_EMPTY),
        # A style present on ONE side but referenced by NEITHER body -> ignored (latent template/boilerplate,
        # e.g. Word's UnresolvedMention). This is the false-missing the old baseline-subtraction produced.
        ("styles_unreferenced_ignored", 0, 0, PLAIN_P, PLAIN_P, STY(), STY_EMPTY),
        # A style PRELOADED on both sides (content-equal) + referenced by both -> MATCH regardless of which side
        # added it lazily. This is the fd-link Hyperlink regression case (the whole point of the refactor).
        ("styles_preloaded_match", 0, 0, REF, REF, STY(), STY()),
        # A referenced style present on both but with DIFFERING content -> missing(real attr)+extra(clone attr).
        ("styles_content_differs", 1, 1, REF, REF, STY('<w:color w:val="FF0000"/>'), STY('<w:color w:val="00FF00"/>')),
        # rId VALUES are per-doc relationship pointers (Word rId9 vs clone rId7): the SAME
        # default footer ref under different rIds must diff to 0 (match on type, not the id value).
        ("rid_canon", 0, 0, P('<w:footerReference w:type="default" r:id="rId9"/>'),
                            P('<w:footerReference w:type="default" r:id="rId7"/>'), None, None),
        # ...but a genuinely different TYPE (default vs even) must still surface as missing+extra.
        ("rid_type_differs", 1, 1, P('<w:footerReference w:type="default" r:id="rId9"/>'),
                                   P('<w:footerReference w:type="even" r:id="rId8"/>'), None, None),
        # numId/abstractNumId VALUES are per-doc numbering indices (Word numId=1 vs clone numId=4 for
        # the SAME fresh list): they must canonicalize to 0 diff, like rId.
        ("numid_canon", 0, 0, P('<w:pPr><w:numPr><w:numId w:val="1"/></w:numPr></w:pPr>'),
                              P('<w:pPr><w:numPr><w:numId w:val="4"/></w:numPr></w:pPr>'), None, None),
        # ...but the list LEVEL (w:ilvl) is meaningful and must NOT be canonicalized — level 0 vs 1 surfaces.
        ("ilvl_not_canon", 1, 1, P('<w:pPr><w:numPr><w:ilvl w:val="0"/></w:numPr></w:pPr>'),
                                 P('<w:pPr><w:numPr><w:ilvl w:val="1"/></w:numPr></w:pPr>'), None, None),
        # w:t CONTENT is feature signal (the Tables-pilot tb-totext-comma false pass): different
        # document text must surface. 2 missing + 2 extra = the per-node w:t sig AND the ordered
        # textOrder stream both flip.
        ("text_content_differs", 2, 2, P('<w:r><w:t>a, b,</w:t></w:r>'),
                                       P('<w:r><w:t xml:space="preserve">a\tb</w:t></w:r>'), None, None),
        # A PURE PERMUTATION of the same text nodes (table Sort: b/a/c -> a/b/c) is invisible to
        # the node multiset — the ordered textOrder stream must catch it: exactly 1 missing + 1 extra.
        ("row_order", 1, 1,
         '<w:tbl>' + ''.join(f'<w:tr><w:tc><w:p><w:r><w:t>{x}</w:t></w:r></w:p></w:tc></w:tr>' for x in ('a', 'b', 'c')) + '</w:tbl>',
         '<w:tbl>' + ''.join(f'<w:tr><w:tc><w:p><w:r><w:t>{x}</w:t></w:r></w:p></w:tc></w:tr>' for x in ('b', 'a', 'c')) + '</w:tbl>',
         None, None),
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


def build_golden_baseline():
    """Hand-labeled cases for BASELINE SUBTRACTION (v2 differ): diff each side's
    delta-vs-its-own-baseline so blank-document boilerplate cancels and only the
    feature delta remains. Each case = (name, exp_missing, exp_extra, ra, ca, rb, cb)
    where rb/cb are the real/clone baselines and ra/ca the action docs."""
    os.makedirs(GOLDEN_DIR, exist_ok=True)
    P = lambda inner: f'<w:p>{inner}</w:p>'
    PLAIN = P('<w:r><w:t>Hi</w:t></w:r>')
    TWO_PLAIN = PLAIN + PLAIN
    LISTPARA = P('<w:pPr><w:pStyle w:val="ListParagraph"/></w:pPr><w:r><w:t>Hi</w:t></w:r>')
    BOLD = P('<w:r><w:rPr><w:b/></w:rPr><w:t>Hi</w:t></w:r>')
    BOLD_LISTPARA = P('<w:pPr><w:pStyle w:val="ListParagraph"/></w:pPr><w:r><w:rPr><w:b/></w:rPr><w:t>Hi</w:t></w:r>')
    BOLD_CNTXT = P('<w:r><w:rPr><w:b/><w:cntxtAlts/></w:rPr><w:t>Hi</w:t></w:r>')
    FTRREF = P('<w:r><w:t>Hi</w:t></w:r>') + '<w:footerReference w:type="default" w:id="rId7"/>'
    # (name, exp_missing, exp_extra, exp_divergent, real_action, clone_action, real_baseline, clone_baseline)
    spec = [
        # clone's baseline carries a ListParagraph the real baseline lacks; the feature is
        # "add bold". After subtraction the ListParagraph cancels -> no spurious extra, and the
        # baseline divergence (clone blank over-emits ListParagraph) is FLAGGED, not silent.
        ("cancels_boilerplate", 0, 0, True, BOLD, BOLD_LISTPARA, PLAIN, LISTPARA),
        # real adds a footerReference the clone never emits -> a real GAP must survive subtraction.
        ("keeps_real_missing", 1, 0, False, FTRREF, PLAIN, PLAIN, PLAIN),
        # clone over-emits cntxtAlts (not in its baseline) -> a real over-emission must survive.
        ("keeps_real_extra", 0, 1, False, BOLD, BOLD_CNTXT, PLAIN, PLAIN),
        # the feature REMOVES a node present in the baseline on Word's side (action count < baseline)
        # but the clone keeps it -> a real over-emission. Counter '-' flooring would HIDE this (0/0);
        # signed per-signature deltas must surface it as extra (the clone over-emits the para/run/text).
        # (4 extra since the w:t-content/textOrder upgrade: p + r + t|text + the textOrder stream)
        ("reduction_surfaces_extra", 0, 4, False, "", PLAIN, PLAIN, PLAIN),
        # the two empty-doc baselines DIVERGE (clone blank has 2 paras, Word blank 1) while the actions
        # are identical -> the divergence must be FLAGGED loudly (baseline_divergence non-empty), never silent.
        # (4/1 since the textOrder upgrade: Word's signed delta nets +textOrder(Hi↵Hi)/−textOrder(Hi).)
        ("flags_divergent_baseline", 4, 1, True, TWO_PLAIN, TWO_PLAIN, PLAIN, TWO_PLAIN),
    ]
    cases = []
    for name, em, ee, ed, ra, ca, rb, cb in spec:
        pra = make_docx(os.path.join(GOLDEN_DIR, f"gb_{name}_ra.docx"), ra)
        pca = make_docx(os.path.join(GOLDEN_DIR, f"gb_{name}_ca.docx"), ca)
        prb = make_docx(os.path.join(GOLDEN_DIR, f"gb_{name}_rb.docx"), rb)
        pcb = make_docx(os.path.join(GOLDEN_DIR, f"gb_{name}_cb.docx"), cb)
        cases.append((name, em, ee, ed, pra, pca, prb, pcb))
    return cases


def run_golden_baseline():
    out = []
    for name, exp_m, exp_e, exp_div, ra, ca, rb, cb in build_golden_baseline():
        d = ooxml_diff.diff(ra, ca, name, real_baseline=rb, clone_baseline=cb)
        got_m, got_e = d["counts"]["missing"], d["counts"]["extra"]
        got_div = bool(d.get("baseline_divergence"))
        ok = (got_m == exp_m and got_e == exp_e and got_div == exp_div and d.get("baselined") is True)
        out.append({"name": name, "exp": [exp_m, exp_e], "got": [got_m, got_e],
                    "exp_div": exp_div, "got_div": got_div, "ok": ok, "baselined": d.get("baselined"),
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
    golden_bl = run_golden_baseline()
    word_self = run_self("rw")
    clone_self = run_self("wc")

    g_pass = sum(1 for g in golden if g["ok"])
    g_all = len(golden)
    gb_pass = sum(1 for g in golden_bl if g["ok"])
    gb_all = len(golden_bl)
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

    L.append("## GOLDEN-BASELINE — baseline-subtraction correctness (v2)")
    L.append(f"**{gb_pass}/{gb_all} pass** — signed delta-vs-baseline cancels boilerplate, keeps real "
             "gaps/over-emissions/reductions, flags divergent baselines\n")
    L.append("| case | exp miss/extra/div | got miss/extra/div | status |")
    L.append("|---|---|---|---|")
    for g in golden_bl:
        status = "✅" if g["ok"] else "❌ " + "; ".join(g["detail"]) + f" (baselined={g['baselined']})"
        L.append(f"| {g['name']} | {g['exp'][0]}/{g['exp'][1]}/{str(g['exp_div'])[0]} "
                 f"| {g['got'][0]}/{g['got'][1]}/{str(g['got_div'])[0]} | {status} |")
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
    ok_all = (g_pass == g_all) and (gb_pass == gb_all) and not w_leaks and not c_leaks
    L.append(f"- **Differ logic (golden):** {'PASS' if g_pass == g_all else 'FAIL — fix differ before scaling'}")
    L.append(f"- **Baseline subtraction (golden-baseline):** {'PASS' if gb_pass == gb_all else 'FAIL — baseline subtraction is unsound'}")
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
