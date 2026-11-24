# Consignes agents — SemantiK_Runtime_Orchestrator

> Proposition rédigée à partir du SmartDump du 20 novembre 2026. Ce fichier ne remplace pas une décision, un contrat ni une politique du propriétaire. En cas de consigne plus récente, **la consigne propriétaire prévaut**.

- Commencer par [`docs/ai/INDEX.md`](docs/ai/INDEX.md), puis [`docs/ai/AI_CONTEXT.md`](docs/ai/AI_CONTEXT.md).
- Domaine : Orchestrateur transactionnel de qualification, promotion et activation des RuntimeSets SemantiK.
- Autorité : Ce composant coordonne les gates et rollback; SemantiK Architect et WordBench détiennent la validité des artefacts linguistiques.
- Précaution principale : Ne pas importer les états Kristal amont, contourner un refus fail-closed ou annoncer une activation sur la seule présence d’un fichier RuntimeSet.
- Avant de modifier, relire les sources propriétaire listées dans l'index, les éventuels locks et les tests du dépôt actif.
- Ne lancer ni effet distant, ni déploiement, ni publication, ni migration, ni promotion de preuves sans approbation explicite.
- Les rapports RepoSurveyor sont des **profils d'ingénierie**, pas des certificats de maturité. Ne pas les inventer.
- Le Framework Kristal v11 reste facultatif et non bloquant, sauf contrat adopté explicitement par ce propriétaire.

## Interface fédérée diK V5.9 — règle additive candidate

Ne jamais traiter `dik.federated-semantic-registry/0.1-candidate` comme une source d’autorité canonique ou une permission de publier. Toute identité locale exige `namespace_id+KQ/KP`; un Q/P Wikidata n’est qu’un alignement externe revu. Le précontrôle vérifie uniquement l’intégrité. Consulter `docs/DIK_FEDERATED_REGISTRY_BOUNDARY.md`. Les contraintes propriétaire existantes prévalent.
