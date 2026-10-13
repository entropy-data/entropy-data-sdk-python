from __future__ import annotations

from datetime import date
from typing import Any

from entropy_data_sdk._http import YAML, Page, seg
from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import (
    ApiKeyCreated,
    Customization,
    DataProductTypes,
    EmailTemplatesSettings,
    GitCredentialCreateRequest,
    GitCredentialResponse,
    GitCredentialUpdateRequest,
    OrganizationFeatures,
    OrganizationMember,
    OrganizationSettings,
    ScimMappingConfiguration,
    TeamRolesSettings,
)


class OrganizationApi(ApiGroup):
    def get_features(self) -> OrganizationFeatures:
        return self._http.get_model("/api/organization/features", OrganizationFeatures)

    def put_features(self, features: OrganizationFeatures | dict[str, Any]) -> OrganizationFeatures:
        return self._http.put_model("/api/organization/features", features, OrganizationFeatures)

    def get_settings(self) -> OrganizationSettings:
        return self._http.get_model("/api/organization/settings", OrganizationSettings)

    def list_members(self, *, page: int | None = None) -> Page[OrganizationMember]:
        return self._http.get_list("/api/organization/members", OrganizationMember, params={"p": page})

    def get_member(self, email_address: str) -> OrganizationMember:
        return self._http.get_model(f"/api/organization/members/{seg(email_address)}", OrganizationMember)

    # Organization git credentials

    def list_git_credentials(self) -> Page[GitCredentialResponse]:
        return self._http.get_list("/api/organization/gitcredentials", GitCredentialResponse)

    def create_git_credential(self, request: GitCredentialCreateRequest | dict[str, Any]) -> GitCredentialResponse:
        return self._http.post_model("/api/organization/gitcredentials", GitCredentialResponse, request)

    def get_git_credential(self, git_credential_id: str) -> GitCredentialResponse:
        return self._http.get_model(f"/api/organization/gitcredentials/{seg(git_credential_id)}", GitCredentialResponse)

    def update_git_credential(
        self, git_credential_id: str, request: GitCredentialUpdateRequest | dict[str, Any]
    ) -> GitCredentialResponse:
        return self._http.put_model(
            f"/api/organization/gitcredentials/{seg(git_credential_id)}", request, GitCredentialResponse
        )

    def delete_git_credential(self, git_credential_id: str) -> None:
        self._http.delete(f"/api/organization/gitcredentials/{seg(git_credential_id)}")

    # Settings

    def get_customization(self) -> Customization:
        return self._http.get_model("/api/settings/customization", Customization)

    def get_customization_yaml(self) -> str:
        return self._http.get_text("/api/settings/customization", accept=YAML)

    def put_customization(self, customization: Customization | dict[str, Any]) -> None:
        self._http.put_json("/api/settings/customization", customization)

    def put_customization_yaml(self, yaml_text: str) -> None:
        self._http.put_text("/api/settings/customization", yaml_text)

    def get_scim_mapping(self) -> ScimMappingConfiguration:
        return self._http.get_model("/api/settings/scim-mapping", ScimMappingConfiguration)

    def get_scim_mapping_yaml(self) -> str:
        return self._http.get_text("/api/settings/scim-mapping", accept=YAML)

    def put_scim_mapping(self, mapping: ScimMappingConfiguration | dict[str, Any]) -> None:
        self._http.put_json("/api/settings/scim-mapping", mapping)

    def put_scim_mapping_yaml(self, yaml_text: str) -> None:
        self._http.put_text("/api/settings/scim-mapping", yaml_text)

    def get_email_templates(self) -> EmailTemplatesSettings:
        return self._http.get_model("/api/settings/email-templates", EmailTemplatesSettings)

    def put_email_templates(self, templates: EmailTemplatesSettings | dict[str, Any]) -> EmailTemplatesSettings:
        return self._http.put_model("/api/settings/email-templates", templates, EmailTemplatesSettings)

    def get_data_product_types(self) -> DataProductTypes:
        return self._http.get_model("/api/settings/dataproduct-types", DataProductTypes)

    def get_data_product_types_yaml(self) -> str:
        return self._http.get_text("/api/settings/dataproduct-types", accept=YAML)

    def put_data_product_types(self, types: DataProductTypes | dict[str, Any]) -> None:
        self._http.put_json("/api/settings/dataproduct-types", types)

    def put_data_product_types_yaml(self, yaml_text: str) -> None:
        self._http.put_text("/api/settings/dataproduct-types", yaml_text)

    def get_team_roles(self) -> TeamRolesSettings:
        return self._http.get_model("/api/settings/team-roles", TeamRolesSettings)

    def put_team_roles(self, settings: TeamRolesSettings | dict[str, Any]) -> TeamRolesSettings:
        return self._http.put_model("/api/settings/team-roles", settings, TeamRolesSettings)

    # API keys

    def create_api_key(
        self,
        *,
        scope: str,
        team_id: str | None = None,
        display_name: str | None = None,
        expires_at: date | str | None = None,
        permissions: list[str] | None = None,
    ) -> ApiKeyCreated:
        body = {
            "scope": scope,
            "teamId": team_id,
            "displayName": display_name,
            "expiresAt": expires_at.isoformat() if isinstance(expires_at, date) else expires_at,
            "permissions": permissions,
        }
        return self._http.post_model(
            "/api/api-keys", ApiKeyCreated, {key: value for key, value in body.items() if value is not None}
        )

    def delete_api_key(self, organization_api_key_id: str) -> None:
        self._http.delete(f"/api/api-keys/{seg(organization_api_key_id)}")
