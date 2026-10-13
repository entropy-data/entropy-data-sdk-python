from __future__ import annotations

from typing import Any

from entropy_data_sdk._http import Page, seg
from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import DataProductBuilder


class DataProductBuildersApi(ApiGroup):
    def list(self) -> Page[DataProductBuilder]:
        return self._http.get_list("/api/dataproductbuilders", DataProductBuilder)

    def get(self, id: str) -> DataProductBuilder:
        return self._http.get_model(f"/api/dataproductbuilders/{seg(id)}", DataProductBuilder)

    def put(self, id: str, builder: DataProductBuilder | dict[str, Any]) -> DataProductBuilder:
        return self._http.put_model(f"/api/dataproductbuilders/{seg(id)}", builder, DataProductBuilder)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/dataproductbuilders/{seg(id)}")
