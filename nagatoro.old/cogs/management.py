from discord import Color
from discord.ext.commands import (
    Cog,
    Context,
    command,
    group,
    is_owner,
    has_guild_permissions,
    cooldown,
    BucketType,
)

from nagatoro.objects import Embed
from nagatoro.checks import is_moderator
from nagatoro.db import Guild
from nagatoro.utils import available_locales, t


class Management(Cog, command_attrs=dict(ignore_extra=True)):
    """Bot settings and info"""

    def __init__(self, bot):
        self.bot = bot

    @command(name="reload", aliases=["r"], hidden=True)
    @is_owner()
    async def reload(self, ctx: Context):
        """Reload all cogs and commands"""

        ctx.bot.reload_cogs()
        await ctx.send(
            t(
                ctx,
                "message",
                commands=len(ctx.bot.commands),
                modules=len(ctx.bot.cogs),
            )
        )

    @command(name="cache", hidden=True)
    @is_owner()
    async def cache(self, ctx: Context):
        """Rebuild all caches"""

        cached_prefixes = await self.bot.generate_prefix_cache()
        cached_moderators = await self.bot.generate_moderator_cache()
        cached_locales = await self.bot.generate_locale_cache()

        await ctx.send(
            t(
                ctx,
                "description",
                prefixes=cached_prefixes,
                moderators=cached_moderators,
                locales=cached_locales,
            )
        )

    @group(name="language", aliases=["lang", "locale"], invoke_without_command=True)
    @cooldown(rate=2, per=10, type=BucketType.user)
    async def language(self, ctx: Context):
        """Bot language"""

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)

        if not guild.locale:
            return await ctx.send(t(ctx, "not_set", guild=ctx.guild.name))

        return await ctx.send(
            t(ctx, "message", guild=ctx.guild.name, locale=guild.locale)
        )

    @language.command(name="available")
    @cooldown(rate=2, per=10, type=BucketType.user)
    async def language_available(self, ctx: Context):
        """Available languages"""

        await ctx.send(t(ctx, "message", locales=", ".join(available_locales())))

    @language.command(name="set")
    @is_moderator()
    @cooldown(rate=2, per=30, type=BucketType.guild)
    async def language_set(self, ctx: Context, language: str):
        """Set Nagatoro's language on this server"""

        if language not in available_locales():
            return await ctx.send(t(ctx, "not_available", language=language))

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        guild.locale = language
        await guild.save()
        await self.bot.generate_locale_cache()

        await ctx.send(t(ctx, "message", language=language))

    @group(name="prefix", invoke_without_command=True)
    @cooldown(rate=2, per=10, type=BucketType.user)
    async def prefix(self, ctx: Context):
        """Custom bot prefix"""

        embed = Embed(
            ctx,
            title=t(ctx, "title", guild=ctx.guild.name),
            description="",
            color=Color.blue(),
        )

        for i in (await ctx.bot.command_prefix(ctx.bot, ctx.message))[1:]:
            embed.description += f"- **{i}**\n"

        return await ctx.send(embed=embed)

    @prefix.command(name="set")
    @is_moderator()
    @cooldown(rate=2, per=30, type=BucketType.guild)
    async def prefix_set(self, ctx: Context, prefix: str):
        """Set a custom prefix for this server"""

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        guild.prefix = prefix
        await guild.save()
        await self.bot.generate_prefix_cache()

        await ctx.send(t(ctx, "message", prefix=prefix))

    @prefix.command(name="delete", aliases=["unset", "remove", "del"])
    @is_moderator()
    @cooldown(rate=2, per=30, type=BucketType.guild)
    async def prefix_delete(self, ctx: Context):
        """Delete the prefix from this server"""

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        if not guild.prefix:
            return await ctx.send(t(ctx, "not_set", guild=ctx.guild.name))

        guild.prefix = None
        await guild.save()
        await self.bot.generate_prefix_cache()

        await ctx.send(t(ctx, "message", name=ctx.guild.name))

    @command(name="level-up-messages", usage="[disable|enable]")
    @has_guild_permissions(manage_channels=True)
    @cooldown(rate=5, per=10, type=BucketType.user)
    async def level_up_messages(self, ctx: Context, action: str):
        """Toggle level up messages on this server

        Level up messages are not sent until you reach level 6.
        """

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)

        if action == "disable":
            if not guild.level_up_messages:
                return await ctx.send(t(ctx, "already_disabled", guild=ctx.guild))

            guild.level_up_messages = False
            await ctx.send(t(ctx, "disabled", guild=ctx.guild))

        elif action == "enable":
            if guild.level_up_messages:
                return await ctx.send(t(ctx, "already_enabled", guild=ctx.guild))

            guild.level_up_messages = True
            await ctx.send(t(ctx, "enabled", guild=ctx.guild))

        await guild.save()


def setup(bot):
    bot.add_cog(Management(bot))
