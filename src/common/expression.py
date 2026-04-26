import sympy as sp


def normalize_expression(expr: str) -> str:
    return (
        expr.replace("^", "**")
        .replace("δ", "delta")
        .replace("∆", "Delta")
        .replace("ω", "omega")
        .replace("γ", "gamma")
        .replace("τ", "tau")
        .replace("µ", "mu")
        .replace("κ′", "edge_connectivity")
        .replace("κ", "kappa")
    )


def evaluate_expression(expr: str, variables: dict) -> float:
    expr = normalize_expression(expr)

    local_vars = {k: sp.Symbol(k) for k in variables.keys()}
    parsed = sp.sympify(expr, locals=local_vars)

    value = parsed.subs(variables)
    return float(value)