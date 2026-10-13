import pytest
import respx

from entropy_data_sdk import EntropyDataClient

HOST = "https://api.example.test"


@pytest.fixture
def api():
    with respx.mock(base_url=HOST, assert_all_called=False) as mock:
        yield mock


@pytest.fixture
def client(api):
    with EntropyDataClient("APIKEY", HOST) as client:
        yield client


ACCESS = {
    "dataUsageAgreementSpecification": "0.0.1",
    "id": "2OzPnlv1OVp20sKQaqRQAl",
    "info": {"purpose": "purpose-1", "status": "approved", "active": True, "startDate": "2024-11-09"},
    "provider": {"teamId": "my-example-team", "dataProductId": "my-example-data-product", "outputPortId": "snowflake"},
    "consumer": {"userId": "demo.user@example.test"},
    "tags": [],
    "links": {},
    "custom": {},
}

DATA_PRODUCT = {
    "dataProductSpecification": "0.0.1",
    "id": "my-example-data-product",
    "info": {"title": "My Example Data Product", "owner": "my-example-team", "status": "active"},
    "outputPorts": [{"id": "snowflake", "name": "My Example Output Port", "type": "snowflake"}],
    "custom": {"platformRole": "dp_my_example_data_product_role"},
}

CONNECTOR = {
    "id": "unittest",
    "info": {"type": "databricks", "description": "This is a databricks connector.", "connectorVersion": "1.0.0"},
    "health": {"status": "running", "startedAt": "2023-01-01T09:15:20.705Z"},
    "state": {"lastEventId": "95837f96-766f-4f8b-96f8-4f337f2a36a6"},
}


def cloud_event(event_id: str, event_type: str, subject: str) -> dict:
    return {
        "specversion": "1.0",
        "id": event_id,
        "type": f"com.entropy-data.events.{event_type}",
        "source": "https://app.entropy-data.com",
        "time": "2024-11-09T17:26:56.640037Z",
        "subject": subject,
        "datacontenttype": "application/json",
        "data": {"id": subject, "timestamp": "2024-11-09T17:26:56.640035Z"},
    }
