from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class MediaTitle(BaseModel):
    romaji: str | None
    english: str | None
    native: str | None


class MediaType(str, Enum):
    ANIME = "ANIME"
    MANGA = "MANGA"


class MediaFormat(str, Enum):
    TV = "TV"
    TV_SHORT = "TV_SHORT"
    MOVIE = "MOVIE"
    SPECIAL = "OVA"
    ONA = "ONA"
    MUSIC = "MUSIC"
    MANGA = "MANGA"
    NOVEL = "NOVEL"
    ONE_SHOT = "ONE_SHOT"


class MediaStatus(str, Enum):
    FINISHED = "FINISHED"
    RELEASING = "RELEASING"
    NOT_YET_RELEASED = "NOT_YET_RELEASED"
    CANCELLED = "CANCELLED"
    HIATUS = "HIATUS"


class FuzzyDate(BaseModel):
    year: int | None
    month: int | None
    day: int | None


class MediaSeason(str, Enum):
    WINTER = "WINTER"
    SPRING = "SPRING"
    SUMMER = "SUMMER"
    FALL = "FALL"


class MediaSource(str, Enum):
    ORIGINAL = "ORIGINAL"
    MANGA = "MANGA"
    LIGHT_NOVEL = "LIGHT_NOVEL"
    VISUAL_NOVEL = "VISUAL_NOVEL"
    VIDEO_GAME = "VIDEO_GAME"
    OTHER = "OTHER"
    NOVEL = "NOVEL"
    DOUJINSHI = "DOUJINSHI"
    ANIME = "ANIME"
    WEB_NOVEL = "WEB_NOVEL"
    LIVE_ACTION = "LIVE_ACTION"
    GAME = "GAME"
    COMIC = "COMIC"
    MULTIMEDIA_PROJECT = "MULTIMEDIA_PROJECT"
    PICTURE_BOOK = "PICTURE_BOOK"


class MediaTrailer(BaseModel):
    id: str | None
    site: str | None
    thumbnail: str | None


class MediaCoverImage(BaseModel):
    extra_large: str | None
    large: str | None
    medium: str | None
    color: str | None


class MediaTag(BaseModel):
    id: int
    name: str
    description: str | None
    category: str | None
    rank: int | None
    is_general_spoiler: bool | None
    is_media_spoiler: bool | None
    is_adult: bool | None
    user_id: int | None


class ExternalLinkType(str, Enum):
    INFO = "INFO"
    STREAMING = "STREAMING"
    SOCIAL = "SOCIAL"


class AiringSchedule(BaseModel):
    id: int
    airing_at: int
    time_until_airing: int
    episode: int
    media_id: int
    media: Media | None


class MediaExternalLink(BaseModel):
    id: int
    url: str | None
    site: str
    site_id: int | None
    type: ExternalLinkType | None
    language: str | None
    color: str | None
    icon: str | None
    notes: str | None
    is_disabled: bool | None


class MediaStreamingEpisode(BaseModel):
    title: str | None
    thumbnail: str | None
    url: str | None
    site: str | None


class MediaRankType(str, Enum):
    RATED = "RATED"
    POPULAR = "POPULAR"


class MediaRank(BaseModel):
    id: int
    rank: int
    type: MediaRankType
    format: MediaFormat
    year: int | None
    season: MediaSeason
    all_time: bool | None
    context: str


class ScoreDistribution(BaseModel):
    score: int | None
    amount: int | None


class MediaListStatus(str, Enum):
    CURRENT = "CURRENT"
    PLANNING = "PLANNING"
    COMPLETED = "COMPLETED"
    DROPPED = "DROPPED"
    PAUSED = "PAUSED"
    REPEATING = "REPEATING"


class StatusDistribution(BaseModel):
    status: MediaListStatus | None
    amount: int | None


class MediaStats(BaseModel):
    score_distribution: list[ScoreDistribution | None] | None
    status_distribution: list[StatusDistribution | None] | None


class Media(BaseModel):
    id: int
    id_mal: int | None
    title: MediaTitle | None
    type: MediaType | None
    format: MediaFormat | None
    status: MediaStatus | None
    description: str | None
    start_date: FuzzyDate | None
    end_date: FuzzyDate | None
    season: MediaSeason | None
    season_year: int | None
    season_int: int | None
    episodes: int | None
    duration: int | None
    chapters: int | None
    volumes: int | None
    country_of_origin: str | None
    is_licensed: bool | None
    source: MediaSource | None
    hashtag: str | None
    trailer: MediaTrailer | None
    updated_at: int | None
    cover_image: MediaCoverImage | None
    banner_image: str | None
    genres: list[str | None] | None
    synonyms: list[str | None] | None
    average_score: int | None
    mean_score: int | None
    popularity: int | None
    is_locked: bool | None
    trending: int | None
    favourites: int | None
    tags: list[MediaTag | None] | None
    # TODO: relations
    # TODO: characters
    # TODO: staff
    # TODO: studios
    # TODO: is_favourite
    is_favourite_blocked: bool
    is_adult: bool | None
    next_airing_episode: AiringSchedule | None
    # TODO: airing_schedule
    # TODO: trends
    external_links: list[MediaExternalLink | None] | None
    streaming_episodes: list[MediaStreamingEpisode | None] | None
    rankings: list[MediaRank | None] | None
    # TODO: media_list_entry
    # TODO: reviews
    # TODO: recommendations
    stats: MediaStats | None
    site_url: str | None
    auto_create_forum_thread: bool | None
    is_recommendation_blocked: bool | None
    is_review_blocked: bool | None
    mod_notes: str | None
