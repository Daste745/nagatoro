import asyncio
from os import path

from aiohttp import ClientSession

from nagatoro.extensions.anilist.models import Media, MediaBasic, MediaRank, MediaType

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
        """Find a Media object by its title and type"""

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

        rankings = []
        for ranking in media_data.get("rankings", []):
            rankings.append(
                MediaRank(
                    id=ranking.get("id"),
                    rank=ranking.get("rank"),
                    type=ranking.get("type"),
                    format=ranking.get("format"),
                    year=ranking.get("year"),
                    season=ranking.get("season"),
                    all_time=ranking.get("allTime"),
                    context=ranking.get("context"),
                )
            )

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
            episodes=media_data.get("episodes"),
            duration=media_data.get("duration"),
            chapters=media_data.get("chapters"),
            volumes=media_data.get("volumes"),
            cover_image=media_data.get("coverImage"),
            banner_image=media_data.get("bannerImage"),
            genres=media_data.get("genres"),
            is_favourite_blocked=media_data.get("isFavouriteBlocked"),
            rankings=rankings,
            site_url=media_data.get("siteUrl"),
        )

    async def search_media(
        self,
        title: str,
        media_type: MediaType,
        *,
        max_results: int = 10,
    ) -> list[MediaBasic]:
        """Search basic information about Media by its title and type"""

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
            MediaBasic(
                id=entry.get("id"),
                title=entry.get("title"),
            )
            for entry in media_entries
        ]
