from __future__ import annotations

import pytest

from raid_ops.main import _load_params


def test_load_params_accepts_json_object() -> None:
    assert _load_params('{"hero_id": 5}') == {"hero_id": 5}


def test_load_params_rejects_non_object_json() -> None:
    with pytest.raises(ValueError, match="JSON object"):
        _load_params('["not", "an", "object"]')
