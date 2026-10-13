import httpx
import pytest

from entropy_data_sdk import ApiError, NotFoundError, UnprocessableContentError, models
from tests.conftest import ACCESS, CONNECTOR, DATA_PRODUCT


def test_sends_api_key_and_parses_model(api, client):
    route = api.get("/api/access/2OzPnlv1OVp20sKQaqRQAl").respond(200, json=ACCESS)

    access = client.access.get("2OzPnlv1OVp20sKQaqRQAl")

    assert route.calls.last.request.headers["x-api-key"] == "APIKEY"
    assert access.provider.dataProductId == "my-example-data-product"
    assert access.consumer.userId == "demo.user@example.test"
    assert access.consumer.teamId is None


def test_data_products_are_passed_through_as_dicts(api, client):
    api.get("/api/dataproducts/my-example-data-product").respond(200, json=DATA_PRODUCT)
    put = api.put("/api/dataproducts/my-example-data-product").respond(200)

    data_product = client.data_products.get("my-example-data-product")
    client.data_products.put("my-example-data-product", data_product)

    assert data_product["custom"]["platformRole"] == "dp_my_example_data_product_role"
    assert put.calls.last.request.content == httpx.Response(200, json=DATA_PRODUCT).content


def test_models_are_serialized_without_unset_fields(api, client):
    put = api.put("/api/connectors/unittest").respond(200)

    client.connectors.put("unittest", models.Connector(id="unittest", info=models.ConnectorInfo(type="databricks")))

    assert put.calls.last.request.content == b'{"id":"unittest","info":{"type":"databricks"}}'


def test_query_params_drop_none_values(api, client):
    route = api.get("/api/teams").respond(200, json=[])

    client.teams.list(page=2)

    assert route.calls.last.request.url.params == httpx.QueryParams({"p": "2"})


def test_yaml_endpoints_exchange_text(api, client):
    get = api.get("/api/datacontracts/orders/datacontract.yaml").respond(200, text="apiVersion: v3.1.0\n")
    put = api.put("/api/datacontracts/orders/branches/draft/datacontract.yaml").respond(200)

    yaml_text = client.data_contracts.get_yaml("orders")
    client.data_contracts.put_branch_yaml("orders", "draft", yaml_text)

    assert yaml_text == "apiVersion: v3.1.0\n"
    assert get.calls.last.request.headers["Accept"] == "application/yaml"
    assert put.calls.last.request.headers["Content-Type"] == "application/yaml"
    assert put.calls.last.request.content == b"apiVersion: v3.1.0\n"


def test_errors_map_to_status_specific_exceptions(api, client):
    api.get("/api/connectors/missing").respond(404, json={"title": "Not Found", "detail": "No connector missing"})
    api.put("/api/assets/bad").respond(422, text="invalid asset")
    api.get("/api/connectors/boom").respond(500, text="<html><title>Internal Server Error</title></html>")

    with pytest.raises(NotFoundError) as not_found:
        client.connectors.get("missing")
    with pytest.raises(UnprocessableContentError):
        client.assets.put("bad", {"id": "bad"})
    with pytest.raises(ApiError) as server_error:
        client.connectors.get("boom")

    assert not_found.value.status_code == 404
    assert not_found.value.message == "No connector missing"
    assert server_error.value.message == "Internal Server Error"


def test_iterate_pages_follows_link_header(api, client):
    api.get("/api/assets", params={"p": "0"}).respond(
        200, json=[{"id": "a"}], headers={"Link": '</api/assets?p=1>; rel="next"'}
    )
    api.get("/api/assets", params={"p": "1"}).respond(200, json=[{"id": "b"}])

    ids = [item["id"] for item in client.http.iterate_pages("/api/assets")]

    assert ids == ["a", "b"]


def test_poll_events_uses_cloudevents_accept_header(api, client):
    route = api.get("/api/events").respond(200, json=[])

    client.events.poll(last_event_id="abc")

    request = route.calls.last.request
    assert request.headers["Accept"] == "application/cloudevents-batch+json"
    assert request.url.params["lastEventId"] == "abc"


def test_remote_state_round_trip(api, client):
    from entropy_data_sdk import RemoteStateRepository

    api.get("/api/connectors/unittest").respond(200, json=CONNECTOR)
    put = api.put("/api/connectors/unittest").respond(200)
    repository = RemoteStateRepository("unittest", client)

    assert repository.get_state() == {"lastEventId": "95837f96-766f-4f8b-96f8-4f337f2a36a6"}
    repository.save_state({"lastEventId": "new"})

    body = put.calls.last.request.content
    assert b'"state":{"lastEventId":"new"}' in body
    assert b'"type":"databricks"' in body


def test_path_segments_are_encoded_and_validated(api, client):
    from entropy_data_sdk._http import seg

    route = api.get("/api/assets/a%20b%3Fc%23d").respond(200, json={"id": "a b?c#d"})

    client.assets.get("a b?c#d")

    assert route.called
    assert seg("catalog.schema.table") == "catalog.schema.table"
    assert seg("user@example.test") == "user%40example.test"
    for bad in ("", "../x", "a/../b", "x" * 257):
        with pytest.raises(ValueError):
            seg(bad)


def test_unknown_enum_values_are_kept(api, client):
    api.get("/api/access/x").respond(200, json={**ACCESS, "info": {**ACCESS["info"], "status": "brand-new"}})

    access = client.access.get("x")

    assert access.info.status == "brand-new"
    assert isinstance(access.info.status, models.AccessInfoStatus)
    assert access.model_dump(mode="json")["info"]["status"] == "brand-new"


def test_401_maps_to_unauthorized(api, client):
    from entropy_data_sdk import UnauthorizedError

    api.get("/api/teams").respond(401, json={"detail": "Invalid API key"})

    with pytest.raises(UnauthorizedError):
        client.teams.list()


def test_lists_are_pages_with_has_next(api, client):
    api.get("/api/teams").respond(
        200, json=[{"id": "a", "name": "A", "type": "Team"}], headers={"Link": '<x>; rel="next"'}
    )
    api.get("/api/dataproducts").respond(200, json=[{"id": "dp"}])

    teams = client.teams.list()
    products = client.data_products.list()

    assert teams.has_next is True
    assert teams[0].id == "a"
    assert products.has_next is False
    assert products == [{"id": "dp"}]


def test_write_calls_expose_the_html_location(api, client):
    api.put("/api/teams/a").respond(200, headers={"location-html": "https://app.example.test/teams/a"})
    api.post("/api/access/x/approve").respond(200)

    result = client.http.put_json("/api/teams/a", {"id": "a"})
    approved = client.http.post_json("/api/access/x/approve")

    assert result.location_html == "https://app.example.test/teams/a"
    assert result.data is None
    assert approved.location_html is None


def test_transport_retries_connection_failures():
    from entropy_data_sdk import EntropyDataClient

    with EntropyDataClient("key", "https://api.example.test", retries=5) as client:
        assert client.http._client._transport._pool._retries == 5
