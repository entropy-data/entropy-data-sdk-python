from __future__ import annotations

from typing import Any

from entropy_data_sdk._http import Page, seg
from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import Definition


class DefinitionsApi(ApiGroup):
    def list(self, *, page: int | None = None) -> Page[Definition]:
        return self._http.get_list("/api/definitions", Definition, params={"p": page})

    def get(self, id: str) -> Definition:
        return self._http.get_model(f"/api/definitions/{seg(id)}", Definition)

    def put(self, id: str, definition: Definition | dict[str, Any]) -> None:
        self._http.put_json(f"/api/definitions/{seg(id)}", definition)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/definitions/{seg(id)}")
