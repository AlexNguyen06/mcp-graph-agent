import json
from pathlib import Path

import networkx as nx

from tools.load_conjecture import load_conjecture
from tools.search_annor import search_counterexample

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def invalidate_conjecture(conjecture_path: str) -> dict:
    conjecture = load_conjecture(conjecture_path)

    search_result = search_counterexample(conjecture)

    output = {
        "conjecture_id": conjecture["id"],
        "status": search_result["status"],
        "source": conjecture.get("source"),
        "graph_class": conjecture["graph_class"],
        "search": {
            "method": "random_search",
            "evaluated": search_result["evaluated"],
            "time_seconds": search_result["time_seconds"]
        }
    }

    if "best_gap" in search_result:
        output["best_gap"] = search_result.get("best_gap")

    if "best_violation_score" in search_result:
        output["best_violation_score"] = search_result.get("best_violation_score")

    if search_result["status"] == "counterexample_found":
        result = search_result["result"]

        output["graph"] = result["graph"]
        output["verification"] = {
            "valid_graph_class": result["valid_graph_class"],
            "conjecture_satisfied": result["conjecture_satisfied"],
            "is_counterexample": result["is_counterexample"],
            "left_value": result["left_value"],
            "relation": result["relation"],
            "right_value": result["right_value"],
            "invariants": result["invariants"]
        }

    else:
        output["best_result"] = search_result.get("best_result")
        output["message"] = (
            "No counterexample was found within the search limits. "
            "This does not prove that the conjecture is true."
        )

    return output


def save_result(result: dict, output_path: str) -> None:
    path = PROJECT_ROOT / output_path
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    result = invalidate_conjecture("data/conjectures/annor/ANNOR-001.json")

    print(json.dumps(result, indent=2, ensure_ascii=False))

    save_result(result, "data/results/ANNOR-001_result.json")
    print("\nResult saved to data/results/ANNOR-001_result.json")
