import pytest

from semantik_runtime_orchestrator.lexical import validate_lexical_artifact


def test_v11_wikidata_knowledge_artifact_is_valid_and_has_standard_policy():
    data = {
        "schema_version": "1.1",
        "lexicon_id": "wd",
        "source_kind": "wikidata",
        "entries": [
            {
                "semantic_ref": "wikidata:Q1",
                "language": "fr",
                "lexical_ref": "wikidata:L1-S1",
                "binding_kind": "lexeme_ref",
                "use_for": "knowledge",
            }
        ],
    }
    policy = validate_lexical_artifact(data)
    assert policy["precedence"] == [
        "request_override",
        "domain",
        "project",
        "wikidata",
        "gf_generic",
    ]


def test_lexeme_ref_cannot_be_executable_binding():
    data = {
        "schema_version": "1.1",
        "lexicon_id": "wd",
        "source_kind": "wikidata",
        "entries": [
            {
                "semantic_ref": "wikidata:Q1",
                "language": "fr",
                "lexical_ref": "wikidata:L1-S1",
                "binding_kind": "lexeme_ref",
                "use_for": "both",
            }
        ],
    }
    with pytest.raises(ValueError):
        validate_lexical_artifact(data)
