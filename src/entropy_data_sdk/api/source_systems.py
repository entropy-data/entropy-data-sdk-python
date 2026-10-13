from __future__ import annotations

from typing import Any

from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import SourceSystem


class SourceSystemsApi(ApiGroup):
    def list(self, *, page: int | None = None) -> list[SourceSystem]:
        return self._http.get_list("/api/sourcesystems", SourceSystem, params={"p": page})

    def get(self, id: str) -> SourceSystem:
        return self._http.get_model(f"/api/sourcesystems/{id}", SourceSystem)

    def put(self, id: str, source_system: SourceSystem | dict[str, Any]) -> None:
        self._http.put_json(f"/api/sourcesystems/{id}", source_system)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/sourcesystems/{id}")
