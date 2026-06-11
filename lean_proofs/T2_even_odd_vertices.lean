import Mathlib.Combinatorics.SimpleGraph.Finite

/-!
T2 - Enonce informel du sujet de stage :
dans tout graphe simple fini, le nombre de sommets de degre impair est pair.
-/

open scoped BigOperators

universe u

namespace Internship

theorem T2_even_odd_vertices
    (V : Type u) [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] :
    Even ((Finset.univ.filter fun v : V => Odd (G.degree v)).card) := by
  simpa using G.even_card_odd_degree_vertices

end Internship
