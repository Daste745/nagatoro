import aiohttp

from discord.ext.commands.errors import BadArgument


async def anilist(query: str, variables: dict) -> dict:
    async with aiohttp.ClientSession() as cs:
        async with cs.post(
                "https://graphql.anilist.co",
                json={'query': query, 'variables': variables}) as request:
            response = await request.json()

            if "errors" not in response:
                return response

            errors = response["errors"]
            for error in errors:
                if error["status"] == 404:
                    raise BadArgument(message=error["message"])
