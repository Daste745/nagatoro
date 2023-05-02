import asyncio
from os import path

from aiohttp import ClientSession

from nagatoro.extensions.anilist.models import Media, MediaSearch, MediaType

API_URL = "https://graphql.anilist.co/"


class AniListClient:
    def __init__(self):
        self._session = ClientSession()

    async def close(self):
        await self._session.close()

    async def find_media(
        self,
        title: str,
        media_type: MediaType,
        *,
        description_as_html: bool = False,
    ) -> Media:
        with open(path.join(path.dirname(__file__), "queries/media_full.gql")) as query:
            request_data = {
                "query": query.read().strip(),
                "variables": {
                    "title": title,
                    "type": media_type,
                    "descriptionAsHtml": description_as_html,
                },
            }

        async with self._session.post(API_URL, json=request_data) as response:
            response_data = await response.json()
            media_data = response_data["data"]["Media"]

        return Media(
            # TODO: Add missing fields
            id=media_data.get("id"),
            id_mal=media_data.get("idMal"),
            title=media_data.get("title"),
            type=media_data.get("type"),
            format=media_data.get("format"),
            status=media_data.get("status"),
            description=media_data.get("description"),
            start_date=media_data.get("startDate"),
            end_date=media_data.get("endDate"),
            season=media_data.get("season"),
            cover_image=media_data.get("coverImage"),
            banner_image=media_data.get("bannerImage"),
            is_favourite_blocked=media_data.get("isFavouriteBlocked"),
        )

    async def search_media(
        self,
        title: str,
        media_type: MediaType,
        max_results: int = 10,
    ) -> list[MediaSearch]:
        with open(
            path.join(path.dirname(__file__), "queries/media_search.gql")
        ) as query:
            request_data = {
                "query": query.read().strip(),
                "variables": {
                    "title": title,
                    "type": media_type,
                    "perPage": max_results,
                },
            }

        async with self._session.post(API_URL, json=request_data) as response:
            response_data = await response.json()
            media_entries = response_data["data"]["Page"]["media"]

        return [
            MediaSearch(
                id=entry.get("id"),
                title=entry.get("title"),
            )
            for entry in media_entries
        ]


async def main():
    client = AniListClient()
    anime = await client.find_media("yofukashi no uta", MediaType.ANIME)
    print(anime.season)
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
