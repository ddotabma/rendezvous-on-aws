import httpx
from typing import List
import asyncio
import os


async def multiple_get_requests(url_list: List[str]):
    async with httpx.AsyncClient(timeout=20) as client:
        return await asyncio.gather(*[get(client, i) for i in url_list])


async def get(session: httpx.AsyncClient, url: str) -> list:
    response = await session.get(url)  # Make single http request
    return response.json()  # type: ignore # Obtain response body as dict


results = asyncio.run(
    multiple_get_requests(
        [os.environ["API"] for _ in range(2)]  # todo make var
    )
)

print(results)

print(f"{len(results)} responses")
