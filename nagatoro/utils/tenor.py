import aiohttp


async def get_gif(query: str, api_key: str) -> str:
    action = f"anime {query}".replace(" ", "+")
    request_url = f"https://api.tenor.com/v1/random?" \
                  f"q={action}&key={api_key}&limit=1&media_filter=basic" \
                  f"&contentfilter=low"

    async with aiohttp.ClientSession() as cs:
        async with cs.get(request_url) as r:
            response = await r.json()

            return response["results"][0]["media"][0]["gif"]["url"]
