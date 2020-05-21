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
                title {romaji}
                coverImage {extraLarge color}
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
                studios(isMain: true) {nodes {name}}
            }
        }
        """
        anime = (await anilist(query, {"title": title}))["data"]["Media"]
        # TODO: Add error raises to 'anilist' function
        if not anime:
            return await ctx.send(f"Anime {title} not found.")

        embed = Embed(ctx, title=anime["title"]["romaji"],
                      color=Color(int(
                          anime["coverImage"]["color"].replace("#", ""), 16)),
                      url=anime["siteUrl"], footer="Via AniList")

        description = \
            anime["description"].replace("<br>", "").replace("\n", " ")
        embed.description = f"Synopsis: ||{description[:250]}...||" \
            if len(description) >= 250 else f"Synopsis: ||{description}||"

        embed.set_thumbnail(url=anime["coverImage"]["extraLarge"])

        embed.add_fields(
            ("Status", anime["status"].title()),
            ("Episodes", anime["episodes"]),
            ("Episode length", f"{anime['duration']} minutes"),
            ("Season", f"{anime['season'].title()} {anime['seasonYear']}"),
            ("Format", anime["format"].title().replace("_", " ")),
            ("Score", f"{anime['averageScore']} / 100"),

        )

        # These information are not guaranteed to exist for every anime
        if anime["studios"]["nodes"]:
            embed.add_field(name="Studio",
                            value=anime["studios"]["nodes"][0]["name"])

        if anime["genres"]:
            embed.add_field(name="Genres", value=", ".join(anime["genres"]))

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Anime(bot))
