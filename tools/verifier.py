import math
import itertools
import networkx as nx

from tools.annor_invariants import (
    is_connected_isolated_free,
    domination_number,
    total_domination_number,
    connected_domination_number
)


INVARIANT_ALIASES = {
    "n": "order",
    "m": "size",
    "d": "density",
    "rad": "radius",
    "diam": "diameter",
    "delta": "min_degree",
    "Delta": "max_degree",
    "avg": "avg_degree",
    "t": "triangles",
    "omega": "clique_number",
    "alpha": "independence_number",
    "tau": "vertex_cover_number",
    "mu": "matching_number",
    "kappa": "node_connectivity",
    "kappa_prime": "edge_connectivity",
    "gamma": "domination_number",
    "gamma_t": "total_domination_number",
    "gamma_c": "connected_domination_number",
}


def _normalize_required(required_invariants) -> set[str]:
    required = set(required_invariants or [
        "domination_number",
        "total_domination_number",
        "connected_domination_number",
    ])
    return {INVARIANT_ALIASES.get(name, name) for name in required}


def clique_number(G: nx.Graph) -> int:
    if G.number_of_nodes() == 0:
        return 0
    return max((len(clique) for clique in nx.find_cliques(G)), default=0)


def independence_number(G: nx.Graph) -> int:
    return clique_number(nx.complement(G))


def is_claw_free(G: nx.Graph) -> bool:
    for center in G.nodes:
        neighbors = list(G.neighbors(center))
        if len(neighbors) < 3:
            continue
        for triple in itertools.combinations(neighbors, 3):
            induced = G.subgraph(triple)
            if induced.number_of_edges() == 0:
                return False
    return True


def compute_invariants(G: nx.Graph, required_invariants=None) -> dict:
    required = _normalize_required(required_invariants)
    order = G.number_of_nodes()
    size = G.number_of_edges()
    degrees = dict(G.degree())

    values = {
        "order": order,
        "size": size,
    }

    if "domination_number" in required:
        values["domination_number"] = domination_number(G)

    if "total_domination_number" in required:
        values["total_domination_number"] = total_domination_number(G)

    if "connected_domination_number" in required:
        values["connected_domination_number"] = connected_domination_number(G)

    if "radius" in required:
        values["radius"] = nx.radius(G)

    if "density" in required:
        values["density"] = nx.density(G)

    if "diameter" in required:
        values["diameter"] = nx.diameter(G)

    if "min_degree" in required:
        values["min_degree"] = min(degrees.values(), default=0)

    if "max_degree" in required:
        values["max_degree"] = max(degrees.values(), default=0)

    if "avg_degree" in required:
        values["avg_degree"] = (2 * size / order) if order else 0

    if "triangles" in required:
        values["triangles"] = sum(nx.triangles(G).values()) // 3

    if "clique_number" in required:
        values["clique_number"] = clique_number(G)

    if "independence_number" in required:
        values["independence_number"] = independence_number(G)

    if "vertex_cover_number" in required:
        alpha = values.get("independence_number", independence_number(G))
        values["vertex_cover_number"] = order - alpha

    if "matching_number" in required:
        values["matching_number"] = len(nx.max_weight_matching(G, maxcardinality=True))

    if "node_connectivity" in required:
        values["node_connectivity"] = nx.node_connectivity(G)

    if "edge_connectivity" in required:
        values["edge_connectivity"] = nx.edge_connectivity(G)

    for short_name, long_name in INVARIANT_ALIASES.items():
        if long_name in values:
            values[short_name] = values[long_name]

    return values


def check_graph_class(G: nx.Graph, graph_class: str) -> bool:
    if graph_class == "connected_isolated_free":
        return is_connected_isolated_free(G)

    if graph_class == "connected":
        return nx.is_connected(G)

    if graph_class == "tree":
        return nx.is_tree(G)

    if graph_class == "bipartite":
        return nx.is_bipartite(G)

    if graph_class == "planar":
        return nx.check_planarity(G)[0]

    if graph_class == "claw_free":
        return is_claw_free(G)

    raise ValueError(f"Unsupported graph class: {graph_class}")


def evaluate_expression(expression: str, values: dict):
    allowed_functions = {
        "floor": math.floor,
        "ceil": math.ceil,
        "sqrt": math.sqrt
    }

    safe_context = {}
    safe_context.update(allowed_functions)
    safe_context.update(values)

    expression = expression.replace("^", "**")

    return eval(expression, {"__builtins__": {}}, safe_context)


def compare(left_value, relation: str, right_value) -> bool:
    if relation == ">=":
        return left_value >= right_value
    if relation == "<=":
        return left_value <= right_value
    if relation == ">":
        return left_value > right_value
    if relation == "<":
        return left_value < right_value
    if relation == "==":
        return left_value == right_value

    raise ValueError(f"Unsupported relation: {relation}")


def verify_conjecture(conjecture: dict, G: nx.Graph) -> dict:
    graph_class = conjecture["graph_class"]

    valid_graph_class = check_graph_class(G, graph_class)

    if not valid_graph_class:
        return {
            "conjecture_id": conjecture["id"],
            "valid_graph_class": False,
            "message": f"Graph does not satisfy graph_class={graph_class}",
            "is_counterexample": False
        }

    required_invariants = conjecture.get("invariants")
    values = compute_invariants(G, required_invariants)

    left_expression = conjecture["left_expression"]
    right_expression = conjecture["right_expression"]
    relation = conjecture["relation"]

    left_value = evaluate_expression(left_expression, values)
    right_value = evaluate_expression(right_expression, values)

    conjecture_satisfied = compare(left_value, relation, right_value)

    return {
        "conjecture_id": conjecture["id"],
        "valid_graph_class": True,
        "graph": {
            "order": G.number_of_nodes(),
            "size": G.number_of_edges(),
            "graph6": nx.to_graph6_bytes(G, header=False).decode().strip()
        },
        "invariants": values,
        "left_expression": left_expression,
        "left_value": left_value,
        "relation": relation,
        "right_expression": right_expression,
        "right_value": right_value,
        "conjecture_satisfied": conjecture_satisfied,
        "is_counterexample": not conjecture_satisfied
    }


def verify_known_counterexample(conjecture: dict) -> dict:
    known_counterexample = conjecture.get("known_counterexample")

    if not known_counterexample or not known_counterexample.get("value"):
        return {
            "conjecture_id": conjecture["id"],
            "status": "no_known_counterexample",
            "message": "No known counterexample is provided in this conjecture file."
        }

    if known_counterexample.get("format") != "graph6":
        return {
            "conjecture_id": conjecture["id"],
            "status": "unsupported_counterexample_format",
            "error": f"Unsupported known counterexample format: {known_counterexample.get('format')}"
        }

    graph6_value = known_counterexample["value"]

    try:
        G = nx.from_graph6_bytes(graph6_value.encode())
    except Exception as exc:
        return {
            "conjecture_id": conjecture["id"],
            "status": "invalid_graph6",
            "error": str(exc)
        }

    return verify_conjecture(conjecture, G)
