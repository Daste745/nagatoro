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
            Media (search: $title, type: ANIME) {
                title {romaji}
                coverImage {extraLarge color}
                description (asHtml: false)
                siteUrl
                rankings {rank allTime type context}
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

        embed = Embed(ctx, title=anime["title"]["romaji"], description="",
                      url=anime["siteUrl"], footer="Via AniList")

        embed.set_thumbnail(url=anime["coverImage"]["extraLarge"])

        for i in anime["rankings"]:
            if not i["allTime"]:
                continue

            if i["type"] == "RATED":
                embed.description += "⭐"
            elif i["type"] == "POPULAR":
                embed.description += "❤️"

            embed.description += f" #{i['rank']} {i['context'].title()}\n"
        embed.description += "\n"

        if description := clean_description(anime["description"]):
            embed.description += f"Synopsis: ||{description[:250]}...||" \
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

    @command(name="manga")
    @cooldown(rate=5, per=20, type=BucketType.user)
    async def manga(self, ctx: Context, *, title: str):
        """Manga info from AniList"""

        query = """
        query ($title: String) {
            Media (search: $title, type: MANGA) {
                title {romaji}
                coverImage {extraLarge color}
                description (asHtml: false)
                siteUrl
                rankings {rank allTime type context}
                status
                chapters
                volumes
                format
                averageScore
                genres
            }
        }
        """
        manga = (await anilist(query, {"title": title}))["data"]["Media"]

        embed = Embed(ctx, title=manga["title"]["romaji"], description="",
                      url=manga["siteUrl"], footer="Via AniList")

        embed.set_thumbnail(url=manga["coverImage"]["extraLarge"])

        for i in manga["rankings"]:
            if not i["allTime"]:
                continue

            if i["type"] == "RATED":
                embed.description += "⭐"
            elif i["type"] == "POPULAR":
                embed.description += "❤️"

            embed.description += f" #{i['rank']} {i['context'].title()}\n"
        embed.description += "\n"

        if manga["description"]:
            description = clean_description(manga["description"])
            embed.description += f"Synopsis: ||{description[:250]}...||" \
                if len(description) >= 250 else f"Synopsis: ||{description}||"

        if color_hex := manga["coverImage"]["color"]:
            embed.color = Color(int(color_hex.replace("#", ""), 16))
        else:
            embed.color = Color.blue()

        embed.add_field(name="Status", value=manga["status"].title())

        if manga["chapters"]:
            embed.add_field(name="Chapters", value=manga["chapters"])

        if manga["volumes"]:
            embed.add_field(name="Volumes", value=manga["volumes"])

        embed.add_field(name="Format", value=manga["format"].title())
        embed.add_field(name="Score", value=f"{manga['averageScore']} / 100")

        if manga["genres"]:
            embed.add_field(name="Genres", value=", ".join(manga["genres"]))

        # TODO: Add pagination.
        await ctx.send(embed=embed)

    @command(name="studio")
    @cooldown(rate=5, per=20, type=BucketType.user)
    async def studio(self, ctx: Context, *, name: str):
        """Studio info from AniList"""

        query = """
        query ($name: String) {
            Studio (search: $name, sort: SEARCH_MATCH) {
                name
                siteUrl
                isAnimationStudio
                media (sort: POPULARITY_DESC, perPage: 10) {
                    nodes {
                        title {romaji}
                        coverImage {extraLarge}
                        siteUrl
                        popularity
                        favourites
                    }
                }
            }
        }
        """
        studio = (await anilist(query, {"name": name}))["data"]["Studio"]

        embed = Embed(ctx, title=studio["name"],
                      url=studio["siteUrl"], footer="Via AniList")

        embed.set_thumbnail(
            url=studio["media"]["nodes"][0]["coverImage"]["extraLarge"])

        if studio["isAnimationStudio"]:
            embed.description = "Animation Studio"

        # TODO: Observe, if this breaks when isAnimationStudio=False.
        most_popular = ["(Popularity ⭐ Favorites ❤)"]
        for i in studio["media"]["nodes"]:
            most_popular.append(
                f"{i['popularity']} ⭐ {i['favourites']} ❤️ "
                f"[{i['title']['romaji']}]({i['siteUrl']}) "
            )

        embed.add_field(name="Most popular productions",
                        value="\n".join(most_popular))

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Anime(bot))
