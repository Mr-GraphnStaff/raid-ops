import asyncio

from raid_ops.connectors.rtk_client import RaidToolkitAccountsGateway
from raid_ops.services.account_service import AccountService


async def main() -> None:
    gateway = RaidToolkitAccountsGateway()
    gateway.connect()

    service = AccountService(gateway)
    accounts = await service.list_account_summaries()
    print("Accounts found:", service.as_raw_list(accounts))

    gateway.close()


if __name__ == "__main__":
    asyncio.run(main())
