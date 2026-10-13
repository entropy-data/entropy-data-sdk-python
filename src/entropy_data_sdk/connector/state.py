from __future__ import annotations

import logging
from typing import Any, Protocol

from entropy_data_sdk.client import EntropyDataClient
from entropy_data_sdk.errors import NotFoundError

log = logging.getLogger(__name__)

State = dict[str, Any]


class StateRepository(Protocol):
    """Where a connector keeps what it has processed, for example the last event id."""

    def get_state(self) -> State: ...

    def save_state(self, state: State) -> None: ...


class InMemoryStateRepository:
    """Keeps the state in the process. Lost on restart, so meant for tests."""

    def __init__(self, connector_id: str):
        self.connector_id = connector_id
        self._state: dict[str, State] = {}

    def get_state(self) -> State:
        return dict(self._state.get(self.connector_id, {}))

    def save_state(self, state: State) -> None:
        self._state[self.connector_id] = dict(state)


class RemoteStateRepository:
    """Stores the state on the connector resource in Entropy Data. The connector must be registered first."""

    def __init__(self, connector_id: str, client: EntropyDataClient):
        self.connector_id = connector_id
        self.client = client

    def get_state(self) -> State:
        return dict(self.client.connectors.get(self.connector_id).state or {})

    def save_state(self, state: State) -> None:
        try:
            connector = self.client.connectors.get(self.connector_id)
        except NotFoundError:
            log.error("Connector %s not found, register it first", self.connector_id)
            raise
        connector.state = dict(state)
        self.client.connectors.put(self.connector_id, connector)
