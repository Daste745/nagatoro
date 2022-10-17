from typing import Literal

from discord import Embed, Interaction, Member, Role, User, app_commands
from discord.utils import format_dt

from nagatoro.common import Bot, Cog
from nagatoro.utils import format_bool, get_user_avatar


class Utility(Cog):
    AssetSizeChoices = Literal[16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
    AssetFormatChoices = Literal["webp", "jpeg", "jpg", "png", "gif"]
    AssetProfileChoices = Literal["user", "server"]

    @app_commands.command()
    @app_commands.describe(profile="Profile (default: server if available)")
    @app_commands.describe(size="Image size (default: 1024)")
    @app_commands.describe(format="Image format (default: gif or png)")
    async def avatar(
        self,
        itx: Interaction,
        user: User | Member,
        profile: AssetProfileChoices | None = None,
        size: AssetSizeChoices = 1024,
        format: AssetFormatChoices | None = None,
    ):
        """Get someone's avatar"""

        if profile == "server":
            if itx.guild is None:
                return await itx.response.send_message(
                    f"The server profile is only supported on servers"
                )

            elif isinstance(user, User):
                return await itx.response.send_message(
                    f"{user} is not a member of this server"
                )

            elif isinstance(user, Member):
                if user.guild_avatar is None:
                    return await itx.response.send_message(
                        f"{user} doesn't have a server avatar"
                    )
                else:
                    avatar = user.guild_avatar

        elif profile == "user":
            # Manually get the `default_avatar`, because when user is of type `Member`,
            # `display_avatar` will return their guild avatar when available
            avatar = user.avatar or user.default_avatar

        elif profile is None:
            # `display_avatar` has an override on the `Member` type, which returns
            # `guild_avatar` or `avatar` or `default_avatar`
            avatar = user.display_avatar

        if format == "gif" and not avatar.is_animated():
            return await itx.response.send_message(
                f"{user} doesn't have an animated avatar, please use a different format"
            )

        elif format is None:
            format = "gif" if avatar.is_animated() else "png"

        avatar_url = avatar.with_size(size).with_format(format).url  # type: ignore
        embed = Embed(description=f"{user}'s avatar")
        embed.set_image(url=avatar_url)

        await itx.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.describe(size="Image size (default: 1024)")
    @app_commands.describe(format="Image format (default: gif or png)")
    async def banner(
        self,
        itx: Interaction,
        user: User | Member,
        size: AssetSizeChoices = 1024,
        format: AssetFormatChoices | None = None,
    ):
        """Get someone's banner"""
        # TODO: Guild vs global banner

        # Re-fetch the user in order to see their profile banner
        user = await self.bot.fetch_user(user.id)

        if user.banner is None:
            return await itx.response.send_message(f"{user} doesn't have a banner")

        if format == "gif" and not user.banner.is_animated():
            return await itx.response.send_message(
                f"{user} doesn't have an animated banner, please use a different format"
            )

        if format is None:
            format = "gif" if user.banner.is_animated() else "png"

        banner_url = user.banner.with_size(size).with_format(format).url  # type: ignore
        embed = Embed(description=f"{user}'s banner")
        embed.set_image(url=banner_url)

        await itx.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.guild_only()
    async def server(self, itx: Interaction):
        """See info about this server"""

        guild = itx.guild
        assert guild  # guild-only
        assert guild.owner  # members intent

        embed = Embed(title=guild.name)
        embed.set_footer(text=f"ID: {guild.id}")

        embed.add_field(name="Owner", value=guild.owner.mention)
        embed.add_field(
            name="Creation Date",
            value=format_dt(guild.created_at, style="D"),
        )

        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Roles", value=len(guild.roles))

        boosts_value = (
            f"Level: {guild.premium_tier}\n"
            f"Boosts: {guild.premium_subscription_count}"
        )
        embed.add_field(name="Server Boosts", value=boosts_value)

        channels_value = (
            f"Text: {len(guild.text_channels)}\n"
            f"Voice: {len(guild.voice_channels)}\n"
            f"Stage: {len(guild.stage_channels)}"
        )
        embed.add_field(name="Channels", value=channels_value)

        emoji_count = len(guild.emojis)
        if (emoji_count := len(guild.emojis)) > 0:
            emoji_value = " ".join(str(i) for i in guild.emojis[:20])
            if emoji_count > 20:
                emoji_value += f" ({emoji_count - 20} more)"
            embed.add_field(name="Emoji", value=emoji_value, inline=False)

        if icon := guild.icon:
            embed.set_thumbnail(url=icon.url)

        if banner := guild.banner:
            embed.set_image(url=banner)

        await itx.response.send_message(embed=embed)

    @app_commands.command()
    async def user(self, itx: Interaction, user: User | Member):
        """See info about a user"""

        if user.system:
            title = f"{user} [SYSTEM]"
        elif user.bot:
            title = f"{user} [BOT]"
        elif itx.guild and user == itx.guild.owner:
            title = f"{user} :crown:"
        else:
            title = str(user)

        embed = Embed(title=title)
        embed.set_footer(text=f"ID: {user.id}")

        embed.add_field(
            name="Creation Date", value=format_dt(user.created_at, style="D")
        )

        if isinstance(user, Member):
            assert user.joined_at  # Member instance

            embed.add_field(
                name="Server Join Date", value=format_dt(user.joined_at, style="D")
            )
            embed.add_field(name="Top Role", value=user.top_role.mention)
            roles_count = len(user.roles[1:])  # Exclude @everyone
            embed.add_field(name="Roles", value=roles_count)

        avatar = get_user_avatar(user)
        embed.set_thumbnail(url=avatar.url)

        await itx.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.guild_only()
    async def role(self, itx: Interaction, role: Role):
        """See info about a role"""

        if role.is_default():
            description = "Default role"
        elif role.is_bot_managed():
            description = "Managed by a bot"
        elif role.is_premium_subscriber():
            description = "Nitro booster role"
        else:
            description = ""

        embed = Embed(title=role, description=description)
        embed.set_footer(text=f"ID: {role.id}")

        embed.add_field(
            name="Creation Date", value=format_dt(role.created_at, style="D")
        )
        embed.add_field(name="Members", value=len(role.members))
        embed.add_field(name="Mentionable", value=format_bool(role.mentionable))
        embed.add_field(name="Position", value=role.position)

        color_value = f"Hex: {role.color}\nRGB: {role.color.to_rgb()}"
        embed.add_field(name="Color", value=color_value)

        if icon := role.icon:
            embed.set_thumbnail(url=icon.url)

        if color := role.color:
            embed.color = color  # type: ignore

        await itx.response.send_message(embed=embed)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Utility(bot))
