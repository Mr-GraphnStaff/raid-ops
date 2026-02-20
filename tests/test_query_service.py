from __future__ import annotations

import asyncio
from typing import Any

import pytest

from raid_ops.connectors.rtk_client import RaidToolkitAccountsGateway
from raid_ops.services.query_service import RaidToolkitQueryService


class FakeStaticDataApi:
    async def get_hero_data(self, hero_id: int) -> dict[str, Any]:
        return {"hero_id": hero_id, "name": "Kael"}


class FakeClient:
    def __init__(self) -> None:
        self.StaticDataApi = FakeStaticDataApi()


class FakeQueryGateway:
    async def query(self, api_group: str, method: str, **params: Any) -> Any:
        return {"api_group": api_group, "method": method, "params": params}


def test_query_service_forwards_query_request() -> None:
    service = RaidToolkitQueryService(FakeQueryGateway())

    result = asyncio.run(
        service.fetch(
            api_group="StaticDataApi",
            method="get_hero_data",
            params={"hero_id": 7},
        )
    )

    assert result == {
        "api_group": "StaticDataApi",
        "method": "get_hero_data",
        "params": {"hero_id": 7},
    }


def test_rtk_gateway_query_calls_underlying_api_method() -> None:
    gateway = RaidToolkitAccountsGateway(client=FakeClient())

    result = asyncio.run(
        gateway.query("StaticDataApi", "get_hero_data", hero_id=6)
    )

    assert result == {"hero_id": 6, "name": "Kael"}


def test_rtk_gateway_query_rejects_unknown_api_group() -> None:
    gateway = RaidToolkitAccountsGateway(client=FakeClient())

    with pytest.raises(ValueError, match="Unknown API group"):
        asyncio.run(gateway.query("NopeApi", "get_hero_data"))


def test_rtk_gateway_query_rejects_unknown_method() -> None:
    gateway = RaidToolkitAccountsGateway(client=FakeClient())

    with pytest.raises(ValueError, match="Unknown method"):
        asyncio.run(gateway.query("StaticDataApi", "missing_method"))
