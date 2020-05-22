import aiohttp

from discord.ext.commands.errors import BadArgument


async def anilist(query: str, variables: dict) -> dict:
    async with aiohttp.ClientSession() as cs:
        async with cs.post(
                "https://graphql.anilist.co",
                json={'query': query, 'variables': variables}) as request:
            response = await request.json()

            if not (errors := response["errors"]):
                return response

            for error in errors:
                if error["status"] == 404:
                    raise BadArgument(message=error["message"])
