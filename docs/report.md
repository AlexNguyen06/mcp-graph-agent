# Project Report — MCP Graph Agent

## Objective

Build an AI-assisted system capable of analyzing graph theory conjectures.

The system must:
- Detect false conjectures via counterexamples
- Attempt validation via formal methods
- Ensure correctness independently

---

## Methodology

1. Represent conjectures in JSON format
2. Compute graph invariants using NetworkX
3. Transform conjectures into score functions
4. Use local search to find violations
5. Verify results independently

---

## Key Design Choice

The LLM is not trusted as a mathematical oracle.

Instead:
- It orchestrates tools
- All results are verified algorithmically

---

## Results

- Verified multiple HDR conjectures
- Successfully detected counterexamples
- Built reproducible experiment pipeline

---

## Insight

Separating reasoning and verification:
- avoids hallucination
- ensures reliability
- aligns with scientific computing principles

---

## Limitations

- Local search is naive
- Some invariants are expensive
- No full Lean automation

---

## Conclusion

This project demonstrates how LLMs can be used safely in mathematical research by delegating correctness to specialized tools.