import json
import random
import time
from typing import Callable

import networkx as nx

from tools.load_conjecture import load_conjecture
from tools.logging_utils import log_call
from tools.verifier import verify_conjecture


def random_connected_graph(n: int, edge_probability: float, seed=None) -> nx.Graph:
    rng = random.Random(seed)

    for _ in range(100):
        G = nx.gnp_random_graph(n, edge_probability, seed=rng.randint(0, 10**9))

        if nx.is_connected(G) and all(G.degree(v) > 0 for v in G.nodes):
            return G

    return nx.path_graph(n)


def dense_connected_graph(n: int, rng: random.Random) -> nx.Graph:
    G = nx.complete_graph(n)
    nodes = list(G.nodes)
    rng.shuffle(nodes)
    for i in range(0, n - 1, 2):
        G.remove_edge(nodes[i], nodes[i + 1])
    return G


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


def _score_graph(conjecture: dict, G: nx.Graph) -> tuple[float | None, dict | None]:
    try:
        result = verify_conjecture(conjecture, G)
    except Exception:
        return None, None

    if not result["valid_graph_class"]:
        return None, result

    score = compute_violation_score(
        result["left_value"],
        result["relation"],
        result["right_value"],
    )
    return score, result


def _candidate_order(best_result: dict | None) -> int | None:
    if not best_result:
        return None
    graph = best_result.get("graph") or {}
    return graph.get("order")


def _finish_result(
    status: str,
    method: str,
    start: float,
    iterations: int,
    best_violation_score: float | None,
    result: dict | None = None,
    best_result: dict | None = None,
) -> dict:
    output = {
        "status": status,
        "method": method,
        "evaluated": iterations,
        "iterations": iterations,
        "time_seconds": round(time.time() - start, 3),
        "best_gap": best_violation_score,
        "best_violation_score": best_violation_score,
    }
    if result is not None:
        output["result"] = result
        output["counterexample_graph6"] = result["graph"]["graph6"]
    if best_result is not None:
        output["best_result"] = best_result
        output["best_candidate_order"] = _candidate_order(best_result)
    return output


def random_search(conjecture: dict, verbose: bool = False) -> dict:
    params = conjecture["parameters"]

    min_order = params.get("min_order", 2)
    max_order = params.get("max_order", 30)
    timeout_seconds = params.get("timeout_seconds", 60)
    seed = params.get("seed", 42)

    max_evaluations = params.get("max_evaluations", 5000)

    rng = random.Random(seed)
    start = time.time()

    evaluated = 0
    best_result = None
    best_violation_score = None

    while time.time() - start < timeout_seconds and evaluated < max_evaluations:
        n = rng.randint(min_order, max_order)
        p = rng.uniform(0.25, 0.75)

        G = random_connected_graph(n, p, seed=rng.randint(0, 10**9))

        evaluated += 1
        violation_score, result = _score_graph(conjecture, G)

        if result is None or violation_score is None:
            continue

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
            return _finish_result(
                "counterexample_found",
                "random_search",
                start,
                evaluated,
                best_violation_score,
                result=result,
            )

    return _finish_result(
        "no_counterexample_found",
        "random_search",
        start,
        evaluated,
        best_violation_score,
        best_result=best_result,
    )


def _connected_isolate_free(G: nx.Graph) -> bool:
    return G.number_of_nodes() > 0 and nx.is_connected(G) and all(deg > 0 for _, deg in G.degree)


def _random_neighbor(G: nx.Graph, rng: random.Random, min_order: int, max_order: int) -> nx.Graph:
    H = G.copy()
    moves: list[Callable[[], nx.Graph | None]] = []

    def add_edge() -> nx.Graph | None:
        non_edges = list(nx.non_edges(H))
        if not non_edges:
            return None
        u, v = rng.choice(non_edges)
        J = H.copy()
        J.add_edge(u, v)
        return J

    def remove_edge() -> nx.Graph | None:
        if H.number_of_edges() == 0:
            return None
        u, v = rng.choice(list(H.edges))
        J = H.copy()
        J.remove_edge(u, v)
        return J if _connected_isolate_free(J) else None

    def rewire_edge() -> nx.Graph | None:
        if H.number_of_edges() == 0:
            return None
        u, v = rng.choice(list(H.edges))
        nodes = list(H.nodes)
        rng.shuffle(nodes)
        for a in (u, v):
            for b in nodes:
                if a != b and not H.has_edge(a, b):
                    J = H.copy()
                    J.remove_edge(u, v)
                    J.add_edge(a, b)
                    return J if _connected_isolate_free(J) else None
        return None

    def add_vertex() -> nx.Graph | None:
        if H.number_of_nodes() >= max_order:
            return None
        J = H.copy()
        new_node = max(J.nodes, default=-1) + 1
        J.add_node(new_node)
        nodes = list(H.nodes)
        k = rng.randint(1, min(4, len(nodes)))
        J.add_edges_from((new_node, v) for v in rng.sample(nodes, k))
        return J

    def remove_low_degree_vertex() -> nx.Graph | None:
        if H.number_of_nodes() <= min_order:
            return None
        min_degree = min(dict(H.degree).values())
        candidates = [node for node, degree in H.degree if degree == min_degree]
        J = H.copy()
        J.remove_node(rng.choice(candidates))
        return J if _connected_isolate_free(J) else None

    moves.extend([add_edge, remove_edge, rewire_edge, add_vertex, remove_low_degree_vertex])
    rng.shuffle(moves)
    for move in moves:
        candidate = move()
        if candidate is not None:
            return nx.convert_node_labels_to_integers(candidate)
    return G.copy()


def local_search(conjecture: dict, verbose: bool = False) -> dict:
    params = conjecture["parameters"]
    min_order = params.get("min_order", 2)
    max_order = params.get("max_order", 30)
    timeout_seconds = params.get("timeout_seconds", 60)
    seed = params.get("seed", 42)
    restart_after = params.get("restart_after", 300)
    accept_worse_probability = params.get("accept_worse_probability", 0.1)

    rng = random.Random(seed)
    start = time.time()
    iterations = 0
    stagnant = 0
    best_result = None
    best_violation_score = None

    def restart_graph() -> nx.Graph:
        n = rng.randint(min_order, max_order)
        if rng.random() < 0.35 and n >= 12:
            return dense_connected_graph(n, rng)
        p = rng.uniform(0.25, 0.9)
        return random_connected_graph(n, p, seed=rng.randint(0, 10**9))

    current = restart_graph()
    current_score, current_result = _score_graph(conjecture, current)
    if current_score is None:
        current_score = float("-inf")

    while time.time() - start < timeout_seconds:
        iterations += 1
        candidate = _random_neighbor(current, rng, min_order, max_order)
        score, result = _score_graph(conjecture, candidate)
        if result is None or score is None:
            stagnant += 1
            continue

        if best_violation_score is None or score > best_violation_score:
            best_violation_score = score
            best_result = result
            stagnant = 0
        else:
            stagnant += 1

        if verbose:
            print(
                f"iterations={iterations}, n={candidate.number_of_nodes()}, "
                f"violation_score={score}, counterexample={result['is_counterexample']}"
            )

        if score > 0 and result["is_counterexample"]:
            return _finish_result(
                "counterexample_found",
                "local_search",
                start,
                iterations,
                best_violation_score,
                result=result,
            )

        if score > current_score or rng.random() < accept_worse_probability:
            current = candidate
            current_score = score
            current_result = result

        if stagnant >= restart_after:
            current = restart_graph()
            current_score, current_result = _score_graph(conjecture, current)
            if current_score is None:
                current_score = float("-inf")
            stagnant = 0

    return _finish_result(
        "no_counterexample_found",
        "local_search",
        start,
        iterations,
        best_violation_score,
        best_result=best_result or current_result,
    )


def search_counterexample(conjecture: dict, verbose: bool = False, method: str = "local_search") -> dict:
    start = time.time()
    log_call("invalidator", "search_start", {"id": conjecture.get("id"), "method": method}, "started", 0)
    if method == "random_search":
        result = random_search(conjecture, verbose=verbose)
    elif method == "local_search":
        result = local_search(conjecture, verbose=verbose)
    else:
        raise ValueError(f"Unsupported search method: {method}")
    log_call(
        "invalidator",
        "search_end",
        {"id": conjecture.get("id"), "method": method},
        f"{result.get('status')} best={result.get('best_violation_score')}",
        time.time() - start,
    )
    return result


if __name__ == "__main__":
    conjecture = load_conjecture("data/conjectures/annor/ANNOR-001.json")

    result = search_counterexample(conjecture)

    print("\nFinal result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
