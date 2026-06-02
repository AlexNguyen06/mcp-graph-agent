# Demo Scenario - MCP Graph Agent

## 1. Objective

This project implements a local LLM agent that orchestrates graph conjecture tools. The LLM does not prove mathematical truth by itself. It calls independent tools:

- an invalidator that searches for counterexamples;
- a verifier that checks whether a graph satisfies the hypotheses and violates the conjecture;
- an experiment runner that produces reproducible summaries.

## 2. Start the local agent

```bash
cd /Users/nguyenquynh/mcp-graph-agent
python agent/agent_files.py
```

## 3. Test ANNOR-001

Prompt:

```text
Utilise l’outil invalidate_from_path avec le chemin data/conjectures/annor/ANNOR-001.json pour tester la conjecture. /no_think
```

Expected interpretation:

- no_counterexample_found
- 200 graphs evaluated
- this is not a proof
- the conjecture is not refuted by this limited search

## 4. Test HDR-001 with random invalidation

Prompt:

```text
Utilise l’outil invalidate_from_path avec le chemin data/conjectures/hdr_false/HDR-001.json pour tester la conjecture HDR-001. /no_think
```

Expected interpretation:

- random search may not find a counterexample
- best_violation_score <= 0 means the best tested graph still satisfies the conjecture
- no_counterexample_found is not a mathematical proof

## 5. Verify known HDR-001 counterexample

Prompt:

```text
Utilise l’outil verify_counterexample_from_path avec le chemin data/conjectures/hdr_false/HDR-001.json pour vérifier le contre-exemple connu. /no_think
```

Expected interpretation:

- valid_graph_class = True
- conjecture_satisfied = False
- is_counterexample = True
- therefore HDR-001 is refuted by the known graph6 counterexample

## 6. Run experiments

```bash
python -m tools.run_experiments
```

Expected output:

- experiments_summary.json is created
- experiments_summary.md is created if markdown export is enabled
- table contains ANNOR-001 and HDR-001

## 7. Key explanation for oral presentation

L’agent LLM sert d’orchestrateur. Il ne décide pas seul si une conjecture est vraie ou fausse. Il appelle des outils indépendants. L’invalidateur cherche automatiquement des graphes candidats. Le vérificateur recalcule les invariants du graphe et vérifie les hypothèses et l’inégalité. Si un graphe satisfait les hypothèses mais viole l’inégalité, alors c’est un contre-exemple. Si la recherche ne trouve rien, cela ne prouve pas la conjecture.

## 8. Current results

| Conjecture | Search result | Known counterexample verified | Interpretation |
|---|---|---|---|
| ANNOR-001 | no_counterexample_found | no known counterexample | not refuted by limited search |
| HDR-001 | no_counterexample_found by random search | true | refuted by verified graph6 counterexample |
