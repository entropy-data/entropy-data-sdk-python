from __future__ import annotations

from entropy_data_sdk._http import HttpClient


class ApiGroup:
    def __init__(self, http: HttpClient):
        self._http = http
