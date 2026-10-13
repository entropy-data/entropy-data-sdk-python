from __future__ import annotations

from typing import Any

from entropy_data_sdk._http import seg
from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import ExampleData


class ExampleDataApi(ApiGroup):
    def list(
        self,
        *,
        data_product_id: str | None = None,
        output_port_id: str | None = None,
        data_contract_id: str | None = None,
    ) -> list[ExampleData]:
        params = {
            "dataProductId": data_product_id,
            "outputPortId": output_port_id,
            "dataContractId": data_contract_id,
        }
        return self._http.get_list("/api/example-data", ExampleData, params=params)

    def get(self, id: str) -> ExampleData:
        return self._http.get_model(f"/api/example-data/{seg(id)}", ExampleData)

    def put(self, id: str, example_data: ExampleData | dict[str, Any]) -> None:
        self._http.put_json(f"/api/example-data/{seg(id)}", example_data)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/example-data/{seg(id)}")
