from __future__ import annotations

from typing import Any

from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import OtelTracesRequest


class UsageApi(ApiGroup):
    def get_traces(
        self,
        *,
        scope_name: str | None = None,
        data_product_id: str | None = None,
        data_contract_id: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        page: int | None = None,
        size: int | None = None,
    ) -> OtelTracesRequest:
        params = {
            "scopeName": scope_name,
            "dataProductId": data_product_id,
            "dataContractId": data_contract_id,
            "from": from_,
            "to": to,
            "p": page,
            "size": size,
        }
        return self._http.get_model("/api/v1/traces", OtelTracesRequest, params=params)

    def post_traces(self, traces: OtelTracesRequest | dict[str, Any]) -> None:
        self._http.post_json("/api/v1/traces", traces)

    def delete_traces(
        self,
        *,
        scope_name: str | None = None,
        data_product_id: str | None = None,
        data_contract_id: str | None = None,
        span_id: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "scopeName": scope_name,
            "dataProductId": data_product_id,
            "dataContractId": data_contract_id,
            "spanId": span_id,
        }
        return self._http.delete("/api/v1/traces", params=params)
