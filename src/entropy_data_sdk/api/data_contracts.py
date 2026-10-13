from __future__ import annotations

from typing import Any

from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import (
    DataContractBranch,
    DataContractBranchChange,
    GenerateRequest,
    GenerateResponse,
    GitConnectionRequest,
    GitConnectionResponse,
    GitImportRequest,
    GitPullRequestRequest,
    GitPushRequest,
    SemanticBranchMergeRequest,
    TestResults,
)

DataContract = dict[str, Any]
"""A data contract document (ODCS, or the deprecated DCS). Passed through unchanged."""


class DataContractsApi(ApiGroup):
    def list(
        self,
        *,
        q: str | None = None,
        owner: str | None = None,
        domain: str | None = None,
        team_id: str | None = None,
        domain_id: str | None = None,
        tag: str | None = None,
        status: str | None = None,
        sort: str | None = None,
        page: int | None = None,
    ) -> list[DataContract]:
        params = {
            "q": q,
            "owner": owner,
            "domain": domain,
            "teamId": team_id,
            "domainId": domain_id,
            "tag": tag,
            "status": status,
            "sort": sort,
            "p": page,
        }
        return self._http.get_json("/api/datacontracts", params=params)

    def get(self, id: str) -> DataContract:
        return self._http.get_json(f"/api/datacontracts/{id}")

    def put(self, id: str, data_contract: DataContract) -> None:
        self._http.put_json(f"/api/datacontracts/{id}", data_contract)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/datacontracts/{id}")

    def get_yaml(self, id: str) -> str:
        return self._http.get_text(f"/api/datacontracts/{id}/datacontract.yaml")

    def test(self, id: str, *, server: str | None = None, timeout: float | None = None) -> TestResults:
        return self._http.post_model(
            f"/api/datacontracts/{id}/test", TestResults, params={"server": server}, timeout=timeout
        )

    def generate(
        self, id: str, request: GenerateRequest | dict[str, Any], *, timeout: float | None = None
    ) -> GenerateResponse:
        return self._http.post_model(f"/api/datacontracts/{id}/generate", GenerateResponse, request, timeout=timeout)

    def import_from_git(self, request: GitImportRequest | dict[str, Any]) -> GitConnectionResponse:
        return self._http.post_model("/api/datacontracts/import/git", GitConnectionResponse, request)

    def get_git_connection(self, id: str) -> GitConnectionResponse:
        return self._http.get_model(f"/api/datacontracts/{id}/gitconnection", GitConnectionResponse)

    def put_git_connection(self, id: str, request: GitConnectionRequest | dict[str, Any]) -> GitConnectionResponse:
        return self._http.put_model(f"/api/datacontracts/{id}/gitconnection", request, GitConnectionResponse)

    def delete_git_connection(self, id: str) -> None:
        self._http.delete(f"/api/datacontracts/{id}/gitconnection")

    def pull_from_git(self, id: str) -> GitConnectionResponse:
        return self._http.post_model(f"/api/datacontracts/{id}/gitconnection/pull", GitConnectionResponse)

    def push_to_git(self, id: str, request: GitPushRequest | dict[str, Any]) -> GitConnectionResponse:
        return self._http.post_model(f"/api/datacontracts/{id}/gitconnection/push", GitConnectionResponse, request)

    def push_to_git_as_pull_request(
        self, id: str, request: GitPullRequestRequest | dict[str, Any]
    ) -> GitConnectionResponse:
        return self._http.post_model(f"/api/datacontracts/{id}/gitconnection/push-pr", GitConnectionResponse, request)

    # Branches

    def list_branches(self, id: str) -> list[DataContractBranch]:
        return self._http.get_list(f"/api/datacontracts/{id}/branches", DataContractBranch)

    def get_branch(self, id: str, branch: str) -> DataContractBranch:
        return self._http.get_model(f"/api/datacontracts/{id}/branches/{branch}", DataContractBranch)

    def create_branch(self, id: str, branch: str) -> DataContractBranch:
        return self._http.put_model(f"/api/datacontracts/{id}/branches/{branch}", {}, DataContractBranch)

    def delete_branch(self, id: str, branch: str) -> None:
        self._http.delete(f"/api/datacontracts/{id}/branches/{branch}")

    def rebase_branch(self, id: str, branch: str) -> DataContractBranch:
        return self._http.post_model(f"/api/datacontracts/{id}/branches/{branch}/rebase", DataContractBranch)

    def get_branch_yaml(self, id: str, branch: str) -> str:
        return self._http.get_text(f"/api/datacontracts/{id}/branches/{branch}/datacontract.yaml")

    def put_branch_yaml(self, id: str, branch: str, yaml_text: str) -> None:
        self._http.put_text(f"/api/datacontracts/{id}/branches/{branch}/datacontract.yaml", yaml_text)

    def list_branch_changes(self, id: str, branch: str) -> list[DataContractBranchChange]:
        return self._http.get_list(f"/api/datacontracts/{id}/branches/{branch}/changes", DataContractBranchChange)

    def merge_branch(
        self,
        id: str,
        branch: str,
        *,
        version: str | None = None,
        update_port_versions: bool | None = None,
        route: str | None = None,
    ) -> SemanticBranchMergeRequest | None:
        """Merge a branch. Returns the merge request when ``route`` is ``pull_request``, otherwise ``None``."""
        body = {"version": version, "update_port_versions": update_port_versions, "route": route}
        result = self._http.post_json(
            f"/api/datacontracts/{id}/branches/{branch}/merge",
            {key: value for key, value in body.items() if value is not None},
        )
        return SemanticBranchMergeRequest.model_validate(result) if result else None

    def list_branch_test_results(
        self,
        id: str,
        branch: str,
        *,
        server: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        page: int | None = None,
        size: int | None = None,
    ) -> list[TestResults]:
        params = {"server": server, "from": from_, "to": to, "p": page, "size": size}
        return self._http.get_list(
            f"/api/datacontracts/{id}/branches/{branch}/test-results", TestResults, params=params
        )

    def post_branch_test_results(self, id: str, branch: str, test_results: TestResults | dict[str, Any]) -> None:
        self._http.post_json(f"/api/datacontracts/{id}/branches/{branch}/test-results", test_results)

    def test_branch(
        self, id: str, branch: str, *, server: str | None = None, timeout: float | None = None
    ) -> TestResults:
        return self._http.post_model(
            f"/api/datacontracts/{id}/branches/{branch}/test", TestResults, params={"server": server}, timeout=timeout
        )

    def generate_branch(
        self, id: str, branch: str, request: GenerateRequest | dict[str, Any], *, timeout: float | None = None
    ) -> GenerateResponse:
        return self._http.post_model(
            f"/api/datacontracts/{id}/branches/{branch}/generate", GenerateResponse, request, timeout=timeout
        )
