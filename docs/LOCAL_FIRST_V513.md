# Local-first V5.13 — SemantiK_Runtime_Orchestrator authority boundary

**Status:** candidate coordination note; owner instructions and exact pinned contracts prevail.

## Owned responsibilities

The Runtime Orchestrator coordinates transactional RuntimeSet gates and rollback, not upstream Kristal canonical authority.

## Required review and exclusions

Do not import/alter the source canonical state as a shortcut. RuntimeSet promotion remains separate from Kit candidate staging, C3, independent C1/C2 and immutable publication.

The canonical source is each owner workspace in `C:\mycode\Kristal\locals`. `kristal-public` is a derived hosted read surface, never a place for semantic corrections. diK's federated semantic key is `(namespace_id, KQ/KP)`; bare `KQ1001` is ambiguous. Wikidata Q/P are external, reviewed links, not replacement Kristal IDs. Labels, meanings, source provenance and additive revision history remain retrievable.

Manager `audit-local-public` compares declared canonical bytes and sync-manifest scope, not semantic correctness. Excluded local files stay excluded. A candidate can move through Kit private staging and C3 only after exact owner decisions; independent C1/C2 plus exact commit/policy approval are required for public push. No direct public edits, Git push or RuntimeSet activation are allowed by this note.
