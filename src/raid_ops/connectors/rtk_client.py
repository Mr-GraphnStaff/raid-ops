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


class RaidToolkitAccountsGateway:
    """RTK-backed implementation of account gateway."""

    def __init__(self) -> None:
        self._client = RaidToolkitClient()

    def connect(self) -> None:
        self._client.connect()

    def close(self) -> None:
        self._client.close()

    async def get_accounts(self) -> list[dict[str, Any]]:
        accounts = await self._client.AccountApi.get_accounts()
        if isinstance(accounts, list):
            return accounts
        return []
