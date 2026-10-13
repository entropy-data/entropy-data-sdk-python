"""The entry point of the SDK: one client, one API group per resource."""

from __future__ import annotations

import httpx

from entropy_data_sdk._http import DEFAULT_RETRIES, DEFAULT_TIMEOUT, HttpClient
from entropy_data_sdk.api import (
    AccessApi,
    AgentIdentitiesApi,
    AssetsApi,
    CertificationsApi,
    ClassificationsApi,
    ConnectorsApi,
    CostsApi,
    DataContractsApi,
    DataProductBuildersApi,
    DataProductsApi,
    DefinitionsApi,
    EventsApi,
    ExampleDataApi,
    IntegrationsApi,
    LineageApi,
    OrganizationApi,
    PoliciesApi,
    SchemasApi,
    ScimApi,
    SearchApi,
    SemanticsApi,
    SourceSystemsApi,
    TagsApi,
    TeamsApi,
    TestResultsApi,
    UsageApi,
)

DEFAULT_HOST = "https://api.entropy-data.com"


class EntropyDataClient:
    """Client for the Entropy Data API.

    >>> client = EntropyDataClient(api_key="ed_live_...")
    >>> client.data_products.get("my-data-product")

    Use it as a context manager, or call :meth:`close`, to release the connection pool. ``retries`` applies to
    connection failures only; a request the server may have received is never repeated.
    """

    def __init__(
        self,
        api_key: str,
        host: str = DEFAULT_HOST,
        *,
        timeout: float | httpx.Timeout = DEFAULT_TIMEOUT,
        verify: bool | str = True,
        retries: int = DEFAULT_RETRIES,
        transport: httpx.BaseTransport | None = None,
    ):
        self.http = HttpClient(host, api_key, timeout=timeout, verify=verify, retries=retries, transport=transport)

        self.access = AccessApi(self.http)
        self.agent_identities = AgentIdentitiesApi(self.http)
        self.assets = AssetsApi(self.http)
        self.certifications = CertificationsApi(self.http)
        self.classifications = ClassificationsApi(self.http)
        self.connectors = ConnectorsApi(self.http)
        self.costs = CostsApi(self.http)
        self.data_contracts = DataContractsApi(self.http)
        self.data_product_builders = DataProductBuildersApi(self.http)
        self.data_products = DataProductsApi(self.http)
        self.definitions = DefinitionsApi(self.http)
        self.events = EventsApi(self.http)
        self.example_data = ExampleDataApi(self.http)
        self.integrations = IntegrationsApi(self.http)
        self.lineage = LineageApi(self.http)
        self.organization = OrganizationApi(self.http)
        self.policies = PoliciesApi(self.http)
        self.schemas = SchemasApi(self.http)
        self.scim = ScimApi(self.http)
        self.search = SearchApi(self.http)
        self.semantics = SemanticsApi(self.http)
        self.source_systems = SourceSystemsApi(self.http)
        self.tags = TagsApi(self.http)
        self.teams = TeamsApi(self.http)
        self.test_results = TestResultsApi(self.http)
        self.usage = UsageApi(self.http)

    @property
    def host(self) -> str:
        return self.http.base_url

    def close(self) -> None:
        self.http.close()

    def __enter__(self) -> EntropyDataClient:
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()
