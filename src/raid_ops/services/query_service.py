from __future__ import annotations

from typing import Any

from raid_ops.connectors.rtk_client import QueryGateway


class RaidToolkitQueryService:
    """Application service for generic, read-only RTK API queries."""

    def __init__(self, gateway: QueryGateway) -> None:
        self._gateway = gateway

    async def fetch(self, api_group: str, method: str, params: dict[str, Any]) -> Any:
        return await self._gateway.query(api_group=api_group, method=method, **params)
