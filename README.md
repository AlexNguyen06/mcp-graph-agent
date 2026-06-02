# MCP Graph Agent

## Objective

This project implements a local LLM agent that orchestrates graph-theory tools through a tool-calling architecture. The LLM is not considered a mathematical source of truth. It only coordinates independent tools that search for counterexamples and verify results.

## Architecture

```text
User prompt
→ Local LLM agent
→ Tool call
→ Invalidator / Verifier
→ JSON result
→ Agent explanation
```

Main components:

- `agent/agent_files.py`: local LLM agent using Ollama tool calling
- `tools/invalidator_tool.py`: launches the counterexample search
- `tools/verifier.py`: independently checks hypotheses, invariants and inequalities
- `tools/search_annor.py`: random/local search engine for graph candidates
- `tools/verify_counterexample_tool.py`: verifies known graph6 counterexamples
- `tools/run_experiments.py`: runs experiments and exports summary results
- `data/conjectures/`: stores conjectures in JSON format
- `data/results/`: stores experiment outputs

## Supported conjectures

| ID | Source | Status |
|---|---|---|
| ANNOR-001 | Annor 2026 domination conjecture | no counterexample found by limited search |
| HDR-001 | HDR benchmark false conjecture | known graph6 counterexample verified |

## Installation

```bash
cd /Users/nguyenquynh/mcp-graph-agent
pip install -r requirements.txt
```

Ollama must be installed, and a local model such as `qwen3:8b` must be available.

## Run the local agent

```bash
python agent/agent_files.py
```

## Example prompts

1. Test ANNOR-001:

```text
Utilise l’outil invalidate_from_path avec le chemin data/conjectures/annor/ANNOR-001.json pour tester la conjecture. /no_think
```

2. Test HDR-001 with random invalidation:

```text
Utilise l’outil invalidate_from_path avec le chemin data/conjectures/hdr_false/HDR-001.json pour tester la conjecture HDR-001. /no_think
```

3. Verify known HDR-001 counterexample:

```text
Utilise l’outil verify_counterexample_from_path avec le chemin data/conjectures/hdr_false/HDR-001.json pour vérifier le contre-exemple connu. /no_think
```

## Run experiments

```bash
python -m tools.run_experiments
```

This creates:

```text
data/results/experiments_summary.json
data/results/experiments_summary.md
```

## Test commands

```bash
python -m tests.test_mcp_servers_import
python -m tests.test_conjecture_generator
python -m tests.test_lean_prover
python -m tools.run_experiments
```

## Docker

```bash
docker compose build
docker compose run --rm experiments
docker compose run --rm mcp-invalidator
docker compose run --rm mcp-graph-tools
docker compose run --rm mcp-generator
docker compose run --rm mcp-prover
```

- `experiments` runs the full experiment summary.
- MCP services stay open because they wait for stdio input.
- The prover may return `lean_not_found` if Lean 4 is not installed inside the container.

## Full evaluation

```bash
python -m tools.run_full_evaluation
docker compose run --rm full-evaluation
```

The full evaluation generates candidate conjectures, runs invalidation experiments, checks Lean proof files, and writes:

```text
data/results/full_evaluation_summary.json
data/results/full_evaluation_summary.md
```

## MCP Servers

- `mcp_servers/mcp_invalidator_server.py` exposes invalidation and known counterexample verification.
- `mcp_servers/mcp_graph_tools_server.py` exposes graph6 parsing and invariant computation.
- These servers separate the LLM agent from mathematical tools.

## MCP Conjecture Generator

The generator creates simple candidate conjectures in the common JSON format. These candidates can then be tested by the invalidator. This demonstrates the generation → invalidation workflow required by the project.

```bash
python -m tests.test_conjecture_generator
python -m mcp_servers.mcp_conjecture_generator_server
```

The MCP server stays open waiting for stdio input, which is normal.

## MCP Prover Server

The prover server checks Lean 4 files. It does not accept proofs containing `sorry` as complete proofs. It returns structured JSON with status `proved`, `failed`, `incomplete_proof`, or `lean_not_found`.

```bash
python -m tools.lean_prover
python -m tests.test_lean_prover
python -m mcp_servers.mcp_prover_server
```

Lean 4 must be installed separately. If Lean 4 is not installed, the tool returns `lean_not_found` instead of crashing. The MCP server stays open waiting for stdio input, which is normal.

## Current experimental results

| Conjecture | Search result | Known counterexample verified | Interpretation |
|---|---|---|---|
| ANNOR-001 | no_counterexample_found | not provided | not refuted by limited search |
| HDR-001 | no_counterexample_found by random search | true | refuted by verified graph6 counterexample |

## Important interpretation

- `no_counterexample_found` does not prove the conjecture.
- It only means the search did not find a counterexample within the configured limits.
- A verified counterexample must satisfy the graph class hypotheses and violate the conjecture inequality.
- For HDR-001, the random search did not find a counterexample in 200 evaluations, but the known graph6 counterexample was independently verified.

## Reproducibility

- Conjectures are stored as JSON.
- Results are stored as JSON/Markdown.
- Each tool returns structured output.
- The verifier is independent from the LLM response.
