import aiohttp


async def anilist(query: str, variables: dict) -> dict:
    async with aiohttp.ClientSession() as cs:
        async with cs.post(
                "https://graphql.anilist.co",
                json={'query': query, 'variables': variables}) as request:
            return await request.json()
