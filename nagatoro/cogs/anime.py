from discord import Color
from discord.ext.commands import Cog, Context, command, cooldown, BucketType

from nagatoro.objects import Embed
from nagatoro.utils import anilist


class Anime(Cog):
    """Anime and manga info using AniList"""

    def __init__(self, bot):
        self.bot = bot

    @command(name="anime")
    @cooldown(rate=5, per=20, type=BucketType.user)
    async def anime(self, ctx: Context, *, title: str):
        """Anime info from AniList"""
        query = """
        query ($title: String) {
            Media (search: $title, type: ANIME) {
                title {english}
                coverImage {medium color}
                description(asHtml: false)
                siteUrl
                status
                episodes
                duration
                season
                seasonYear
                format
                averageScore
                genres
            }
        }
        """
        anime = (await anilist(query, {"title": title}))["data"]["Media"]

        embed = Embed(ctx, title=anime["title"]["english"],
                      color=Color(int(
                          anime["coverImage"]["color"].replace("#", ""), 16)),
                      url=anime["siteUrl"], footer="Via AniList")
        description = \
            anime["description"].replace("<br>", "").replace("\n", " ")
        embed.description = f"{description[:250]}..." \
            if len(description) >= 250 else description
        embed.set_thumbnail(url=anime["coverImage"]["medium"])

        embed.add_fields(
            ("Status", anime["status"].title()),
            ("Episodes", anime["episodes"]),
            ("Episode length", f"{anime['duration']} minute(s)"),
            ("Season", f"{anime['season'].title()} {anime['seasonYear']}"),
            ("Format", anime["format"].title().replace("_", " ")),
            ("Score", f"{anime['averageScore']} / 100"),
            ("Genres", ", ".join(anime["genres"]))
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Anime(bot))
