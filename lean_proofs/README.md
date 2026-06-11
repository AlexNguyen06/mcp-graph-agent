# Lean proofs

These files formalize graph-theory statements from the internship subject with Lean 4 and Mathlib.

Build locally:

```bash
elan toolchain install stable
lake update
lake exe cache get
lake build
```

The prover tool reports `lean_not_found` when Lean is not installed. When Lean and Lake are available, it checks every `.lean` file in this directory and rejects files containing `sorry` as `incomplete_proof`.
