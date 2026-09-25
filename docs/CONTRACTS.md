# External contracts

## GF Wordbench

A consumed release must contain `manifest.json` using `gf-wordbench.artifact-manifest/1.0` and `summary.json`. The summary must describe a completed `release` run with `overall_status=OK`, `decision=READY`, passed release gates, and a verified manifest. Every manifest artifact is checked by size and SHA-256.

Exactly one `role=pgf` artifact is required unless `wordbench.pgf_artifact` explicitly selects one.

## SemantiK Architect

The orchestrator stages the public SA RuntimeSet artifact shapes and invokes SA using configured public commands. No Python import from `semantik_architect` occurs.

`sa.conformance.command` must create `{evidence}` and the evidence must state `passed=true` plus matching `runtime_set_id`, `language`, and `profile_id`. Alternatively, `sa.conformance.evidence` may supply already-produced evidence for a resumed transaction.

`sa.validate_runtime.command` is mandatory and must exit zero only when the staged RuntimeSet satisfies the canonical SA release contract.

## LevelUpDiag

`levelupdiag.command` is optional. When configured and `required=true`, a non-zero exit rolls back the promoted-but-not-activated RuntimeSet.

## GF Observatory

`observatory.command` is optional. It is treated as a consumer hook. With `required=false`, failure is recorded as WARN and does not become an authority over SA release validity. With `required=true`, it becomes an explicit deployment gate by operator choice.

## Command placeholders

Commands are arrays of argv tokens, never shell strings. Depending on stage, these placeholders are available:

`{runtime_set_id}`, `{language}`, `{profile}`, `{profile_id}`, `{runtime_root}`, `{state_root}`, `{candidate_root}`, `{candidate_runtime_root}`, `{runtime_dir}`, `{suite}`, `{evidence}`, `{grammar}`, `{bridge}`, `{lexicon}`, `{capability_profile}`, `{transaction_report}`.
