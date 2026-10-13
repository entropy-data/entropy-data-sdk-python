from __future__ import annotations

from typing import Any

from entropy_data_sdk._http import Page, seg
from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import Tag


class TagsApi(ApiGroup):
    def list(self, *, page: int | None = None, owner: str | None = None) -> Page[Tag]:
        return self._http.get_list("/api/tags", Tag, params={"p": page, "owner": owner})

    def get(self, id: str) -> Tag:
        return self._http.get_model(f"/api/tags/{seg(id)}", Tag)

    def put(self, id: str, tag: Tag | dict[str, Any]) -> None:
        self._http.put_json(f"/api/tags/{seg(id)}", tag)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/tags/{seg(id)}")
