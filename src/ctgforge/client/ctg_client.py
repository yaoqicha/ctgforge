import random
import time
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Optional


class CTGTransportError(RuntimeError):
    """Raised when ClinicalTrials.gov transport layer fails."""


@dataclass(frozen=True)
class RetryConfig:
    max_retries: int = 5
    backoff_base: float = 0.6  # in seconds
    backoff_cap: float = 15.0  # in seconds
    jitter: float = 0.25  # +/- jitter fraction
    retry_statuses: tuple[int, ...] = (429, 500, 502, 503, 504)


class CTGClient(ABC):
    """
    Abstract thin HTTP transport for ClinicalTrials.gov v2.

    Provides:
      - search() returning an iterator of raw study dicts
      - get(nct_id) returning a raw study dict
      - built-in pagination
      - retry/backoff on transient failures / rate limits

    Subclasses must implement _request_json() and close().
    """

    BASE_URL = "https://clinicaltrials.gov/api/v2"
    SEARCH_PATH = "/studies"
    STUDY_PATH = "/studies/{nct_id}"

    DEFAULT_HEADERS = {
        "Accept": "application/json",
        "User-Agent": "ctgforge (https://pypi.org/project/ctgforge)",
    }

    def __init__(
        self,
        *,
        headers: Optional[dict[str, str]] = None,
        retry: Optional[RetryConfig] = None,
        client: Optional[Any] = None,
    ) -> None:
        self._retry = retry or RetryConfig()

        self._headers = self.DEFAULT_HEADERS.copy()
        if headers:
            self._headers.update(headers)

        self._client = client
        self._owns_client = client is None

    @abstractmethod
    def close(self) -> None:
        """Close any underlying resources (e.g., HTTP client)."""
        raise NotImplementedError()

    @abstractmethod
    def _request_json(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        **_: Any,
    ) -> dict[str, Any]:
        """Perform an HTTP request and return the JSON response as a dict."""
        raise NotImplementedError()

    # ------ public API ------

    def get(self, nct_id: str) -> dict[str, Any]:
        """Fetch a single study by NCT ID."""
        path = self.STUDY_PATH.format(nct_id=nct_id)
        return self._request_json("GET", path)

    def count(
        self,
        query: Optional[dict[str, Any]] = None,
    ) -> int:
        """
        Count studies matching the query.

        Args:
            query: compiled query object as a dict of query parameters
        """
        params: dict[str, Any] = dict(query or {})

        # Use a page size of 1 to minimize data transfer
        params["pageSize"] = 1
        params["countTotal"] = "true"

        payload = self._request_json("GET", self.SEARCH_PATH, params=params)

        # The total count is included in the response's metadata
        return payload.get("totalCount", 0)

    def search(
        self,
        query: Optional[dict[str, Any]] = None,
        *,
        fields: Optional[list[str]] = None,
        offset: int = 0,
        limit: int = 100,
        sort: str = "LastUpdatePostDate",
    ) -> Iterator[dict[str, Any]]:
        """
        Search studies with pagination.

        Args:
            query: compiled query string
            fields: list of fields to return
            offset: number of records to skip
            limit: maximum number of records to return, up to 1000
            sort: sort order
            extra_params: additional query parameters
        """
        limit = min(limit, 1000)

        params: dict[str, Any] = dict(query or {})
        
        if fields:
            params["fields"] = ",".join(fields)

        params["pageSize"] = 100
        params["sort"] = sort

        yielded = 0
        skipped = 0
        next_token: Optional[str] = None

        while True:
            if next_token:
                params["pageToken"] = next_token

            payload = self._request_json("GET", self.SEARCH_PATH, params=params)

            studies = payload.get("studies") or payload.get("StudyFieldsResponse", {}).get(
                "StudyFields", []
            )
            for s in studies:
                if skipped < offset:
                    skipped += 1
                    continue
                yield s
                yielded += 1
                if limit is not None and yielded >= limit:
                    return

            next_token = payload.get("nextPageToken")
            if not next_token:
                return

    # ------ internal helpers ------

    def _sleep_backoff(self, attempt: int, retry_after: Optional[Any]) -> None:
        """
        A simple exponential backoff with jitter strategy.
        Might be used in implementations of _request_json().

        Args:
            attempt: current retry attempt (0-based)
            retry_after: HTTP "Retry-After" header value from the last attempt
        """
        if attempt >= self._retry.max_retries:
            return

        # honor Retry-After header if present
        ra = None
        if retry_after is not None:
            try:
                ra = float(retry_after)
            except ValueError:
                ra = None

        if ra is not None:
            time.sleep(min(ra, self._retry.backoff_cap))
            return

        base = min(self._retry.backoff_cap, self._retry.backoff_base * (2**attempt))
        jitter = base * self._retry.jitter * (2 * random.random() - 1)
        time.sleep(max(0.0, base + jitter))
