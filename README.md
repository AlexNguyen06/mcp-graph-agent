# MCP Graph Agent — AI System for Graph Conjecture Analysis

## Overview

This project implements an experimental AI-driven system for graph theory research.

Instead of relying on a language model as a source of truth, the system follows a **tool-based architecture**:

- The LLM acts as an orchestrator
- Mathematical validity is ensured by independent modules

The system can:
- Validate conjectures
- Search for counterexamples
- Attempt formal verification (Lean)
- Ensure correctness via independent checks

---

## Key Idea

Traditional LLMs often hallucinate in mathematical reasoning.

This project avoids that by separating:

- **Reasoning (controller / LLM-ready layer)**
- **Verification (algorithms / graph tools)**

This ensures:
- Reliability
- Reproducibility
- Scientific validity

---

## Architecture

Conjecture (JSON)
        ↓
Controller (LLM-ready)
        ↓
| Invalidator (local search) |
| Graph Tools (NetworkX invariants) |
| Verifier (independent correctness check) |
| Prover (Lean 4, optional) |
        ↓
Final Report (JSON + CSV)

---

## Features

- Graph invariant computation:
  - density, diameter, radius, degree, clique number, etc.
- Counterexample verification (independent module)
- Local search invalidation algorithm
- Graph mutation strategies (edge add/remove)
- Support for graph6 format
- Batch experiments with CSV export
- Modular architecture (MCP-ready design)

---

## Example Results

| ID      | Status               | Method       | Time  | Nodes |
|---------|----------------------|--------------|-------|-------|
| HDR-001 | Counterexample found | Local search | 0.01s | 4     |
| HDR-002 | Counterexample found | Local search | 0.02s | 6     |

Results are automatically saved as:

- JSON reports (`data/results/*.json`)
- CSV summary (`data/results/experiments_false_conjectures.csv`)

---

## Project Structure
mcp-graph-agent/
│
├── src/
│ ├── common/
│ │ ├── verifier.py
│ │ └── expression.py
│ │
│ ├── graph_tools/
│ │ ├── io.py
│ │ └── invariants.py
│ │
│ ├── invalidator/
│ │ ├── scoring.py
│ │ └── local_search.py
│ │
│ ├── controller/
│ │ └── main.py
│ │
│ └── prover/
│ └── lean_runner.py
│
├── data/
│ ├── false_conjectures/
│ └── results/
│
├── docs/
│ └── report.md
│
└── README.md

---

## Tech Stack

- Python
- NetworkX
- SymPy
- Graph6 format
- Lean 4 (optional / planned)
- MCP architecture (conceptual)

---

## Run

### 1. Install dependencies

- pip install -r requirements.txt

2. Run batch experiments

- python -m src.controller.main

Experimental Setup
- Dataset: HDR conjectures benchmark
- Strategy: local search with graph mutation
- Evaluation:
- counterexample detection
- independent verification
Output:
- JSON result per conjecture
- global CSV summary

Key Results
- Successfully verified all known counterexamples
- Rediscovered counterexamples using heuristic search
- Built a reproducible experimental pipeline
- Demonstrated separation between reasoning and validation

Key Insight

The LLM is not used as a mathematical oracle.

Instead:

- It orchestrates tools
- It proposes strategies
- All results are verified algorithmically

This design:

- avoids hallucination
- ensures correctness
- aligns with scientific computing principles

Limitations :  
- Domination number computed via brute force (slow)
- Local search is basic (no advanced heuristics)
- Lean integration is minimal
- No conjecture generation yet

Future Work
- Improve graph mutation strategies
- Add conjecture generation module
- Implement full MCP server architecture
- Integrate Lean prover more deeply
- Introduce smarter search (simulated annealing, heuristics)

Author Alex Nguyen

Keywords : Graph Theory · AI Agent · LLM · Local Search · Counterexamples · NetworkX · Formal Verification · Lean · MCP Architecture · Research Prototype

Run : 
~ git add README.md
~ git commit -m "Final README upgrade"
~ git push
