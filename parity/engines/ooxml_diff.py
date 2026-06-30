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


def diff(real_path, clone_path, task_id=None):
    rw, rw_parts = collect(real_path)
    cl, cl_parts = collect(clone_path)
    allsigs = set(rw) | set(cl)
    match, missing, extra = [], [], []
    for s in allsigs:
        r, c = rw.get(s, 0), cl.get(s, 0)
        if r and c:
            match.append((s, min(r, c)))
        if r > c:
            missing.append((s, r - c))   # Word has more -> clone gap
        if c > r:
            extra.append((s, c - r))     # clone has more -> over-emission
    # part-count structural note
    part_note = {k: {"word": rw_parts.get(k, 0), "clone": cl_parts.get(k, 0)}
                 for k in set(rw_parts) | set(cl_parts)}
    # verdict heuristic: PASS if clone is not missing any node Word emitted; warnings = extra+structural
    semantic_pass = len(missing) == 0
    return {
        "task": task_id,
        "verdict": "semantic-pass" if semantic_pass else "gap",
        "counts": {"match": len(match), "missing": len(missing), "extra": len(extra)},
        "missing_nodes": sorted([s for s, _ in missing]),   # clone SHOULD emit these
        "extra_nodes": sorted([s for s, _ in extra]),        # clone over-emits these
        "part_counts": part_note,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("real")
    ap.add_argument("clone")
    ap.add_argument("--id", default=None)
    a = ap.parse_args()
    print(json.dumps(diff(a.real, a.clone, a.id), indent=2, ensure_ascii=False))
