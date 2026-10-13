from __future__ import annotations

from typing import Any

from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import (
    IngestIntegrationRequest,
    IngestionRun,
    Integration,
    TriggerRunResponse,
    UnityCatalogMetadataActionResponse,
    UnityCatalogMetadataIntegration,
    UnityCatalogMetadataIntegrationRequest,
    UnityCatalogMetadataQueueEntry,
    UnityCatalogMetadataTable,
)


class IngestIntegrationsApi(ApiGroup):
    """Asset imports (reading integrations)."""

    def list(
        self, *, owning_team_external_id: str | None = None, source: str | None = None, enabled: bool | None = None
    ) -> list[Integration]:
        params = {"owningTeamExternalId": owning_team_external_id, "source": source, "enabled": enabled}
        return self._http.get_list("/api/integrations/ingest", Integration, params=params)

    def get(self, integration: str) -> Integration:
        return self._http.get_model(f"/api/integrations/ingest/{integration}", Integration)

    def put(self, integration: str, request: IngestIntegrationRequest | dict[str, Any]) -> Integration:
        return self._http.put_model(f"/api/integrations/ingest/{integration}", request, Integration)

    def delete(self, integration: str, *, delete_assets: bool | None = None) -> None:
        self._http.delete(f"/api/integrations/ingest/{integration}", params={"deleteAssets": delete_assets})

    def list_runs(self, integration: str, *, limit: int | None = None, status: str | None = None) -> list[IngestionRun]:
        params = {"limit": limit, "status": status}
        return self._http.get_list(f"/api/integrations/ingest/{integration}/runs", IngestionRun, params=params)

    def get_latest_run(self, integration: str) -> IngestionRun:
        return self._http.get_model(f"/api/integrations/ingest/{integration}/runs/latest", IngestionRun)

    def get_run(self, integration: str, run_id: str) -> IngestionRun:
        return self._http.get_model(f"/api/integrations/ingest/{integration}/runs/{run_id}", IngestionRun)

    def trigger_run(self, integration: str) -> TriggerRunResponse:
        return self._http.post_model(f"/api/integrations/ingest/{integration}/run", TriggerRunResponse)

    def cancel_run(self, integration: str) -> None:
        self._http.post_json(f"/api/integrations/ingest/{integration}/cancel")


class UnityCatalogMetadataIntegrationsApi(ApiGroup):
    """Unity Catalog metadata writers."""

    def list(self, *, enabled: bool | None = None) -> list[UnityCatalogMetadataIntegration]:
        return self._http.get_list(
            "/api/integrations/unity-catalog-metadata", UnityCatalogMetadataIntegration, params={"enabled": enabled}
        )

    def get(self, integration: str) -> UnityCatalogMetadataIntegration:
        return self._http.get_model(
            f"/api/integrations/unity-catalog-metadata/{integration}", UnityCatalogMetadataIntegration
        )

    def put(
        self, integration: str, request: UnityCatalogMetadataIntegrationRequest | dict[str, Any]
    ) -> UnityCatalogMetadataIntegration:
        return self._http.put_model(
            f"/api/integrations/unity-catalog-metadata/{integration}", request, UnityCatalogMetadataIntegration
        )

    def delete(self, integration: str) -> None:
        self._http.delete(f"/api/integrations/unity-catalog-metadata/{integration}")

    def list_tables(self, integration: str, *, state: str | None = None) -> list[UnityCatalogMetadataTable]:
        return self._http.get_list(
            f"/api/integrations/unity-catalog-metadata/{integration}/tables",
            UnityCatalogMetadataTable,
            params={"state": state},
        )

    def list_queue(self, integration: str) -> list[UnityCatalogMetadataQueueEntry]:
        return self._http.get_list(
            f"/api/integrations/unity-catalog-metadata/{integration}/queue", UnityCatalogMetadataQueueEntry
        )

    def retry_failed_tables(self, integration: str) -> UnityCatalogMetadataActionResponse:
        return self._http.post_model(
            f"/api/integrations/unity-catalog-metadata/{integration}/tables/retry-failed",
            UnityCatalogMetadataActionResponse,
        )

    def discard_queue(self, integration: str) -> UnityCatalogMetadataActionResponse:
        return self._http.post_model(
            f"/api/integrations/unity-catalog-metadata/{integration}/queue/discard",
            UnityCatalogMetadataActionResponse,
        )


class IntegrationsApi(ApiGroup):
    def __init__(self, http):
        super().__init__(http)
        self.ingest = IngestIntegrationsApi(http)
        self.unity_catalog_metadata = UnityCatalogMetadataIntegrationsApi(http)
