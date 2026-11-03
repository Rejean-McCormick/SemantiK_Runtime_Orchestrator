# Inspection stricte d'un profil pour Spek

Nouvelle commande, sans mutation et sans activation :

`semantik-runtime-orchestrator inspect-profile --runtime-root <runtime> --language fr --profile agriculture-reference-1`

Le contrôle vérifie le binding d'activation, l'état RELEASED, les fichiers
normatifs, les SHA256, la présence d'un `grammar.pgf` et l'attestation locale
de conformité. Un fichier source GF n'est pas un `.pgf` compilé.

Le résultat `LOCAL_ARTIFACTS_VERIFIED_EXECUTION_NOT_PROVEN` autorise seulement
une tentative de réalisation. Il **ne prouve pas** la réalisation correcte
du corpus. Sans artefact complet, le statut est `BLOCKED` et le code de
sortie est différent de zéro. Aucun artefact ne peut être publié par cette
commande.
