"""Generate delivery-1 — one folder per task containing the prompt + the
verifier script as separate files.

Reads:
  cua-eval/figma_tasks_finished.csv      (the 50 prompts)
  test-verifier/tasks/task_NN_*.py       (the matching verifiers)

Writes:
  delivery-1/README.md
  delivery-1/task_NN/prompt.md
  delivery-1/task_NN/verifier.py
"""
from __future__ import annotations
import csv, glob, os, shutil, sys


CSV_PATH = "cua-eval/figma_tasks_finished.csv"
TASKS_DIR = "test-verifier/tasks"
OUT_DIR = "delivery-1"


def find_verifier(n: int) -> str | None:
    nn = f"{n:02d}"
    matches = sorted(glob.glob(f"{TASKS_DIR}/task_{nn}_*.py"))
    return matches[0] if matches else None


def task_module_name(verifier_path: str) -> str:
    """test-verifier/tasks/task_01_house_task_comprehensive.py → task_01_house_task_comprehensive"""
    return os.path.splitext(os.path.basename(verifier_path))[0]


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
        "Per-task package: each `task_NN/` folder below contains the full",
        "prompt and the verifier script as separate files:",
        "",
        "```",
        "task_NN/",
        "  prompt.md     — difficulty, thorough description, simplified prompt, step-by-step",
        "  verifier.py   — the matching verifier from test-verifier/tasks/",
        "```",
        "",
        "## Running a verifier",
        "",
        "The verifier files in this delivery are READ-ONLY copies for review.",
        "To actually score an agent run, use the framework at `test-verifier/`:",
        "",
        "```bash",
        "# 1. Generate the agent log via the test-app (dev mode)",
        "cd test-app && npm run dev      # http://localhost:5173",
        "# (run the task in the browser, then export the log)",
        "python3 scripts/run_task.py --task <module_name>",
        "",
        "# 2. Or score an existing log directly",
        "cd test-verifier",
        "PYTHONPATH=. python3 run.py --task <module_name> --log logs/<log>.json",
        "",
        "# 3. Smoke-test every verifier against synthetic perfect/empty logs",
        "cd test-verifier",
        "PYTHONPATH=. python3 qa_verifiers.py",
        "```",
        "",
        "The `<module_name>` for each task is shown in the index table below",
        "(it matches the original filename in `test-verifier/tasks/`).",
        "",
        "## Index",
        "",
        "| # | Difficulty | Time | Task | Module |",
        "|---|---|---|---|---|",
    ]

    for i, row in enumerate(data, start=1):
        difficulty, thorough, simplified, time_min, steps = row
        v_path = find_verifier(i)
        folder = f"{OUT_DIR}/task_{i:02d}"
        os.makedirs(folder, exist_ok=True)

        # prompt.md (no verifier code embedded)
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
            "The verifier script for this task lives next to this file as `verifier.py`.",
            f"In the framework it's imported as `tasks.{task_module_name(v_path)}` (see `../README.md` for run commands).",
            "",
        ]
        with open(f"{folder}/prompt.md", "w") as f:
            f.write("\n".join(md))

        # verifier.py (copy)
        if v_path:
            shutil.copy(v_path, f"{folder}/verifier.py")
            module_name = task_module_name(v_path)
        else:
            module_name = "—"

        readme_lines.append(
            f"| {i:02d} | {difficulty} | {time_min} min | [{simplified}](task_{i:02d}/prompt.md) | `{module_name}` |"
        )

    with open(f"{OUT_DIR}/README.md", "w") as f:
        f.write("\n".join(readme_lines) + "\n")

    print(f"wrote {len(data)} task folders + README to {OUT_DIR}/")


if __name__ == "__main__":
    main()
