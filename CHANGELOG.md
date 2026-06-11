# Changelog

## Internship Alignment Update

- Tache 1: replaced the fake Lean arithmetic proof with Mathlib graph formalizations for T1 degree sum and T2 parity of odd-degree vertices; added Lake setup and build notes.
- Tache 2: added `local_search` to the invalidator, raised default search limits, retained `random_search`, and verified HDR-001 counterexample discovery.
- Tache 3: extended the independent verifier with HDR invariants, short-name expression aliases, and graph classes including tree, bipartite, planar, and claw-free.
- Tache 4: integrated verified HDR false conjectures `HDR-001`, `HDR-003`, `HDR-005`, and `HDR-014`; added benchmark verification tests.
- Tache 5: added a real stdio MCP client for the agent and kept direct imports behind `--direct`.
- Tache 6: changed the default Ollama model to `gemma3:12b`, added `--model`, and removed Qwen-specific prompt conventions from docs.
- Tache 7: added a trivial-conjecture filter, false generated demo conjectures, and a generator-to-invalidator handoff tool.
- Tache 8: updated full evaluation Markdown/JSON summaries with the required French experiment tables and Lean table.
- Journalisation: added JSON-lines logging for MCP tool calls, invalidator search start/end, and agent dispatch.
- Docker: added `verify-benchmark` and an optional heavier Lean/Mathlib `mcp-prover` image.
