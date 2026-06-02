import json
import random
import time

import networkx as nx

from tools.load_conjecture import load_conjecture
from tools.verifier import verify_conjecture


def random_connected_graph(n: int, edge_probability: float, seed=None) -> nx.Graph:
    rng = random.Random(seed)

    for _ in range(100):
        G = nx.gnp_random_graph(n, edge_probability, seed=rng.randint(0, 10**9))

        if nx.is_connected(G) and all(G.degree(v) > 0 for v in G.nodes):
            return G

    return nx.path_graph(n)


def compute_violation_score(left_value, relation, right_value):
    if relation == ">=":
        return right_value - left_value
    if relation == "<=":
        return left_value - right_value
    if relation == ">":
        return right_value - left_value
    if relation == "<":
        return left_value - right_value
    if relation == "==":
        return abs(left_value - right_value)

    raise ValueError(f"Unsupported relation: {relation}")


def search_counterexample(conjecture: dict, verbose: bool = False) -> dict:
    params = conjecture["parameters"]

    min_order = params.get("min_order", 2)
    max_order = params.get("max_order", 8)
    timeout_seconds = params.get("timeout_seconds", 20)
    seed = params.get("seed", 42)

    max_evaluations = 200

    rng = random.Random(seed)
    start = time.time()

    evaluated = 0
    best_result = None
    best_violation_score = None

    while time.time() - start < timeout_seconds and evaluated < max_evaluations:
        n = rng.randint(min_order, max_order)
        p = rng.uniform(0.25, 0.75)

        G = random_connected_graph(n, p, seed=rng.randint(0, 10**9))

        try:
            result = verify_conjecture(conjecture, G)
        except Exception as e:
            continue

        evaluated += 1

        if not result["valid_graph_class"]:
            continue

        violation_score = compute_violation_score(
            result["left_value"],
            result["relation"],
            result["right_value"]
        )

        if best_violation_score is None or violation_score > best_violation_score:
            best_violation_score = violation_score
            best_result = result

        if verbose:
            print(
                f"evaluated={evaluated}, "
                f"n={G.number_of_nodes()}, "
                f"violation_score={violation_score}, "
                f"counterexample={result['is_counterexample']}"
            )

        if result["is_counterexample"]:
            return {
                "status": "counterexample_found",
                "evaluated": evaluated,
                "time_seconds": round(time.time() - start, 3),
                "best_gap": best_violation_score,
                "best_violation_score": best_violation_score,
                "result": result
            }

    return {
        "status": "no_counterexample_found",
        "evaluated": evaluated,
        "time_seconds": round(time.time() - start, 3),
        "best_gap": best_violation_score,
        "best_violation_score": best_violation_score,
        "best_result": best_result
    }


if __name__ == "__main__":
    conjecture = load_conjecture("data/conjectures/annor/ANNOR-001.json")

    result = search_counterexample(conjecture)

    print("\nFinal result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
