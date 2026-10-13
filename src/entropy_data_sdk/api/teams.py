from __future__ import annotations

from typing import Any

from entropy_data_sdk._http import Page, seg
from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import (
    GitCredentialCreateRequest,
    GitCredentialResponse,
    GitCredentialUpdateRequest,
    NotificationChannel,
    Team,
)


class TeamsApi(ApiGroup):
    def list(self, *, page: int | None = None, email: str | None = None) -> Page[Team]:
        return self._http.get_list("/api/teams", Team, params={"p": page, "email": email})

    def get(self, id: str) -> Team:
        return self._http.get_model(f"/api/teams/{seg(id)}", Team)

    def put(self, id: str, team: Team | dict[str, Any]) -> None:
        self._http.put_json(f"/api/teams/{seg(id)}", team)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/teams/{seg(id)}")

    # Notification channels

    def list_notification_channels(self, team_id: str) -> Page[NotificationChannel]:
        return self._http.get_list(f"/api/teams/{seg(team_id)}/notification-channels", NotificationChannel)

    def get_notification_channel(self, team_id: str, channel_id: str) -> NotificationChannel:
        return self._http.get_model(
            f"/api/teams/{seg(team_id)}/notification-channels/{seg(channel_id)}", NotificationChannel
        )

    def put_notification_channel(
        self, team_id: str, channel_id: str, channel: NotificationChannel | dict[str, Any]
    ) -> None:
        self._http.put_json(f"/api/teams/{seg(team_id)}/notification-channels/{seg(channel_id)}", channel)

    def delete_notification_channel(self, team_id: str, channel_id: str) -> None:
        self._http.delete(f"/api/teams/{seg(team_id)}/notification-channels/{seg(channel_id)}")

    # Git credentials

    def list_git_credentials(self, team_id: str) -> Page[GitCredentialResponse]:
        return self._http.get_list(f"/api/teams/{seg(team_id)}/gitcredentials", GitCredentialResponse)

    def create_git_credential(
        self, team_id: str, request: GitCredentialCreateRequest | dict[str, Any]
    ) -> GitCredentialResponse:
        return self._http.post_model(f"/api/teams/{seg(team_id)}/gitcredentials", GitCredentialResponse, request)

    def get_git_credential(self, team_id: str, git_credential_id: str) -> GitCredentialResponse:
        return self._http.get_model(
            f"/api/teams/{seg(team_id)}/gitcredentials/{seg(git_credential_id)}", GitCredentialResponse
        )

    def update_git_credential(
        self, team_id: str, git_credential_id: str, request: GitCredentialUpdateRequest | dict[str, Any]
    ) -> GitCredentialResponse:
        return self._http.put_model(
            f"/api/teams/{seg(team_id)}/gitcredentials/{seg(git_credential_id)}", request, GitCredentialResponse
        )

    def delete_git_credential(self, team_id: str, git_credential_id: str) -> None:
        self._http.delete(f"/api/teams/{seg(team_id)}/gitcredentials/{seg(git_credential_id)}")
