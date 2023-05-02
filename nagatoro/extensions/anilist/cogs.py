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

    async def media_autocomplete(
        self, current: str, media_type: MediaType
    ) -> list[app_commands.Choice[str]]:
        searched = await self.api_client.search_media(
            current, media_type, max_results=10
        )
        return [
            app_commands.Choice(name=entry.title.romaji, value=entry.title.romaji)
            for entry in searched
        ]

    async def anime_autocomplete(
        self, _itx: Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        return await self.media_autocomplete(current, MediaType.ANIME)

    async def manga_autocomplete(
        self, _itx: Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        return await self.media_autocomplete(current, MediaType.MANGA)

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

    @app_commands.command()
    @app_commands.autocomplete(title=manga_autocomplete)
    async def manga(self, itx: Interaction, title: str):
        found_manga = await self.api_client.find_media(title, MediaType.MANGA)

        embed = Embed(title=found_manga.title.romaji)
        if cover_image := found_manga.cover_image:
            embed.set_thumbnail(url=cover_image.large)

        embed.add_field(name="Format", value=f"{found_manga.format}")
        embed.add_field(name="Status", value=f"{found_manga.status}")

        await itx.response.send_message(embed=embed)
