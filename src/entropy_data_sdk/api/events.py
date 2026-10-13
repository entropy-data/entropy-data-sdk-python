from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from entropy_data_sdk.api._base import ApiGroup

CLOUDEVENTS_BATCH = "application/cloudevents-batch+json"


class CloudEvent(BaseModel):
    """One entry of the event feed, in CloudEvents 1.0 shape."""

    model_config = ConfigDict(extra="allow")

    specversion: str | None = None
    type: str
    id: str
    source: str | None = None
    subject: str | None = None
    time: datetime | None = None
    datacontenttype: str | None = None
    dataschema: str | None = None
    principal: str | None = None
    data: dict[str, Any] | None = None

    @property
    def event_name(self) -> str:
        """The event type without its namespace, for example ``AccessActivatedEvent``."""
        return self.type.rsplit(".", 1)[-1]


class EventsApi(ApiGroup):
    def poll(
        self, *, last_event_id: str | None = None, long_polling: bool | None = None, timeout: float | None = None
    ) -> list[CloudEvent]:
        """Fetch the events after ``last_event_id``. With ``long_polling`` the server holds the request until events arrive."""
        response = self._http.request(
            "GET",
            "/api/events",
            params={"lastEventId": last_event_id, "longPolling": long_polling},
            accept=CLOUDEVENTS_BATCH,
            timeout=timeout,
        )
        return [CloudEvent.model_validate(item) for item in response.json()]
