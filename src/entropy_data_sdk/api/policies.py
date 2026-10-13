from __future__ import annotations

from typing import Any

from entropy_data_sdk._http import Page, seg
from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import Policy


class PoliciesApi(ApiGroup):
    def list(self) -> Page[Policy]:
        return self._http.get_list("/api/policies", Policy)

    def get(self, id: str) -> Policy:
        return self._http.get_model(f"/api/policies/{seg(id)}", Policy)

    def put(self, id: str, policy: Policy | dict[str, Any]) -> Policy:
        return self._http.put_model(f"/api/policies/{seg(id)}", policy, Policy)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/policies/{seg(id)}")
