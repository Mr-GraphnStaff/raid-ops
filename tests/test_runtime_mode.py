from __future__ import annotations

import pytest

from raid_ops.services.runtime_mode import (
    AutomationDisabledError,
    RuntimeConfig,
    RuntimeMode,
    require_automation_enabled,
)


def test_require_automation_enabled_allows_explicit_mode() -> None:
    config = RuntimeConfig(mode=RuntimeMode.AUTOMATION_ENABLED)
    require_automation_enabled(config, "run")


def test_require_automation_enabled_blocks_read_only_mode() -> None:
    config = RuntimeConfig(mode=RuntimeMode.READ_ONLY)
    with pytest.raises(AutomationDisabledError, match="disabled"):
        require_automation_enabled(config, "run")
