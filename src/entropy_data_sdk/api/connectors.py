from __future__ import annotations

from typing import Any

from entropy_data_sdk._http import Page, seg
from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import Connector


class ConnectorsApi(ApiGroup):
    def list(self) -> Page[Connector]:
        return self._http.get_list("/api/connectors", Connector)

    def get(self, id: str) -> Connector:
        return self._http.get_model(f"/api/connectors/{seg(id)}", Connector)

    def put(self, id: str, connector: Connector | dict[str, Any]) -> None:
        self._http.put_json(f"/api/connectors/{seg(id)}", connector)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/connectors/{seg(id)}")
