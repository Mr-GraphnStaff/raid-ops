from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from raid_ops.connectors.snapshot_gateway import JsonSnapshotAccountsGateway


def test_snapshot_gateway_returns_accounts_list(tmp_path: Path) -> None:
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text(
        json.dumps([{"id": "1", "name": "Main"}, {"id": "2", "name": "Alt"}]),
        encoding="utf-8",
    )
    gateway = JsonSnapshotAccountsGateway(snapshot)

    payloads = asyncio.run(gateway.get_accounts())

    assert len(payloads) == 2
    assert payloads[0]["id"] == "1"


def test_snapshot_gateway_ignores_non_dict_rows(tmp_path: Path) -> None:
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text(json.dumps([{"id": "1"}, 42, "bad", ["x"]]), encoding="utf-8")
    gateway = JsonSnapshotAccountsGateway(snapshot)

    payloads = asyncio.run(gateway.get_accounts())

    assert payloads == [{"id": "1"}]


def test_snapshot_gateway_missing_file_returns_empty(tmp_path: Path) -> None:
    gateway = JsonSnapshotAccountsGateway(tmp_path / "missing.json")

    payloads = asyncio.run(gateway.get_accounts())

    assert payloads == []


def test_snapshot_gateway_rejects_non_list_payload(tmp_path: Path) -> None:
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text(json.dumps({"id": "1"}), encoding="utf-8")
    gateway = JsonSnapshotAccountsGateway(snapshot)

    with pytest.raises(ValueError, match="JSON list"):
        asyncio.run(gateway.get_accounts())
