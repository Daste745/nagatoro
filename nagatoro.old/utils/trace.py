import aiohttp


async def trace(image_url: str) -> dict:
    async with aiohttp.ClientSession() as cs:
        async with cs.post(
                f"https://trace.moe/api/search?url={image_url}") as request:
            if request.status == 500:
                return {"errors": "Invalid URL", "code": 500}

            search = await request.json()

    return search
