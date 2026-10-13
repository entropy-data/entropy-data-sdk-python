from __future__ import annotations

import logging

from entropy_data_sdk.client import EntropyDataClient
from entropy_data_sdk.errors import NotFoundError
from entropy_data_sdk.models import Connector, ConnectorInfo

log = logging.getLogger(__name__)


class ConnectorRegistration:
    """Registers a connector in Entropy Data so its state and health are visible there.

    ``connector_id`` must stay constant across restarts: it identifies the connector and keys its stored state.
    ``connector_type`` is free text such as ``databricks-assets`` or ``snowflake-access``.
    """

    def __init__(
        self, client: EntropyDataClient, connector_id: str, connector_type: str, connector_version: str | None = None
    ):
        if not connector_id:
            raise ValueError("connector_id is required")
        if not connector_type:
            raise ValueError("connector_type is required")
        self.client = client
        self.id = connector_id
        self.type = connector_type
        self.connector_version = connector_version

    def register(self) -> Connector:
        try:
            log.debug("Checking if connector %s already exists", self.id)
            connector = self.client.connectors.get(self.id)
        except NotFoundError:
            connector = Connector(id=self.id, info=ConnectorInfo())
        connector.id = self.id
        connector.info = ConnectorInfo(
            type=self.type,
            description=connector.info.description if connector.info else None,
            connectorVersion=self.connector_version,
        )
        log.info("Registering connector %s", self.id)
        self.client.connectors.put(self.id, connector)
        return connector

    def delete(self) -> None:
        log.info("Deleting connector %s", self.id)
        try:
            self.client.connectors.delete(self.id)
        except NotFoundError:
            log.error("Connector %s already deleted", self.id)
