# Full Evaluation Summary

## 1. Conjecture Invalidation Experiments

| ID | Source | Status | Evaluated | Best violation score | Known CE checked | Known CE valid | Interpretation |
|---|---|---:|---:|---:|---|---|---|
| ANNOR-001 | Annor 2026 - A Note on Inequalities for Three Domination Parameters | no_counterexample_found | 200 | -1 | false | null | not refuted by limited search |
| GEN-001 | generated | no_counterexample_found | 200 | -1 | false | null | not refuted by limited search |
| GEN-002 | generated | no_counterexample_found | 200 | 0 | false | null | not refuted by limited search |
| GEN-003 | generated | no_counterexample_found | 200 | 0 | false | null | not refuted by limited search |
| GEN-004 | generated | no_counterexample_found | 200 | 0 | false | null | not refuted by limited search |
| GEN-005 | generated | no_counterexample_found | 200 | -0.21212 | false | null | not refuted by limited search |
| HDR-001 | HDR benchmark | no_counterexample_found | 200 | -0.06558 | true | true | refuted by verified known counterexample |

## 2. Lean Proof Checks

| File | Status | Contains sorry | Interpretation |
|---|---|---|---|
| lean_proofs/T1_basic.lean | lean_not_found | false | Lean is not installed or not available in PATH |

## 3. Interpretation

- no_counterexample_found does not prove a conjecture.
- A verified counterexample refutes a conjecture.
- Lean proof is accepted only if Lean compiles and the file contains no sorry.
- lean_not_found means Lean is not installed, not that the theorem is false.
