from __future__ import annotations

from datetime import datetime
from typing import Any

from entropy_data_sdk._http import Page, seg
from entropy_data_sdk.api._base import ApiGroup
from entropy_data_sdk.models import (
    AgentApiKey,
    AgentConnection,
    AgentConnectionRequest,
    AgentIdentity,
    AgentOAuthClient,
    AgentTokenIssuer,
)


class AgentIdentitiesApi(ApiGroup):
    def list(self, *, owner: str | None = None) -> Page[AgentIdentity]:
        return self._http.get_list("/api/agent-identities", AgentIdentity, params={"owner": owner})

    def get(self, id: str) -> AgentIdentity:
        return self._http.get_model(f"/api/agent-identities/{seg(id)}", AgentIdentity)

    def put(self, id: str, agent: AgentIdentity | dict[str, Any]) -> AgentIdentity:
        return self._http.put_model(f"/api/agent-identities/{seg(id)}", agent, AgentIdentity)

    def delete(self, id: str) -> None:
        self._http.delete(f"/api/agent-identities/{seg(id)}")

    def list_api_keys(self, id: str) -> Page[AgentApiKey]:
        return self._http.get_list(f"/api/agent-identities/{seg(id)}/api-keys", AgentApiKey)

    def create_api_key(self, id: str, *, expires_at: datetime | str, display_name: str | None = None) -> AgentApiKey:
        expires = expires_at.isoformat() if isinstance(expires_at, datetime) else expires_at
        body = {"expiresAt": expires, "displayName": display_name}
        return self._http.post_model(
            f"/api/agent-identities/{seg(id)}/api-keys",
            AgentApiKey,
            {key: value for key, value in body.items() if value is not None},
        )

    def delete_api_key(self, id: str, key_id: str) -> None:
        self._http.delete(f"/api/agent-identities/{seg(id)}/api-keys/{seg(key_id)}")

    def list_oauth_clients(self, id: str) -> Page[AgentOAuthClient]:
        return self._http.get_list(f"/api/agent-identities/{seg(id)}/oauth-clients", AgentOAuthClient)

    def create_oauth_client(self, id: str, *, display_name: str | None = None) -> AgentOAuthClient:
        body = {"displayName": display_name} if display_name else {}
        return self._http.post_model(f"/api/agent-identities/{seg(id)}/oauth-clients", AgentOAuthClient, body)

    def delete_oauth_client(self, id: str, client_id: str) -> None:
        self._http.delete(f"/api/agent-identities/{seg(id)}/oauth-clients/{seg(client_id)}")

    def list_connections(self, id: str) -> Page[AgentConnection]:
        return self._http.get_list(f"/api/agent-identities/{seg(id)}/connections", AgentConnection)

    def create_connection(self, id: str, request: AgentConnectionRequest | dict[str, Any]) -> AgentConnection:
        return self._http.post_model(f"/api/agent-identities/{seg(id)}/connections", AgentConnection, request)

    def delete_connection(self, id: str, connection_id: str) -> None:
        self._http.delete(f"/api/agent-identities/{seg(id)}/connections/{seg(connection_id)}")

    def list_token_issuers(self) -> Page[AgentTokenIssuer]:
        return self._http.get_list("/api/agent-token-issuers", AgentTokenIssuer)

    def put_token_issuer(self, id: str, issuer: AgentTokenIssuer | dict[str, Any]) -> AgentTokenIssuer:
        return self._http.put_model(f"/api/agent-token-issuers/{seg(id)}", issuer, AgentTokenIssuer)

    def delete_token_issuer(self, id: str) -> None:
        self._http.delete(f"/api/agent-token-issuers/{seg(id)}")
