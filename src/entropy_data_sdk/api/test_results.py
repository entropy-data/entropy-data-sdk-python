from __future__ import annotations

from typing import Any

from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import TestResults


class TestResultsApi(ApiGroup):
    def list(
        self,
        *,
        data_contract_id: str | None = None,
        branch: str | None = None,
        server: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        page: int | None = None,
        size: int | None = None,
    ) -> list[TestResults]:
        params = {
            "dataContractId": data_contract_id,
            "branch": branch,
            "server": server,
            "from": from_,
            "to": to,
            "p": page,
            "size": size,
        }
        return self._http.get_list("/api/test-results", TestResults, params=params)

    def get(self, id: str) -> TestResults:
        return self._http.get_model(f"/api/test-results/{id}", TestResults)

    def post(self, test_results: TestResults | dict[str, Any]) -> None:
        self._http.post_json("/api/test-results", test_results)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/test-results/{id}")
