from __future__ import annotations

from typing import Any

from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import (
    ScimGroup,
    ScimListResponseGroups,
    ScimListResponseResourceTypes,
    ScimListResponseSchemas,
    ScimListResponseUsers,
    ScimPatchRequest,
    ScimResourceType,
    ScimSchema,
    ScimServiceProviderConfig,
    ScimUser,
)


class ScimApi(ApiGroup):
    def list_users(
        self, *, start_index: int | None = None, count: int | None = None, filter: str | None = None
    ) -> ScimListResponseUsers:
        params = {"startIndex": start_index, "count": count, "filter": filter}
        return self._http.get_model("/api/scim/v2/Users", ScimListResponseUsers, params=params)

    def create_user(self, user: ScimUser | dict[str, Any]) -> ScimUser:
        return self._http.post_model("/api/scim/v2/Users", ScimUser, user)

    def get_user(self, id: str) -> ScimUser:
        return self._http.get_model(f"/api/scim/v2/Users/{id}", ScimUser)

    def replace_user(self, id: str, user: ScimUser | dict[str, Any]) -> ScimUser:
        return self._http.put_model(f"/api/scim/v2/Users/{id}", user, ScimUser)

    def update_user(self, id: str, patch: ScimPatchRequest | dict[str, Any]) -> ScimUser:
        return self._http.patch_model(f"/api/scim/v2/Users/{id}", patch, ScimUser)

    def delete_user(self, id: str) -> None:
        self._http.delete(f"/api/scim/v2/Users/{id}")

    def list_groups(
        self, *, start_index: int | None = None, count: int | None = None, filter: str | None = None
    ) -> ScimListResponseGroups:
        params = {"startIndex": start_index, "count": count, "filter": filter}
        return self._http.get_model("/api/scim/v2/Groups", ScimListResponseGroups, params=params)

    def create_group(self, group: ScimGroup | dict[str, Any]) -> ScimGroup:
        return self._http.post_model("/api/scim/v2/Groups", ScimGroup, group)

    def get_group(self, id: str) -> ScimGroup:
        return self._http.get_model(f"/api/scim/v2/Groups/{id}", ScimGroup)

    def replace_group(self, id: str, group: ScimGroup | dict[str, Any]) -> ScimGroup:
        return self._http.put_model(f"/api/scim/v2/Groups/{id}", group, ScimGroup)

    def update_group(self, id: str, patch: ScimPatchRequest | dict[str, Any]) -> ScimGroup:
        return self._http.patch_model(f"/api/scim/v2/Groups/{id}", patch, ScimGroup)

    def delete_group(self, id: str) -> None:
        self._http.delete(f"/api/scim/v2/Groups/{id}")

    def get_service_provider_config(self) -> ScimServiceProviderConfig:
        return self._http.get_model("/api/scim/v2/ServiceProviderConfig", ScimServiceProviderConfig)

    def list_resource_types(self) -> ScimListResponseResourceTypes:
        return self._http.get_model("/api/scim/v2/ResourceTypes", ScimListResponseResourceTypes)

    def get_resource_type(self, resource_type: str) -> ScimResourceType:
        return self._http.get_model(f"/api/scim/v2/ResourceTypes/{resource_type}", ScimResourceType)

    def list_schemas(self) -> ScimListResponseSchemas:
        return self._http.get_model("/api/scim/v2/Schemas", ScimListResponseSchemas)

    def get_schema(self, schema_id: str) -> ScimSchema:
        return self._http.get_model(f"/api/scim/v2/Schemas/{schema_id}", ScimSchema)
