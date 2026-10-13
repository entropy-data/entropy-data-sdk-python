from __future__ import annotations

from typing import Any

from entropy_data_sdk._http import Page, seg
from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import ClassificationScheme


class ClassificationsApi(ApiGroup):
    def list_schemes(self) -> Page[ClassificationScheme]:
        return self._http.get_list("/api/classification-schemes", ClassificationScheme)

    def get_scheme(self, scheme: str) -> ClassificationScheme:
        return self._http.get_model(f"/api/classification-schemes/{seg(scheme)}", ClassificationScheme)

    def put_scheme(self, scheme: str, body: ClassificationScheme | dict[str, Any]) -> ClassificationScheme:
        return self._http.put_model(f"/api/classification-schemes/{seg(scheme)}", body, ClassificationScheme)

    def delete_scheme(self, scheme: str) -> None:
        self._http.delete(f"/api/classification-schemes/{seg(scheme)}")
