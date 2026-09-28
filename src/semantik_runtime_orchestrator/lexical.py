from __future__ import annotations

from typing import Any

STANDARD_PRECEDENCE = (
    "request_override",
    "domain",
    "project",
    "wikidata",
    "gf_generic",
)
VALID_SOURCE_KINDS = frozenset(STANDARD_PRECEDENCE)
VALID_USES = frozenset({"knowledge", "binding", "both"})
VALID_BINDING_KINDS = frozenset({"gf_expr", "literal", "lexeme_ref"})


def lexical_policy_from_artifact(data: dict[str, Any]) -> dict[str, Any]:
    raw = data.get("lexical_policy")
    if raw is None:
        return {
            "policy_version": "1.0",
            "precedence": list(STANDARD_PRECEDENCE),
            "default_source_kind": "project",
            "equal_precedence_conflict": "fail",
        }
    if not isinstance(raw, dict):
        raise ValueError("lexical_policy must be an object")
    precedence = raw.get("precedence") or list(STANDARD_PRECEDENCE)
    if (
        not isinstance(precedence, list)
        or not precedence
        or len(precedence) != len(set(precedence))
        or any(item not in VALID_SOURCE_KINDS for item in precedence)
    ):
        raise ValueError("invalid lexical precedence")
    default = str(raw.get("default_source_kind") or "project")
    if default not in precedence:
        raise ValueError("default_source_kind must appear in lexical precedence")
    if str(raw.get("equal_precedence_conflict") or "fail") != "fail":
        raise ValueError("only fail equal-precedence conflicts are supported")
    return {
        "policy_version": "1.0",
        "precedence": list(precedence),
        "default_source_kind": default,
        "equal_precedence_conflict": "fail",
    }


def validate_lexical_artifact(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("schema_version") not in {"1.0", "1.1"}:
        raise ValueError("unsupported lexical artifact schema")
    if not isinstance(data.get("lexicon_id"), str) or not data["lexicon_id"]:
        raise ValueError("missing lexicon_id")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise ValueError("entries must be an array")
    artifact_source = str(data.get("source_kind") or "project")
    if artifact_source not in VALID_SOURCE_KINDS:
        raise ValueError(f"invalid source_kind={artifact_source}")

    for index, row in enumerate(entries):
        if not isinstance(row, dict):
            raise ValueError(f"entry[{index}] must be an object")
        for key in ("semantic_ref", "language", "lexical_ref"):
            if not isinstance(row.get(key), str):
                raise ValueError(f"entry[{index}].{key} is required")
        source_kind = str(row.get("source_kind") or artifact_source)
        if source_kind not in VALID_SOURCE_KINDS:
            raise ValueError(f"entry[{index}].source_kind={source_kind}")
        use_for = str(row.get("use_for") or "both")
        if use_for not in VALID_USES:
            raise ValueError(f"entry[{index}].use_for={use_for}")
        binding_kind = str(
            row.get("binding_kind")
            or (
                "lexeme_ref"
                if source_kind == "wikidata" and use_for == "knowledge"
                else "gf_expr"
            )
        )
        if binding_kind not in VALID_BINDING_KINDS:
            raise ValueError(f"entry[{index}].binding_kind={binding_kind}")
        if use_for in {"binding", "both"} and binding_kind == "lexeme_ref":
            raise ValueError(
                f"entry[{index}] lexeme_ref is knowledge-only and cannot be an executable binding"
            )

    return lexical_policy_from_artifact(data)
