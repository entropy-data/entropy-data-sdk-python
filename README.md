Entropy Data SDK for Python
===========================

Python SDK to interact with [Entropy Data](https://entropy-data.com): a typed client for the
[Entropy Data API](https://api.entropy-data.com/swagger/index.html) and a small framework for building
connectors that run on your data platform.

Using the SDK, you can automate data platform operations, such as:

- Synchronize data products and data assets from the data platform to Entropy Data
- Automate permissions in the data platform when an access request has been approved
- Notify downstream consumers when data contract tests have failed
- Publish data product costs, usage and lineage to Entropy Data

The Java counterpart is [entropy-data-sdk](https://github.com/entropy-data/entropy-data-sdk).

Installation
---

```bash
pip install entropy-data-sdk
# or
uv add entropy-data-sdk
```

Requires Python 3.11 or later.

Getting started
---

You need an [API key](https://docs.entropy-data.com/quickstart).

```python
from entropy_data_sdk import EntropyDataClient

client = EntropyDataClient(api_key="ed_live_...")  # host defaults to https://api.entropy-data.com

data_product = client.data_products.get("my-data-product")
access_list = client.access.list(provider_data_product_id="my-data-product")
for access in access_list:
    print(access.id, access.info.status, access.consumer.teamId)
```

The client has one attribute per API area: `data_products`, `data_contracts`, `access`, `teams`, `assets`,
`connectors`, `events`, `integrations`, `organization`, `semantics`, `scim`, and so on. Methods are named after what
they do (`list`, `get`, `put`, `delete`, `approve`, `push_to_git`, ...). Query parameters are keyword arguments.

Resources are [pydantic](https://docs.pydantic.dev/) models under `entropy_data_sdk.models`. Data products and data
contracts are the exception: their documents are customizable per organization, so they are returned and accepted as
plain dictionaries.

```python
from entropy_data_sdk import models

client.teams.put("analytics", models.Team(id="analytics", name="Analytics", type="Team"))
client.teams.put("analytics", {"id": "analytics", "name": "Analytics", "type": "Team"})  # a dict works as well
```

Errors are raised as `ApiError` subclasses: `NotFoundError` (404), `UnprocessableContentError` (422),
`ConflictError` (409), `ForbiddenError` (403), `UnauthorizedError` (401), `BadRequestError` (400).

```python
from entropy_data_sdk import NotFoundError

try:
    client.assets.get("catalog.schema.table")
except NotFoundError:
    ...
```

List calls return a `Page`, a list with a `has_next` attribute, and take a `page` argument for the next one.
`client.http.iterate_pages(path)` walks every page of a list endpoint.

Enum fields such as `access.info.status` are typed, but a value the SDK does not know yet is kept as a string-like
pseudo-member instead of failing validation, so an SDK release never has to precede a new status on the server.

Resource ids are validated and percent-encoded before they become part of a URL. Connection failures are retried
(`retries=3` by default); a request the server may have received is never repeated.

The typed methods cover every endpoint. For anything else, or to read response headers such as the link to the
resource in the web application, use the generic layer underneath:

```python
result = client.http.put_json("/api/teams/analytics", {"id": "analytics", "name": "Analytics", "type": "Team"})
print(result.location_html)
```

Building a connector
---

A connector is a long-running process on your data platform. The SDK registers it in Entropy Data under a stable
connector id, keeps its state there, and runs the loop for you.

### Synchronize assets

Implement an assets provider that reads tables, views, topics, ... from your platform and reports them as
`models.Asset`:

```python
from datetime import timedelta

from entropy_data_sdk import AssetsSynchronizer, EntropyDataClient, models


class MyAssetsProvider:
    def fetch_assets(self, callback):
        for table in my_platform.list_tables():
            callback.on_asset_updated(
                models.Asset(id=table.full_name, info=models.AssetInfo(name=table.name, type="table"))
            )
        for name in my_platform.dropped_tables():
            callback.on_asset_deleted(name)


client = EntropyDataClient(api_key="ed_live_...")
synchronizer = AssetsSynchronizer("my-assets-connector", client, MyAssetsProvider(), delay=timedelta(minutes=30))
synchronizer.start()  # registers the connector, then calls fetch_assets every 30 minutes until stop() is called
```

Assets are only written when the provider's version differs from what Entropy Data has; fields the server adds on
its own are ignored in that comparison.

### React to events

Subclass `EventHandler` and override the methods for the events you care about. There is one method per event
type (`on_access_activated`, `on_data_contract_updated`, ...), and `on_event` receives every event.

```python
from entropy_data_sdk import EntropyDataClient, EventHandler, EventListener, RemoteStateRepository, models


class MyEventHandler(EventHandler):
    def on_access_activated(self, event: models.AccessActivatedEvent):
        access = client.access.get(event.id)
        my_platform.grant(access)  # look up the data product and consumer for details

    def on_access_deactivated(self, event: models.AccessDeactivatedEvent):
        my_platform.revoke(client.access.get(event.id))


client = EntropyDataClient(api_key="ed_live_...")
connector_id = "my-access-connector"
listener = EventListener(
    connector_id,
    "access-management",
    client,
    MyEventHandler(),
    RemoteStateRepository(connector_id, client),
    connector_version="1.0.0",
)
listener.start()  # registers the connector, then polls the event feed and remembers the last processed event id
```

If a handler method raises, the listener calls `on_error(event, error)`. The default returns `False`, which retries the
same event after a backoff so nothing is lost. Return `True` to skip a poison event and move on.

Both `start()` methods register the connector first and keep retrying the registration while the API is unreachable,
so a connector can start before Entropy Data is available.

### State

`EventListener` stores the id of the last processed event through a `StateRepository`. `RemoteStateRepository` keeps it
on the connector resource in Entropy Data, `InMemoryStateRepository` is for tests, and any object with `get_state()` and
`save_state(state)` works.

Run several connectors in one process by starting each `start()` in its own thread.

Development
---

```bash
uv sync
uv run pytest
uv run ruff check && uv run ruff format --check
```

`src/entropy_data_sdk/models.py` is generated. To pick up API changes:

```bash
scripts/update-openapi             # fetch spec/openapi.yaml and the JSON schemas from api.entropy-data.com
uv run python scripts/generate_models.py
```

The generator hoists nested objects into named models (`Connector.info` becomes `ConnectorInfo`) so that names stay
stable across spec updates. The API methods in `src/entropy_data_sdk/api/` are maintained by hand: add the new
operation there after regenerating the models.

Release
---

Bump `version` in `pyproject.toml`, add the changelog entry, commit, then run `./release`. The tag triggers the
release workflow, which publishes to PyPI via trusted publishing.

License
---

[MIT License](LICENSE)
