# Scientific Report - MCP Graph Agent

## 1. Introduction

The objective of the project is to build an AI-assisted research environment for graph theory conjectures. The LLM is not considered a mathematical source of truth. It acts as an orchestrator that calls independent tools, receives structured results, and explains them to the user.

## 2. Architecture

The global workflow is:

```text
User prompt
→ Local LLM agent
→ Tool call / MCP server
→ Invalidator, verifier, generator, prover
→ Structured JSON result
→ Agent explanation
```

Main components:

- `agent/agent_files.py`: local Ollama-based agent with tool calling.
- `tools/invalidator_tool.py`: launches a counterexample search for a conjecture JSON file.
- `tools/verifier.py`: independently checks graph class hypotheses, invariants, expressions, and relations.
- `tools/verify_counterexample_tool.py`: verifies a known graph6 counterexample stored in a conjecture file.
- `tools/conjecture_generator.py`: generates simple candidate conjectures in the common JSON format.
- `tools/lean_prover.py`: checks Lean 4 proof files and rejects files containing `sorry`.
- `tools/run_experiments.py`: runs invalidation experiments and exports JSON/Markdown summaries.
- `tools/run_full_evaluation.py`: runs the complete evaluation pipeline, including generated conjectures and Lean checks.
- `mcp_servers/`: contains MCP servers exposing invalidation, graph tools, conjecture generation, and Lean proof checking.

## 3. Conjecture JSON Format

All conjectures use a common JSON format:

- `id`: unique conjecture identifier.
- `source`: origin of the conjecture.
- `domain`: mathematical domain.
- `graph_class`: hypotheses on the graph class.
- `description`: human-readable statement.
- `left_expression`: left side of the inequality.
- `relation`: comparison operator.
- `right_expression`: right side of the inequality.
- `invariants`: graph invariants required to evaluate the conjecture.
- `parameters`: search parameters.
- `known_counterexample`: optional known graph6 counterexample.
- `status`: current status of the conjecture.

Examples:

- `ANNOR-001`: Annor domination conjecture using domination parameters.
- `HDR-001`: HDR benchmark false conjecture using density and radius.
- `GEN-001`: generated candidate stating that for every connected graph, `radius <= order - 1`.

## 4. Invalidator

The invalidator searches for graph candidates and tests whether they violate a conjecture. It generates connected random graphs, computes the requested invariants, evaluates the inequality, and returns a structured JSON result.

The main statuses are:

- `counterexample_found`: a graph violating the conjecture was found.
- `no_counterexample_found`: no counterexample was found within the configured limits.

Important: `no_counterexample_found` is not a proof. It only means that the search procedure did not find a counterexample in the explored graph space.

## 5. Independent Verifier

The verifier recomputes graph invariants independently and checks:

1. graph class hypotheses;
2. left expression;
3. right expression;
4. relation;
5. whether the graph is a counterexample.

HDR-001 example:

- graph6: `M~~~~zz|~^z~n~^~_`
- `valid_graph_class = True`
- `density = 0.9230769230769231`
- `right_value = 0.907340034257034`
- relation `<=`
- `conjecture_satisfied = False`
- `is_counterexample = True`

Conclusion: HDR-001 is refuted by a verified known counterexample.

## 6. Conjecture Generator

The generator creates simple candidate conjectures in JSON format.

Generated examples:

- `GEN-001`
- `GEN-002`
- `GEN-003`
- `GEN-004`
- `GEN-005`

These generated conjectures can then be passed to the invalidator.

## 7. Lean Prover

A minimal Lean prover module was added. It checks Lean files and returns:

- `proved`
- `failed`
- `incomplete_proof`
- `lean_not_found`

Files containing `sorry` are not accepted as complete proofs. If Lean is not installed, the system returns `lean_not_found` instead of crashing.

Current result: `lean_proofs/T1_basic.lean` returned `lean_not_found` in the current environment.

## 8. MCP Servers

The project includes MCP servers to separate the LLM agent from the mathematical tools.

Servers:

- `mcp_invalidator_server.py`
- `mcp_graph_tools_server.py`
- `mcp_conjecture_generator_server.py`
- `mcp_prover_server.py`

They expose tools for invalidation, graph invariant computation, conjecture generation, and Lean checking.

## 9. Docker and Reproducibility

Dockerfile and `docker-compose.yml` were added. The full evaluation can be run with:

```bash
python -m tools.run_full_evaluation
```

or:

```bash
docker compose run --rm full-evaluation
```

Both local Python and Docker execution were tested successfully.

## 10. Experimental Results

| ID | Source | Status | Evaluated | Best violation score | Known CE checked | Known CE valid | Interpretation |
|---|---|---:|---:|---:|---|---|---|
| ANNOR-001 | Annor 2026 - A Note on Inequalities for Three Domination Parameters | no_counterexample_found | 200 | -1 | false | null | not refuted by limited search |
| GEN-001 | generated | no_counterexample_found | 200 | -1 | false | null | not refuted by limited search |
| GEN-002 | generated | no_counterexample_found | 200 | 0 | false | null | not refuted by limited search |
| GEN-003 | generated | no_counterexample_found | 200 | 0 | false | null | not refuted by limited search |
| GEN-004 | generated | no_counterexample_found | 200 | 0 | false | null | not refuted by limited search |
| GEN-005 | generated | no_counterexample_found | 200 | -0.21212 | false | null | not refuted by limited search |
| HDR-001 | HDR benchmark | no_counterexample_found | 200 | -0.06558 | true | true | refuted by verified known counterexample |

Lean table:

| File | Status | Contains sorry | Interpretation |
|---|---|---|---|
| lean_proofs/T1_basic.lean | lean_not_found | false | Lean is not installed or not available in PATH |

## 11. Limitations

- The invalidator currently uses limited random/local search.
- `no_counterexample_found` does not prove truth.
- Lean is not installed in the current environment.
- Only a small subset of HDR benchmark was integrated.
- The generated conjectures are simple examples.

## 12. Future Work

- integrate more HDR conjectures;
- improve local search heuristics;
- install Lean 4 in Docker;
- add more true graph theory theorems in Lean;
- connect the local agent directly to MCP clients;
- improve conjecture generation and filtering.

## 13. Conclusion

The project provides a complete prototype of an AI-assisted graph conjecture environment. The LLM orchestrates tools but does not validate mathematics by itself. Counterexamples and proofs are handled by independent verifiers and provers.
