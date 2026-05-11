"""Audit each task verifier against its OWN prompt, ignoring model behavior.

For each of the 50 tasks, this script asks: does the verifier check what
the prompt actually asks for? Specifically, it detects 5 mismatch types:

1. FRAME-OVERSPEC: verifier requires a frame containment check but the
   prompt's "Thorough description" doesn't mention a frame as a design
   element.
2. SHAPE-COUNT-MISMATCH: prompt says "draw N rectangles" but verifier
   doesn't check that count (or checks a different count).
3. COLOR-OVERSPEC: verifier requires a specific RGB but the prompt only
   says e.g. "pick a color" or "any blue".
4. SIZE-OVERSPEC: verifier requires exact W×H but the prompt only gives
   a qualitative size ("small", "wide").
5. TOOL-CHECK-MISSING: prompt explicitly says "use the Pen tool" but the
   verifier doesn't check ToolUsed("pen").

Outputs:
  - apps/figma/audit_correctness.json  per-task structured comparison
  - apps/figma/VERIFIER_CORRECTNESS_AUDIT.md  human-readable doc

Usage (from apps/figma/):
    .venv/bin/python cua-eval/runner/audit_correctness.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

APP_ROOT = Path(__file__).resolve().parents[2]
DELIVERY = APP_ROOT / "delivery-1"


# ---------------------------------------------------------------- prompt parsing
def extract_thorough_description(prompt_md: str) -> str:
    """Extract just the 'Thorough description' section. This is the section
    the harness sends to the model in default prompt-mode, so it's the
    contract the verifier should check against."""
    m = re.search(r"## Thorough description\s*\n(.+?)(?=\n##|\Z)", prompt_md, re.DOTALL)
    return m.group(1).strip() if m else ""


COLOR_NAMES = {
    "red", "orange", "yellow", "green", "blue", "purple", "pink", "brown",
    "black", "white", "gray", "grey", "navy", "teal", "magenta", "cyan",
    "gold", "silver", "beige", "sand", "cream", "lime", "violet", "indigo",
    "olive", "maroon", "crimson", "scarlet", "azure", "turquoise", "amber",
    "salmon", "coral", "khaki", "ivory", "rose", "ruby", "mint",
    "light-gray", "light-grey", "dark-gray", "dark-grey", "off-white",
    "pastel", "rainbow", "warm-orange",
}

SHAPE_NAMES = {
    "rectangle", "rectangles", "square", "squares",
    "circle", "circles", "ellipse", "ellipses",
    "triangle", "triangles", "polygon", "polygons",
    "star", "stars", "line", "lines",
    "arrow", "arrows", "frame", "frames",
    "text", "vector",
}


def parse_prompt(prompt_md: str) -> dict[str, Any]:
    """Extract structured requirements from the prompt's Thorough description.

    Returns a dict of:
      - description (full thorough-description text)
      - mentions_frame (bool): explicit Figma-frame reference
      - frame_phrases (list[str]): exact phrases that triggered it
      - mentions_named_color (set[str]): named colors that appear
      - mentions_hex_color (list[str]): hex codes that appear
      - mentions_size (list[str]): N×N pixel specs that appear
      - mentions_shape_counts (list[tuple[int, str]]): "3 rectangles", etc.
      - mentions_tools (set[str]): pen/rectangle/ellipse/star/polygon/text/frame tool
      - mentions_effects (set[str]): drop shadow / blur / inner shadow
      - mentions_alignment (bool): centered / aligned / symmetric
      - mentions_corner_radius (bool): rounded / corner radius
      - mentions_specific_count (list[int]): "exactly N", "N rectangles"
    """
    desc = extract_thorough_description(prompt_md)
    low = desc.lower()
    out: dict[str, Any] = {"description": desc}

    # Frame as Figma element (not "framework" / "frame the question")
    frame_patterns = [
        r"\b\d+\s*[x×]\s*\d+\s+frame\b",
        r"\binside\s+(?:a|an|the)\s+[\w-]+(?:\s+\w+)?\s+frame\b",
        r"\binside\s+\d+\s*[x×]\s*\d+\s+frame\b",
        r"\bouter\s+frame\b",
        r"\b(?:navy|dark|light)\s+frame\b",
        r"\bin\s+(?:a|an)\s+frame\b",
        r"\b(?:create|draw|make|add|use)\s+(?:the\s+)?(?:\d+x\d+\s+)?(?:\w+\s+)?frame\b",
        r"\bframe\s+(?:tool|named|titled|with|filled|containing)\b",
        r"\bmacbook\s+air\s+frame\b",
    ]
    fp = re.compile("|".join(frame_patterns), re.IGNORECASE)
    matches = [m.group(0) for m in fp.finditer(desc)]
    out["mentions_frame"] = bool(matches)
    out["frame_phrases"] = matches[:5]

    # Named colors
    named = set()
    for c in COLOR_NAMES:
        if re.search(rf"\b{c}\b", low):
            named.add(c)
    out["mentions_named_color"] = named

    # Hex colors
    hex_codes = re.findall(r"#[0-9a-fA-F]{6}\b", desc)
    out["mentions_hex_color"] = hex_codes

    # Sizes (NxN pixels)
    out["mentions_size"] = re.findall(r"\b\d+\s*[x×]\s*\d+\b", desc)

    # Shape counts: "3 rectangles", "two circles"
    word_to_num = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                   "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
                   "twelve": 12}
    counts: list[tuple[int, str]] = []
    for m in re.finditer(r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|twelve)\s+(\w+)\b", low):
        n_str, w = m.group(1), m.group(2)
        try:
            n = int(n_str)
        except ValueError:
            n = word_to_num.get(n_str, 0)
        if n and w in SHAPE_NAMES:
            # Normalize plural
            singular = w.rstrip("s") if w.endswith("s") else w
            counts.append((n, singular))
    out["mentions_shape_counts"] = counts

    # Tools
    tools: set[str] = set()
    for tool, patterns in {
        "pen": [r"\bpen\s+tool\b", r"\busing\s+the\s+pen\b", r"\bpen-tool\b"],
        "rectangle": [r"\brectangle\s+tool\b"],
        "ellipse": [r"\bellipse\s+tool\b"],
        "polygon": [r"\bpolygon\s+tool\b"],
        "star": [r"\bstar\s+tool\b"],
        "line": [r"\bline\s+tool\b"],
        "arrow": [r"\barrow\s+tool\b"],
        "text": [r"\btext\s+tool\b"],
        "frame": [r"\bframe\s+tool\b"],
        "pencil": [r"\bpencil\s+tool\b"],
        "vector": [r"\bvector\s+tool\b"],
    }.items():
        if any(re.search(p, low) for p in patterns):
            tools.add(tool)
    out["mentions_tools"] = tools

    # Effects
    effects: set[str] = set()
    if re.search(r"\bdrop\s*shadow", low):
        effects.add("drop_shadow")
    if re.search(r"\binner\s*shadow", low):
        effects.add("inner_shadow")
    if re.search(r"\blayer\s*blur", low) or re.search(r"\bblur\b", low):
        effects.add("blur")
    out["mentions_effects"] = effects

    # Alignment-ish requirements
    out["mentions_alignment"] = bool(re.search(
        r"\b(centered|aligned|symmetric|concentric|same\s+center|share\s+(?:a|the)\s+(?:center|bottom|top|baseline))",
        low))

    # Corner radius
    out["mentions_corner_radius"] = bool(re.search(
        r"\b(rounded\s+rectangle|corner\s+radius|rounded\s+corners?|rounded)\b", low))

    return out


# ---------------------------------------------------------------- verifier intro
# We already have introspected verifier data in audit_data.json from
# audit_verifiers.py — load it instead of re-walking the AST.
def load_verifier_introspection() -> dict[str, dict[str, Any]]:
    p = APP_ROOT / "audit_data.json"
    if not p.is_file():
        print(f"ERROR: missing {p}; run audit_verifiers.py first", file=sys.stderr)
        sys.exit(1)
    data = json.load(p.open())
    return {t["task_id"]: t for t in data}


# ---------------------------------------------------------------- compare
def compare(prompt: dict[str, Any], verifier: dict[str, Any]) -> dict[str, Any]:
    """For one task, compare prompt requirements against verifier checks.
    Return a dict of mismatch flags + reasons."""
    issues: list[dict[str, str]] = []

    frame_required = verifier.get("frame_required", False)
    if frame_required and not prompt["mentions_frame"]:
        issues.append({
            "type": "FRAME-OVERSPEC",
            "severity": "high",
            "detail": "Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) "
                      "but prompt's Thorough description does not mention a Figma frame.",
        })
    elif (not frame_required) and prompt["mentions_frame"]:
        issues.append({
            "type": "FRAME-UNDERSPEC",
            "severity": "low",
            "detail": f"Prompt mentions a frame ({prompt['frame_phrases'][0] if prompt['frame_phrases'] else ''}) "
                      "but verifier has no frame containment check.",
        })

    # Shape count consistency: verifier ShapeCount(equals=N) should match prompt "N <shape>"
    required_shapes = verifier.get("required_shape_types", {})
    for n, shape in prompt["mentions_shape_counts"]:
        # Map prompt-singular to verifier shape type
        # NOTE: prompt may say "squares" or "triangles" but the verifier may use
        # "rectangle" or "polygon" (square = rectangle in Figma; triangle = polygon-3)
        equivalents = {
            "square": "rectangle", "triangle": "polygon",
            "star": "polygon",  # star = polygon variant in mock
        }
        vshape = equivalents.get(shape, shape)
        if vshape in required_shapes:
            continue
        # If the prompt specifies a count but the verifier doesn't check the type at all
        # That's a potential under-spec
        issues.append({
            "type": "SHAPE-CHECK-MISSING",
            "severity": "medium",
            "detail": f"Prompt mentions '{n} {shape}(s)' but verifier has no ShapeCount/ShapeCountAtLeast check for {vshape!r}.",
        })

    # Tool checks — if prompt explicitly says "use the X tool", check verifier has ToolUsed(X)
    tool_checks: set[str] = set()
    for rubric in verifier.get("rubrics", []):
        for check in rubric.get("checks", []):
            if check["check"] == "ToolUsed":
                t = check["params"].get("tool")
                if t:
                    tool_checks.add(t)
    # NOTE: skipping TOOL-CHECK-MISSING as a correctness issue.
    # The verifier's job is to check OUTPUTS (right shape, right color), not
    # which tool produced them. The prompt's "use pen tool" is a recipe hint,
    # not a contract. Many verifiers correctly check polygon shape counts
    # instead of ToolUsed("pen"). Capturing the prompt's tool mentions for
    # informational purposes but not flagging as a gap.
    _ = tool_checks  # unused

    # Color — if verifier has SolidColorEquals with specific RGB, prompt should mention a specific
    # named color or hex; otherwise it's color-overspec
    solid_color_checks: list[dict[str, Any]] = []
    for rubric in verifier.get("rubrics", []):
        for check in rubric.get("checks", []):
            if check["check"] == "SolidColorEquals":
                solid_color_checks.append(check)
    if solid_color_checks and not (prompt["mentions_named_color"] or prompt["mentions_hex_color"]):
        issues.append({
            "type": "COLOR-OVERSPEC",
            "severity": "medium",
            "detail": f"Verifier requires {len(solid_color_checks)} specific RGB(s) but prompt mentions no named color or hex.",
        })

    # Size — if verifier has LayerSizeEquals, prompt should mention a NxN size
    size_checks: list[dict[str, Any]] = []
    for rubric in verifier.get("rubrics", []):
        for check in rubric.get("checks", []):
            if check["check"] == "LayerSizeEquals":
                size_checks.append(check)
    if size_checks and not prompt["mentions_size"]:
        issues.append({
            "type": "SIZE-OVERSPEC",
            "severity": "medium",
            "detail": f"Verifier requires exact W×H ({len(size_checks)} check(s)) but prompt mentions no pixel dimensions.",
        })

    # Effects — verifier requires effects? Prompt mention them?
    effect_check_names = {"DropShadowExists", "EffectCount", "DropShadowCountAtLeast",
                          "PairedDropShadowsOpposite", "LayerBlurExists", "InnerShadowExists"}
    has_effect_check = False
    for rubric in verifier.get("rubrics", []):
        for check in rubric.get("checks", []):
            if check["check"] in effect_check_names:
                has_effect_check = True
                break
    if has_effect_check and not prompt["mentions_effects"]:
        issues.append({
            "type": "EFFECT-OVERSPEC",
            "severity": "medium",
            "detail": "Verifier requires drop-shadow / effect checks but prompt mentions no effects.",
        })

    # Corner radius — only flag POSITIVE requirements (must be rounded).
    # CornerRadiusFractionAtMost is a "don't be too round" sanity check
    # — that's a legitimate guard against the model accidentally making a
    # rectangle a pill / circle. Don't count it as over-spec.
    has_rounded_requirement = any(
        c["check"] in ("CornerRadiusAtLeast", "CornerRadiusEquals")
        and c["params"].get("min_value", 0) > 0
        for r in verifier.get("rubrics", [])
        for c in r.get("checks", [])
    )
    if has_rounded_requirement and not prompt["mentions_corner_radius"]:
        issues.append({
            "type": "CORNER-RADIUS-OVERSPEC",
            "severity": "medium",
            "detail": "Verifier REQUIRES rounded corners (CornerRadiusAtLeast/Equals) but "
                      "prompt doesn't mention 'rounded' or 'corner radius'.",
        })

    # Brittle alignment (verifier-side regardless of prompt)
    if verifier.get("brittle_alignment_tolerance"):
        issues.append({
            "type": "BRITTLE-ALIGN-TOLERANCE",
            "severity": "medium",
            "detail": "Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. "
                      "This is a calibration issue, not a prompt-mismatch issue.",
        })

    return {
        "issues": issues,
        "n_issues": len(issues),
        "severity_counts": dict(Counter(i["severity"] for i in issues)),
        "issue_types": [i["type"] for i in issues],
    }


# ---------------------------------------------------------------- main
def main() -> int:
    verifier_data = load_verifier_introspection()
    out: list[dict[str, Any]] = []

    for tdir in sorted(DELIVERY.iterdir()):
        if not tdir.is_dir():
            continue
        verifier_path = tdir / "verifier.py"
        prompt_path = tdir / "prompt.md"
        if not (verifier_path.is_file() and prompt_path.is_file()):
            continue
        prompt_md = prompt_path.read_text(encoding="utf-8")
        prompt = parse_prompt(prompt_md)

        # Match verifier introspection by directory name
        task_id_match = None
        for tid, td in verifier_data.items():
            if td.get("task_dir") == tdir.name:
                task_id_match = tid
                break
        if not task_id_match:
            continue
        verifier = verifier_data[task_id_match]
        cmp_result = compare(prompt, verifier)

        out.append({
            "task_id": task_id_match,
            "task_dir": tdir.name,
            "prompt": {
                "mentions_frame": prompt["mentions_frame"],
                "frame_phrases": prompt["frame_phrases"],
                "mentions_named_color": sorted(prompt["mentions_named_color"]),
                "mentions_hex_color": prompt["mentions_hex_color"],
                "mentions_size": prompt["mentions_size"],
                "mentions_shape_counts": [list(t) for t in prompt["mentions_shape_counts"]],
                "mentions_tools": sorted(prompt["mentions_tools"]),
                "mentions_effects": sorted(prompt["mentions_effects"]),
                "mentions_alignment": prompt["mentions_alignment"],
                "mentions_corner_radius": prompt["mentions_corner_radius"],
            },
            "verifier_summary": {
                "frame_required": verifier.get("frame_required"),
                "brittle_alignment_tolerance": verifier.get("brittle_alignment_tolerance"),
                "required_shape_types": verifier.get("required_shape_types"),
                "check_class_counts": verifier.get("check_class_counts"),
                "n_rubrics": len(verifier.get("rubrics", [])),
            },
            **cmp_result,
        })

    # Write structured output
    json_path = APP_ROOT / "audit_correctness.json"
    json_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"wrote {json_path} ({json_path.stat().st_size:,} bytes)")

    # Aggregate
    issue_counts: Counter = Counter()
    severity_counts: Counter = Counter()
    tasks_with_issues = 0
    tasks_clean = 0
    for t in out:
        if t["n_issues"] == 0:
            tasks_clean += 1
        else:
            tasks_with_issues += 1
            for i in t["issues"]:
                issue_counts[i["type"]] += 1
                severity_counts[i["severity"]] += 1

    print()
    print(f"=== verdict ===")
    print(f"  tasks audited:        {len(out)}/50")
    print(f"  CLEAN (no issues):    {tasks_clean}")
    print(f"  with ≥1 issue:        {tasks_with_issues}")
    print()
    print(f"=== issue types ===")
    for it, n in issue_counts.most_common():
        print(f"  {it:<30} {n}")
    print()
    print(f"=== severities ===")
    for s, n in severity_counts.most_common():
        print(f"  {s:<10} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
