from discord import Color
from discord.ext.commands import Cog, Context, command, cooldown, BucketType

from nagatoro.objects import Embed
from nagatoro.utils import anilist


def clean_description(text: str) -> str:
    return text. \
        replace("<br>", ""). \
        replace("\n", " "). \
        replace("&ndash;", " - ")


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
            Media (search: $title, type: ANIME, sort: POPULARITY_DESC) {
                title {romaji}
                coverImage {extraLarge color}
                description (asHtml: false)
                siteUrl
                status
                episodes
                duration
                season
                seasonYear
                format
                averageScore
                genres
                studios (isMain: true) {nodes {name}}
            }
        }
        """
        anime = (await anilist(query, {"title": title}))["data"]["Media"]

        embed = Embed(ctx, title=anime["title"]["romaji"],
                      url=anime["siteUrl"], footer="Via AniList")

        embed.set_thumbnail(url=anime["coverImage"]["extraLarge"])

        description = clean_description(anime["description"])
        embed.description = f"Synopsis: ||{description[:250]}...||" \
            if len(description) >= 250 else f"Synopsis: ||{description}||"

        if color_hex := anime["coverImage"]["color"]:
            embed.color = Color(int(color_hex.replace("#", ""), 16))
        else:
            embed.color = Color.blue()

        embed.add_fields(
            ("Status", anime["status"].title()),
            ("Episodes", anime["episodes"]),
            ("Episode length", f"{anime['duration']} minutes"),
            ("Season", f"{anime['season'].title()} {anime['seasonYear']}"),
            ("Format", anime["format"].title().replace("_", " ")),
            ("Score", f"{anime['averageScore']} / 100"),

        )

        if anime_studios := anime["studios"]["nodes"]:
            embed.add_field(name="Studio", value=anime_studios[0]["name"])

        if anime["genres"]:
            embed.add_field(name="Genres", value=", ".join(anime["genres"]))

        # TODO: Add pagination.
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Anime(bot))
