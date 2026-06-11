import json
import random
from pathlib import Path

import networkx as nx

from tools.search_annor import compute_violation_score, random_connected_graph
from tools.verifier import verify_conjecture


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
        },
        {
            "id": "GEN-101",
            "source": "generated",
            "domain": "graph_theory",
            "graph_class": "connected",
            "description": "False demo: For every connected graph G, density <= 0.5.",
            "left_expression": "density",
            "relation": "<=",
            "right_expression": "0.5",
            "invariants": ["density"],
            "parameters": base_parameters,
            "known_counterexample": known_counterexample,
            "status": "candidate"
        },
        {
            "id": "GEN-102",
            "source": "generated",
            "domain": "graph_theory",
            "graph_class": "connected",
            "description": "False demo: For every connected graph G, size <= order.",
            "left_expression": "size",
            "relation": "<=",
            "right_expression": "order",
            "invariants": ["size", "order"],
            "parameters": base_parameters,
            "known_counterexample": known_counterexample,
            "status": "candidate"
        },
        {
            "id": "GEN-103",
            "source": "generated",
            "domain": "graph_theory",
            "graph_class": "connected",
            "description": "False demo: For every connected graph G, radius >= 2.",
            "left_expression": "radius",
            "relation": ">=",
            "right_expression": "2",
            "invariants": ["radius"],
            "parameters": base_parameters,
            "known_counterexample": known_counterexample,
            "status": "candidate"
        }
    ]


def is_trivial(conjecture: dict, sample_size: int = 50) -> tuple[bool, str]:
    structural_trivialities = {
        ("density", "<=", "1"): "density is always at most 1",
        ("density", ">=", "0"): "density is always non-negative",
        ("size", "<=", "order*(order-1)/2"): "simple graphs have at most n(n-1)/2 edges",
        ("radius", "<=", "order - 1"): "connected graph radius is bounded by order - 1",
        ("radius", ">=", "1"): "nontrivial connected graph radius is at least 1",
    }
    key = (
        conjecture.get("left_expression", "").replace(" ", ""),
        conjecture.get("relation"),
        conjecture.get("right_expression", "").replace(" ", ""),
    )
    normalized = {
        (left.replace(" ", ""), rel, right.replace(" ", "")): reason
        for (left, rel, right), reason in structural_trivialities.items()
    }

    rng = random.Random(conjecture.get("parameters", {}).get("seed", 42))
    epsilon = 1e-9
    max_score = float("-inf")
    params = conjecture.get("parameters", {})
    min_order = params.get("min_order", 3)
    max_order = min(params.get("max_order", 12), 30)

    for _ in range(sample_size):
        n = rng.randint(min_order, max_order)
        p = rng.uniform(0.1, 0.95)
        G = random_connected_graph(n, p, seed=rng.randint(0, 10**9))
        result = verify_conjecture(conjecture, G)
        score = compute_violation_score(result["left_value"], result["relation"], result["right_value"])
        max_score = max(max_score, score)

    if key in normalized and max_score <= epsilon:
        return True, normalized[key]
    return False, f"sample max violation score={max_score:.6g}"


def generate_basic_conjectures(
    output_dir: str = "data/conjectures/generated",
    limit: int = 5,
    filter_trivial: bool = True,
) -> list[dict]:
    output_path = PROJECT_ROOT / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    conjectures = generated_conjecture_templates()[:limit]

    for conjecture in conjectures:
        if filter_trivial:
            trivial, reason = is_trivial(conjecture)
            conjecture["trivial_filter"] = {"is_trivial": trivial, "reason": reason}
            if trivial:
                conjecture["status"] = "trivial"
        file_path = output_path / f"{conjecture['id']}.json"
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(conjecture, f, indent=2, ensure_ascii=False)

    return conjectures


def submit_to_invalidator(conjecture_path: str, method: str = "local_search") -> dict:
    from tools.invalidator_tool import invalidate_conjecture

    return invalidate_conjecture(conjecture_path, method=method)


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
