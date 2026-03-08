from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonSnapshotAccountsGateway:
    """File-backed account gateway for offline/snapshot workflows."""

    def __init__(self, snapshot_path: Path) -> None:
        self._snapshot_path = snapshot_path

    def connect(self) -> None:
        return None

    def close(self) -> None:
        return None

    async def get_accounts(self) -> list[dict[str, Any]]:
        if not self._snapshot_path.exists():
            return []

        payload = json.loads(self._snapshot_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(
                f"Snapshot file '{self._snapshot_path}' must contain a JSON list."
            )

        entries: list[dict[str, Any]] = []
        for item in payload:
            if isinstance(item, dict):
                entries.append(item)
        return entries
