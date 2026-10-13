from __future__ import annotations

from typing import Any

from entropy_data_sdk.api._base import ApiGroup


class SchemasApi(ApiGroup):
    """JSON Schemas for data contracts (ODCS) and data products (ODPS), with or without the organization's customization."""

    def get_odcs(self, *, version: str | None = None, custom: bool = False) -> dict[str, Any]:
        return self._http.get_json(_schema_path("odcs", version, custom))

    def get_odps(self, *, version: str | None = None, custom: bool = False) -> dict[str, Any]:
        return self._http.get_json(_schema_path("odps", version, custom))


def _schema_path(standard: str, version: str | None, custom: bool) -> str:
    name = standard if version is None else f"{standard}-{version}"
    if custom:
        name += "-custom"
    return f"/api/schemas/{name}.schema.json"
