from __future__ import annotations

import asyncio
from typing import Any

from raid_ops.services.account_service import AccountService


class FakeGateway:
    def __init__(self, payload: list[dict[str, Any]]) -> None:
        self.payload = payload

    def connect(self) -> None:
        return None

    def close(self) -> None:
        return None

    async def get_accounts(self) -> list[dict[str, Any]]:
        return self.payload


def test_list_account_summaries_maps_payload() -> None:
    gateway = FakeGateway([
        {"id": "1", "name": "Main", "level": 100},
        {"id": "2", "name": "Alt", "level": 80},
    ])
    service = AccountService(gateway)

    accounts = asyncio.run(service.list_account_summaries())

    assert [a.id for a in accounts] == ["1", "2"]
    assert [a.name for a in accounts] == ["Main", "Alt"]
    assert accounts[0].raw["level"] == 100


def test_list_account_summaries_defaults_missing_fields() -> None:
    gateway = FakeGateway([{"region": "global"}])
    service = AccountService(gateway)

    accounts = asyncio.run(service.list_account_summaries())

    assert accounts[0].id == "unknown"
    assert accounts[0].name == "unknown"


def test_list_account_summaries_handles_empty_payload() -> None:
    gateway = FakeGateway([])
    service = AccountService(gateway)

    accounts = asyncio.run(service.list_account_summaries())

    assert accounts == []
