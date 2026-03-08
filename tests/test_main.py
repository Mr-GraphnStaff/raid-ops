from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

import raid_ops.main as main_module
from raid_ops.main import AccountsSource, _list_accounts, _load_params


def test_load_params_accepts_json_object() -> None:
    assert _load_params('{"hero_id": 5}') == {"hero_id": 5}


def test_load_params_rejects_non_object_json() -> None:
    with pytest.raises(ValueError, match="JSON object"):
        _load_params('["not", "an", "object"]')


def test_list_accounts_uses_snapshot_source(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "accounts.json"
    snapshot_path.write_text(
        json.dumps([{"id": "1", "name": "Main", "level": 100}]),
        encoding="utf-8",
    )

    used_source, raw_rows, summary_rows = asyncio.run(
        _list_accounts(
            source=AccountsSource.SNAPSHOT,
            snapshot_path=snapshot_path,
            rtk_timeout_sec=0.1,
        )
    )

    assert used_source == AccountsSource.SNAPSHOT.value
    assert raw_rows[0]["level"] == 100
    assert summary_rows == [{"id": "1", "name": "Main"}]


def test_list_accounts_falls_back_when_rtk_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    snapshot_path = tmp_path / "accounts.json"
    snapshot_path.write_text(
        json.dumps([{"id": "snapshot", "name": "Fallback"}]),
        encoding="utf-8",
    )

    class FakeBrokenRtkGateway:
        def connect(self) -> None:
            return None

        def close(self) -> None:
            return None

        async def get_accounts(self) -> list[dict[str, str]]:
            raise RuntimeError("rtk unavailable")

    monkeypatch.setattr(main_module, "RaidToolkitAccountsGateway", FakeBrokenRtkGateway)

    used_source, raw_rows, summary_rows = asyncio.run(
        _list_accounts(
            source=AccountsSource.RTK,
            snapshot_path=snapshot_path,
            rtk_timeout_sec=0.1,
        )
    )

    assert used_source == AccountsSource.SNAPSHOT.value
    assert raw_rows == [{"id": "snapshot", "name": "Fallback"}]
    assert summary_rows == [{"id": "snapshot", "name": "Fallback"}]
