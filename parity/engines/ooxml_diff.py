#!/usr/bin/env python3
"""Generic 3-bucket OOXML differ — the heart of the parity pipeline.

Compares a real-Word .docx (ground truth) against the clone's .docx for the SAME
task and classifies every meaningful node into:
  match   — present in both (semantic core agrees)
  missing — Word emits it, clone does NOT  (clone GAP / missing hidden default)
  extra   — clone emits it, Word does NOT  (clone OVER-emission)
  (noise) — rsid/paraId/textId attrs are stripped before comparison

It is feature-AGNOSTIC: it never looks for specific features. Whatever Word wrote
beyond the explicit ask falls out automatically as 'match' or 'missing'.

Usage: ooxml_diff.py <realword.docx> <clone.docx> [--id TASKID]
"""
import sys, re, json, zipfile, argparse, hashlib
import xml.etree.ElementTree as ET
from collections import Counter

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
# attribute LOCAL names that are per-save noise (random every save) -> stripped
NOISE_ATTRS = {"rsid", "rsidr", "rsidrpr", "rsidrdefault", "rsidp", "rsidtr",
               "rsiddel", "rsidsect", "paraid", "textid",
               # per-doc numbering identifier + the mc:Ignorable namespace list — random/boilerplate per save,
               # surfaced by the ribbon oracle (a fresh Bullets gallery mints a new durableId every time).
               "durableid", "ignorable"}
# element LOCAL names that are per-save revision bookkeeping -> skipped entirely. The
# <w:rsids> list (rsidRoot + many <w:rsid w:val=...>) lives in styles.xml and is random
# every save; without this, diffing styles.xml leaks the rsid VALUES as false differences.
NOISE_ELEMENTS = {"rsid", "rsidroot", "rsids",
                  # numbering.xml per-definition opaque identifiers: <w:nsid> (numbering-style id) + <w:tmpl>
                  # (template code) are random every time a list definition is minted (ribbon or clone), so they
                  # are the same noise class as rsid — strip them so only the SEMANTIC list structure diffs.
                  "nsid", "tmpl"}
# Relationship-id VALUES (r:id="rId9", r:embed="rId4"...) are per-doc pointers assigned
# arbitrarily per save: Word emits rId9 where the clone emits rId7 for the SAME semantic
# reference. Canonicalize the VALUE to a constant so references match on their real
# discriminator (e.g. footerReference w:type) — but keep the attribute present, so a clone
# that DROPS the relationship entirely still surfaces as a gap.
RID_RE = re.compile(r"^rId\d+$")
RID_CANON = "rId#"
# Numbering-instance ids: <w:numId w:val> / <w:abstractNumId w:val> are per-doc indices assigned
# arbitrarily (Word's fresh list gets numId=1; the clone's gets numId=4 because its template already
# defines a few) — the same opaque-pointer class as rId. Canonicalize the VALUE so the same list
# reference matches. NOTE: this is a document.xml-only view — it does NOT resolve numId -> abstractNum
# -> numFmt, so it cannot tell a bullet from a numbered list (that needs numbering.xml resolution, a
# future refinement). w:ilvl (the list LEVEL) is meaningful and is deliberately NOT canonicalized.
NUM_REF_ELEMENTS = {"numid", "abstractnumid"}
NUM_CANON = "#"
# text content matters for these -> folded into the signature. w:t/w:delText were BLIND
# until the Tables pilot caught the false pass (clone tab-text vs Word comma-text diffed
# to 0 because only structure was compared) — document content is feature signal.
TEXT_NODES = {"instrText", "t", "delText"}
# Ordered text-stream signature (one per part): the differ's node multiset is ORDER-BLIND,
# so a pure permutation (table Sort: rows b/a/c -> a/b/c) was invisible — same nodes, new
# order. The stream folds the part's visible text IN DOCUMENT ORDER into one signature, so
# any reorder or content change surfaces as one missing+extra pair. Long streams are capped
# with a digest tail (deterministic, keeps ledger lines readable).
TEXT_STREAM_CAP = 600


def local(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def part_kind(name):
    if name == "word/document.xml":
        return "body"
    if re.match(r"word/header\d*\.xml", name):
        return "header"
    if re.match(r"word/footer\d*\.xml", name):
        return "footer"
    if name == "word/numbering.xml":
        return "numbering"   # list/bullet definitions (Define New Bullet/Number Format)
    if name == "word/styles.xml":
        return "styles"      # style definitions (Create/Modify a Style)
    return None


def meaningful_attrs(el):
    is_num_ref = local(el.tag).lower() in NUM_REF_ELEMENTS
    out = []
    for k, v in el.attrib.items():
        ln = local(k).lower()
        if ln in NOISE_ATTRS:
            continue
        if RID_RE.match(v):
            v = RID_CANON           # canonicalize per-doc relationship-id values
        elif ln in NUM_REF_ELEMENTS or (is_num_ref and ln == "val"):
            # canonicalize per-doc numbering INDEX values (not w:ilvl): the numId/abstractNumId ATTRIBUTE on
            # <w:num w:numId>/<w:abstractNum w:abstractNumId>, AND the <w:val> of a <w:numId>/<w:abstractNumId>
            # ref element. Word's ribbon and the clone assign these indices arbitrarily per doc.
            v = NUM_CANON
        out.append((local(k), v))
    return tuple(sorted(out))


def collect(docx_path):
    """Return a Counter of node signatures across body/header/footer parts."""
    sigs = Counter()
    parts_seen = Counter()
    z = zipfile.ZipFile(docx_path)
    for name in z.namelist():
        kind = part_kind(name)
        if not kind or kind == "styles":
            # styles.xml is diffed SEPARATELY by _styles_diff (styleId presence/content, NOT
            # baseline-subtracted) because the clone PRELOADS its full styles.xml while Word LAZILY
            # materializes styles on use — baseline-subtraction would false-flag a preloaded-but-
            # identical style as 'missing'. See report 4c.
            continue
        parts_seen[kind] += 1
        root = ET.fromstring(z.read(name))
        # for the body, only look inside w:body (skip sectPr-of-doc boilerplate? keep it; it's real)
        scope = root.find(W + "body") if kind == "body" else root
        if scope is None:
            scope = root
        stream = []
        for el in scope.iter():
            if el is scope:
                continue   # the part-root container itself (<w:numbering>/<w:hdr>/<w:body>…) — structural, not
                           # semantic; its bare presence is a preloaded-vs-lazy artifact (the clone preloads
                           # numbering.xml, Word lazily creates it), not a feature signal.
            ln = local(el.tag)
            if ln.lower() in NOISE_ELEMENTS:
                continue   # per-save revision bookkeeping (<w:rsids>/<w:rsid>) — not feature signal
            attrs = meaningful_attrs(el)
            txt = ""
            if ln in TEXT_NODES and el.text:
                txt = "|text=" + re.sub(r"\s+", " ", el.text).strip()
            if ln in ("t", "delText") and el.text:
                stream.append(re.sub(r"\s+", " ", el.text).strip())
            sig = f"{kind}:{ln}{list(attrs)}{txt}"
            sigs[sig] += 1
        # The ORDERED text stream — catches pure permutations the node multiset can't
        # (table Sort). scope.iter() walks in document order, so joining preserves it.
        flow = "↵".join(s for s in stream if s)
        if flow:
            if len(flow) > TEXT_STREAM_CAP:
                digest = hashlib.sha1(flow.encode("utf-8")).hexdigest()[:10]
                flow = flow[:TEXT_STREAM_CAP] + "~" + digest
            sigs[f"{kind}:textOrder|text={flow}"] += 1
    return sigs, parts_seen


def collect_styles(docx_path):
    """Parse styles.xml into {styleId: Counter(child-signatures)} + the set of styleIds the
    document body REFERENCES (via w:rStyle / w:pStyle / w:tblStyle w:val). The referenced set
    scopes the styles diff to styles the task actually USES — so latent template/boilerplate
    styles (which the clone preloads or Word lazily adds but nobody references) are ignored."""
    styles_map = {}
    referenced = set()
    z = zipfile.ZipFile(docx_path)
    names = z.namelist()
    if "word/styles.xml" in names:
        root = ET.fromstring(z.read("word/styles.xml"))
        for style in root.iter(W + "style"):
            sid = style.get(W + "styleId")
            if not sid:
                continue
            sigs = Counter()
            sigs[f"@type={style.get(W + 'type')}"] += 1   # the style's own type (character/paragraph/table)
            for el in style.iter():
                ln = local(el.tag)
                if ln == "style" or ln.lower() in NOISE_ELEMENTS:
                    continue   # skip the wrapper + per-save rsid bookkeeping
                sigs[f"{ln}{list(meaningful_attrs(el))}"] += 1
            styles_map[sid] = sigs
    if "word/document.xml" in names:
        root = ET.fromstring(z.read("word/document.xml"))
        for el in root.iter():
            if local(el.tag) in ("rStyle", "pStyle", "tblStyle"):
                v = el.get(W + "val")
                if v:
                    referenced.add(v)
    return styles_map, referenced


def _styles_diff(real_path, clone_path):
    """styleId-presence/content diff of styles.xml — the preloaded-vs-lazy-safe replacement for
    baseline-subtracted styles signatures. Compares ONLY styleIds referenced by either body
    (action-to-action, no baseline): a referenced style present in both with equal content is a
    MATCH regardless of which side added it lazily; a referenced style Word has + clone lacks/differs
    is MISSING; clone-only referenced is EXTRA. Returns (missing, extra, match_count)."""
    rstyles, rrefs = collect_styles(real_path)
    cstyles, crefs = collect_styles(clone_path)
    relevant = rrefs | crefs
    missing, extra, match = [], [], 0
    for sid in sorted(relevant):
        rc = rstyles.get(sid, Counter())
        cc = cstyles.get(sid, Counter())
        for sig in set(rc) | set(cc):
            r, c = rc.get(sig, 0), cc.get(sig, 0)
            if min(r, c) > 0:
                match += 1
            if r > c:
                missing.append(f"styles:{sid}:{sig}")
            if c > r:
                extra.append(f"styles:{sid}:{sig}")
    return sorted(missing), sorted(extra), match


def _signed_delta(action, baseline):
    """Per-signature SIGNED delta (action - baseline). Unlike Counter '-', negatives are
    KEPT — so a feature that REMOVES a node present in the baseline shows up as a negative
    delta and its asymmetry vs the other side survives instead of being floored to 0."""
    return {k: action.get(k, 0) - baseline.get(k, 0) for k in set(action) | set(baseline)}


def _divergence(rb, cb):
    """Signatures where the two empty-doc baselines disagree in multiplicity, for the parts
    where blank-equivalence is a SOUNDNESS concern (body/header/footer). The baselines come
    from different engines (Word COM vs the clone probe); a body/header/footer divergence
    means the net-of-baseline deltas reflect a blank-document gap, not only the feature — so
    report it. styles.xml/numbering.xml are EXCLUDED: the clone's default styles/numbering
    legitimately differ from Word's (their per-task deltas still cancel via signed subtraction),
    so flagging them here would just flood the report with default-template differences."""
    return [f"{s} (word_blank={rb.get(s, 0)}, clone_blank={cb.get(s, 0)})"
            for s in sorted(set(rb) | set(cb))
            if not s.startswith(("styles:", "numbering:")) and rb.get(s, 0) != cb.get(s, 0)]


def _bucket(rw, cl, rw_parts, cl_parts, task_id, baselined, baseline_divergence=None):
    """Classify two per-signature delta maps (+ part deltas) into match/missing/extra.
    rw/cl may hold SIGNED counts (action-minus-baseline); comparing the deltas surfaces a
    node the feature removed on one side (negative there, larger on the other) correctly."""
    allsigs = set(rw) | set(cl)
    match, missing, extra = [], [], []
    for s in allsigs:
        r, c = rw.get(s, 0), cl.get(s, 0)
        if min(r, c) > 0:
            match.append((s, min(r, c)))
        if r > c:
            missing.append((s, r - c))   # Word's delta exceeds clone's -> clone gap
        if c > r:
            extra.append((s, c - r))     # clone's delta exceeds Word's -> over-emission
    # part-count structural note (drop parts absent on both sides after delta)
    part_note = {k: {"word": rw_parts.get(k, 0), "clone": cl_parts.get(k, 0)}
                 for k in set(rw_parts) | set(cl_parts)
                 if rw_parts.get(k, 0) or cl_parts.get(k, 0)}
    # verdict heuristic: PASS if clone is not missing any node Word emitted; warnings = extra+structural.
    # D1.2 pass-with-note: a MISSING node that is provably functionally-harmless (an empty element Word
    # writes but the clone omits, or an explicit-default value that equals the implicit default) is a
    # NOTE, not a gap. If EVERY missing is benign -> pass-with-note (counts as pass; the note list is the
    # byte-parity backlog, NEVER deleted). Conservative on purpose (the hyperlink-style lesson): only the
    # classified-benign patterns qualify; anything else stays a real gap.
    missing_sigs = sorted([s for s, _ in missing])
    benign = [s for s in missing_sigs if _is_benign_missing(s)]
    real_missing = [s for s in missing_sigs if s not in set(benign)]
    if not real_missing and benign:
        verdict = "pass-with-note"
    elif not real_missing:
        verdict = "semantic-pass"
    else:
        verdict = "gap"
    return {
        "task": task_id,
        "baselined": baselined,
        "baseline_divergence": baseline_divergence or [],
        "verdict": verdict,
        "counts": {"match": len(match), "missing": len(real_missing), "extra": len(extra)},
        "missing_nodes": real_missing,                       # clone SHOULD emit these (real gaps)
        "notes": benign,                                     # D1.2: benign byte-diffs (pass-with-note)
        "extra_nodes": sorted([s for s, _ in extra]),        # clone over-emits these (fidelity warnings)
        "part_counts": part_note,
    }


# D1.2 benign-missing classifier — a MISSING signature that is functionally harmless. Conservative:
#   - body:pPr[]  — an EMPTY <w:pPr/> Word writes in a cell paragraph; the clone's <w:p/> is identical.
#   - body:jc[('val', 'left')]  — an EXPLICIT default (left is the implicit paragraph default).
#   - body:tblLook explicit all-zeros beyond val  — covered elsewhere; not listed here.
# Everything else (real borders, widths, heights, shading attrs, content) stays a real gap.
_BENIGN_MISSING_EXACT = {
    "body:pPr[]",
    "body:jc[('val', 'left')]",
}


def _is_benign_missing(sig):
    return sig in _BENIGN_MISSING_EXACT


def diff(real_path, clone_path, task_id=None, real_baseline=None, clone_baseline=None):
    """3-bucket diff of clone vs. real Word for one task.

    With baselines (v2): compare each side's SIGNED delta-vs-its-own-empty-doc, so unrelated
    blank-document boilerplate present equally in action and baseline cancels, while real gaps,
    over-emissions, AND feature-driven reductions all survive (signed deltas, not Counter '-'
    flooring). The two baselines come from different engines (Word COM vs the clone); when they
    disagree the divergence is reported in `baseline_divergence` rather than silently folded into
    the task. Baselines must be provided as a PAIR — one alone is ignored.
    """
    rw, rw_parts = collect(real_path)
    cl, cl_parts = collect(clone_path)
    baselined = bool(real_baseline and clone_baseline)
    divergence = None
    if baselined:
        rb, rb_parts = collect(real_baseline)
        cb, cb_parts = collect(clone_baseline)
        divergence = _divergence(rb, cb)
        rw, cl = _signed_delta(rw, rb), _signed_delta(cl, cb)
        rw_parts, cl_parts = _signed_delta(rw_parts, rb_parts), _signed_delta(cl_parts, cb_parts)
    result = _bucket(rw, cl, rw_parts, cl_parts, task_id, baselined, divergence)
    # styles.xml: merge the styleId-presence diff (NOT baseline-subtracted — preloaded-vs-lazy safe).
    s_missing, s_extra, s_match = _styles_diff(real_path, clone_path)
    if s_missing or s_extra or s_match:
        # styles-part missing may include benign styles:*:pPr[] (the empty style paragraph props) —
        # classify with the same D1.2 rule so a style-def whose only gap is the empty pPr passes-with-note.
        s_benign = [s for s in s_missing if _is_benign_styles_missing(s)]
        s_real = [s for s in s_missing if s not in set(s_benign)]
        result["missing_nodes"] = sorted(result["missing_nodes"] + s_real)
        result["notes"] = sorted(result.get("notes", []) + s_benign)
        result["extra_nodes"] = sorted(result["extra_nodes"] + s_extra)
        result["counts"]["match"] += s_match
        result["counts"]["missing"] = len(result["missing_nodes"])
        result["counts"]["extra"] += len(s_extra)
        if result["missing_nodes"]:
            result["verdict"] = "gap"
        elif result["notes"]:
            result["verdict"] = "pass-with-note"
        else:
            result["verdict"] = "semantic-pass"
    return result


def _is_benign_styles_missing(sig):
    # a styles-part missing that is functionally harmless: an empty pPr on a style def.
    return sig.startswith("styles:") and sig.endswith(":pPr[]")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("real")
    ap.add_argument("clone")
    ap.add_argument("--id", default=None)
    ap.add_argument("--rw-baseline", default=None, help="real-Word empty-doc baseline (.docx) to subtract")
    ap.add_argument("--cl-baseline", default=None, help="clone empty-doc baseline (.docx) to subtract")
    a = ap.parse_args()
    print(json.dumps(diff(a.real, a.clone, a.id, a.rw_baseline, a.cl_baseline), indent=2, ensure_ascii=False))
