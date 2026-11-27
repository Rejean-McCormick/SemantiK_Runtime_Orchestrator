<!-- kOA Doc Server · Docs IA · lot 03 · projet : SemantiK_Runtime_Orchestrator · proposition dérivée à valider -->
# Navigation IA — SemantiK_Runtime_Orchestrator

**Objet constaté :** Orchestrateur transactionnel de qualification, promotion et activation des RuntimeSets SemantiK.

**Frontière de responsabilité :** Ce composant coordonne les gates et rollback; SemantiK Architect et WordBench détiennent la validité des artefacts linguistiques.

**Source :** `SmartDump_20261120_221507.zip` → `SemantiK_Runtime_Orchestrator_Code_snapshot.zip` (20 novembre 2026). Le chemin Windows est une déclaration de snapshot, pas une vérification de l'état actuel.

**Statut :** Documentation de navigation dérivée de sources propriétaires, à revoir. Ce document ne vaut ni profil d'ingénierie mesuré, ni certification, ni permission d'exécution.

## Ordre de lecture — fichiers réellement présents dans la capture

1. [`README.md`](../../README.md) — SHA-256 `a5426432164f3df7…` dans la capture.
2. [`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md) — SHA-256 `876c058e22738b73…` dans la capture.
3. [`docs/CONTRACTS.md`](../../docs/CONTRACTS.md) — SHA-256 `caaaaccee4f56081…` dans la capture.
4. [`pyproject.toml`](../../pyproject.toml) — SHA-256 `c7ccd3eb05b0538a…` dans la capture.

## Parcours recommandé pour une intervention assistée par IA

1. Identifier la question, le sous-système concerné et les responsabilités du propriétaire.
2. Lire les documents ci-dessus **dans cet ordre**; consulter les contrats et consignes propriétaires plus récents si le checkout a évolué.
3. Épingler versions des PGF et rapports, vérifier les reçus de conformité, prévisualiser la promotion puis exécuter seulement le workflow explicitement autorisé.
4. Établir les vérifications effectivement disponibles dans la révision locale, consigner les résultats et ne conclure qu'à l'intérieur du périmètre couvert.
5. Proposer les changements; demander une décision explicite avant toute écriture à effet, déploiement, publication ou promotion de preuves.

## Risque propre à ce dépôt

Ne pas importer les états Kristal amont, contourner un refus fail-closed ou annoncer une activation sur la seule présence d’un fichier RuntimeSet.

## Compléments

- [`AI_CONTEXT.md`](AI_CONTEXT.md) : règles de travail et frontières de confiance.
- `AGENTS.md` : s'il existe déjà chez le propriétaire, ses consignes priment sur ces propositions; sinon l'overlay peut en ajouter un sans remplacement.
- `PROFIL_INGENIERIE.md` : optionnel, uniquement après exécution réelle de RepoSurveyor sur un dépôt local et accord explicite pour sa copie.
- Le Framework Kristal v11 est un standard documentaire **facultatif** : lire le profil réellement verrouillé, sans imposer de migration.

## Multilingual alignment — 2026-11-26

Read the [dated owner-context addendum](MULTILINGUAL_ALIGNMENT_2026-11-26.md). It records the observed scope, authority and pending gates; it does not replace owner contracts or certify current code.
