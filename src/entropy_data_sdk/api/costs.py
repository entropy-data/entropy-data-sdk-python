from __future__ import annotations

from typing import Any

from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import Cost


class CostsApi(ApiGroup):
    def list(self, *, data_product_id: str) -> list[Cost]:
        return self._http.get_list("/api/costs", Cost, params={"dataProductId": data_product_id})

    def add(self, cost: Cost | dict[str, Any]) -> None:
        self._http.post_json("/api/costs", cost)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/costs/{id}")
