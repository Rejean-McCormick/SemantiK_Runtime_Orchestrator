# SemantiK Runtime Orchestrator — diK is not an activation gate

**Coordination-only, 24 November 2026.** The orchestrator must continue
to validate independently built, pinned language artifacts and RuntimeSet
receipts. A successful diK lookup cannot bypass GF WordBench validation,
SemantiK Architect's typed planning contracts, the staging transaction,
rollback rules, or release/activation authorization.

diK's V5.11 selection is a **derived read view**. It uses
`(namespace_id, KQ/KP)` as a local key and Wikidata Q/P as external reviewed
evidence; `candidate`, `relatedMatch` and `closeMatch` are not `exactMatch`.
The updated `/0.2` decision format binds all five input digests, including
the inspected graph, and refuses stale/legacy `/0.1` files for new views.

This note neither imports Kristal state nor creates a RuntimeSet or
qualifies/activates a language. Fail-closed production gates remain unchanged.
