from __future__ import annotations

from typing import Any

from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import (
    Access,
    AccessDeprovisioningSucceededReport,
    AccessProvisioning,
    AccessProvisioningFailedReport,
    AccessProvisioningReport,
    AccessProvisioningStartedReport,
    AccessProvisioningSucceededReport,
    CopyAccessPreview,
    CopyAccessResponse,
)


class AccessApi(ApiGroup):
    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        provider_data_product_id: str | None = None,
        consumer_data_product_id: str | None = None,
        consumer_type: str | None = None,
    ) -> list[Access]:
        params = {
            "p": page,
            "pageSize": page_size,
            "providerDataProductId": provider_data_product_id,
            "consumerDataProductId": consumer_data_product_id,
            "consumerType": consumer_type,
        }
        return self._http.get_list("/api/access", Access, params=params)

    def get(self, id: str) -> Access:
        return self._http.get_model(f"/api/access/{id}", Access)

    def put(self, id: str, access: Access | dict[str, Any]) -> None:
        self._http.put_json(f"/api/access/{id}", access)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/access/{id}")

    def approve(self, id: str) -> None:
        self._http.post_json(f"/api/access/{id}/approve")

    def reject(self, id: str) -> None:
        self._http.post_json(f"/api/access/{id}/reject")

    def cancel(self, id: str) -> None:
        self._http.post_json(f"/api/access/{id}/cancel")

    # Provisioning reports

    def get_provisioning(self, id: str) -> AccessProvisioning:
        return self._http.get_model(f"/api/access/{id}/provisioning", AccessProvisioning)

    def put_provisioning(self, id: str, report: AccessProvisioningReport | dict[str, Any]) -> AccessProvisioning:
        return self._http.put_model(f"/api/access/{id}/provisioning", report, AccessProvisioning)

    def report_provisioning_started(
        self, id: str, report: AccessProvisioningStartedReport | dict[str, Any] | None = None
    ) -> AccessProvisioning:
        return self._http.post_model(
            f"/api/access/{id}/provisioning/provisioning-started", AccessProvisioning, report or {}
        )

    def report_provisioning_succeeded(
        self, id: str, report: AccessProvisioningSucceededReport | dict[str, Any] | None = None
    ) -> AccessProvisioning:
        return self._http.post_model(
            f"/api/access/{id}/provisioning/provisioning-succeeded", AccessProvisioning, report or {}
        )

    def report_provisioning_failed(
        self, id: str, report: AccessProvisioningFailedReport | dict[str, Any]
    ) -> AccessProvisioning:
        return self._http.post_model(f"/api/access/{id}/provisioning/provisioning-failed", AccessProvisioning, report)

    def report_deprovisioning_started(
        self, id: str, report: AccessProvisioningStartedReport | dict[str, Any] | None = None
    ) -> AccessProvisioning:
        return self._http.post_model(
            f"/api/access/{id}/provisioning/deprovisioning-started", AccessProvisioning, report or {}
        )

    def report_deprovisioning_succeeded(
        self, id: str, report: AccessDeprovisioningSucceededReport | dict[str, Any] | None = None
    ) -> AccessProvisioning:
        return self._http.post_model(
            f"/api/access/{id}/provisioning/deprovisioning-succeeded", AccessProvisioning, report or {}
        )

    def report_deprovisioning_failed(
        self, id: str, report: AccessProvisioningFailedReport | dict[str, Any]
    ) -> AccessProvisioning:
        return self._http.post_model(f"/api/access/{id}/provisioning/deprovisioning-failed", AccessProvisioning, report)

    # Copying access between output ports

    def preview_copy(
        self, data_product_id: str, output_port_id: str, *, source_output_port_id: str
    ) -> CopyAccessPreview:
        return self._http.get_model(
            f"/api/dataproducts/{data_product_id}/outputports/{output_port_id}/copy-access",
            CopyAccessPreview,
            params={"sourceOutputPortId": source_output_port_id},
        )

    def copy(
        self,
        data_product_id: str,
        output_port_id: str,
        *,
        source_output_port_id: str,
        access: list[str] | None = None,
        notify_consumers: bool | None = None,
    ) -> CopyAccessResponse:
        body = {"sourceOutputPortId": source_output_port_id, "access": access, "notifyConsumers": notify_consumers}
        return self._http.post_model(
            f"/api/dataproducts/{data_product_id}/outputports/{output_port_id}/copy-access",
            CopyAccessResponse,
            {key: value for key, value in body.items() if value is not None},
        )

    def evaluate(self, request: dict[str, Any]) -> dict[str, Any]:
        """Evaluate an access decision for ``{"subject": ..., "resource": ..., "action": ...}``."""
        return self._http.post_json("/api/access/evaluation", request)
