from discord import Color
from discord.ext.commands import Cog, Context, command, BucketType, \
    CooldownMapping
from discord.ext.commands.errors import CommandOnCooldown

from nagatoro.objects import Embed
from nagatoro.utils import anilist, trace


def clean_description(text: str) -> str:
    return text. \
        replace("<br>", ""). \
        replace("\n", " "). \
        replace("&ndash;", " - "). \
        replace("<i>", "*"). \
        replace("</i>", "*"). \
        replace("<b>", "**"). \
        replace("</b>", "**"). \
        replace("~!", " "). \
        replace("!~", " ")


class Anime(Cog):
    """Anime and manga info using AniList"""

    def __init__(self, bot):
        self.bot = bot
        self._cooldown = CooldownMapping.from_cooldown(rate=5, per=20,
                                                       type=BucketType.user)

    async def cog_before_invoke(self, ctx: Context):
        # Cog-wide cooldowns, every command is on a shared cooldown.
        # Will get removed if any command gets its own cooldown.
        bucket = self._cooldown.get_bucket(ctx.message)
        if retry_after := bucket.update_rate_limit():
            raise CommandOnCooldown(self._cooldown, retry_after)

    @command(name="anilist", aliases=["al"])
    async def anilist(self, ctx: Context, *, username: str):
        """AniList profile

        Shows anime/manga stats and favorites.
        """

        query = """
        query ($username: String) {
            User (name: $username) {
                name
                avatar {large}
                siteUrl
                favourites {
                    anime {
                        nodes {title {romaji} siteUrl}
                    }
                    manga {
                        nodes {title {romaji} siteUrl}
                    }
                    characters {
                        nodes {name {full} siteUrl}
                    }
                    staff {
                        nodes {name {full} siteUrl}
                    }
                    studios {
                        nodes {name siteUrl}
                    }
                }
            }
        }
        """
        list_query = """
        query ($username: String, $type: MediaType) {
            MediaListCollection (userName: $username, type: $type) {
                lists {status name entries {id}}
            }
        }
        """

        await ctx.trigger_typing()
        user = (await anilist(query, {"username": username}))["data"]["User"]
        anime_lists, manga_lists = [(await anilist(
            list_query,
            {"username": username, "type": i}
        ))["data"]["MediaListCollection"]["lists"]
                                    for i in ["ANIME", "MANGA"]]

        embed = Embed(ctx, title=user["name"],
                      url=user["siteUrl"], footer="Via AniList")

        embed.set_thumbnail(url=user["avatar"]["large"])

        if anime_lists:
            anime_list_body = ""
            for i in anime_lists:
                if i["status"]:
                    status = i["status"] \
                        .replace("COMPLETED", "✅") \
                        .replace("PLANNING", "🗓️") \
                        .replace("DROPPED", "🗑️") \
                        .replace("CURRENT", "📺") \
                        .replace("PAUSED", "⏸️") \
                        .replace("REPEATING", "🔁")
                else:
                    status = "⚙️"

                anime_list_body += f"{status} **{len(i['entries'])}** " \
                                   f"{i['name']}\n"

            embed.add_field(name="Anime", value=anime_list_body)

        if manga_lists:
            manga_list_body = ""
            for i in manga_lists:
                if i["status"]:
                    status = i["status"] \
                        .replace("COMPLETED", "✅") \
                        .replace("PLANNING", "🗓️") \
                        .replace("DROPPED", "🗑️️") \
                        .replace("CURRENT", "📖") \
                        .replace("PAUSED", "⏸️") \
                        .replace("REPEATING", "🔁")
                else:
                    status = "⚙️"

                manga_list_body += f"{status} **{len(i['entries'])}** " \
                                   f"{i['name']}\n"

            embed.add_field(name="Manga", value=manga_list_body)

        if any(user["favourites"][i]["nodes"] for i in user["favourites"]):
            favorites_body = ""
            for i in user["favourites"]:
                if not user["favourites"][i]["nodes"]:
                    continue

                # Section header
                favorites_body += f"__{i.title()}__"

                # Show total amount of favs if they exceed a limit (3)
                if (favorites_count := len(user['favourites'][i]['nodes'])) > 3:
                    favorites_body += \
                        f" ({favorites_count})"
                favorites_body += "\n"

                for item in user["favourites"][i]["nodes"][:3]:
                    # There are three types of names, so unify them.
                    if i in ["anime", "manga"]:
                        name = item['title']['romaji']
                    elif i in ["characters", "staff"]:
                        name = item['name']['full']
                    else:
                        name = item['name']

                    favorites_body += f"[{name}]({item['siteUrl']})\n"

            embed.add_field(name="Favorites", value=favorites_body,
                            inline=False)

        await ctx.send(embed=embed)

    @command(name="anime")
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
        most_popular = ["Popularity ⭐ Favorites ❤"]
        for i in studio["media"]["nodes"]:
            most_popular.append(
                f"{i['popularity']} ⭐ {i['favourites']} ❤️ "
                f"[{i['title']['romaji']}]({i['siteUrl']}) "
            )

        embed.add_field(name="Most popular productions",
                        value="\n".join(most_popular))

        await ctx.send(embed=embed)

    @command(name="character", aliases=["char", "chr"])
    async def character(self, ctx: Context, *, name: str):
        """Character info from AniList"""

        query = """
        query ($name: String) {
            Character (search: $name) {
                name {full}
                image {large}
                description (asHtml: false)
                siteUrl
                favourites
                media (perPage: 10) {
                    edges {
                        node {
                            title {romaji}
                            siteUrl
                        }
                        characterRole
                    }
                }
            }
        }
        """

        character = (await anilist(query, {"name": name}))["data"]["Character"]

        embed = Embed(ctx, title=character["name"]["full"], description="",
                      url=character["siteUrl"], footer="Via AniList",
                      color=Color.blue())

        embed.set_thumbnail(url=character["image"]["large"])

        if character["favourites"]:
            embed.description += f"❤️ {character['favourites']} favorites \n\n"

        if character["description"]:
            description = clean_description(character["description"])
            embed.description += f"Description: ||{description[:250]}...||" \
                if len(description) >= 250 \
                else f"Description: ||{description}||"

        appears_in = ["Main 🌕 Supporting 🌗 Background 🌑"]
        for i in character["media"]["edges"]:
            role = i["characterRole"] \
                .replace("MAIN", "🌕") \
                .replace("SUPPORTING", "🌗") \
                .replace("BACKGROUND", "🌑")

            appears_in.append(f"{role} [{i['node']['title']['romaji']}]"
                              f"({i['node']['siteUrl']})")

        embed.add_field(name="Appears in", value="\n".join(appears_in))

        await ctx.send(embed=embed)

    @command(name="trace")
    async def trace(self, ctx: Context, image_url: str = None):
        """Trace.moe image search

        Uses the trace.moe image search to find what anime it's from.
        This search engine recognizes only images/gifs from anime.
        When searching with a gif, the first frame is used.
        Tenor links don't work, because they don't provide a direct image URL.
        All NSFW results are hidden.
        """

        if not image_url:
            if not (attachments := ctx.message.attachments):
                # TODO: Raise a MissingRequiredArgument or other error
                return await ctx.send(
                    "Please provide an image (url or attachment)")

            image_url = attachments[0].url

        image_name = image_url.split("/")[-1]
        embed = Embed(ctx, title="Image search", footer="Via trace.moe",
                      description=f"Searching with *{image_name}* ...",
                      color=Color.blue())
        message = await ctx.send(embed=embed)
        search = await trace(image_url)
        embed.description = ""

        for result in search["docs"]:
            if result["is_adult"]:
                continue

            embed.description += \
                f"[{result['title_romaji']}]" \
                f"(https://anilist.co/anime/{result['anilist_id']}) " \
                f"episode {result['episode']} " \
                f"({round(result['similarity'] * 100)}%)\n"

        # TODO: Implement video previews
        await message.edit(embed=embed)


def setup(bot):
    bot.add_cog(Anime(bot))
