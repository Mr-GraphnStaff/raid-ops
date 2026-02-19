import asyncio
from raidtoolkit import RaidToolkitClient


async def main():
    client = RaidToolkitClient()
    client.connect()

    accounts = await client.AccountApi.get_accounts()
    print("Accounts found:", accounts)

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
