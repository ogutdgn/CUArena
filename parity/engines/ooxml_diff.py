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
import sys, re, json, zipfile, argparse
import xml.etree.ElementTree as ET
from collections import Counter

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
# attribute LOCAL names that are per-save noise (random every save) -> stripped
NOISE_ATTRS = {"rsid", "rsidr", "rsidrpr", "rsidrdefault", "rsidp", "rsidtr",
               "rsiddel", "rsidsect", "paraid", "textid"}
# text content matters for these (field instructions) -> folded into the signature
TEXT_NODES = {"instrText"}


def local(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def part_kind(name):
    if name == "word/document.xml":
        return "body"
    if re.match(r"word/header\d*\.xml", name):
        return "header"
    if re.match(r"word/footer\d*\.xml", name):
        return "footer"
    return None


def meaningful_attrs(el):
    out = []
    for k, v in el.attrib.items():
        ln = local(k).lower()
        if ln in NOISE_ATTRS:
            continue
        out.append((local(k), v))
    return tuple(sorted(out))


def collect(docx_path):
    """Return a Counter of node signatures across body/header/footer parts."""
    sigs = Counter()
    parts_seen = Counter()
    z = zipfile.ZipFile(docx_path)
    for name in z.namelist():
        kind = part_kind(name)
        if not kind:
            continue
        parts_seen[kind] += 1
        root = ET.fromstring(z.read(name))
        # for the body, only look inside w:body (skip sectPr-of-doc boilerplate? keep it; it's real)
        scope = root.find(W + "body") if kind == "body" else root
        if scope is None:
            scope = root
        for el in scope.iter():
            ln = local(el.tag)
            attrs = meaningful_attrs(el)
            txt = ""
            if ln in TEXT_NODES and el.text:
                txt = "|text=" + re.sub(r"\s+", " ", el.text).strip()
            sig = f"{kind}:{ln}{list(attrs)}{txt}"
            sigs[sig] += 1
    return sigs, parts_seen


def _signed_delta(action, baseline):
    """Per-signature SIGNED delta (action - baseline). Unlike Counter '-', negatives are
    KEPT — so a feature that REMOVES a node present in the baseline shows up as a negative
    delta and its asymmetry vs the other side survives instead of being floored to 0."""
    return {k: action.get(k, 0) - baseline.get(k, 0) for k in set(action) | set(baseline)}


def _divergence(rb, cb):
    """Signatures where the two empty-doc baselines disagree in multiplicity. The baselines
    come from different engines (Word COM vs the clone probe); when they diverge, the
    net-of-baseline deltas reflect a blank-document gap, not only the feature — so report it
    loudly here instead of silently folding it into every task's missing/extra."""
    return [f"{s} (word_blank={rb.get(s, 0)}, clone_blank={cb.get(s, 0)})"
            for s in sorted(set(rb) | set(cb)) if rb.get(s, 0) != cb.get(s, 0)]


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
    # verdict heuristic: PASS if clone is not missing any node Word emitted; warnings = extra+structural
    semantic_pass = len(missing) == 0
    return {
        "task": task_id,
        "baselined": baselined,
        "baseline_divergence": baseline_divergence or [],
        "verdict": "semantic-pass" if semantic_pass else "gap",
        "counts": {"match": len(match), "missing": len(missing), "extra": len(extra)},
        "missing_nodes": sorted([s for s, _ in missing]),   # clone SHOULD emit these
        "extra_nodes": sorted([s for s, _ in extra]),        # clone over-emits these
        "part_counts": part_note,
    }


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
    return _bucket(rw, cl, rw_parts, cl_parts, task_id, baselined, divergence)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("real")
    ap.add_argument("clone")
    ap.add_argument("--id", default=None)
    ap.add_argument("--rw-baseline", default=None, help="real-Word empty-doc baseline (.docx) to subtract")
    ap.add_argument("--cl-baseline", default=None, help="clone empty-doc baseline (.docx) to subtract")
    a = ap.parse_args()
    print(json.dumps(diff(a.real, a.clone, a.id, a.rw_baseline, a.cl_baseline), indent=2, ensure_ascii=False))
