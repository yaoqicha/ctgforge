from collections.abc import Iterator
from typing import Any, Optional

from .client.ctg_client import CTGClient
from .client.httpx_client import CTGHttpxClient
from .query.compiler import compile_to_params
from .query.expr import Expr


class CTG:
    def __init__(self, client: Optional[CTGClient] = None) -> None:
        self.client = client or CTGHttpxClient()

    def close(self) -> None:
        self.client.close()

    def get(self, nct_id: str) -> dict[str, Any]:
        return self.client.get(nct_id)

    def count(
        self,
        query: Optional[Expr] = None,
        **params: Any,
    ) -> int:
        compiled = compile_to_params(query).params if query is not None else {}

        # user-supplied params override compiled params
        merged = {**compiled, **params}

        # Use a page size of 1 to minimize data transfer
        total = self.client.count(
            None,  # backend should accept raw params; keep query arg for compatibility
            **merged,
        )
        return total

    def search(
        self,
        query: Optional[Expr] = None,
        *,
        fields: Optional[list[str]] = None,
        offset: int = 0,
        limit: int = 100,  # Allowed max records returned, up to 1000,
        sort: str = "LastUpdatePostDate",
        **params: Any,
    ) -> Iterator[dict[str, Any]]:
        limit = min(limit, 1000)  # Enforce max limit of 1000

        compiled = compile_to_params(query).params if query is not None else {}

        # user-supplied params override compiled params
        merged = {**compiled, **params}

        return self.client.search(
            None,  # backend should accept raw params; keep query arg for compatibility
            fields=fields,
            offset=offset,
            limit=limit,
            sort=sort,
            **merged,
        )
