import Lake
open Lake DSL

package «mcp-graph-agent» where
  -- Mathlib is fetched through the dependency below.

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git"

lean_lib LeanProofs where
  globs := #[.submodules `lean_proofs]
