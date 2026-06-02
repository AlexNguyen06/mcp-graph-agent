# Experiment Summary

## Overview

This file summarizes the results of the conjecture invalidation and counterexample verification experiments.

## Results

| ID | Source | Invalidation status | Evaluated graphs | Best violation score | Known counterexample checked | Known counterexample valid |
|---|---|---|---:|---:|---|---|
| ANNOR-001 | Annor 2026 - A Note on Inequalities for Three Domination Parameters | no_counterexample_found | 200 | -1 | false | null |
| GEN-001 | generated | no_counterexample_found | 200 | -1 | false | null |
| GEN-002 | generated | no_counterexample_found | 200 | 0 | false | null |
| GEN-003 | generated | no_counterexample_found | 200 | 0 | false | null |
| GEN-004 | generated | no_counterexample_found | 200 | 0 | false | null |
| GEN-005 | generated | no_counterexample_found | 200 | -0.21212 | false | null |
| HDR-001 | HDR benchmark | no_counterexample_found | 200 | -0.06558 | true | true |

## Interpretation

- no_counterexample_found means that the search procedure did not find a counterexample within the configured limits.
- This is not a mathematical proof of the conjecture.
- known_counterexample_valid = true means that the independent verifier confirmed that the graph6 counterexample satisfies the hypotheses and violates the conjecture.
- For HDR-001, the random invalidator did not find a counterexample in 200 evaluations, but the known graph6 counterexample was independently verified.
