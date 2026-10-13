from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from datetime import timedelta
from typing import Any, Protocol

from entropy_data_sdk._http import to_payload
from entropy_data_sdk.client import EntropyDataClient
from entropy_data_sdk.connector.registration import ConnectorRegistration
from entropy_data_sdk.errors import NotFoundError
from entropy_data_sdk.models import Asset

log = logging.getLogger(__name__)

ASSETS_SYNCHRONIZER_TYPE = "assets-synchronizer"


class AssetCallback(Protocol):
    def on_asset_updated(self, asset: Asset) -> None: ...

    def on_asset_deleted(self, asset_id: str) -> None: ...


class AssetsProvider(Protocol):
    """Fetches assets (tables, views, schemas, ...) from a data platform and reports them through the callback."""

    def fetch_assets(self, callback: AssetCallback) -> None: ...


class _SynchronizerCallback:
    def __init__(self, on_updated: Callable[[Asset], None], on_deleted: Callable[[str], None]):
        self.on_asset_updated = on_updated
        self.on_asset_deleted = on_deleted


def is_subset(expected: Any, actual: Any) -> bool:
    """True when every value in ``expected`` is present in ``actual``; ``actual`` may carry more keys."""
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and is_subset(value, actual[key]) for key, value in expected.items()
        )
    if isinstance(expected, list):
        return isinstance(actual, list) and len(expected) == len(actual) and all(map(is_subset, expected, actual))
    return expected == actual


class AssetsSynchronizer:
    """Periodically asks the provider for assets and upserts them into Entropy Data.

    :meth:`start` registers the connector, then blocks and loops until :meth:`stop` is called from another thread.
    A failed run is logged and the loop waits for the next attempt, so a transient platform error does not take the
    connector down.
    """

    def __init__(
        self,
        connector_id: str,
        client: EntropyDataClient,
        assets_provider: AssetsProvider,
        connector_version: str | None = None,
        *,
        delay: timedelta = timedelta(minutes=60),
        error_backoff: timedelta = timedelta(seconds=30),
    ):
        self.connector_id = connector_id
        self.client = client
        self.assets_provider = assets_provider
        self.delay = delay
        self.error_backoff = error_backoff
        self._stop = threading.Event()
        self.registration = ConnectorRegistration(client, connector_id, ASSETS_SYNCHRONIZER_TYPE, connector_version)

    def register(self) -> None:
        self.registration.register()

    def start(self) -> None:
        log.info("%s: start syncing assets", self.connector_id)
        self._stop.clear()
        if not self.registration.register_until(self._stop, self.error_backoff):
            return
        while not self._stop.is_set():
            try:
                self.synchronize_assets()
            except Exception:
                log.exception("%s: failed to synchronize assets, next attempt in %s", self.connector_id, self.delay)
            log.info("%s: waiting %s until the next sync", self.connector_id, self.delay)
            if self._stop.wait(self.delay.total_seconds()):
                break
        log.info("%s: stopped syncing assets", self.connector_id)

    def stop(self) -> None:
        if self._stop.is_set():
            log.info("%s: asset synchronization already stopped", self.connector_id)
            return
        self._stop.set()

    def synchronize_assets(self) -> None:
        self.assets_provider.fetch_assets(_SynchronizerCallback(self.save_asset, self.delete_asset))

    def save_asset(self, asset: Asset) -> None:
        if not asset.id:
            raise ValueError("Asset id is required")
        payload = to_payload(asset)
        try:
            existing = self.client.assets.get(asset.id)
            # The server adds fields of its own (assigned tags, ...), so only compare what the provider sent.
            if is_subset(payload, to_payload(existing)):
                log.info("Asset %s already exists and is unchanged", asset.id)
                return
        except NotFoundError:
            log.debug("Asset %s does not exist yet", asset.id)
        log.info("Saving asset %s", asset.id)
        self.client.assets.put(asset.id, payload)

    def delete_asset(self, asset_id: str) -> None:
        log.info("Deleting asset %s", asset_id)
        self.client.assets.delete(asset_id)
