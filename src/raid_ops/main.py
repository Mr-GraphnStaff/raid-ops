import asyncio
import json
from argparse import ArgumentParser, Namespace
from typing import Any

from raid_ops.connectors.rtk_client import RaidToolkitAccountsGateway
from raid_ops.services.account_service import AccountService
from raid_ops.services.query_service import RaidToolkitQueryService


def _parse_args() -> Namespace:
    parser = ArgumentParser(description="raid-ops RTK connectivity CLI")
    parser.add_argument(
        "command",
        nargs="?",
        default="accounts",
        choices=("accounts", "query"),
        help="Operation to run.",
    )
    parser.add_argument("--api-group", default="StaticDataApi")
    parser.add_argument("--method", default="get_all_data")
    parser.add_argument(
        "--params",
        default="{}",
        help="JSON object of keyword args passed to the chosen RTK method.",
    )
    return parser.parse_args()


def _load_params(raw_params: str) -> dict[str, Any]:
    parsed = json.loads(raw_params)
    if not isinstance(parsed, dict):
        raise ValueError("--params must decode to a JSON object.")
    return parsed


async def main() -> None:
    args = _parse_args()
    gateway = RaidToolkitAccountsGateway()
    gateway.connect()

    if args.command == "accounts":
        service = AccountService(gateway)
        accounts = await service.list_account_summaries()
        print("Accounts found:", service.as_raw_list(accounts))
    else:
        params = _load_params(args.params)
        service = RaidToolkitQueryService(gateway)
        payload = await service.fetch(
            api_group=args.api_group, method=args.method, params=params
        )
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))

    gateway.close()


if __name__ == "__main__":
    asyncio.run(main())
