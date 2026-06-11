import json
import copy
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.conjecture_generator import generate_basic_conjectures
from tools.invalidator_tool import invalidate_conjecture
from tools.search_annor import search_counterexample
from tools.lean_prover import check_lean_file, list_lean_proofs
from tools.load_conjecture import load_conjecture
from tools.verifier import verify_known_counterexample


CONJECTURES_DIR = PROJECT_ROOT / "data" / "conjectures"
RESULTS_DIR = PROJECT_ROOT / "data" / "results"
JSON_OUTPUT_PATH = RESULTS_DIR / "full_evaluation_summary.json"
MARKDOWN_OUTPUT_PATH = RESULTS_DIR / "full_evaluation_summary.md"
EVALUATION_TIMEOUT_SECONDS = 3
EVALUATION_MAX_EVALUATIONS = 150


def relative_project_path(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def has_known_counterexample(conjecture: dict) -> bool:
    known_counterexample = conjecture.get("known_counterexample") or {}
    return bool(known_counterexample.get("value"))


def format_markdown_value(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, float):
        return f"{value:.5f}".rstrip("0").rstrip(".")
    return str(value)


def interpretation_for_experiment(item: dict) -> str:
    if item.get("error"):
        return "error during evaluation"
    if item.get("invalidation_status") == "counterexample_found":
        return "contre-exemple vérifié indépendamment"
    if item.get("invalidation_status") == "no_counterexample_found":
        if item.get("known_counterexample_valid") is True:
            return "non réfutée par recherche limitée; contre-exemple connu vérifié"
        return "non réfutée par recherche limitée"
    if item.get("known_counterexample_valid") is True:
        return "contre-exemple connu vérifié indépendamment"
    return "unknown"


def interpretation_for_lean_check(item: dict) -> str:
    status = item.get("status")

    if status == "proved":
        return "Lean compiled without sorry"
    if status == "failed":
        return "Lean compilation failed"
    if status == "incomplete_proof":
        return "contains sorry, not accepted as complete proof"
    if status == "lean_not_found":
        return "Lean is not installed or not available in PATH"
    if item.get("error"):
        return "error during Lean check"
    return "unknown"


def summarize_conjecture(conjecture_path: Path) -> dict:
    relative_path = relative_project_path(conjecture_path)

    try:
        conjecture = load_conjecture(relative_path)
        method = getattr(summarize_conjecture, "method", "local_search")
        evaluation_conjecture = copy.deepcopy(conjecture)
        evaluation_conjecture.setdefault("parameters", {})
        evaluation_conjecture["parameters"]["timeout_seconds"] = EVALUATION_TIMEOUT_SECONDS
        evaluation_conjecture["parameters"]["max_evaluations"] = EVALUATION_MAX_EVALUATIONS
        search_result = search_counterexample(evaluation_conjecture, method=method)
        invalidation_result = {
            "status": search_result.get("status"),
            "search": {
                "method": search_result.get("method", method),
                "evaluated": search_result.get("evaluated"),
                "time_seconds": search_result.get("time_seconds"),
            },
            "best_gap": search_result.get("best_gap"),
            "best_violation_score": search_result.get("best_violation_score"),
            "best_result": search_result.get("best_result"),
            "best_candidate_order": search_result.get("best_candidate_order"),
        }
        if search_result.get("result"):
            invalidation_result["graph"] = search_result["result"].get("graph")

        known_checked = has_known_counterexample(conjecture)
        known_valid = None

        if known_checked:
            known_result = verify_known_counterexample(conjecture)
            known_valid = known_result.get("is_counterexample")

        return {
            "id": conjecture["id"],
            "source": conjecture.get("source"),
            "path": relative_path,
            "graph_class": conjecture.get("graph_class"),
            "invalidation_status": invalidation_result.get("status"),
            "method": invalidation_result.get("search", {}).get("method", method),
            "time_seconds": invalidation_result.get("search", {}).get("time_seconds"),
            "counterexample_order": (invalidation_result.get("graph") or {}).get("order"),
            "best_candidate_order": (
                (invalidation_result.get("best_result") or {}).get("graph", {}).get("order")
                or invalidation_result.get("best_candidate_order")
            ),
            "evaluated": invalidation_result.get("search", {}).get("evaluated"),
            "best_gap": invalidation_result.get("best_gap"),
            "best_violation_score": invalidation_result.get("best_violation_score"),
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


def run_generation(metadata: dict) -> None:
    try:
        generated = generate_basic_conjectures(limit=5)
        metadata["generated_conjectures"] = len(generated)
    except Exception as exc:
        metadata["generated_conjectures"] = 0
        metadata["generation_error"] = str(exc)


def run_invalidation_experiments() -> list[dict]:
    conjecture_files = sorted((CONJECTURES_DIR / "hdr_false").glob("*.json"))
    rows = []
    for path in conjecture_files:
        for method in ("random_search", "local_search"):
            summarize_conjecture.method = method
            rows.append(summarize_conjecture(path))
    return rows


def run_lean_proof_checks() -> list[dict]:
    checks = []

    try:
        proofs = list_lean_proofs()
    except Exception as exc:
        return [{
            "file": "lean_proofs",
            "error": str(exc)
        }]

    for proof in proofs:
        path = proof.get("path")
        try:
            result = check_lean_file(path)
            checks.append(result)
        except Exception as exc:
            checks.append({
                "file": path,
                "error": str(exc)
            })

    return checks


def render_markdown_summary(summary: dict) -> str:
    lines = [
        "# Full Evaluation Summary",
        "",
        "## 1. Conjecture Invalidation Experiments",
        "",
        "| ID | Statut | Méthode | Temps (s) | Ordre du graphe | Commentaire |",
        "|---|---|---|---:|---:|---|",
    ]

    for item in summary["invalidation_experiments"]:
        graph_order = item.get("counterexample_order") or item.get("best_candidate_order")
        lines.append(
            "| "
            f"{format_markdown_value(item.get('id'))} | "
            f"{format_markdown_value(item.get('invalidation_status', item.get('error', 'error')))} | "
            f"{format_markdown_value(item.get('method'))} | "
            f"{format_markdown_value(item.get('time_seconds'))} | "
            f"{format_markdown_value(graph_order)} | "
            f"{interpretation_for_experiment(item)} |"
        )

    lines.extend([
        "",
        "## 2. Lean Proof Checks",
        "",
        "| ID | Énoncé | Statut Lean | Difficulté rencontrée |",
        "|---|---|---|---|",
    ])

    for item in summary["lean_proof_checks"]:
        file_path = item.get("file", "")
        theorem_id = Path(file_path).stem.split("_")[0].upper() if file_path else "unknown"
        lines.append(
            "| "
            f"{format_markdown_value(theorem_id)} | "
            f"{format_markdown_value(file_path)} | "
            f"{format_markdown_value(item.get('status', item.get('error', 'error')))} | "
            f"{interpretation_for_lean_check(item)} |"
        )

    lines.extend([
        "",
        "## 3. Interpretation",
        "",
        "- no_counterexample_found does not prove a conjecture.",
        "- A verified counterexample refutes a conjecture.",
        "- Lean proof is accepted only if Lean compiles and the file contains no sorry.",
        "- lean_not_found means Lean is not installed, not that the theorem is false.",
        "",
    ])

    return "\n".join(lines)


def save_outputs(summary: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with JSON_OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    MARKDOWN_OUTPUT_PATH.write_text(render_markdown_summary(summary), encoding="utf-8")


def run_full_evaluation() -> dict:
    metadata = {}

    run_generation(metadata)
    invalidation_experiments = run_invalidation_experiments()
    lean_proof_checks = run_lean_proof_checks()

    metadata["total_conjectures_tested"] = len(invalidation_experiments)
    metadata["total_lean_files_checked"] = len(lean_proof_checks)

    summary = {
        "metadata": metadata,
        "invalidation_experiments": invalidation_experiments,
        "lean_proof_checks": lean_proof_checks
    }

    save_outputs(summary)

    return summary


if __name__ == "__main__":
    result = run_full_evaluation()
    print("Full evaluation completed.")
    print(f"Conjectures tested: {result['metadata']['total_conjectures_tested']}")
    print(f"Lean files checked: {result['metadata']['total_lean_files_checked']}")
    print(f"JSON saved to {relative_project_path(JSON_OUTPUT_PATH)}")
    print(f"Markdown saved to {relative_project_path(MARKDOWN_OUTPUT_PATH)}")
