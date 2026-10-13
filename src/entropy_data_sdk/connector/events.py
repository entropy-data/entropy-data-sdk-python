"""Long-running event listener and the handler base class connectors subclass."""

from __future__ import annotations

import logging
import threading
from datetime import timedelta

from pydantic import BaseModel

from entropy_data_sdk.api.events import CloudEvent
from entropy_data_sdk.client import EntropyDataClient
from entropy_data_sdk.connector.registration import ConnectorRegistration
from entropy_data_sdk.connector.state import StateRepository
from entropy_data_sdk.models import (
    AccessActivatedEvent,
    AccessApprovedEvent,
    AccessCanceledEvent,
    AccessCreatedEvent,
    AccessDeactivatedEvent,
    AccessDeletedEvent,
    AccessDeprovisionedEvent,
    AccessDeprovisioningFailedEvent,
    AccessDeprovisioningStartedEvent,
    AccessProvisionedEvent,
    AccessProvisioningFailedEvent,
    AccessProvisioningStartedEvent,
    AccessRejectedEvent,
    AccessRequestedEvent,
    AccessUpdatedEvent,
    AssetCreatedEvent,
    AssetDeletedEvent,
    AssetUpdatedEvent,
    DataContractCreatedEvent,
    DataContractDeletedEvent,
    DataContractUpdatedEvent,
    DataProductCreatedEvent,
    DataProductDeletedEvent,
    DataProductUpdatedEvent,
    DefinitionCreatedEvent,
    DefinitionDeletedEvent,
    DefinitionUpdatedEvent,
    OutputPortCreatedEvent,
    OutputPortDeletedEvent,
    OutputPortUpdatedEvent,
    SourceSystemCreatedEvent,
    SourceSystemDeletedEvent,
    SourceSystemUpdatedEvent,
    TagCreatedEvent,
    TagDeletedEvent,
    TagUpdatedEvent,
    TeamCreatedEvent,
    TeamDeletedEvent,
    TeamUpdatedEvent,
    TestResultsCreatedEvent,
    TestResultsDeletedEvent,
)

log = logging.getLogger(__name__)

LAST_EVENT_ID = "lastEventId"
DEPRECATED_EVENT_PREFIX = "DataUsageAgreement"


class EventHandler:
    """Override the methods for the events the connector cares about. Every method is a no-op by default."""

    def on_event(self, event: CloudEvent) -> None:
        """Called for every event, before the typed method."""

    def on_data_product_created(self, event: DataProductCreatedEvent) -> None:
        pass

    def on_data_product_updated(self, event: DataProductUpdatedEvent) -> None:
        pass

    def on_data_product_deleted(self, event: DataProductDeletedEvent) -> None:
        pass

    def on_output_port_created(self, event: OutputPortCreatedEvent) -> None:
        pass

    def on_output_port_updated(self, event: OutputPortUpdatedEvent) -> None:
        pass

    def on_output_port_deleted(self, event: OutputPortDeletedEvent) -> None:
        pass

    def on_data_contract_created(self, event: DataContractCreatedEvent) -> None:
        pass

    def on_data_contract_updated(self, event: DataContractUpdatedEvent) -> None:
        pass

    def on_data_contract_deleted(self, event: DataContractDeletedEvent) -> None:
        pass

    def on_access_created(self, event: AccessCreatedEvent) -> None:
        pass

    def on_access_updated(self, event: AccessUpdatedEvent) -> None:
        pass

    def on_access_deleted(self, event: AccessDeletedEvent) -> None:
        pass

    def on_access_requested(self, event: AccessRequestedEvent) -> None:
        pass

    def on_access_approved(self, event: AccessApprovedEvent) -> None:
        pass

    def on_access_rejected(self, event: AccessRejectedEvent) -> None:
        pass

    def on_access_activated(self, event: AccessActivatedEvent) -> None:
        pass

    def on_access_deactivated(self, event: AccessDeactivatedEvent) -> None:
        pass

    def on_access_canceled(self, event: AccessCanceledEvent) -> None:
        pass

    def on_access_provisioning_started(self, event: AccessProvisioningStartedEvent) -> None:
        pass

    def on_access_provisioned(self, event: AccessProvisionedEvent) -> None:
        pass

    def on_access_provisioning_failed(self, event: AccessProvisioningFailedEvent) -> None:
        pass

    def on_access_deprovisioning_started(self, event: AccessDeprovisioningStartedEvent) -> None:
        pass

    def on_access_deprovisioned(self, event: AccessDeprovisionedEvent) -> None:
        pass

    def on_access_deprovisioning_failed(self, event: AccessDeprovisioningFailedEvent) -> None:
        pass

    def on_source_system_created(self, event: SourceSystemCreatedEvent) -> None:
        pass

    def on_source_system_updated(self, event: SourceSystemUpdatedEvent) -> None:
        pass

    def on_source_system_deleted(self, event: SourceSystemDeletedEvent) -> None:
        pass

    def on_team_created(self, event: TeamCreatedEvent) -> None:
        pass

    def on_team_updated(self, event: TeamUpdatedEvent) -> None:
        pass

    def on_team_deleted(self, event: TeamDeletedEvent) -> None:
        pass

    def on_definition_created(self, event: DefinitionCreatedEvent) -> None:
        pass

    def on_definition_updated(self, event: DefinitionUpdatedEvent) -> None:
        pass

    def on_definition_deleted(self, event: DefinitionDeletedEvent) -> None:
        pass

    def on_tag_created(self, event: TagCreatedEvent) -> None:
        pass

    def on_tag_updated(self, event: TagUpdatedEvent) -> None:
        pass

    def on_tag_deleted(self, event: TagDeletedEvent) -> None:
        pass

    def on_asset_created(self, event: AssetCreatedEvent) -> None:
        pass

    def on_asset_updated(self, event: AssetUpdatedEvent) -> None:
        pass

    def on_asset_deleted(self, event: AssetDeletedEvent) -> None:
        pass

    def on_test_results_created(self, event: TestResultsCreatedEvent) -> None:
        pass

    def on_test_results_deleted(self, event: TestResultsDeletedEvent) -> None:
        pass


_DISPATCH: dict[str, tuple[str, type[BaseModel]]] = {
    "DataProductCreatedEvent": ("on_data_product_created", DataProductCreatedEvent),
    "DataProductUpdatedEvent": ("on_data_product_updated", DataProductUpdatedEvent),
    "DataProductDeletedEvent": ("on_data_product_deleted", DataProductDeletedEvent),
    "OutputPortCreatedEvent": ("on_output_port_created", OutputPortCreatedEvent),
    "OutputPortUpdatedEvent": ("on_output_port_updated", OutputPortUpdatedEvent),
    "OutputPortDeletedEvent": ("on_output_port_deleted", OutputPortDeletedEvent),
    "DataContractCreatedEvent": ("on_data_contract_created", DataContractCreatedEvent),
    "DataContractUpdatedEvent": ("on_data_contract_updated", DataContractUpdatedEvent),
    "DataContractDeletedEvent": ("on_data_contract_deleted", DataContractDeletedEvent),
    "AccessCreatedEvent": ("on_access_created", AccessCreatedEvent),
    "AccessUpdatedEvent": ("on_access_updated", AccessUpdatedEvent),
    "AccessDeletedEvent": ("on_access_deleted", AccessDeletedEvent),
    "AccessRequestedEvent": ("on_access_requested", AccessRequestedEvent),
    "AccessApprovedEvent": ("on_access_approved", AccessApprovedEvent),
    "AccessRejectedEvent": ("on_access_rejected", AccessRejectedEvent),
    "AccessActivatedEvent": ("on_access_activated", AccessActivatedEvent),
    "AccessDeactivatedEvent": ("on_access_deactivated", AccessDeactivatedEvent),
    "AccessCanceledEvent": ("on_access_canceled", AccessCanceledEvent),
    "AccessProvisioningStartedEvent": ("on_access_provisioning_started", AccessProvisioningStartedEvent),
    "AccessProvisionedEvent": ("on_access_provisioned", AccessProvisionedEvent),
    "AccessProvisioningFailedEvent": ("on_access_provisioning_failed", AccessProvisioningFailedEvent),
    "AccessDeprovisioningStartedEvent": ("on_access_deprovisioning_started", AccessDeprovisioningStartedEvent),
    "AccessDeprovisionedEvent": ("on_access_deprovisioned", AccessDeprovisionedEvent),
    "AccessDeprovisioningFailedEvent": ("on_access_deprovisioning_failed", AccessDeprovisioningFailedEvent),
    "SourceSystemCreatedEvent": ("on_source_system_created", SourceSystemCreatedEvent),
    "SourceSystemUpdatedEvent": ("on_source_system_updated", SourceSystemUpdatedEvent),
    "SourceSystemDeletedEvent": ("on_source_system_deleted", SourceSystemDeletedEvent),
    "TeamCreatedEvent": ("on_team_created", TeamCreatedEvent),
    "TeamUpdatedEvent": ("on_team_updated", TeamUpdatedEvent),
    "TeamDeletedEvent": ("on_team_deleted", TeamDeletedEvent),
    "DefinitionCreatedEvent": ("on_definition_created", DefinitionCreatedEvent),
    "DefinitionUpdatedEvent": ("on_definition_updated", DefinitionUpdatedEvent),
    "DefinitionDeletedEvent": ("on_definition_deleted", DefinitionDeletedEvent),
    "TagCreatedEvent": ("on_tag_created", TagCreatedEvent),
    "TagUpdatedEvent": ("on_tag_updated", TagUpdatedEvent),
    "TagDeletedEvent": ("on_tag_deleted", TagDeletedEvent),
    "AssetCreatedEvent": ("on_asset_created", AssetCreatedEvent),
    "AssetUpdatedEvent": ("on_asset_updated", AssetUpdatedEvent),
    "AssetDeletedEvent": ("on_asset_deleted", AssetDeletedEvent),
    "TestResultsCreatedEvent": ("on_test_results_created", TestResultsCreatedEvent),
    "TestResultsDeletedEvent": ("on_test_results_deleted", TestResultsDeletedEvent),
}


class EventListener:
    """Polls the event feed and dispatches each event to the handler, remembering the last processed event id.

    :meth:`start` blocks and loops until :meth:`stop` is called from another thread.
    """

    def __init__(
        self,
        connector_id: str,
        connector_type: str,
        client: EntropyDataClient,
        event_handler: EventHandler,
        state_repository: StateRepository,
        connector_version: str | None = None,
        *,
        poll_interval: timedelta = timedelta(seconds=5),
        error_backoff: timedelta = timedelta(seconds=30),
    ):
        self.connector_id = connector_id
        self.client = client
        self.event_handler = event_handler
        self.state_repository = state_repository
        self.poll_interval = poll_interval
        self.error_backoff = error_backoff
        self._stop = threading.Event()
        self.registration = ConnectorRegistration(client, connector_id, connector_type, connector_version)
        self.registration.register()

    def start(self) -> None:
        log.info("%s: start polling for events", self.connector_id)
        self._stop.clear()
        last_event_id = self.get_last_event_id()
        while not self._stop.is_set():
            try:
                events = self.fetch_events(last_event_id)
                for event in events:
                    self.process_event(event)
                    last_event_id = event.id
                    self.save_last_event_id(last_event_id)
                if not events:
                    log.debug("No new events, next poll in %s", self.poll_interval)
                    self._stop.wait(self.poll_interval.total_seconds())
            except Exception:
                log.exception("Failed to process events, next attempt in %s", self.error_backoff)
                self._stop.wait(self.error_backoff.total_seconds())
        log.info("%s: stopped polling for events", self.connector_id)

    def stop(self) -> None:
        if self._stop.is_set():
            log.info("%s: polling for events already stopped", self.connector_id)
            return
        self._stop.set()

    def get_last_event_id(self) -> str | None:
        return self.state_repository.get_state().get(LAST_EVENT_ID)

    def save_last_event_id(self, last_event_id: str) -> None:
        self.state_repository.save_state({LAST_EVENT_ID: last_event_id})

    def fetch_events(self, last_event_id: str | None) -> list[CloudEvent]:
        log.debug("Fetching events after %s", last_event_id)
        events = self.client.events.poll(last_event_id=last_event_id)
        log.debug("Fetched %d events", len(events))
        return events

    def process_event(self, event: CloudEvent) -> None:
        log.info("Processing event %s of type %s", event.id, event.type)
        self.event_handler.on_event(event)
        name = event.event_name
        dispatch = _DISPATCH.get(name)
        if dispatch is None:
            if name.startswith(DEPRECATED_EVENT_PREFIX):
                log.debug("Ignoring deprecated event %s", event.type)
            else:
                log.warning("Unknown event type %s", event.type)
            return
        method_name, model = dispatch
        getattr(self.event_handler, method_name)(model.model_validate(event.data or {}))
