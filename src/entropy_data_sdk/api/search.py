from __future__ import annotations

from typing import Any

from entropy_data_sdk.api._base import ApiGroup


class SearchApi(ApiGroup):
    def query(
        self,
        query: str,
        *,
        search_mode: str | None = None,
        resource_type: str | None = None,
        diagnostics: bool | None = None,
    ) -> dict[str, Any]:
        params = {"query": query, "searchMode": search_mode, "resourceType": resource_type, "diagnostics": diagnostics}
        return self._http.get_json("/api/search", params=params)
