from __future__ import annotations

from typing import Any

from entropy_data_sdk._http import Page, seg
from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import Asset, AssetTags


class AssetsApi(ApiGroup):
    def list(self, *, page: int | None = None) -> Page[Asset]:
        return self._http.get_list("/api/assets", Asset, params={"p": page})

    def get(self, id: str) -> Asset:
        return self._http.get_model(f"/api/assets/{seg(id)}", Asset)

    def put(self, id: str, asset: Asset | dict[str, Any]) -> None:
        self._http.put_json(f"/api/assets/{seg(id)}", asset)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/assets/{seg(id)}")

    def get_assigned_tags(self, id: str) -> AssetTags:
        return self._http.get_model(f"/api/assets/{seg(id)}/assigned-tags", AssetTags)

    def assign_tag(self, id: str, tag_id: str) -> None:
        self._http.put_json(f"/api/assets/{seg(id)}/assigned-tags/{seg(tag_id)}", {})

    def unassign_tag(self, id: str, tag_id: str) -> None:
        self._http.delete(f"/api/assets/{seg(id)}/assigned-tags/{seg(tag_id)}")
