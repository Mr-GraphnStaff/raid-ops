from __future__ import annotations

from typing import Any

from raid_ops.connectors.rtk_client import AccountsGateway
from raid_ops.domain.models import AccountSummary
from raid_ops.services.account_dto import AccountRecord


class AccountService:
    """Application service for account-related use-cases."""

    def __init__(self, gateway: AccountsGateway) -> None:
        self._gateway = gateway

    async def list_account_records(self) -> list[AccountRecord]:
        payloads = await self._gateway.get_accounts()
        return [AccountRecord.from_payload(payload) for payload in payloads]

    async def list_account_summaries(self) -> list[AccountSummary]:
        records = await self.list_account_records()
        return [AccountSummary(id=record.id, name=record.name) for record in records]

    @staticmethod
    def as_raw_list(accounts: list[AccountRecord]) -> list[dict[str, Any]]:
        return [account.raw for account in accounts]

    @staticmethod
    def as_summary_list(accounts: list[AccountSummary]) -> list[dict[str, Any]]:
        return [{"id": account.id, "name": account.name} for account in accounts]
