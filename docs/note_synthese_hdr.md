# Note de synthese HDR

## 1. Qu'est-ce qu'une conjecture fausse dans ce contexte ?

- Une conjecture est fausse lorsqu'un graphe satisfait la classe demandee par le JSON mais viole l'inegalite verifiee par `tools.verifier`.
- L'agent LLM ne decide jamais cette verite mathematique : il orchestre l'invalidator, le verificateur independant et le prouveur Lean.
- Un contre-exemple doit etre reconstruit depuis son format `graph6` puis reverifie sans faire confiance a la recherche.

## 2. Pourquoi distinguer echec de recherche et conjecture vraie ?

- Le statut `no_counterexample_found` signifie seulement que `tools.search_annor` n'a rien trouve dans ses limites de temps et d'ordre.
- Une conjecture vraie demande une preuve mathematique, par exemple dans `lean_proofs/`, pas une absence de resultat experimental.
- Cette distinction evite que l'agent presente une recherche limitee comme une preuve.

## 3. Comment transformer une inegalite en fonction de score ?

- Pour une relation `left <= right`, le score de violation est `left - right`; il devient positif quand l'inegalite est violee.
- Pour une relation `left >= right`, le score est `right - left`; le meme critere `score > 0` signale un contre-exemple.
- Le score guide `local_search`, mais seul `verify_conjecture` confirme le contre-exemple.

## 4. Interet des contre-exemples au format g6

- `graph6` donne une representation compacte et reproductible des graphes du benchmark HDR.
- Le verificateur peut reconstruire le graphe avec NetworkX, recalculer les invariants et detecter les erreurs de transcription.
- Les resultats JSON de l'invalidator stockent ce format pour faciliter les comparaisons et les experiences.

## 5. Pourquoi une recherche locale peut etre competitive

- La recherche locale modifie progressivement un graphe par ajout, suppression ou rebranchement d'aretes.
- Le score de violation donne une direction, contrairement au pur echantillonnage aleatoire.
- Les redemarrages et l'acceptation occasionnelle de mouvements non ameliorants aident a sortir des optima locaux.
