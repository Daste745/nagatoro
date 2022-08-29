from typing import Literal

from discord import Embed, Interaction, Member, User, app_commands
from discord.utils import format_dt

from nagatoro.common import Bot, Cog


class Utility(Cog):
    AssetSizeChoices = Literal[16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
    AssetFormatChoices = Literal["webp", "jpeg", "jpg", "png", "gif"]

    @app_commands.command()
    @app_commands.describe(size="Image size (default: 1024)")
    @app_commands.describe(format="Image format (default: png)")
    async def avatar(
        self,
        itx: Interaction,
        user: User | Member,
        size: AssetSizeChoices | None = None,
        format: AssetFormatChoices | None = None,
    ):
        """Get someone's avatar"""
        # TODO: Guild vs global avatar

        if not user.avatar:
            return await itx.response.send_message(f"{user} doesn't have an avatar")

        if not size:
            size = 1024

        if not format:
            format = "png"

        if format == "gif" and not user.avatar.is_animated():
            return await itx.response.send_message(
                f"{user} doesn't have an animated avatar, please use a different format"
            )

        avatar_url = user.avatar.with_size(size).with_format(format).url  # type: ignore
        embed = Embed(description=f"{user}'s avatar")
        embed.set_image(url=avatar_url)

        await itx.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.describe(size="Image size (default: 1024)")
    @app_commands.describe(format="Image format (default: png)")
    async def banner(
        self,
        itx: Interaction,
        user: User | Member,
        size: AssetSizeChoices | None = None,
        format: AssetFormatChoices | None = None,
    ):
        """Get someone's banner"""
        # TODO: Guild vs global banner

        # Re-fetch the user in order to see their profile banner
        user = await self.bot.fetch_user(user.id)

        if not user.banner:
            return await itx.response.send_message(f"{user} doesn't have a banner")

        if not size:
            size = 1024

        if not format:
            format = "png"

        if format == "gif" and not user.banner.is_animated():
            return await itx.response.send_message(
                f"{user} doesn't have an animated banner, please use a different format"
            )

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

        await itx.response.send_message(embed=embed)

    @app_commands.command()
    async def user(self, itx: Interaction, user: User | Member):
        """See info about a user"""

        if user.system:
            title = f"{user} [SYSTEM]"
        elif user.bot:
            title = f"{user} [BOT]"
        else:
            title = str(user)

        embed = Embed(title=title)

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

        if avatar := user.avatar:
            embed.set_thumbnail(url=avatar.url)

        await itx.response.send_message(embed=embed)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Utility(bot))
