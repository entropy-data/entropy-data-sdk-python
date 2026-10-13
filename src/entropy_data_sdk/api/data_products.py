from __future__ import annotations

from typing import Any

from entropy_data_sdk._http import Page, seg
from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import (
    GitConnectionRequest,
    GitConnectionResponse,
    GitImportRequest,
    GitPullRequestRequest,
    GitPushRequest,
)

DataProduct = dict[str, Any]
"""A data product document (Data Product Specification or ODPS). Passed through unchanged."""


class DataProductsApi(ApiGroup):
    def list(
        self,
        *,
        q: str | None = None,
        team_id: str | None = None,
        domain_id: str | None = None,
        type: str | None = None,
        archetype: str | None = None,
        status: str | None = None,
        tag: str | None = None,
        sort: str | None = None,
        page: int | None = None,
    ) -> Page[DataProduct]:
        params = {
            "q": q,
            "teamId": team_id,
            "domainId": domain_id,
            "type": type,
            "archetype": archetype,
            "status": status,
            "tag": tag,
            "sort": sort,
            "p": page,
        }
        return self._http.get_page("/api/dataproducts", params=params)

    def get(self, id: str) -> DataProduct:
        return self._http.get_json(f"/api/dataproducts/{seg(id)}")

    def put(self, id: str, data_product: DataProduct) -> None:
        self._http.put_json(f"/api/dataproducts/{seg(id)}", data_product)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/dataproducts/{seg(id)}")

    def get_star(self, id: str) -> dict[str, Any]:
        """Return ``{"count": int, "starredByMe": bool}``."""
        return self._http.get_json(f"/api/dataproducts/{seg(id)}/star")

    def star(self, id: str) -> None:
        self._http.put_json(f"/api/dataproducts/{seg(id)}/star", {})

    def unstar(self, id: str) -> None:
        self._http.delete(f"/api/dataproducts/{seg(id)}/star")

    def stargazers(self, id: str) -> list[dict[str, Any]]:
        return self._http.get_json(f"/api/dataproducts/{seg(id)}/stargazers")

    def import_from_git(self, request: GitImportRequest | dict[str, Any]) -> GitConnectionResponse:
        return self._http.post_model("/api/dataproducts/import/git", GitConnectionResponse, request)

    def get_git_connection(self, id: str) -> GitConnectionResponse:
        return self._http.get_model(f"/api/dataproducts/{seg(id)}/gitconnection", GitConnectionResponse)

    def put_git_connection(self, id: str, request: GitConnectionRequest | dict[str, Any]) -> GitConnectionResponse:
        return self._http.put_model(f"/api/dataproducts/{seg(id)}/gitconnection", request, GitConnectionResponse)

    def delete_git_connection(self, id: str) -> None:
        self._http.delete(f"/api/dataproducts/{seg(id)}/gitconnection")

    def pull_from_git(self, id: str) -> GitConnectionResponse:
        return self._http.post_model(f"/api/dataproducts/{seg(id)}/gitconnection/pull", GitConnectionResponse)

    def push_to_git(self, id: str, request: GitPushRequest | dict[str, Any]) -> GitConnectionResponse:
        return self._http.post_model(f"/api/dataproducts/{seg(id)}/gitconnection/push", GitConnectionResponse, request)

    def push_to_git_as_pull_request(
        self, id: str, request: GitPullRequestRequest | dict[str, Any]
    ) -> GitConnectionResponse:
        return self._http.post_model(
            f"/api/dataproducts/{seg(id)}/gitconnection/push-pr", GitConnectionResponse, request
        )
