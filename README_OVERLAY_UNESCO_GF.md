# SemantiK Runtime Orchestrator — overlay de prévalidation UNESCO

Racine : `C:\mycode\SemantiK_Architect\SemantiK_Runtime_Orchestrator`.

Ajoute `tools/unesco_candidate_preflight.py`, lecteur privé **sans transaction** qui vérifie les empreintes du candidat, le rapport de compilation Wordbench et la suite de conformité SemantiK avant de le signaler comme candidat vérifié.

Il **ne se substitue pas** au vrai processus de promotion transactionnelle de l'orchestrateur. `PRIVATE_CANDIDATE_EVIDENCE_CHECKED_NOT_RELEASED` n'accorde aucun statut RELEASED, aucune activation et aucune autorisation de wiki.

```powershell
py -3.12 tools/unesco_candidate_preflight.py --candidate "C:\...\candidates\fr"
```

Test : `py -3.12 -m unittest discover -s tests -p test_unesco_candidate_preflight.py -v`.
