import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def generated_conjecture_templates() -> list[dict]:
    base_parameters = {
        "min_order": 3,
        "max_order": 12,
        "timeout_seconds": 10,
        "seed": 42
    }

    known_counterexample = {
        "format": "graph6",
        "value": None
    }

    return [
        {
            "id": "GEN-001",
            "source": "generated",
            "domain": "graph_theory",
            "graph_class": "connected",
            "description": "For every connected graph G, radius <= order - 1.",
            "left_expression": "radius",
            "relation": "<=",
            "right_expression": "order - 1",
            "invariants": ["radius", "order"],
            "parameters": base_parameters,
            "known_counterexample": known_counterexample,
            "status": "candidate"
        },
        {
            "id": "GEN-002",
            "source": "generated",
            "domain": "graph_theory",
            "graph_class": "connected",
            "description": "For every connected graph G, density <= 1.",
            "left_expression": "density",
            "relation": "<=",
            "right_expression": "1",
            "invariants": ["density"],
            "parameters": base_parameters,
            "known_counterexample": known_counterexample,
            "status": "candidate"
        },
        {
            "id": "GEN-003",
            "source": "generated",
            "domain": "graph_theory",
            "graph_class": "connected",
            "description": "For every connected graph G, size <= order*(order-1)/2.",
            "left_expression": "size",
            "relation": "<=",
            "right_expression": "order*(order-1)/2",
            "invariants": ["size", "order"],
            "parameters": base_parameters,
            "known_counterexample": known_counterexample,
            "status": "candidate"
        },
        {
            "id": "GEN-004",
            "source": "generated",
            "domain": "graph_theory",
            "graph_class": "connected",
            "description": "For every connected graph G, radius >= 1.",
            "left_expression": "radius",
            "relation": ">=",
            "right_expression": "1",
            "invariants": ["radius"],
            "parameters": base_parameters,
            "known_counterexample": known_counterexample,
            "status": "candidate"
        },
        {
            "id": "GEN-005",
            "source": "generated",
            "domain": "graph_theory",
            "graph_class": "connected",
            "description": "For every connected graph G, density >= 0.",
            "left_expression": "density",
            "relation": ">=",
            "right_expression": "0",
            "invariants": ["density"],
            "parameters": base_parameters,
            "known_counterexample": known_counterexample,
            "status": "candidate"
        }
    ]


def generate_basic_conjectures(
    output_dir: str = "data/conjectures/generated",
    limit: int = 5
) -> list[dict]:
    output_path = PROJECT_ROOT / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    conjectures = generated_conjecture_templates()[:limit]

    for conjecture in conjectures:
        file_path = output_path / f"{conjecture['id']}.json"
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(conjecture, f, indent=2, ensure_ascii=False)

    return conjectures


def load_generated_conjectures(
    output_dir: str = "data/conjectures/generated"
) -> list[dict]:
    output_path = PROJECT_ROOT / output_dir

    if not output_path.exists():
        return []

    conjectures = []

    for file_path in sorted(output_path.glob("*.json")):
        with file_path.open("r", encoding="utf-8") as f:
            conjectures.append(json.load(f))

    return conjectures


if __name__ == "__main__":
    generated = generate_basic_conjectures()
    print(json.dumps(generated, indent=2, ensure_ascii=False))
