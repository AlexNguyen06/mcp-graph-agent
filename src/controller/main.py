import csv
import json
from pathlib import Path

from src.common.verifier import verify_counterexample
from src.graph_tools.io import graph_order_from_g6
from src.invalidator.local_search import invalidate


CONJECTURE_DIR = Path("data/false_conjectures")
RESULT_DIR = Path("data/results")
CSV_PATH = RESULT_DIR / "experiments_false_conjectures.csv"


def load_conjecture(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(result: dict, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


def run_one_conjecture(path: Path) -> dict:
    conjecture = load_conjecture(path)

    print("=" * 60)
    print(f"Loaded conjecture: {conjecture['id']}")

    known = conjecture.get("known_counterexample")
    known_verification = None
    known_order = None

    if known:
        print("Checking known counterexample...")
        known_verification = verify_counterexample(conjecture, known["value"])
        known_order = graph_order_from_g6(known["value"])

        print(json.dumps(known_verification, indent=2, ensure_ascii=False))

    print("Running invalidator...")
    result = invalidate(conjecture)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    result_path = RESULT_DIR / f"{conjecture['id']}_result.json"
    save_json(result, result_path)

    found_order = ""

    if result["status"] == "counterexample_found":
        found_order = graph_order_from_g6(result["graph"]["value"])

    row = {
        "id": conjecture["id"],
        "known_counterexample_valid": known_verification["is_counterexample"] if known_verification else "",
        "known_graph_order": known_order if known_order is not None else "",
        "status": result["status"],
        "method": result["search"]["method"],
        "time_seconds": result["search"]["time_seconds"],
        "iterations": result["search"]["iterations"],
        "found_graph_order": found_order,
        "best_score": result["search"]["best_score"],
        "comment": "contre-exemple vérifié indépendamment"
        if result["status"] == "counterexample_found"
        else "aucun contre-exemple trouvé"
    }

    return row


def save_csv(rows: list[dict]):
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "id",
        "known_counterexample_valid",
        "known_graph_order",
        "status",
        "method",
        "time_seconds",
        "iterations",
        "found_graph_order",
        "best_score",
        "comment"
    ]

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    conjecture_files = sorted(CONJECTURE_DIR.glob("HDR-*.json"))

    if not conjecture_files:
        print("No conjecture files found.")
        return

    rows = []

    for path in conjecture_files:
        try:
            row = run_one_conjecture(path)
            rows.append(row)
        except Exception as e:
            print(f"ERROR with {path.name}: {e}")

            rows.append({
                "id": path.stem,
                "known_counterexample_valid": "",
                "known_graph_order": "",
                "status": "error",
                "method": "",
                "time_seconds": "",
                "iterations": "",
                "found_graph_order": "",
                "best_score": "",
                "comment": str(e)
            })

    save_csv(rows)

    print("=" * 60)
    print(f"Batch finished. CSV saved to: {CSV_PATH}")


if __name__ == "__main__":
    main()