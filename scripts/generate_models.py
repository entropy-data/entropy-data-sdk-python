"""Generate src/entropy_data_sdk/models.py from spec/openapi.yaml.

The spec is rewritten before it reaches datamodel-code-generator:

* Inline objects and enums nested inside component schemas are hoisted into named
  component schemas (``Connector.info`` becomes ``ConnectorInfo``). The generator would
  otherwise number them (``Info4``, ``Status7``) and the names would shift with every
  spec change.
* A ``oneOf`` made of untitled inline objects (``Access.consumer`` is one of four shapes) is
  merged into a single object with every property optional, so callers read
  ``access.consumer.teamId`` instead of narrowing a union of generated variants.
* The external JSON Schema files for data products and data contracts are replaced by
  open objects. Those documents are customizable per organization and are passed through
  as dictionaries, so the SDK never rejects a field it does not know.
"""

from __future__ import annotations

import copy
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "spec" / "openapi.yaml"
OUTPUT = ROOT / "src" / "entropy_data_sdk" / "models.py"
GENERATOR = "datamodel-code-generator==0.83.0"

SINGULAR_OVERRIDES = {
    "Policies": "Policy",
    "Properties": "Property",
    "Capabilities": "Capability",
    "Categories": "Category",
    "Statuses": "Status",
}


def pascal(name: str) -> str:
    parts = re.split(r"[^0-9a-zA-Z]+", name)
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def singular(name: str) -> str:
    if name in SINGULAR_OVERRIDES:
        return SINGULAR_OVERRIDES[name]
    if name.endswith("ies"):
        return name[:-3] + "y"
    if name.endswith("ses") or name.endswith("xes"):
        return name[:-2]
    if name.endswith("s") and not name.endswith(("ss", "us")):
        return name[:-1]
    return name


def is_inline_object(schema: dict) -> bool:
    return isinstance(schema, dict) and schema.get("type") == "object" and "properties" in schema


def is_inline_enum(schema: dict) -> bool:
    return isinstance(schema, dict) and "enum" in schema and "$ref" not in schema


def merge_inline_one_of(schema: dict) -> dict | None:
    options = schema.get("oneOf")
    if not options or not all(is_inline_object(option) and not option.get("title") for option in options):
        return None
    properties: dict[str, dict] = {}
    for option in options:
        for name, prop_schema in option["properties"].items():
            if name in properties and properties[name] != prop_schema:
                return None
            properties[name] = prop_schema
    merged = {key: value for key, value in schema.items() if key != "oneOf"}
    merged.update({"type": "object", "properties": properties})
    return merged


class Hoister:
    def __init__(self, schemas: dict[str, dict]):
        self.schemas = schemas

    def unique(self, name: str) -> str:
        candidate = name
        counter = 2
        while candidate in self.schemas:
            candidate = f"{name}{counter}"
            counter += 1
        return candidate

    def hoist(self, parent: str, prop: str, schema: dict) -> dict:
        name = self.unique(parent + pascal(prop))
        self.schemas[name] = schema
        self.walk(name, schema)
        return {"$ref": f"#/components/schemas/{name}"}

    def visit(self, parent: str, prop: str, schema: dict) -> dict:
        if not isinstance(schema, dict):
            return schema
        merged = merge_inline_one_of(schema)
        if merged is not None:
            schema = merged
        if is_inline_object(schema) or is_inline_enum(schema):
            return self.hoist(parent, prop, schema)
        if schema.get("type") == "array" and isinstance(schema.get("items"), dict):
            schema["items"] = self.visit(parent, singular(pascal(prop)), schema["items"])
        if isinstance(schema.get("additionalProperties"), dict):
            schema["additionalProperties"] = self.visit(parent, pascal(prop) + "Value", schema["additionalProperties"])
        for combinator in ("allOf", "oneOf", "anyOf"):
            if combinator in schema:
                schema[combinator] = [
                    self.visit(parent, f"{pascal(prop)}Option{i + 1}", option) if is_inline_object(option) else option
                    for i, option in enumerate(schema[combinator])
                ]
        return schema

    def walk(self, name: str, schema: dict) -> None:
        if not isinstance(schema, dict):
            return
        for prop, prop_schema in list(schema.get("properties", {}).items()):
            schema["properties"][prop] = self.visit(name, prop, prop_schema)
        if schema.get("type") == "array" and isinstance(schema.get("items"), dict):
            schema["items"] = self.visit(name, "Item", schema["items"])
        if isinstance(schema.get("additionalProperties"), dict):
            schema["additionalProperties"] = self.visit(name, "Value", schema["additionalProperties"])
        for combinator in ("allOf", "oneOf", "anyOf"):
            for option in schema.get(combinator, []):
                self.walk(name, option)


def replace_external_refs(node):
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and not ref.startswith("#"):
            return {
                "type": "object",
                "additionalProperties": True,
                "description": f"Document validated against {ref}. Passed through unchanged.",
            }
        # ``format: email`` would pull in the optional email-validator dependency for one SCIM field.
        if node.get("format") == "email":
            node = {key: value for key, value in node.items() if key != "format"}
        return {key: replace_external_refs(value) for key, value in node.items()}
    if isinstance(node, list):
        return [replace_external_refs(item) for item in node]
    return node


def preprocess(spec: dict) -> dict:
    spec = replace_external_refs(copy.deepcopy(spec))
    schemas = spec["components"]["schemas"]
    hoister = Hoister(schemas)
    for name in list(schemas):
        hoister.walk(name, schemas[name])
    # Only component schemas become models; inline request/response bodies stay dictionaries.
    spec["paths"] = {}
    return spec


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    processed = preprocess(spec)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_spec = Path(tmp) / "openapi.yaml"
        tmp_spec.write_text(yaml.safe_dump(processed, sort_keys=False))
        command = [
            "uvx",
            "--from",
            GENERATOR,
            "datamodel-codegen",
            "--input",
            str(tmp_spec),
            "--input-file-type",
            "openapi",
            "--openapi-scopes",
            "schemas",
            "--output",
            str(OUTPUT),
            "--output-model-type",
            "pydantic_v2.BaseModel",
            "--target-python-version",
            "3.11",
            "--use-standard-collections",
            "--use-union-operator",
            "--use-schema-description",
            "--use-field-description",
            "--field-constraints",
            "--use-double-quotes",
            "--disable-timestamp",
            "--reuse-model",
            "--formatters",
            "ruff-format",
            "--custom-file-header",
            "# Generated by scripts/generate_models.py from spec/openapi.yaml. Do not edit.",
        ]
        result = subprocess.run(command, text=True, capture_output=True)
        if result.returncode != 0:
            sys.stderr.write(result.stderr)
            return result.returncode
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
