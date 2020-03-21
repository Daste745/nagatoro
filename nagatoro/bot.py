import logging
from time import time
from discord import Color
from discord.ext import commands
from discord.ext.commands import Context, errors as cerrors

from nagatoro.cogs.management import Management
from nagatoro.utils import get_prefixes
from nagatoro.objects import Embed


class Bot(commands.Bot):
    def __init__(self, config, **kwargs):
        super().__init__(command_prefix=get_prefixes, **kwargs)
        self.case_insensitive = True
        self.config = config
        self.start_timestamp = time()
        # TODO: Make custom help command.
        # self.remove_command("help")

    def startup(self):
        Management.load_cogs(bot=self)
        self.run(self.config.token)

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
        except cerrors.MissingRequiredArgument:
            title = "Missing required arguments"
        except cerrors.TooManyArguments:
            title = "Too many arguments"
        except (cerrors.BadArgument, cerrors.BadUnionArgument):
            title = "Bad argument"
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
        except cerrors.CommandError:
            title = "Command Error"
        except Exception:
            logging.error(f"{type(exception)}, {exception}")

        embed = Embed(
            ctx,
            title=title,
            description=str(exception),
            color=Color.red())

        await ctx.send(embed=embed)
