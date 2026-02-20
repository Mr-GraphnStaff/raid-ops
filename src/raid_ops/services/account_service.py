from __future__ import annotations

from typing import Any

from raid_ops.connectors.rtk_client import AccountsGateway
from raid_ops.domain.models import AccountSummary


class AccountService:
    """Application service for account-related use-cases."""

    def __init__(self, gateway: AccountsGateway) -> None:
        self._gateway = gateway

    async def list_account_summaries(self) -> list[AccountSummary]:
        payloads = await self._gateway.get_accounts()
        summaries: list[AccountSummary] = []

        for payload in payloads:
            account_id = str(payload.get("id", "unknown"))
            account_name = str(payload.get("name", "unknown"))
            summaries.append(
                AccountSummary(id=account_id, name=account_name, raw=dict(payload))
            )

        return summaries

    @staticmethod
    def as_raw_list(accounts: list[AccountSummary]) -> list[dict[str, Any]]:
        return [account.raw for account in accounts]
