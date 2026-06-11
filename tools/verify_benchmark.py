import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.load_conjecture import load_conjecture
from tools.verifier import verify_known_counterexample


HDR_FALSE_DIR = PROJECT_ROOT / "data" / "conjectures" / "hdr_false"


def _value(result: dict, key: str):
    value = result.get(key)
    if isinstance(value, float):
        return f"{value:.6g}"
    return value


def verify_all_benchmark_counterexamples() -> list[dict]:
    rows = []
    for path in sorted(HDR_FALSE_DIR.glob("*.json")):
        relative_path = path.relative_to(PROJECT_ROOT).as_posix()
        conjecture = load_conjecture(relative_path)
        result = verify_known_counterexample(conjecture)
        rows.append({
            "id": conjecture.get("id"),
            "path": relative_path,
            "valid_graph_class": result.get("valid_graph_class"),
            "left_value": result.get("left_value"),
            "right_value": result.get("right_value"),
            "is_counterexample": result.get("is_counterexample"),
            "result": result,
        })
    return rows


def print_table(rows: list[dict]) -> None:
    print("| ID | valid_graph_class | left_value | right_value | is_counterexample |")
    print("|---|---|---:|---:|---|")
    for row in rows:
        print(
            "| "
            f"{row['id']} | "
            f"{row['valid_graph_class']} | "
            f"{_value(row, 'left_value')} | "
            f"{_value(row, 'right_value')} | "
            f"{row['is_counterexample']} |"
        )


def main() -> None:
    rows = verify_all_benchmark_counterexamples()
    print_table(rows)
    failures = [row for row in rows if row["is_counterexample"] is not True]
    if failures:
        print("\nBenchmark verification failed:")
        print(json.dumps(failures, indent=2, ensure_ascii=False))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
