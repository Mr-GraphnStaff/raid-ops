import asyncio
import json
from argparse import ArgumentParser, Namespace
from enum import Enum
from pathlib import Path
from typing import Any

from raid_ops.connectors.rtk_client import QueryGateway, RaidToolkitAccountsGateway
from raid_ops.connectors.snapshot_gateway import JsonSnapshotAccountsGateway
from raid_ops.services.account_service import AccountService
from raid_ops.services.query_service import RaidToolkitQueryService
from raid_ops.services.runtime_mode import RuntimeConfig, RuntimeMode


class AccountsSource(str, Enum):
    SNAPSHOT = "snapshot"
    RTK = "rtk"


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
        "--mode",
        default=RuntimeMode.READ_ONLY.value,
        choices=[mode.value for mode in RuntimeMode],
        help="Runtime mode; read_only is the default safe mode.",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="For 'accounts', print raw RTK payloads instead of typed summaries.",
    )
    parser.add_argument(
        "--source",
        default=AccountsSource.SNAPSHOT.value,
        choices=[source.value for source in AccountsSource],
        help="Account source. Defaults to offline snapshot mode.",
    )
    parser.add_argument(
        "--snapshot-path",
        default="data/account_snapshot.json",
        help="Path to JSON snapshot used for --source snapshot.",
    )
    parser.add_argument(
        "--rtk-timeout-sec",
        type=float,
        default=10.0,
        help="Timeout in seconds for RTK API calls before fallback.",
    )
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


async def _list_accounts_with_gateway(gateway: Any) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    service = AccountService(gateway)
    records = await service.list_account_records()
    summaries = await service.list_account_summaries()
    return service.as_raw_list(records), service.as_summary_list(summaries)


async def _list_accounts(
    source: AccountsSource,
    snapshot_path: Path,
    rtk_timeout_sec: float,
) -> tuple[str, list[dict[str, Any]], list[dict[str, str]]]:
    if source is AccountsSource.SNAPSHOT:
        snapshot_gateway = JsonSnapshotAccountsGateway(snapshot_path)
        snapshot_gateway.connect()
        try:
            raw_rows, summary_rows = await _list_accounts_with_gateway(snapshot_gateway)
            return source.value, raw_rows, summary_rows
        finally:
            snapshot_gateway.close()

    rtk_gateway = RaidToolkitAccountsGateway()
    rtk_gateway.connect()
    try:
        raw_rows, summary_rows = await asyncio.wait_for(
            _list_accounts_with_gateway(rtk_gateway),
            timeout=rtk_timeout_sec,
        )
        return source.value, raw_rows, summary_rows
    except Exception as error:
        print(
            "RTK source unavailable "
            f"({type(error).__name__}: {error}). Falling back to snapshot '{snapshot_path}'."
        )
        snapshot_gateway = JsonSnapshotAccountsGateway(snapshot_path)
        snapshot_gateway.connect()
        try:
            raw_rows, summary_rows = await _list_accounts_with_gateway(snapshot_gateway)
            return AccountsSource.SNAPSHOT.value, raw_rows, summary_rows
        finally:
            snapshot_gateway.close()
    finally:
        rtk_gateway.close()


async def _run_query_with_gateway(
    gateway: QueryGateway,
    api_group: str,
    method: str,
    params: dict[str, Any],
    timeout_sec: float,
) -> Any:
    service = RaidToolkitQueryService(gateway)
    return await asyncio.wait_for(
        service.fetch(api_group=api_group, method=method, params=params),
        timeout=timeout_sec,
    )


async def main() -> None:
    args = _parse_args()
    runtime = RuntimeConfig(mode=RuntimeMode(args.mode))
    source = AccountsSource(args.source)
    snapshot_path = Path(args.snapshot_path)

    if args.command == "accounts":
        used_source, raw_rows, summary_rows = await _list_accounts(
            source=source,
            snapshot_path=snapshot_path,
            rtk_timeout_sec=args.rtk_timeout_sec,
        )
        if args.raw:
            print("Accounts found:", raw_rows)
        else:
            print("Accounts found:", summary_rows)
        print("Account source:", used_source)
    else:
        if source is not AccountsSource.RTK:
            print("Query mode requires RTK; forcing source='rtk'.")
        params = _load_params(args.params)
        gateway = RaidToolkitAccountsGateway()
        gateway.connect()
        try:
            payload = await _run_query_with_gateway(
                gateway=gateway,
                api_group=args.api_group,
                method=args.method,
                params=params,
                timeout_sec=args.rtk_timeout_sec,
            )
            print(
                json.dumps(
                    {"runtime_mode": runtime.mode.value, "payload": payload},
                    indent=2,
                    sort_keys=True,
                    default=str,
                )
            )
        finally:
            gateway.close()


if __name__ == "__main__":
    asyncio.run(main())
