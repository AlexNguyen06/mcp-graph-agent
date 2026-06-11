# MCP Graph Agent

Local graph-theory agent for the M1 internship project. The LLM is only an orchestrator: it must never decide mathematical truth. Counterexamples are accepted only after the independent verifier rebuilds the graph from `graph6` and recomputes the hypotheses, invariants, and inequality. Proofs are accepted only by Lean files that compile without `sorry`.

## Architecture

```text
Ollama agent
-> MCP client
-> MCP servers
-> independent tools: invalidator, verifier, generator, Lean prover
-> JSON result
```

Main components:

- `agent/agent_files.py`: Ollama tool-calling agent. MCP mode is the default; `--direct` keeps the old direct-import mode for debugging.
- `agent/mcp_client.py`: stdio MCP client that launches and lists tools from the four MCP servers.
- `mcp_servers/`: invalidator, graph tools, conjecture generator, and prover servers.
- `tools/search_annor.py`: `random_search` and `local_search` counterexample search.
- `tools/verifier.py`: LLM-free independent verifier and invariant computation.
- `lean_proofs/`: Lean 4 + Mathlib formalizations for T1 and T2.
- `logs/`: JSON-lines call journal, with generated `*.jsonl` files ignored by Git.

## Installation

```bash
cd /Users/nguyenquynh/mcp-graph-agent
pip install -r requirements.txt
```

Ollama must be installed. The default model is `gemma3:12b` as required by the subject, but any Ollama model with tool-calling support can be used:

```bash
python agent/agent_files.py --model gemma3:12b
python agent/agent_files.py --model llama3.1:8b
python agent/agent_files.py --direct --model gemma3:12b
```

## Example Prompts

```text
Utilise l’outil invalidator__invalidate_from_path avec le chemin data/conjectures/hdr_false/HDR-001.json et method local_search pour tester HDR-001.
```

```text
Utilise l’outil invalidator__verify_counterexample_from_path avec le chemin data/conjectures/hdr_false/HDR-014.json pour vérifier le contre-exemple connu.
```

`no_counterexample_found` is never a proof. It only means the configured search did not find a violating graph.

## Invalidation

`tools.search_annor` supports:

- `method="local_search"` by default, with connected graph moves: add edge, remove edge when still connected and isolate-free, rewire edge, add vertex, and remove low-degree vertex.
- `method="random_search"` for baseline random connected `G(n,p)` sampling.

Results include `method`, `time_seconds`, `iterations`, `best_violation_score`, and `counterexample_graph6` when a verified counterexample is found.

## Verifier

The verifier supports HDR invariants including `order`, `size`, `density`, `radius`, `diameter`, `min_degree`, `max_degree`, `avg_degree`, `triangles`, `clique_number`, `independence_number`, `vertex_cover_number`, `matching_number`, `node_connectivity`, `edge_connectivity`, `domination_number`, `total_domination_number`, and `connected_domination_number`.

Expression contexts include long names and short names such as `n`, `m`, `d`, `rad`, `diam`, `delta`, `Delta`, `avg`, `t`, `omega`, `alpha`, `tau`, `mu`, `kappa`, `kappa_prime`, and `gamma`.

Graph classes include `connected`, `connected_isolated_free`, `tree`, `bipartite`, `planar`, and `claw_free`.

## HDR Benchmark

Verified false conjectures live in `data/conjectures/hdr_false/`: `HDR-001`, `HDR-003`, `HDR-005`, and `HDR-014`.

```bash
python -m tools.verify_benchmark
python -m tests.test_benchmark_known_counterexamples
python -m tests.test_local_search_hdr001
```

`tools.verify_benchmark` exits non-zero if any known `graph6` counterexample fails independent verification.

## Lean

The toy proof was removed. Current files:

- `lean_proofs/T1_degree_sum.lean`: finite simple graph degree-sum formula.
- `lean_proofs/T2_even_odd_vertices.lean`: the number of odd-degree vertices is even.

Local build:

```bash
elan toolchain install stable
lake update
lake exe cache get
lake build
python -m tests.test_lean_prover
```

Without Lean on `PATH`, the prover returns `lean_not_found`.

## Full Evaluation

```bash
python -m tools.run_full_evaluation
```

The Markdown table for false conjectures uses the required columns: `ID`, `Statut`, `Méthode`, `Temps (s)`, `Ordre du graphe`, `Commentaire`. Lean files are reported separately with `ID`, `Énoncé`, `Statut Lean`, and `Difficulté rencontrée`.

## Docker

```bash
docker compose build
docker compose run --rm verify-benchmark
docker compose run --rm full-evaluation
docker compose run --rm mcp-invalidator
docker compose run --rm mcp-graph-tools
docker compose run --rm mcp-generator
docker compose run --rm mcp-prover
```

`mcp-prover` uses `mcp-prover/Dockerfile`, which installs elan, Lean 4, and fetches the Mathlib cache. This image is heavier than the Python-only services, but it lets the prover return real `proved` or `failed` statuses inside Docker instead of `lean_not_found`.

## Tests

```bash
python -m tests.test_mcp_servers_import
python -m tests.test_conjecture_generator
python -m tests.test_lean_prover
python -m tools.verify_benchmark
python -m tests.test_local_search_hdr001
python -m tools.run_full_evaluation
```
