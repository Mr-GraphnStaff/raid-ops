from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AccountRecord:
    """Typed service-layer representation of RTK account payloads."""

    id: str
    name: str
    raw: dict[str, Any]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> AccountRecord:
        return cls(
            id=str(payload.get("id", "unknown")),
            name=str(payload.get("name", "unknown")),
            raw=dict(payload),
        )
