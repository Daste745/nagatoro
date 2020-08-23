import os
import logging
from time import time

from discord import Color
from discord.ext import commands
from discord.ext.commands import Context, errors as cerrors

from nagatoro.utils import get_prefixes
from nagatoro.objects import Config, Embed, HelpCommand


class Bot(commands.Bot):
    def __init__(self, config: Config, **kwargs):
        super().__init__(
            command_prefix=get_prefixes,
            help_command=HelpCommand(),
            # heartbeat_timeout=30,  # Leaving this untouched, experimentally
            case_insensitive=True,
            **kwargs,
        )
        self.config = config
        self.start_timestamp = time()

    def load_cogs(self) -> None:
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

    def reload_cogs(self) -> None:
        for extension in list(self.extensions):
            try:
                self.reload_extension(extension)
            except cerrors.ExtensionAlreadyLoaded:
                pass

    async def on_ready(self):
        logging.info(f"Bot started as {self.user}.")
        logging.info(f"Loaded cogs: {', '.join(self.cogs)}")
        logging.info(
            f"Loaded commands: {', '.join([i.name for i in self.commands])}")

    async def on_command_error(self, ctx: Context, exception: Exception):
        title = "Error"

        try:
            raise exception
        except cerrors.CommandNotFound:
            return
        except (cerrors.MissingRequiredArgument, cerrors.TooManyArguments,
                cerrors.BadArgument, cerrors.BadUnionArgument):
            # Send the help message
            return await ctx.send_help(ctx.invoked_with)
        except (cerrors.NotOwner, cerrors.MissingPermissions):
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
            logging.error(f"{type(exception)}, {exception}")

        embed = Embed(
            ctx,
            title=title,
            description=str(exception),
            color=Color.red())

        await ctx.send(embed=embed)
