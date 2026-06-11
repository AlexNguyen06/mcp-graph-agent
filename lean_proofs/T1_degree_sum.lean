import Mathlib.Combinatorics.SimpleGraph.Finite

/-!
T1 - Enonce informel du sujet de stage :
dans tout graphe simple fini, la somme des degres des sommets est egale
a deux fois le nombre d'aretes.
-/

open scoped BigOperators

universe u

namespace Internship

theorem T1_degree_sum
    (V : Type u) [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] :
    (∑ v : V, G.degree v) = 2 * G.edgeFinset.card := by
  simpa using G.sum_degrees_eq_twice_card_edges

end Internship
