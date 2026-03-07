from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RuntimeMode(str, Enum):
    READ_ONLY = "read_only"
    AUTOMATION_ENABLED = "automation_enabled"


@dataclass(frozen=True)
class RuntimeConfig:
    mode: RuntimeMode = RuntimeMode.READ_ONLY


class AutomationDisabledError(RuntimeError):
    """Raised when automation side-effects are requested in read-only mode."""


def require_automation_enabled(config: RuntimeConfig, action: str) -> None:
    if config.mode is RuntimeMode.AUTOMATION_ENABLED:
        return
    raise AutomationDisabledError(
        f"Automation action '{action}' is disabled in mode '{config.mode.value}'. "
        "Use --mode automation_enabled to allow side effects."
    )
