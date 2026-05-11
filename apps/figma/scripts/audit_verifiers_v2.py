"""Static audit for all 50 task verifiers, scanning known bug patterns
identified from the sonnet 4.5 rollout audit:

  1. EVENT-NAME — `EventTypeCountAtLeast(name, ...)` where `name` is not in
     the mock's actual event vocabulary (would always score 0).

  2. HARDCODED-RGB — `StrokeColorEquals` / `SolidColorEquals` /
     `LayersHaveColorOrder` with hardcoded RGB constants AND the task
     prompt uses color *names* (not hex codes). The verifier may reject
     reasonable LLM interpretations of named colors.

  3. CRITICAL-SINGLE — A rubric with one check and `critical=[0]`. Any
     failure collapses the entire rubric to 0 (no partial credit possible).

  4. CONTRADICTION — Verifier check whose semantic disagrees with the
     prompt wording. Heuristic: prompt contains hedging words ("around",
     "approximately", "small", "roughly") AND verifier check has tight
     tolerance (< 15 px or < 10°).

Findings are printed for human review. This script does NOT modify any
verifier.

Usage:
    .venv/bin/python scripts/audit_verifiers_v2.py
    .venv/bin/python scripts/audit_verifiers_v2.py --task 07
"""
from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
DELIVERY = APP_ROOT / "delivery-1"
MOCK_EVENTS = set(Path("/tmp/mock_events.txt").read_text().split())


COLOR_WORDS = {
    "red", "blue", "green", "yellow", "orange", "purple", "pink", "magenta",
    "cyan", "teal", "violet", "indigo", "white", "black", "gray", "grey",
    "brown", "gold", "silver", "lime", "navy", "maroon", "olive", "tan",
    "beige", "coral", "salmon", "amber", "rose", "fuchsia", "peach", "ivory",
    "khaki", "azure", "crimson", "scarlet", "emerald", "mint", "aqua",
    "lavender", "lilac", "rust", "ochre", "sepia",
}

HEDGE_WORDS = {
    "around", "approximately", "approximate", "approx", "roughly", "about",
    "small", "slight", "slightly", "nearby", "near", "overhang",
    "similar", "looks like", "kind of", "ish",
}


def parse_verifier(path: Path) -> dict:
    """Pull rubrics, checks, and notable kwargs out of a verifier.py."""
    src = path.read_text()
    tree = ast.parse(src)
    rubrics = []
    # Find the task = Task(...) call
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "Task":
            for kw in node.keywords:
                if kw.arg == "rubrics" and isinstance(kw.value, ast.List):
                    for rb_node in kw.value.elts:
                        if not isinstance(rb_node, ast.Call):
                            continue
                        rb_name = getattr(rb_node.func, "id", "?")
                        # First positional arg is the list of checks
                        checks: list[dict] = []
                        critical: list[int] = []
                        weight: float | None = None
                        for arg in rb_node.args:
                            if isinstance(arg, ast.List):
                                for ch in arg.elts:
                                    if isinstance(ch, ast.Call):
                                        checks.append(_summarize_check(ch))
                        for kk in rb_node.keywords:
                            if kk.arg == "critical" and isinstance(kk.value, ast.List):
                                critical = [
                                    e.value for e in kk.value.elts
                                    if isinstance(e, ast.Constant)
                                ]
                            if kk.arg == "weight" and isinstance(kk.value, ast.Constant):
                                weight = kk.value.value
                        rubrics.append({
                            "name": rb_name, "weight": weight,
                            "checks": checks, "critical": critical,
                        })
    return {"src": src, "rubrics": rubrics}


def _summarize_check(call: ast.Call) -> dict:
    """Pull the check class name + interesting kwargs into a dict."""
    name = getattr(call.func, "id", "?")
    out: dict = {"name": name, "args": [], "kwargs": {}}
    for a in call.args:
        out["args"].append(_literal(a))
    for kw in call.keywords:
        out["kwargs"][kw.arg] = _literal(kw.value)
    return out


def _literal(node):
    """Best-effort literal extraction from an AST node."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return f"<{node.id}>"
    if isinstance(node, ast.Dict):
        return {
            (k.value if isinstance(k, ast.Constant) else "?"): _literal(v)
            for k, v in zip(node.keys, node.values)
        }
    if isinstance(node, ast.List):
        return [_literal(e) for e in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(_literal(e) for e in node.elts)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_literal(node.operand)
    return f"<{type(node).__name__}>"


def read_prompt(task_dir: Path) -> str:
    """Concatenate prompt.md and the 'thorough description' / 'simplified prompt' sections."""
    p = task_dir / "prompt.md"
    if not p.exists():
        return ""
    return p.read_text().lower()


def audit_task(task_dir: Path) -> list[dict]:
    """Return list of finding dicts for this task."""
    findings: list[dict] = []
    name = task_dir.name
    v = parse_verifier(task_dir / "verifier.py")
    prompt = read_prompt(task_dir)

    color_words_in_prompt = {w for w in COLOR_WORDS if re.search(rf"\b{w}\b", prompt)}
    hedge_words_in_prompt = {w for w in HEDGE_WORDS if w in prompt}

    for ri, rb in enumerate(v["rubrics"]):
        single_critical_full = (
            len(rb["checks"]) == 1
            and rb["critical"] == [0]
        )
        for ci, ch in enumerate(rb["checks"]):
            cname = ch["name"]

            # ── 1. EVENT-NAME ──
            if cname in ("EventTypeCount", "EventTypeCountAtLeast", "EventTypeUsed"):
                # First positional arg is the event name string
                ev_name = ch["args"][0] if ch["args"] else None
                if isinstance(ev_name, str) and ev_name not in MOCK_EVENTS:
                    findings.append({
                        "task": name, "kind": "EVENT-NAME",
                        "rubric": rb["name"], "check_idx": ci,
                        "detail": f"event name '{ev_name}' not in mock vocabulary",
                        "suggestion": _suggest_event_name(ev_name),
                    })

            # ── 2. HARDCODED-RGB ──
            if cname in (
                "StrokeColorEquals", "AllStrokeColorEquals",
                "SolidColorEquals", "AllSolidColorEquals",
                "CentermostLayerHasColor",
            ):
                # expected_rgb kwarg should be a hardcoded dict OR a <Name> reference
                rgb = ch["kwargs"].get("expected_rgb")
                if rgb and color_words_in_prompt:
                    findings.append({
                        "task": name, "kind": "HARDCODED-RGB",
                        "rubric": rb["name"], "check_idx": ci,
                        "detail": (f"{cname} requires specific RGB; "
                                   f"prompt uses color names: {sorted(color_words_in_prompt)}"),
                        "suggestion": "Consider HSL hue matching or loosen tolerance to ≥0.40",
                    })
            if cname == "LayersHaveColorOrder":
                if color_words_in_prompt:
                    tol = ch["kwargs"].get("tolerance")
                    if isinstance(tol, (int, float)) and tol <= 0.30:
                        findings.append({
                            "task": name, "kind": "HARDCODED-RGB",
                            "rubric": rb["name"], "check_idx": ci,
                            "detail": (f"LayersHaveColorOrder tolerance={tol} is tight; "
                                       f"prompt uses color names: {sorted(color_words_in_prompt)}"),
                            "suggestion": "Bump tolerance to 0.40+ or switch to hue-based matching",
                        })

            # ── 3. CRITICAL-SINGLE ──
            if single_critical_full and ci == 0:
                findings.append({
                    "task": name, "kind": "CRITICAL-SINGLE",
                    "rubric": rb["name"], "check_idx": ci,
                    "detail": f"Rubric '{rb['name']}' has 1 check with critical=[0]; "
                              f"any failure collapses {rb['weight']} to 0",
                    "suggestion": "Add a secondary partial-credit check, or relax tolerance",
                })

            # ── 4. CONTRADICTION ──
            if cname in (
                "PolygonCornersAligned", "LayersAligned",
                "LayerEdgesAligned",
            ):
                tol = ch["kwargs"].get("tolerance")
                if isinstance(tol, (int, float)) and tol < 15.0 and hedge_words_in_prompt:
                    findings.append({
                        "task": name, "kind": "CONTRADICTION",
                        "rubric": rb["name"], "check_idx": ci,
                        "detail": (f"{cname} tolerance={tol}px is tight; "
                                   f"prompt has hedge words: {sorted(hedge_words_in_prompt)}"),
                        "suggestion": "Loosen tolerance or remove check if prompt explicitly allows variance",
                    })

    return findings


def _suggest_event_name(bad: str) -> str:
    """For event names not in vocab, suggest closest match."""
    # crude: prefix match + token similarity
    candidates = [e for e in MOCK_EVENTS if bad.split("_")[0] in e]
    if candidates:
        return f"Closest matches in mock vocab: {sorted(candidates)[:3]}"
    return "No close match; check the mock's tools/ folder for the actual event name"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task", default=None, help="Audit a single task NN")
    args = p.parse_args()

    all_findings: list[dict] = []
    task_dirs = sorted(d for d in DELIVERY.iterdir() if d.is_dir() and d.name.startswith("task_"))
    if args.task:
        task_dirs = [d for d in task_dirs if d.name.endswith(f"_{args.task}") or d.name == f"task_{args.task}"]

    for d in task_dirs:
        findings = audit_task(d)
        all_findings.extend(findings)

    # Print grouped report
    by_kind: dict[str, list[dict]] = {}
    for f in all_findings:
        by_kind.setdefault(f["kind"], []).append(f)

    print(f"\n=== Audit: {len(task_dirs)} tasks scanned, {len(all_findings)} findings ===\n")
    for kind in ("EVENT-NAME", "HARDCODED-RGB", "CONTRADICTION", "CRITICAL-SINGLE"):
        items = by_kind.get(kind, [])
        print(f"\n──── {kind} ({len(items)} findings) ────")
        for f in items:
            print(f"  [{f['task']}] {f['rubric']} #check{f['check_idx']}")
            print(f"     {f['detail']}")
            if f.get("suggestion"):
                print(f"     → {f['suggestion']}")

    # Per-task summary count
    print(f"\n=== Per-task summary ===")
    task_counts: dict[str, dict[str, int]] = {}
    for f in all_findings:
        d = task_counts.setdefault(f["task"], {})
        d[f["kind"]] = d.get(f["kind"], 0) + 1
    for tn, counts in sorted(task_counts.items()):
        parts = [f"{k}={v}" for k, v in counts.items()]
        print(f"  {tn:30s}  {' '.join(parts)}")


if __name__ == "__main__":
    main()
