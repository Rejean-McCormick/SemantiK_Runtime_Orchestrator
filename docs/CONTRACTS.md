# External contracts

## GF Wordbench

A consumed release must contain `manifest.json` using `gf-wordbench.artifact-manifest/1.0` and `summary.json`. The summary must describe a completed `release` run with `overall_status=OK`, `decision=READY`, passed release gates, and a verified manifest. Every manifest artifact is checked by size and SHA-256.

Exactly one `role=pgf` artifact is required unless `wordbench.pgf_artifact` explicitly selects one.

## SemantiK Architect

The orchestrator stages the public SA RuntimeSet artifact shapes and invokes SA using configured public commands. No Python import from `semantik_architect` occurs.

`sa.conformance.command` must create `{evidence}` and the evidence must state `passed=true` plus matching `runtime_set_id`, `language`, and `profile_id`. Alternatively, `sa.conformance.evidence` may supply already-produced evidence for a resumed transaction.

`sa.validate_runtime.command` is mandatory and must exit zero only when the staged RuntimeSet satisfies the canonical SA release contract.


## Lexical authority contract

The orchestrator accepts lexical artifact schema `1.0` and `1.1`. It validates and pins an explicit lexical policy into every released RuntimeSet. The default is:

`request_override > domain > project > wikidata > gf_generic`

Wikidata Lexeme entries may be knowledge-only (`use_for=knowledge`, `binding_kind=lexeme_ref`). They are not executable GF expressions. GF generic entries may supply realization bindings for the same semantic reference without becoming the semantic dictionary authority. Equal-precedence semantic conflicts are resolved by SA fail-closed behavior, never artifact ordering.

## LevelUpDiag

`levelupdiag.command` is optional. When configured and `required=true`, a non-zero exit rolls back the promoted-but-not-activated RuntimeSet.

## GF Observatory

`observatory.command` is optional. It is treated as a consumer hook. With `required=false`, failure is recorded as WARN and does not become an authority over SA release validity. With `required=true`, it becomes an explicit deployment gate by operator choice.

## Command placeholders

Commands are arrays of argv tokens, never shell strings. Depending on stage, these placeholders are available:

`{runtime_set_id}`, `{language}`, `{profile}`, `{profile_id}`, `{runtime_root}`, `{state_root}`, `{candidate_root}`, `{candidate_runtime_root}`, `{runtime_dir}`, `{suite}`, `{evidence}`, `{grammar}`, `{bridge}`, `{lexicon}`, `{capability_profile}`, `{transaction_report}`.

## SA candidate conformance and Konstellation

The current SA CLI accepts `conformance --suite {suite} --runtime-set-id {runtime_set_id} --candidate-dir {candidate_root} --output {evidence}`. The candidate runner checks pipeline.lock hashes and invokes the real GF adapter without marking the candidate RELEASED. Ordinary HTTP rendering remains restricted to released runtimes. Failure and invalid runtime validation return nonzero exit codes.

Evidence may identify its profile as `capability_profile` (SA contract) or `profile_id` (orchestrator contract). If both exist they must agree. Runtime and language identity checks remain mandatory.

`examples/konstellation-fr.json` points to sibling `semantik-architect/profiles/konstellation-explorer-1` resources. Set the Wordbench READY release directory before release. The example runtime ID matches its suite. Change them together when making a new immutable release. Optional diagnostics gates may be added using the standard configuration; no placeholder gate is silently executed.


## Direct grammar input

`grammar.pgf` is the direct-input contract for already-built grammars. `grammar.sha256` is optional but, when supplied, MUST match exactly. `wordbench` and `grammar` are mutually exclusive. Direct mode does not weaken SA conformance or runtime validation.

## SemantiK Architect 1.2.0 compatibility

Runtime manifests continue to use the declared `sa_version_range`; the default `>=1.0,<2.0` admits 1.2.0. Kristal v6 communication projection contracts are not orchestrator inputs.
