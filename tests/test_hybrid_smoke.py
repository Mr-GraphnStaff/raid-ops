from __future__ import annotations

import asyncio

import pytest

from raid_ops.app import agent_cli
from raid_ops.services.account_service import AccountService


class FakeGateway:
    def connect(self) -> None:
        return None

    def close(self) -> None:
        return None

    async def get_accounts(self) -> list[dict[str, object]]:
        return [{"id": "1", "name": "Main", "level": 100}]


def test_rtk_read_only_smoke_uses_typed_mapping() -> None:
    service = AccountService(FakeGateway())

    summaries = asyncio.run(service.list_account_summaries())
    records = asyncio.run(service.list_account_records())

    assert summaries[0].id == "1"
    assert summaries[0].name == "Main"
    assert records[0].raw["level"] == 100


def test_agent_cli_blocks_automation_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["agent_cli", "run"])

    def _should_not_run() -> None:
        raise AssertionError("automation path should be blocked before observer creation")

    monkeypatch.setattr(agent_cli, "make_default_observer", _should_not_run)

    with pytest.raises(SystemExit, match="disabled"):
        agent_cli.main()
