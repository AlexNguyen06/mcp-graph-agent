import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_conjecture(path: str) -> dict:
    file_path = PROJECT_ROOT / path

    if not file_path.exists():
        raise FileNotFoundError(f"Conjecture file not found: {path}")

    with file_path.open("r", encoding="utf-8") as f:
        conjecture = json.load(f)

    required_fields = [
        "id",
        "domain",
        "graph_class",
        "left_expression",
        "relation",
        "right_expression",
        "invariants",
        "parameters",
        "status"
    ]

    missing = [field for field in required_fields if field not in conjecture]

    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    return conjecture


if __name__ == "__main__":
    conjecture = load_conjecture("data/conjectures/annor/ANNOR-001.json")
    print("Conjecture loaded successfully:")
    print(json.dumps(conjecture, indent=2, ensure_ascii=False))