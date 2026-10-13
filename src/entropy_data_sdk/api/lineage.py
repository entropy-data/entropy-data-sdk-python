from __future__ import annotations

from typing import Any

from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import OpenLineageRunEvent


class LineageApi(ApiGroup):
    def post_event(
        self,
        event: OpenLineageRunEvent | dict[str, Any],
        *,
        data_product_id: str | None = None,
        output_port_name: str | None = None,
    ) -> None:
        params = {"dataProductId": data_product_id, "outputPortName": output_port_name}
        self._http.post_json("/api/v1/lineage", event, params=params)

    def list_events(
        self,
        *,
        job_namespace: str | None = None,
        job_name: str | None = None,
        run_id: str | None = None,
        event_type: str | None = None,
        data_product_id: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        page: int | None = None,
        size: int | None = None,
    ) -> list[OpenLineageRunEvent]:
        params = {
            "jobNamespace": job_namespace,
            "jobName": job_name,
            "runId": run_id,
            "eventType": event_type,
            "dataProductId": data_product_id,
            "from": from_,
            "to": to,
            "p": page,
            "size": size,
        }
        return self._http.get_list("/api/v1/lineage", OpenLineageRunEvent, params=params)

    def delete_events(
        self, *, run_id: str | None = None, job_namespace: str | None = None, job_name: str | None = None
    ) -> dict[str, Any]:
        params = {"runId": run_id, "jobNamespace": job_namespace, "jobName": job_name}
        return self._http.delete("/api/v1/lineage", params=params).data
