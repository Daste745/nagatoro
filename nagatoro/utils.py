from discord import Asset, Member, User


def format_bool(
    value: bool,
    *,
    positive: str = "Yes",
    negative: str = "No",
) -> str:
    return positive if value else negative


def get_user_avatar(user: User | Member) -> Asset:
    """
    Returns user avatar Asset

    - If user is a `Member` and has a guild avatar, return `guild_avatar`
    - If user has a normal avatar, return `avatar`
    - If user doesn't have a guild avatar, nor a normal avatar, return `default_avatar`

    - If user has an animated avatar, return it with the 'gif' format
    """

    avatar = user.display_avatar

    if avatar.is_animated():
        avatar = avatar.with_format("gif")

    return avatar
