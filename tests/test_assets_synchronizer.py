import threading
from datetime import timedelta

from entropy_data_sdk import AssetsSynchronizer, models

ASSET = {"id": "catalog.schema.table", "info": {"name": "table", "type": "table"}}


def register(api):
    api.get("/api/connectors/unittest").respond(404)
    api.put("/api/connectors/unittest").respond(200)


def test_synchronization_continues_after_failed_run(api, client):
    register(api)
    attempts = []

    class FailingOnFirstRun:
        def fetch_assets(self, callback):
            attempts.append(1)
            if len(attempts) == 1:
                raise RuntimeError("Simulated failure of the data platform")

    synchronizer = AssetsSynchronizer("unittest", client, FailingOnFirstRun(), delay=timedelta(milliseconds=10))
    thread = threading.Thread(target=synchronizer.start)
    thread.start()
    try:
        for _ in range(200):
            if len(attempts) >= 2:
                break
            threading.Event().wait(0.01)
    finally:
        synchronizer.stop()
        thread.join(timeout=5)

    assert len(attempts) >= 2
    assert not thread.is_alive()


def test_assets_are_saved_only_when_changed(api, client):
    register(api)
    api.get("/api/assets/catalog.schema.table").respond(200, json=ASSET)
    api.get("/api/assets/catalog.schema.new").respond(404)
    put = api.put("/api/assets/catalog.schema.new").respond(200)
    delete = api.delete("/api/assets/catalog.schema.gone").respond(200)

    class Provider:
        def fetch_assets(self, callback):
            callback.on_asset_updated(models.Asset.model_validate(ASSET))
            callback.on_asset_updated(models.Asset.model_validate({**ASSET, "id": "catalog.schema.new"}))
            callback.on_asset_deleted("catalog.schema.gone")

    AssetsSynchronizer("unittest", client, Provider()).synchronize_assets()

    assert put.call_count == 1
    assert delete.call_count == 1


def test_server_side_fields_do_not_count_as_changes(api, client):
    register(api)
    api.get("/api/assets/catalog.schema.table").respond(
        200, json={**ASSET, "assignedTags": ["pii:true"], "info": {**ASSET["info"], "status": "active"}}
    )
    put = api.put("/api/assets/catalog.schema.table").respond(200)

    class Provider:
        def fetch_assets(self, callback):
            callback.on_asset_updated(models.Asset.model_validate(ASSET))
            callback.on_asset_updated(models.Asset.model_validate({**ASSET, "info": {"name": "renamed"}}))

    AssetsSynchronizer("unittest", client, Provider()).synchronize_assets()

    assert put.call_count == 1
    assert b'"name":"renamed"' in put.calls.last.request.content


def test_constructor_does_not_touch_the_api(api, client):
    AssetsSynchronizer("unittest", client, object())

    assert not api.calls
