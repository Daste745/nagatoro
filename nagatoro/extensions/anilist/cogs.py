from discord import Colour as Color
from discord import Embed, Interaction, app_commands

from nagatoro.common import Cog
from nagatoro.common.bot import Bot
from nagatoro.extensions.anilist.client import AniListClient
from nagatoro.extensions.anilist.models import MediaRank, MediaRankType, MediaType


class AniList(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)
        self.api_client = AniListClient()

    async def cog_unload(self) -> None:
        await self.api_client.close()

    async def _media_autocomplete(
        self, title: str, media_type: MediaType
    ) -> list[app_commands.Choice[str]]:
        if title.strip == "":
            return []

        searched = await self.api_client.search_media(title, media_type, max_results=10)

        return [
            app_commands.Choice(name=entry.title.romaji, value=entry.title.romaji)
            for entry in searched
            if entry.title and entry.title.romaji
        ]

    async def _anime_autocomplete(
        self, _itx: Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        return await self._media_autocomplete(current, MediaType.ANIME)

    async def _manga_autocomplete(
        self, _itx: Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        return await self._media_autocomplete(current, MediaType.MANGA)

    def _format_media_rankings(self, rankings: list[MediaRank | None]) -> str:
        output = ""

        for ranking in rankings:
            if ranking is None or not ranking.all_time:
                continue

            if ranking.type == MediaRankType.POPULAR:
                output += f"❤️ #{ranking.rank} {ranking.context.title()}\n"
            elif ranking.type == MediaRankType.RATED:
                output += f"⭐ #{ranking.rank} {ranking.context.title()}\n"

        return output

    @app_commands.command()
    @app_commands.autocomplete(title=_anime_autocomplete)
    async def anime(self, itx: Interaction, title: str) -> None:
        found_anime = await self.api_client.find_media(title, MediaType.ANIME)
        description = ""

        if found_anime.rankings:
            description += self._format_media_rankings(found_anime.rankings)

        embed = Embed(
            title=found_anime.title.romaji if found_anime.title else title,
            description=description,
            url=found_anime.site_url,
        )
        if cover_image := found_anime.cover_image:
            embed.set_thumbnail(url=cover_image.large)
            if cover_image.color:
                embed.colour = Color.from_str(cover_image.color)

        if found_anime.status:
            embed.add_field(name="Status", value=f"{found_anime.status.title()}")
        if found_anime.episodes:
            embed.add_field(name="Episodes", value=f"{found_anime.episodes}")
        if found_anime.duration:
            embed.add_field(name="Duration", value=f"{found_anime.duration} minutes")
        if found_anime.season:
            embed.add_field(name="Season", value=f"{found_anime.season.title()}")
        if found_anime.format:
            embed.add_field(name="Format", value=f"{found_anime.format.title()}")
        if found_anime.genres:
            embed.add_field(
                name="Genres",
                value=", ".join(genre.title() for genre in found_anime.genres if genre),
            )

        await itx.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.autocomplete(title=_manga_autocomplete)
    async def manga(self, itx: Interaction, title: str) -> None:
        found_manga = await self.api_client.find_media(title, MediaType.MANGA)
        description = ""

        if found_manga.rankings:
            description += self._format_media_rankings(found_manga.rankings)

        embed = Embed(
            title=found_manga.title.romaji if found_manga.title else title,
            description=description,
            url=found_manga.site_url,
        )
        if cover_image := found_manga.cover_image:
            embed.set_thumbnail(url=cover_image.large)
            if cover_image.color:
                embed.colour = Color.from_str(cover_image.color)

        if found_manga.status:
            embed.add_field(name="Status", value=f"{found_manga.status.title()}")
        if found_manga.chapters:
            embed.add_field(name="Chapters", value=f"{found_manga.chapters}")
        if found_manga.volumes:
            embed.add_field(name="Volumes", value=f"{found_manga.volumes}")
        if found_manga.season:
            embed.add_field(name="Season", value=f"{found_manga.season.title()}")
        if found_manga.format:
            embed.add_field(name="Format", value=f"{found_manga.format.title()}")
        if found_manga.genres:
            embed.add_field(
                name="Genres",
                value=", ".join(genre.title() for genre in found_manga.genres if genre),
            )

        await itx.response.send_message(embed=embed)
