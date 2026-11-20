import base64

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


def test_hierarchical_tag_ids_keep_their_slashes(api, client):
    assign = api.put("/api/assets/a1/assigned-tags/governance/PII").respond(200)
    unassign = api.delete("/api/assets/a1/assigned-tags/governance/PII").respond(200)

    client.assets.assign_tag("a1", "governance/PII")
    client.assets.unassign_tag("a1", "governance/PII")

    assert assign.called and unassign.called
    assert assign.calls[0].request.content == b""


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


PROXY_VARIABLES = ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"]


@pytest.fixture
def proxy_env(monkeypatch):
    for name in PROXY_VARIABLES:
        monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv(name.lower(), raising=False)
    return monkeypatch.setenv


def _proxy_url(client, url):
    transport = client.http._client._transport_for_url(httpx.URL(url))
    proxy = getattr(transport._pool, "_proxy_url", None)
    return None if proxy is None else f"{proxy.scheme.decode()}://{proxy.host.decode()}:{proxy.port}"


def test_https_proxy_from_the_environment_is_used(proxy_env):
    from entropy_data_sdk import EntropyDataClient

    proxy_env("HTTPS_PROXY", "http://proxy.example.test:8080")

    with EntropyDataClient("key", "https://api.example.test") as client:
        assert _proxy_url(client, "https://api.example.test/api/teams") == "http://proxy.example.test:8080"
        assert _proxy_url(client, "http://api.example.test/api/teams") is None


def test_http_and_all_proxy_from_the_environment_are_used(proxy_env):
    from entropy_data_sdk import EntropyDataClient

    proxy_env("HTTP_PROXY", "http://plain.example.test:3128")
    proxy_env("ALL_PROXY", "http://fallback.example.test:3128")

    with EntropyDataClient("key", "http://api.example.test") as client:
        assert _proxy_url(client, "http://api.example.test/api/teams") == "http://plain.example.test:3128"
        assert _proxy_url(client, "https://api.example.test/api/teams") == "http://fallback.example.test:3128"


@pytest.mark.parametrize(
    ("no_proxy", "url"),
    [
        ("example.test", "https://api.example.test"),
        (".example.test", "https://api.example.test"),
        ("other.test, api.example.test", "https://api.example.test"),
        ("10.1.2.3", "https://10.1.2.3"),
        ("::1", "https://[::1]:8443"),
        ("https://api.example.test", "https://api.example.test"),
        ("localhost", "https://localhost:8080"),
        ("*", "https://api.example.test"),
    ],
)
def test_no_proxy_hosts_are_reached_directly(proxy_env, no_proxy, url):
    from entropy_data_sdk import EntropyDataClient

    proxy_env("HTTPS_PROXY", "http://proxy.example.test:8080")
    proxy_env("NO_PROXY", no_proxy)

    with EntropyDataClient("key", url) as client:
        assert _proxy_url(client, f"{url}/api/teams") is None
        if no_proxy != "*":
            assert _proxy_url(client, "https://elsewhere.test") == "http://proxy.example.test:8080"


def test_proxy_credentials_from_the_environment_are_sent_to_the_proxy(proxy_env):
    from entropy_data_sdk import EntropyDataClient

    proxy_env("HTTPS_PROXY", "http://user:secret@proxy.example.test:8080")

    with EntropyDataClient("key", "https://api.example.test") as client:
        transport = client.http._client._transport_for_url(httpx.URL("https://api.example.test"))
        expected = b"Basic " + base64.b64encode(b"user:secret")
        assert dict(transport._pool._proxy_headers)[b"Proxy-Authorization"] == expected


def test_a_request_travels_through_the_proxy_from_the_environment(proxy_env):
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    from entropy_data_sdk import EntropyDataClient

    forwarded = []

    class Proxy(BaseHTTPRequestHandler):
        def do_GET(self):
            forwarded.append((self.path, self.headers["x-api-key"]))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"[]")

        def log_message(self, *args):
            pass

    proxy = HTTPServer(("127.0.0.1", 0), Proxy)
    threading.Thread(target=proxy.serve_forever, daemon=True).start()
    try:
        proxy_env("HTTP_PROXY", f"http://127.0.0.1:{proxy.server_port}")
        with EntropyDataClient("APIKEY", "http://api.example.test") as client:
            response = client.http.request("GET", "/api/teams")
    finally:
        proxy.shutdown()
        proxy.server_close()

    assert response.json() == []
    assert forwarded == [("http://api.example.test/api/teams", "APIKEY")]


def test_requests_through_a_proxy_still_send_the_api_key(proxy_env, api):
    from entropy_data_sdk import EntropyDataClient

    proxy_env("HTTPS_PROXY", "http://proxy.example.test:8080")
    route = api.get("/api/teams/a").respond(200, json={"id": "a", "name": "A", "type": "Team"})

    with EntropyDataClient("APIKEY", "https://api.example.test") as client:
        client.http.request("GET", "/api/teams/a")

    assert route.calls.last.request.headers["x-api-key"] == "APIKEY"


def test_an_explicit_transport_ignores_the_proxy_environment(proxy_env):
    from entropy_data_sdk import EntropyDataClient

    proxy_env("HTTPS_PROXY", "http://proxy.example.test:8080")
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=[]))

    with EntropyDataClient("key", "https://api.example.test", transport=transport) as client:
        assert client.http._client._transport_for_url(httpx.URL("https://api.example.test")) is transport


def test_trust_env_false_ignores_the_proxy_environment(proxy_env):
    from entropy_data_sdk import EntropyDataClient

    proxy_env("HTTPS_PROXY", "http://proxy.example.test:8080")
    proxy_env("ALL_PROXY", "http://fallback.example.test:3128")

    with EntropyDataClient("key", "https://api.example.test", trust_env=False) as client:
        assert _proxy_url(client, "https://api.example.test/api/teams") is None
        assert _proxy_url(client, "http://api.example.test/api/teams") is None
        assert client.http._client.trust_env is False


def test_trust_env_false_ignores_certificate_variables(proxy_env, tmp_path):
    from entropy_data_sdk import EntropyDataClient

    proxy_env("SSL_CERT_FILE", str(tmp_path / "missing-ca.pem"))

    with EntropyDataClient("key", "https://api.example.test", trust_env=False) as client:
        assert client.http._client.trust_env is False

    with pytest.raises(FileNotFoundError):
        EntropyDataClient("key", "https://api.example.test")


def test_the_environment_is_trusted_by_default(proxy_env):
    from entropy_data_sdk import EntropyDataClient

    with EntropyDataClient("key", "https://api.example.test") as client:
        assert client.http._client.trust_env is True


def test_a_socks_proxy_from_the_environment_is_used(proxy_env):
    from entropy_data_sdk import EntropyDataClient

    proxy_env("ALL_PROXY", "socks5://proxy.example.test:1080")

    with EntropyDataClient("key", "https://api.example.test") as client:
        transport = client.http._client._transport_for_url(httpx.URL("https://api.example.test"))
        assert type(transport._pool).__name__ == "SOCKSProxy"
