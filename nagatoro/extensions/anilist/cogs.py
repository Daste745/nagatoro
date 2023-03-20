from discord import Embed, Interaction, app_commands

from nagatoro.common import Cog
from nagatoro.common.bot import Bot
from nagatoro.extensions.anilist.client import AniListClient
from nagatoro.extensions.anilist.models import MediaType


class AniList(Cog):
    def __init__(self, bot: Bot):
        super().__init__(bot)
        self.api_client = AniListClient()

    async def cog_unload(self) -> None:
        await self.api_client.close()

    async def anime_autocomplete(
        self, itx: Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        searched = await self.api_client.search_media(
            current, MediaType.ANIME, max_results=25
        )
        return [
            app_commands.Choice(name=entry.title.romaji, value=entry.title.romaji)
            for entry in searched
        ]

    @app_commands.command()
    @app_commands.autocomplete(title=anime_autocomplete)
    async def anime(self, itx: Interaction, title: str):
        found_anime = await self.api_client.find_media(title, MediaType.ANIME)

        embed = Embed(title=found_anime.title.romaji)
        if cover_image := found_anime.cover_image:
            embed.set_thumbnail(url=cover_image.large)

        embed.add_field(name="Format", value=f"{found_anime.format}")
        embed.add_field(name="Status", value=f"{found_anime.status}")

        await itx.response.send_message(embed=embed)
