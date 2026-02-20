from __future__ import annotations

from typing import Any, Protocol

from raidtoolkit import RaidToolkitClient


class AccountsGateway(Protocol):
    """Gateway interface for account retrieval."""

    def connect(self) -> None:
        """Open any required connection resources."""

    def close(self) -> None:
        """Close any open resources."""

    async def get_accounts(self) -> list[dict[str, Any]]:
        """Return account payloads from the backing source."""


class QueryGateway(Protocol):
    """Gateway interface for direct RaidToolkit API queries."""

    async def query(self, api_group: str, method: str, **params: Any) -> Any:
        """Execute a method on an RTK API group and return its payload."""


class RaidToolkitAccountsGateway:
    """RTK-backed implementation of account gateway."""

    def __init__(self, client: RaidToolkitClient | None = None) -> None:
        self._client = client or RaidToolkitClient()

    def connect(self) -> None:
        self._client.connect()

    def close(self) -> None:
        self._client.close()

    async def get_accounts(self) -> list[dict[str, Any]]:
        accounts = await self._client.AccountApi.get_accounts()
        if isinstance(accounts, list):
            return accounts
        return []

    async def query(self, api_group: str, method: str, **params: Any) -> Any:
        api = getattr(self._client, api_group, None)
        if api is None:
            available = [name for name in dir(self._client) if name.endswith("Api")]
            raise ValueError(f"Unknown API group '{api_group}'. Available: {available}")

        fn = getattr(api, method, None)
        if fn is None or not callable(fn):
            available = [name for name in dir(api) if not name.startswith("_")]
            raise ValueError(
                f"Unknown method '{method}' on '{api_group}'. Available: {available}"
            )

        return await fn(**params)
