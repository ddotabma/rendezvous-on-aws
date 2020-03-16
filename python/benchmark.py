import httpx
from typing import List
import asyncio
import os
import matplotlib.pyplot as plt


async def multiple_get_requests(url_list: List[str]):
    async with httpx.AsyncClient(timeout=20) as client:
        return await asyncio.gather(*[get(client, i) for i in url_list])


async def get(session: httpx.AsyncClient, url: str) -> list:
    response = await session.get(url)  # Make single http request
    return response.json()  # type: ignore # Obtain response body as dict


results = asyncio.run(
    multiple_get_requests(
        [os.environ["API"] for _ in range(4)]  # todo make var
    )
)

times = [i['total_time'] for i in results if 'total_time' in i]
no_times = [i['message'] for i in results if 'total_time' not in i]
print(results, len(times), len(no_times))

print(f"{len(results)} responses")
