# Demo Scenario - MCP Graph Agent

## 1. Objective

The demo shows that the LLM agent orchestrates independent graph tools through MCP. It does not prove or refute conjectures by itself.

## 2. Start the Agent

```bash
cd /Users/nguyenquynh/mcp-graph-agent
python agent/agent_files.py --model gemma3:12b
```

Any Ollama model with tool-calling support can be selected with `--model`. Use `--direct` only for debugging the old direct-import path.

## 3. Test HDR-001 With Local Search

Prompt:

```text
Utilise l’outil invalidator__invalidate_from_path avec conjecture_path data/conjectures/hdr_false/HDR-001.json et method local_search.
```

Expected interpretation:

- `counterexample_found`
- the result contains a `graph6` counterexample
- the independent verifier confirms `valid_graph_class = True` and `is_counterexample = True`

## 4. Compare Random Search

Prompt:

```text
Utilise l’outil invalidator__invalidate_from_path avec conjecture_path data/conjectures/hdr_false/HDR-001.json et method random_search.
```

Expected interpretation:

- random search is a baseline and may fail within limited time
- `no_counterexample_found` is not a mathematical proof

## 5. Verify Known Benchmark Counterexamples

```bash
python -m tools.verify_benchmark
```

The script checks `HDR-001`, `HDR-003`, `HDR-005`, and `HDR-014` by rebuilding each graph from `graph6`.

## 6. Run Full Evaluation

```bash
python -m tools.run_full_evaluation
```

Expected outputs:

- `data/results/full_evaluation_summary.json`
- `data/results/full_evaluation_summary.md`
- one false-conjecture row per method (`random_search`, `local_search`)
- one Lean table row per file in `lean_proofs/`

## 7. Oral Presentation Point

L’agent LLM sert d’orchestrateur. L’invalidateur propose des graphes candidats, le vérificateur recalcule les invariants et confirme les contre-exemples, et Lean compile les preuves formelles. Un échec de recherche ne prouve jamais qu’une conjecture est vraie.
