import aiohttp

from discord.ext.commands.errors import BadArgument


async def trace(image_url: str) -> dict:
    async with aiohttp.ClientSession() as cs:
        async with cs.post(
                f"https://trace.moe/api/search?url={image_url}") as request:
            if request.status == 500:
                raise BadArgument(message="Invalid URL")

            search = await request.json()

    return search
