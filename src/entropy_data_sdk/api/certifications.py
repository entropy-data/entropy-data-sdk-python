from __future__ import annotations

from typing import Any

from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import Certification


class CertificationsApi(ApiGroup):
    def list(self) -> list[Certification]:
        return self._http.get_list("/api/certifications", Certification)

    def get(self, id: str) -> Certification:
        return self._http.get_model(f"/api/certifications/{id}", Certification)

    def put(self, id: str, certification: Certification | dict[str, Any]) -> None:
        self._http.put_json(f"/api/certifications/{id}", certification)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/certifications/{id}")
