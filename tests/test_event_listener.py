import threading
from datetime import timedelta

from entropy_data_sdk import EventHandler, EventListener, InMemoryStateRepository, models
from tests.conftest import ACCESS, DATA_PRODUCT, cloud_event

EVENTS = [
    cloud_event("1ef9ebfd-1baf-6800-b4cc-29ec4630cb43", "DataProductCreatedEvent", "my-example-data-product"),
    cloud_event("1ef9ebfe-0748-6002-b4cc-eb62af15d801", "AccessCreatedEvent", "2OzPnlv1OVp20sKQaqRQAl"),
    cloud_event("1ef9ebfe-29f4-6f4a-b4cc-03e3b7d7579f", "AccessActivatedEvent", "2OzPnlv1OVp20sKQaqRQAl"),
    cloud_event("1ef9ebfe-29f4-6f4a-b4cc-03e3b7d757a0", "DataUsageAgreementActivatedEvent", "2OzPnlv1OVp20sKQaqRQAl"),
    cloud_event("1ef9ebfe-29f4-6f4a-b4cc-03e3b7d757a1", "SomethingNewEvent", "x"),
]


def run_listener(api, client, handler, state_repository):
    api.get("/api/connectors/unittest").respond(404)
    api.put("/api/connectors/unittest").respond(200)
    api.get("/api/events", params={"lastEventId": EVENTS[-1]["id"]}).respond(200, json=[])
    api.get("/api/events").respond(200, json=EVENTS)
    listener = EventListener(
        "unittest", "event-listener", client, handler, state_repository, poll_interval=timedelta(milliseconds=10)
    )
    thread = threading.Thread(target=listener.start)
    thread.start()
    try:
        for _ in range(200):
            if state_repository.get_state().get("lastEventId") == EVENTS[-1]["id"]:
                break
            threading.Event().wait(0.01)
    finally:
        listener.stop()
        thread.join(timeout=5)
    assert not thread.is_alive()
    return listener


def test_listener_dispatches_typed_events_and_persists_last_event_id(api, client):
    api.get("/api/access/2OzPnlv1OVp20sKQaqRQAl").respond(200, json=ACCESS)
    api.get("/api/dataproducts/my-example-data-product").respond(200, json=DATA_PRODUCT)
    seen = []

    class Handler(EventHandler):
        def on_event(self, event):
            seen.append(event.event_name)

        def on_access_activated(self, event: models.AccessActivatedEvent):
            access = client.access.get(event.id)
            data_product = client.data_products.get(access.provider.dataProductId)
            seen.append(data_product["custom"]["platformRole"])

    state_repository = InMemoryStateRepository("unittest")
    run_listener(api, client, Handler(), state_repository)

    assert seen == [
        "DataProductCreatedEvent",
        "AccessCreatedEvent",
        "AccessActivatedEvent",
        "dp_my_example_data_product_role",
        "DataUsageAgreementActivatedEvent",
        "SomethingNewEvent",
    ]
    assert state_repository.get_state() == {"lastEventId": EVENTS[-1]["id"]}


def test_listener_resumes_from_stored_event_id(api, client):
    state_repository = InMemoryStateRepository("unittest")
    state_repository.save_state({"lastEventId": EVENTS[-1]["id"]})
    api.get("/api/connectors/unittest").respond(404)
    api.put("/api/connectors/unittest").respond(200)
    feed = api.get("/api/events", params={"lastEventId": EVENTS[-1]["id"]}).respond(200, json=[])
    listener = EventListener("unittest", "event-listener", client, EventHandler(), state_repository)
    listener.poll_interval = timedelta(milliseconds=10)
    thread = threading.Thread(target=listener.start)
    thread.start()
    try:
        for _ in range(200):
            if feed.called:
                break
            threading.Event().wait(0.01)
    finally:
        listener.stop()
        thread.join(timeout=5)

    assert feed.called
    assert feed.calls.last.request.url.params["lastEventId"] == EVENTS[-1]["id"]


def test_registration_keeps_existing_description(api, client):
    api.get("/api/connectors/unittest").respond(
        200, json={"id": "unittest", "info": {"type": "old", "description": "kept"}, "state": {"lastEventId": "x"}}
    )
    put = api.put("/api/connectors/unittest").respond(200)

    EventListener(
        "unittest", "event-listener", client, EventHandler(), InMemoryStateRepository("unittest"), "2.0"
    ).register()

    body = put.calls.last.request.content
    assert b'"type":"event-listener"' in body
    assert b'"description":"kept"' in body
    assert b'"connectorVersion":"2.0"' in body
    assert b'"state":{"lastEventId":"x"}' in body


def test_start_retries_registration_until_the_api_answers(api, client):
    import httpx

    api.get("/api/connectors/unittest").mock(side_effect=[httpx.ConnectError("down"), httpx.Response(404)])
    put = api.put("/api/connectors/unittest").respond(200)
    feed = api.get("/api/events").respond(200, json=[])
    listener = EventListener(
        "unittest",
        "event-listener",
        client,
        EventHandler(),
        InMemoryStateRepository("unittest"),
        poll_interval=timedelta(milliseconds=10),
        error_backoff=timedelta(milliseconds=10),
    )
    thread = threading.Thread(target=listener.start)
    thread.start()
    try:
        for _ in range(200):
            if feed.called:
                break
            threading.Event().wait(0.01)
    finally:
        listener.stop()
        thread.join(timeout=5)

    assert put.called
    assert feed.called


def test_on_error_decides_between_skip_and_retry(api, client):
    attempts = []

    class SkippingHandler(EventHandler):
        def on_access_created(self, event):
            attempts.append(event.id)
            raise RuntimeError("cannot grant")

        def on_error(self, event, error):
            return True

    state_repository = InMemoryStateRepository("unittest")
    run_listener(api, client, SkippingHandler(), state_repository)

    assert attempts == ["2OzPnlv1OVp20sKQaqRQAl"]
    assert state_repository.get_state() == {"lastEventId": EVENTS[-1]["id"]}


def test_default_on_error_retries_the_same_event(api, client):
    attempts = []

    class FailingHandler(EventHandler):
        def on_access_created(self, event):
            attempts.append(event.id)
            raise RuntimeError("cannot grant")

    api.get("/api/connectors/unittest").respond(404)
    api.put("/api/connectors/unittest").respond(200)
    api.get("/api/events").respond(200, json=EVENTS)
    state_repository = InMemoryStateRepository("unittest")
    listener = EventListener(
        "unittest",
        "event-listener",
        client,
        FailingHandler(),
        state_repository,
        poll_interval=timedelta(milliseconds=10),
        error_backoff=timedelta(milliseconds=10),
    )
    thread = threading.Thread(target=listener.start)
    thread.start()
    try:
        for _ in range(200):
            if len(attempts) >= 2:
                break
            threading.Event().wait(0.01)
    finally:
        listener.stop()
        thread.join(timeout=5)

    assert len(attempts) >= 2
    assert state_repository.get_state() == {"lastEventId": EVENTS[0]["id"]}


def test_every_event_type_in_the_spec_has_a_handler():
    from pathlib import Path

    import yaml

    from entropy_data_sdk.connector.events import _DISPATCH

    spec = yaml.safe_load((Path(__file__).resolve().parent.parent / "spec" / "openapi.yaml").read_text())
    feed = spec["paths"]["/api/events"]["get"]["responses"][200]["content"]["application/cloudevents-batch+json"]
    types = feed["schema"]["items"]["properties"]["type"]["x-extensible-enum"]

    missing = [t for t in types if t.rsplit(".", 1)[-1] not in _DISPATCH]

    assert missing == []
    for method_name, _ in _DISPATCH.values():
        assert callable(getattr(EventHandler, method_name))
