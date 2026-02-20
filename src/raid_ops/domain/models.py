from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AccountSummary:
    """Stable domain-level representation of an account."""

    id: str
    name: str
    raw: dict[str, Any]
