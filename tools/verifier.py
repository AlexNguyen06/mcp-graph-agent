import math
import networkx as nx

from tools.annor_invariants import (
    is_connected_isolated_free,
    domination_number,
    total_domination_number,
    connected_domination_number
)


def compute_invariants(G: nx.Graph, required_invariants=None) -> dict:
    required = set(required_invariants or [
        "domination_number",
        "total_domination_number",
        "connected_domination_number"
    ])

    values = {
        "order": G.number_of_nodes(),
        "size": G.number_of_edges()
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

    return values


def check_graph_class(G: nx.Graph, graph_class: str) -> bool:
    if graph_class == "connected_isolated_free":
        return is_connected_isolated_free(G)

    if graph_class == "connected":
        return nx.is_connected(G)

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
