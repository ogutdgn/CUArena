"""Generate delivery-1 — one markdown per task with prompt + verifier code.

Reads:
  cua-eval/figma_tasks_finished.csv      (the 50 prompts)
  test-verifier/tasks/task_NN_*.py       (the matching verifiers)

Writes:
  delivery-1/README.md
  delivery-1/task_NN.md               (one per task)
"""
from __future__ import annotations
import csv, glob, os, sys


CSV_PATH = "cua-eval/figma_tasks_finished.csv"
TASKS_DIR = "test-verifier/tasks"
OUT_DIR = "delivery-1"


def find_verifier(n: int) -> str | None:
    nn = f"{n:02d}"
    matches = sorted(glob.glob(f"{TASKS_DIR}/task_{nn}_*.py"))
    if matches:
        return matches[0]
    return None


def main() -> None:
    if not os.path.exists(CSV_PATH):
        sys.exit(f"missing {CSV_PATH}")
    os.makedirs(OUT_DIR, exist_ok=True)

    with open(CSV_PATH, newline="") as f:
        rows = list(csv.reader(f))
    data = rows[1:]

    readme_lines = [
        "# Delivery 1 — Figma CUA Eval (50 tasks)",
        "",
        "Per-task package: each `task_NN.md` below contains the full prompt",
        "(thorough description, simplified prompt, step-by-step) and the",
        "verifier code that scores agent runs.",
        "",
        "| # | Difficulty | Time | Task |",
        "|---|---|---|---|",
    ]

    for i, row in enumerate(data, start=1):
        difficulty, thorough, simplified, time_min, steps = row
        v_path = find_verifier(i)
        out_path = f"{OUT_DIR}/task_{i:02d}.md"

        md = [
            f"# Task {i} — {simplified}",
            "",
            f"**Difficulty:** {difficulty}  •  **Time horizon:** {time_min} min",
            "",
            "## Thorough description",
            "",
            thorough,
            "",
            "## Simplified prompt",
            "",
            f"> {simplified}",
            "",
            "## Step-by-step",
            "",
            steps,
            "",
            "## Verifier",
            "",
        ]
        if v_path:
            md.append(f"File: `{v_path}`")
            md.append("")
            md.append("```python")
            with open(v_path) as vf:
                md.append(vf.read().rstrip())
            md.append("```")
        else:
            md.append("_(no verifier file found)_")
        md.append("")

        with open(out_path, "w") as f:
            f.write("\n".join(md))

        readme_lines.append(
            f"| {i:02d} | {difficulty} | {time_min} min | [{simplified}](task_{i:02d}.md) |"
        )

    with open(f"{OUT_DIR}/README.md", "w") as f:
        f.write("\n".join(readme_lines) + "\n")

    print(f"wrote {len(data)} task files + README to {OUT_DIR}/")


if __name__ == "__main__":
    main()
