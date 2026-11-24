# Runtime Orchestrator — garde-fou du registre diK fédéré

**Statut : précontrôle facultatif et non promoteur.**

Le registre `dik.federated-semantic-registry/0.1-candidate` est une projection
en lecture seule des identités KQ/KP du Framework et de leurs liens Wikidata
Q/P. Il **n'est pas** un RuntimeSet qualifié, un lexique exécutif, une preuve
GF ou une approbation de licence.

Contrôle explicite disponible :

```
python tools/dik_federation_preflight.py --dir <répertoire de sortie diK>
```

Le code vérifie SHA-256, profil, 13 langues cibles et schéma de l'index sans
modifier de données. Le résultat `INTEGRITY_ONLY` ne modifie aucune gate,
transaction, promotion, activation, désactivation ou rollback. Aucun nouveau
chemin d'activation automatique n'a été ajouté.

Avant d'admettre un artefact linguistique, conserver les critères existants du
propriétaire SemantiK Architect, de WordBench, de la compilation GF et de la
qualité des preuves. L'identité du Kristal reste `(namespace_id,id)` et les
liens candidats/`closeMatch` ne peuvent satisfaire une équivalence exacte.

Les données `no` préexistantes restent archivées ; le nouveau périmètre diK
à 13 langues ne réécrit pas les versions antérieures des RuntimeSets.
