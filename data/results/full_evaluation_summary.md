# Full Evaluation Summary

## 1. Conjecture Invalidation Experiments

| ID | Statut | Méthode | Temps (s) | Ordre du graphe | Commentaire |
|---|---|---|---:|---:|---|
| HDR-001 | no_counterexample_found | random_search | 0.056 | 7 | non réfutée par recherche limitée; contre-exemple connu vérifié |
| HDR-001 | counterexample_found | local_search | 0.002 | 26 | contre-exemple vérifié indépendamment |
| HDR-003 | no_counterexample_found | random_search | 0.573 | 8 | non réfutée par recherche limitée; contre-exemple connu vérifié |
| HDR-003 | no_counterexample_found | local_search | 3.003 | 10 | non réfutée par recherche limitée; contre-exemple connu vérifié |
| HDR-005 | no_counterexample_found | random_search | 0.034 | 7 | non réfutée par recherche limitée; contre-exemple connu vérifié |
| HDR-005 | no_counterexample_found | local_search | 3.001 | 9 | non réfutée par recherche limitée; contre-exemple connu vérifié |
| HDR-014 | no_counterexample_found | random_search | 0.553 | 10 | non réfutée par recherche limitée; contre-exemple connu vérifié |
| HDR-014 | no_counterexample_found | local_search | 3 | 14 | non réfutée par recherche limitée; contre-exemple connu vérifié |

## 2. Lean Proof Checks

| ID | Énoncé | Statut Lean | Difficulté rencontrée |
|---|---|---|---|
| T1 | lean_proofs/T1_degree_sum.lean | lean_not_found | Lean is not installed or not available in PATH |
| T2 | lean_proofs/T2_even_odd_vertices.lean | lean_not_found | Lean is not installed or not available in PATH |

## 3. Interpretation

- no_counterexample_found does not prove a conjecture.
- A verified counterexample refutes a conjecture.
- Lean proof is accepted only if Lean compiles and the file contains no sorry.
- lean_not_found means Lean is not installed, not that the theorem is false.
