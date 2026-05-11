"""Apply targeted patches to delivery-1/task_NN/verifier.py based on the
audit_correctness.json findings.

Patches applied per task:
  FRAME-OVERSPEC          → remove LayerInsideFrame(...), AllLayerBoundsInside(...outer_type="frame"...),
                            and frame-targeting LayerRotationEquals/LayerSizeEquals lines.
                            If the entire StructureRubric becomes empty, scope it to no checks
                            (full weight awarded per the framework's empty-checks rule).
  BRITTLE-ALIGN-TOLERANCE → raise alignment tolerance from <15 to 25 in Layers* checks.
  EFFECT-OVERSPEC         → replace EffectRubric([...]) check list with EffectRubric([], ...)
                            so the rubric awards full weight.
  SIZE-OVERSPEC           → remove offending LayerSizeEquals lines (verified safe via audit).
  COLOR-OVERSPEC          → remove offending SolidColorEquals lines.
  SHAPE-CHECK-MISSING     → manual review; skip for now.
  FRAME-UNDERSPEC         → leave alone (low severity).
  CORNER-RADIUS-OVERSPEC  → no patches yet (none flagged after refinement).

Per CLAUDE.md, this script makes real source edits. It backs up the
original .py to .py.bak in the same directory. After all patches, it
loads every patched verifier.py via importlib to confirm parsing.

Usage (from apps/figma/):
    .venv/bin/python cua-eval/runner/patch_verifiers.py [--dry-run]
"""
from __future__ import annotations

import ast
import importlib.util
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def _find_frame_call_lines(src: str) -> list[tuple[int, int]]:
    """Return (start_lineno, end_lineno) inclusive ranges for each Call node
    in the source that should be removed by FRAME-OVERSPEC patching.

    Targets:
      - LayerInsideFrame(...)
      - AllLayerBoundsInside(...outer_type="frame"...)
      - LayerRotationEquals(layer_type="frame", ...)
      - LayerSizeEquals(layer_type="frame", ...)
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    ranges: list[tuple[int, int]] = []

    def _kwarg(node: ast.Call, name: str) -> str | None:
        for kw in node.keywords:
            if kw.arg == name and isinstance(kw.value, ast.Constant):
                return kw.value.value
        return None

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        fname = None
        if isinstance(fn, ast.Name):
            fname = fn.id
        elif isinstance(fn, ast.Attribute):
            fname = fn.attr
        if not fname:
            continue
        match = False
        if fname == "LayerInsideFrame":
            match = True
        elif fname == "AllLayerBoundsInside" and _kwarg(node, "outer_type") == "frame":
            match = True
        elif fname in ("LayerRotationEquals", "LayerSizeEquals") and _kwarg(node, "layer_type") == "frame":
            match = True
        if match:
            start = node.lineno
            end = node.end_lineno or start
            ranges.append((start, end))
    return ranges


def _remove_line_ranges(src: str, ranges: list[tuple[int, int]]) -> tuple[str, int]:
    """Remove inclusive 1-based line ranges from source. Also strips a
    trailing comma+optional comment on the immediately-preceding line if
    that was the call's line. Returns (new_src, n_removed)."""
    if not ranges:
        return src, 0
    lines = src.splitlines(keepends=True)
    to_remove: set[int] = set()
    for start, end in ranges:
        for ln in range(start - 1, end):
            to_remove.add(ln)
    new_lines: list[str] = []
    for i, ln in enumerate(lines):
        if i in to_remove:
            continue
        new_lines.append(ln)
    new_src = "".join(new_lines)
    new_src = re.sub(r"\n{3,}", "\n\n", new_src)
    return new_src, len(ranges)

APP_ROOT = Path(__file__).resolve().parents[2]
DELIVERY = APP_ROOT / "delivery-1"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))


# Match a single python "call" line that's part of a check list.
# These checks are typically one-per-line inside a rubric block.
FRAME_LINE_PATTERNS = [
    # LayerInsideFrame("rectangle"), or LayerInsideFrame('rectangle'),
    re.compile(r"^[ \t]*LayerInsideFrame\([^)]*\)[ \t]*,?[ \t]*(?:#.*)?$", re.MULTILINE),
    # AllLayerBoundsInside(... outer_type="frame" ...),  — match the FULL call
    # including whatever is inside the parens, up to the matching ).
    # Use a permissive line-level match: any line that calls AllLayerBoundsInside
    # AND contains outer_type="frame".
    re.compile(
        r"^[ \t]*AllLayerBoundsInside\([^)]*outer_type=\"frame\"[^)]*\)[ \t]*,?[ \t]*(?:#.*)?$",
        re.MULTILINE,
    ),
    # LayerRotationEquals(layer_type="frame", ...),
    re.compile(
        r"^[ \t]*LayerRotationEquals\([^)]*layer_type=\"frame\"[^)]*\)[ \t]*,?[ \t]*(?:#.*)?$",
        re.MULTILINE,
    ),
    # LayerSizeEquals(layer_type="frame", ...),
    re.compile(
        r"^[ \t]*LayerSizeEquals\([^)]*layer_type=\"frame\"[^)]*\)[ \t]*,?[ \t]*(?:#.*)?$",
        re.MULTILINE,
    ),
]


def patch_frame_overspec(src: str) -> tuple[str, int]:
    """Remove frame-related check lines. Uses AST to find the call line
    ranges, so multi-line calls are handled correctly."""
    ranges = _find_frame_call_lines(src)
    return _remove_line_ranges(src, ranges)


def patch_brittle_align(src: str) -> tuple[str, int]:
    """Raise sub-15 alignment tolerances to 25 across ALL Layers* checks.

    The audit flags any `Layers*` check with `tolerance < 15`. Match the
    same set here.
    """
    new_src = src
    changed = 0
    # Any Layers<word>( ... tolerance=<num>
    pat = re.compile(r"(Layers\w+\([^)]*?\btolerance=)(\d+(?:\.\d+)?)")
    def repl(m: re.Match) -> str:
        nonlocal changed
        prefix = m.group(1)
        val = float(m.group(2))
        if val < 15:
            changed += 1
            return f"{prefix}25.0"
        return m.group(0)
    new_src = pat.sub(repl, new_src)
    # Also tolerance_px= (used in LayersStrictlyNested)
    pat2 = re.compile(r"(tolerance_px=)(\d+(?:\.\d+)?)")
    def repl2(m: re.Match) -> str:
        nonlocal changed
        val = float(m.group(2))
        if val < 15:
            changed += 1
            return f"{m.group(1)}25.0"
        return m.group(0)
    new_src = pat2.sub(repl2, new_src)
    return new_src, changed


def patch_effect_overspec(src: str) -> tuple[str, int]:
    """Empty out EffectRubric check list — i.e. EffectRubric([X, Y, Z], weight=...) -> EffectRubric([], weight=...).

    Per the framework's empty-checks rule, an empty checks list earns full
    rubric weight. This effectively removes the over-specified effect
    requirement while preserving overall rubric weighting.
    """
    new_src = src
    # Find the entire EffectRubric([ ... ], weight=..., critical=...) block
    # — match the [ ... ] balanced-brackets non-greedy.
    # Simpler approach: walk character-by-character to find the matching ]
    out_chunks: list[str] = []
    i = 0
    changed = 0
    while True:
        m = re.search(r"EffectRubric\(\[", new_src[i:])
        if not m:
            out_chunks.append(new_src[i:])
            break
        out_chunks.append(new_src[i:i + m.start()])
        i += m.end()
        # Now find the matching ']' by counting brackets
        depth = 1
        j = i
        while j < len(new_src) and depth > 0:
            ch = new_src[j]
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
            j += 1
        # j is now just past the matching ']'
        # Skip the original check-list content
        out_chunks.append("EffectRubric([]")
        changed += 1
        i = j  # j is just past ']' so the rest starts with the trailing ',' or ')'
    new_src = "".join(out_chunks)
    return new_src, changed


def _find_call_lines_by_name(src: str, target_names: set[str]) -> list[tuple[int, int]]:
    """Find line ranges for every Call whose function name is in target_names."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    ranges = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        fname = fn.id if isinstance(fn, ast.Name) else (
            fn.attr if isinstance(fn, ast.Attribute) else None)
        if fname in target_names:
            ranges.append((node.lineno, node.end_lineno or node.lineno))
    return ranges


def patch_size_overspec(src: str) -> tuple[str, int]:
    """Remove all LayerSizeEquals lines (treat as a class - the audit
    flagged the verifier as a whole)."""
    ranges = _find_call_lines_by_name(src, {"LayerSizeEquals"})
    return _remove_line_ranges(src, ranges)


def patch_color_overspec(src: str) -> tuple[str, int]:
    """Remove all SolidColorEquals lines."""
    ranges = _find_call_lines_by_name(src, {"SolidColorEquals"})
    return _remove_line_ranges(src, ranges)


def load_audit() -> list[dict[str, Any]]:
    p = APP_ROOT / "audit_correctness.json"
    if not p.is_file():
        print("ERROR: audit_correctness.json missing; run audit_correctness.py first")
        sys.exit(1)
    return json.load(p.open())


def smoke_test_load(verifier_path: Path) -> tuple[bool, str]:
    """Import the patched verifier and check that `task` is well-formed."""
    spec = importlib.util.spec_from_file_location(
        f"smoketest_{verifier_path.parent.name}", verifier_path
    )
    try:
        if spec is None or spec.loader is None:
            return False, "spec failed"
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        task = mod.task
        # Sanity: rubrics list, each has run()
        for r in task.rubrics:
            if not hasattr(r, "run"):
                return False, f"rubric {r} has no run()"
        return True, "ok"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    audit = load_audit()
    audit_by_taskdir = {t["task_dir"]: t for t in audit}

    patch_summary: list[dict[str, Any]] = []
    issue_type_counter: Counter = Counter()
    total_patches = 0

    for tdir in sorted(DELIVERY.iterdir()):
        if not tdir.is_dir() or not (tdir / "verifier.py").is_file():
            continue
        record = audit_by_taskdir.get(tdir.name)
        if not record or record["n_issues"] == 0:
            continue
        verifier_path = tdir / "verifier.py"
        src = verifier_path.read_text(encoding="utf-8")
        original = src
        issue_types = set(i["type"] for i in record["issues"])
        n_frame = n_align = n_effect = n_size = n_color = 0

        if "FRAME-OVERSPEC" in issue_types:
            src, n_frame = patch_frame_overspec(src)
        if "BRITTLE-ALIGN-TOLERANCE" in issue_types:
            src, n_align = patch_brittle_align(src)
        if "EFFECT-OVERSPEC" in issue_types:
            src, n_effect = patch_effect_overspec(src)
        if "SIZE-OVERSPEC" in issue_types:
            src, n_size = patch_size_overspec(src)
        if "COLOR-OVERSPEC" in issue_types:
            src, n_color = patch_color_overspec(src)

        n_changes = n_frame + n_align + n_effect + n_size + n_color
        if n_changes == 0:
            continue

        # Validate by parsing+exec
        if not dry_run:
            backup = verifier_path.with_suffix(".py.bak")
            if not backup.is_file():
                shutil.copyfile(verifier_path, backup)
            verifier_path.write_text(src, encoding="utf-8")
            ok, msg = smoke_test_load(verifier_path)
            if not ok:
                # Revert
                print(f"  ✗ {tdir.name}: smoke_test failed ({msg}), reverting")
                verifier_path.write_text(original, encoding="utf-8")
                patch_summary.append({
                    "task_dir": tdir.name, "patches": {}, "smoke_test": "fail",
                    "error": msg,
                })
                continue
        patch_summary.append({
            "task_dir": tdir.name,
            "patches": {
                "FRAME-OVERSPEC": n_frame,
                "BRITTLE-ALIGN-TOLERANCE": n_align,
                "EFFECT-OVERSPEC": n_effect,
                "SIZE-OVERSPEC": n_size,
                "COLOR-OVERSPEC": n_color,
            },
            "smoke_test": "dry-run" if dry_run else "pass",
        })
        for it_name, cnt in [
            ("FRAME-OVERSPEC", n_frame), ("BRITTLE-ALIGN-TOLERANCE", n_align),
            ("EFFECT-OVERSPEC", n_effect), ("SIZE-OVERSPEC", n_size),
            ("COLOR-OVERSPEC", n_color),
        ]:
            if cnt:
                issue_type_counter[it_name] += cnt
        total_patches += n_changes
        print(f"  {'(dry)' if dry_run else '   '} {tdir.name}: "
              f"frame={n_frame} align={n_align} effect={n_effect} "
              f"size={n_size} color={n_color}")

    print()
    print(f"=== summary ===")
    print(f"  tasks patched:        {len(patch_summary)}")
    print(f"  total line changes:   {total_patches}")
    for it, n in issue_type_counter.most_common():
        print(f"    {it:<28} {n}")
    print(f"  dry_run={dry_run}")
    if not dry_run:
        print(f"  originals saved to {tdir.parent}/task_*/verifier.py.bak")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
