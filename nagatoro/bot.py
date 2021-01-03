import os
import logging
from time import time
from itertools import groupby

from discord import Color, Intents
from discord.ext import commands
from discord.ext.commands import Context, errors as cerrors

from nagatoro.utils import get_prefixes
from nagatoro.objects import Config, Embed, HelpCommand
from nagatoro.checks.is_moderator import NotModerator
from nagatoro.db import init_redis, Guild, Moderator


log = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self, config: Config, **kwargs):
        super().__init__(
            command_prefix=get_prefixes,
            help_command=HelpCommand(),
            # heartbeat_timeout=30,  # Leaving this untouched, experimentally
            case_insensitive=True,
            intents=Intents(
                guilds=True,
                messages=True,
                members=True,
                reactions=True,
            ),
            **kwargs,
        )
        self.config = config
        self.start_timestamp = time()

        # Redis cache
        self.cache = init_redis(self.config, db=0)

    def load_cogs(self):
        path = "nagatoro/cogs/"
        extensions = [
            path.replace("/", ".") + file.replace(".py", "")
            for file in os.listdir(path)
            if os.path.isfile(f"{path}{file}")
        ]

        for extension in extensions:
            try:
                self.load_extension(extension)
            except cerrors.ExtensionAlreadyLoaded:
                pass

        log.info(f"Loaded {len(self.cogs)} cogs: {', '.join(self.cogs)}")

    def reload_cogs(self):
        for extension in list(self.extensions):
            try:
                self.reload_extension(extension)
            except cerrors.ExtensionAlreadyLoaded:
                pass

        log.info(f"Reloaded {len(self.extensions)} cogs")

    async def generate_prefix_cache(self) -> int:
        cached_prefixes: int = 0

        async for guild in Guild.all():
            if not guild.prefix:
                self.cache.delete(f"{guild.id}:prefix")
            else:
                self.cache.set(f"{guild.id}:prefix", guild.prefix)
                cached_prefixes += 1

        log.info(f"Cached {cached_prefixes} prefix(es).")
        return cached_prefixes

    async def generate_moderator_cache(self) -> int:
        cached_moderators: int = 0

        # TODO: Come up with a better solution to removing orphan moderators.
        for guild in self.guilds:
            self.cache.delete(f"{guild.id}:moderators")

        all_moderators = await Moderator.all().prefetch_related("guild", "user")
        for guild_id, moderators in groupby(
            # Sort before grouping so every guild has exactly one list of mods
            sorted(all_moderators, key=lambda x: x.guild.id),
            key=lambda x: x.guild.id,
        ):
            moderator_ids = [i.user.id for i in moderators]
            self.cache.sadd(
                f"{guild_id}:moderators",
                *moderator_ids,
            )
            cached_moderators += len(moderator_ids)

        log.info(f"Cached {cached_moderators} moderator(s).")
        return cached_moderators

    async def on_ready(self):
        log.info(f"Bot ready as {self.user} with prefix {self.config.prefix}")

    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        permissions = message.channel.permissions_for(message.guild.me)
        if not permissions.send_messages:
            # Every command retuns with a message, so ignore channels
            # where the bot can't send messages.
            return

        await self.process_commands(message)

    async def on_command_error(self, ctx: Context, exception: Exception):
        title = "Error"

        try:
            raise exception
        except cerrors.CommandNotFound:
            return
        except (
            cerrors.MissingRequiredArgument,
            cerrors.TooManyArguments,
        ):
            # Send the help message
            return await ctx.send_help(ctx.command)
        except (cerrors.BadArgument, cerrors.BadUnionArgument):
            title = "Bad argument(s)"
        except (cerrors.NotOwner, cerrors.MissingPermissions, NotModerator):
            title = "Insufficient permissions"
        except cerrors.BotMissingPermissions:
            title = "Missing bot permissions"
        except cerrors.MissingRole:
            title = "Missing role"
        except cerrors.NSFWChannelRequired:
            title = "Channel is not NSFW"
        except cerrors.CommandOnCooldown:
            title = "Cooldown"
        except Exception:
            log.exception(exception)

        embed = Embed(
            ctx,
            title=title,
            description=str(exception),
            color=Color.red(),
        )

        await ctx.send(embed=embed)
