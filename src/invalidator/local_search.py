import random
import time
import networkx as nx

from src.graph_tools.io import write_graph6
from src.invalidator.scoring import score_graph
from src.common.verifier import verify_counterexample


def random_graph(max_order: int) -> nx.Graph:
    n = random.randint(4, max_order)
    p = random.uniform(0.1, 0.5)
    G = nx.gnp_random_graph(n, p)

    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        for i in range(len(components) - 1):
            u = random.choice(list(components[i]))
            v = random.choice(list(components[i + 1]))
            G.add_edge(u, v)

    return G


def mutate_graph(G: nx.Graph) -> nx.Graph:
    H = G.copy()
    nodes = list(H.nodes())

    if len(nodes) < 2:
        return H

    operation = random.choice(["add_edge", "remove_edge"])

    if operation == "add_edge":
        u, v = random.sample(nodes, 2)
        H.add_edge(u, v)

    elif operation == "remove_edge" and H.number_of_edges() > 0:
        edge = random.choice(list(H.edges()))
        H.remove_edge(*edge)

    return H


def invalidate(conjecture: dict) -> dict:
    params = conjecture.get("parameters", {})
    max_order = params.get("max_order", 30)
    iterations = params.get("iterations", 3000)
    timeout = params.get("timeout_seconds", 10)

    start = time.time()

    best_G = random_graph(max_order)
    best_score = score_graph(best_G, conjecture)

    for i in range(iterations):
        if time.time() - start > timeout:
            break

        candidate = mutate_graph(best_G)
        candidate_score = score_graph(candidate, conjecture)

        if candidate_score > best_score:
            best_G = candidate
            best_score = candidate_score

        if candidate_score > 0:
            g6 = write_graph6(candidate)
            verification = verify_counterexample(conjecture, g6)

            if verification["is_counterexample"]:
                return {
                    "status": "counterexample_found",
                    "conjecture_id": conjecture["id"],
                    "graph": {
                        "format": "graph6",
                        "value": g6
                    },
                    "verification": verification,
                    "search": {
                        "method": "local_search",
                        "time_seconds": round(time.time() - start, 4),
                        "iterations": i + 1,
                        "best_score": candidate_score
                    }
                }

    return {
        "status": "no_counterexample_found",
        "conjecture_id": conjecture["id"],
        "search": {
            "method": "local_search",
            "timeout_reached": time.time() - start >= timeout,
            "time_seconds": round(time.time() - start, 4),
            "iterations": i + 1,
            "best_score": best_score
        }
    }