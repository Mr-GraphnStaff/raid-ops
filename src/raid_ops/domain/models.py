from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AccountSummary:
    """Stable domain-level representation of an account."""

    id: str
    name: str
