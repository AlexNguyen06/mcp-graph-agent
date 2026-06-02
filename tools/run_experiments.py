import json
from pathlib import Path

from tools.invalidator_tool import invalidate_conjecture
from tools.load_conjecture import load_conjecture
from tools.verifier import verify_known_counterexample


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONJECTURES_DIR = PROJECT_ROOT / "data" / "conjectures"
SUMMARY_PATH = PROJECT_ROOT / "data" / "results" / "experiments_summary.json"
MARKDOWN_SUMMARY_PATH = PROJECT_ROOT / "data" / "results" / "experiments_summary.md"


def relative_project_path(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def has_known_counterexample(conjecture: dict) -> bool:
    known_counterexample = conjecture.get("known_counterexample") or {}
    return bool(known_counterexample.get("value"))


def summarize_conjecture(conjecture_path: Path) -> dict:
    relative_path = relative_project_path(conjecture_path)

    try:
        conjecture = load_conjecture(relative_path)
        invalidation_result = invalidate_conjecture(relative_path)

        known_checked = has_known_counterexample(conjecture)
        known_valid = None

        if known_checked:
            known_result = verify_known_counterexample(conjecture)
            known_valid = known_result.get("is_counterexample")

        return {
            "id": conjecture["id"],
            "source": conjecture.get("source"),
            "path": relative_path,
            "graph_class": conjecture["graph_class"],
            "invalidation_status": invalidation_result.get("status"),
            "evaluated": invalidation_result.get("search", {}).get("evaluated"),
            "best_gap": invalidation_result.get("best_gap"),
            "known_counterexample_checked": known_checked,
            "known_counterexample_valid": known_valid,
            "message": invalidation_result.get("message", "")
        }
    except Exception as exc:
        try:
            conjecture_id = load_conjecture(relative_path).get("id", "unknown")
        except Exception:
            conjecture_id = "unknown"

        return {
            "id": conjecture_id,
            "path": relative_path,
            "error": str(exc)
        }


def print_summary_table(summary: list[dict]) -> None:
    print("ID | invalidation_status | evaluated | best_gap | known_ce_valid")

    for item in summary:
        print(
            f"{item.get('id')} | "
            f"{item.get('invalidation_status', 'error')} | "
            f"{item.get('evaluated')} | "
            f"{item.get('best_gap')} | "
            f"{item.get('known_counterexample_valid')}"
        )


def format_markdown_value(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, float):
        return f"{value:.5f}".rstrip("0").rstrip(".")
    return str(value)


def render_markdown_summary(summary: list[dict]) -> str:
    lines = [
        "# Experiment Summary",
        "",
        "## Overview",
        "",
        "This file summarizes the results of the conjecture invalidation and counterexample verification experiments.",
        "",
        "## Results",
        "",
        "| ID | Source | Invalidation status | Evaluated graphs | Best violation score | Known counterexample checked | Known counterexample valid |",
        "|---|---|---|---:|---:|---|---|",
    ]

    for item in summary:
        lines.append(
            "| "
            f"{format_markdown_value(item.get('id'))} | "
            f"{format_markdown_value(item.get('source'))} | "
            f"{format_markdown_value(item.get('invalidation_status', item.get('error', 'error')))} | "
            f"{format_markdown_value(item.get('evaluated'))} | "
            f"{format_markdown_value(item.get('best_gap'))} | "
            f"{format_markdown_value(item.get('known_counterexample_checked'))} | "
            f"{format_markdown_value(item.get('known_counterexample_valid'))} |"
        )

    lines.extend([
        "",
        "## Interpretation",
        "",
        "- no_counterexample_found means that the search procedure did not find a counterexample within the configured limits.",
        "- This is not a mathematical proof of the conjecture.",
        "- known_counterexample_valid = true means that the independent verifier confirmed that the graph6 counterexample satisfies the hypotheses and violates the conjecture.",
        "- For HDR-001, the random invalidator did not find a counterexample in 200 evaluations, but the known graph6 counterexample was independently verified.",
        "",
    ])

    return "\n".join(lines)


def save_markdown_summary(summary: list[dict]) -> None:
    MARKDOWN_SUMMARY_PATH.write_text(render_markdown_summary(summary), encoding="utf-8")


def run_experiments() -> list[dict]:
    conjecture_files = sorted(CONJECTURES_DIR.rglob("*.json"))
    summary = [summarize_conjecture(path) for path in conjecture_files]

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY_PATH.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    save_markdown_summary(summary)

    return summary


if __name__ == "__main__":
    results = run_experiments()
    print_summary_table(results)
    print(f"\nSummary saved to {relative_project_path(SUMMARY_PATH)}")
    print(f"Markdown summary saved to {relative_project_path(MARKDOWN_SUMMARY_PATH)}")
