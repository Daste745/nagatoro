from typing import Literal

from discord import Embed, Interaction, Member, User, app_commands

from nagatoro.common import Bot, Cog


class Utility(Cog):
    @app_commands.command()
    @app_commands.describe(size="Image size (default: 1024)")
    @app_commands.describe(format="Image format (default: png)")
    async def avatar(
        self,
        itx: Interaction,
        user: User | Member,
        size: Literal[16, 32, 64, 128, 256, 512, 1024, 2048, 4096] | None = None,
        format: Literal["webp", "jpeg", "jpg", "png", "gif"] | None = None,
    ):
        """Get someone's avatar"""

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


async def setup(bot: Bot) -> None:
    await bot.add_cog(Utility(bot))
