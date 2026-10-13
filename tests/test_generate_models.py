import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "generate_models", Path(__file__).resolve().parent.parent / "scripts" / "generate_models.py"
)
generate_models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_models)


def test_inline_objects_and_enums_get_names_from_their_parent():
    schemas = {
        "Connector": {
            "type": "object",
            "properties": {
                "info": {"type": "object", "properties": {"type": {"type": "string"}}},
                "status": {"type": "string", "enum": ["running", "stopped"]},
                "runs": {"type": "array", "items": {"type": "object", "properties": {"at": {"type": "string"}}}},
            },
        }
    }
    hoister = generate_models.Hoister(schemas)

    hoister.walk("Connector", schemas["Connector"])

    assert schemas["Connector"]["properties"]["info"] == {"$ref": "#/components/schemas/ConnectorInfo"}
    assert schemas["Connector"]["properties"]["status"] == {"$ref": "#/components/schemas/ConnectorStatus"}
    assert schemas["Connector"]["properties"]["runs"]["items"] == {"$ref": "#/components/schemas/ConnectorRun"}
    assert schemas["ConnectorInfo"]["properties"]["type"] == {"type": "string"}


def test_untitled_one_of_objects_are_merged_into_one_optional_shape():
    schema = {
        "oneOf": [
            {"type": "object", "properties": {"teamId": {"type": "string"}}, "required": ["teamId"]},
            {"type": "object", "properties": {"userId": {"type": "string"}}, "required": ["userId"]},
        ]
    }

    merged = generate_models.merge_inline_one_of(schema)

    assert merged == {"type": "object", "properties": {"teamId": {"type": "string"}, "userId": {"type": "string"}}}


def test_conflicting_one_of_objects_are_left_alone():
    schema = {
        "oneOf": [
            {"type": "object", "properties": {"id": {"type": "string"}}},
            {"type": "object", "properties": {"id": {"type": "integer"}}},
        ]
    }

    assert generate_models.merge_inline_one_of(schema) is None


def test_external_schema_files_become_open_objects():
    spec = {
        "DataContract": {"$ref": "schemas/odcs-json-schema-v3.1.0.json"},
        "email": {"type": "string", "format": "email"},
    }

    result = generate_models.replace_external_refs(spec)

    assert result["DataContract"]["additionalProperties"] is True
    assert "format" not in result["email"]


def test_singular_keeps_words_that_only_look_plural():
    assert generate_models.singular("Statuses") == "Status"
    assert generate_models.singular("UsageInstructionsByStatus") == "UsageInstructionsByStatus"
    assert generate_models.singular("Policies") == "Policy"
    assert generate_models.singular("Runs") == "Run"
