import os
import logging
from typing import Optional, Union

import yaml
from redis import Redis
from discord.ext.commands import Context, Command, Cog, Group


LOCALE_PATH = "locale/"

log = logging.getLogger(__name__)


def load_locale(path: str, cache: Redis) -> None:
    with open(path) as f:
        data = yaml.safe_load(f)

    locale: str = data["locale"]
    cached_strings: int = 0

    # Global keys
    cache.hmset(f"{locale}:global", data["global"])

    # Command translations
    for category, commands in data["commands"].items():
        for command, keys in commands.items():
            if command == "description":
                cache.set(f"{locale}:commands:{category}:description", keys)
                continue

            cache.hmset(f"{locale}:commands:{category}:{command}", keys)
            cached_strings += len(keys)

    log.info(f"Loaded {cached_strings} strings from locale {locale}.")


def load_locales(cache: Redis) -> None:
    for file in os.listdir(LOCALE_PATH):
        load_locale(f"{LOCALE_PATH}{file}", cache)


def available_locales() -> list[str]:
    files = os.listdir(LOCALE_PATH)
    return [os.path.splitext(file)[0] for file in files]


def get_locale(ctx: Context) -> str:
    locale = (
        ctx.bot.cache.get(f"{ctx.guild.id}:locale").decode()
        if ctx.bot.cache.exists(f"{ctx.guild.id}:locale")
        else ctx.bot.config.locale
    )
    return locale


def translate(ctx: Context, key: str, item: str, **kwargs) -> str:
    locale = get_locale(ctx)

    if ctx.bot.locale_cache.hexists(f"{locale}:{key}", item):
        string = ctx.bot.locale_cache.hget(f"{locale}:{key}", item).decode()
        if not kwargs:
            return string
        return string.format(**kwargs)
    else:
        return f"{locale}:{key}:{item}"


def get_command_name(command: Command) -> str:
    return command.qualified_name.replace(" ", "_").replace("-", "_")


def translate_command(
    ctx: Context,
    key: str,
    command: Optional[Union[Command, Group]] = None,
    **kwargs,
) -> str:
    command_name = get_command_name(command or ctx.command)
    cog_name = command.cog.qualified_name if command else ctx.cog.qualified_name
    return translate(
        ctx,
        f"commands:{cog_name.lower()}:{command_name}",
        key,
        **kwargs,
    )


def translate_cog_description(ctx: Context, cog: Cog = None, **kwargs) -> str:
    locale = get_locale(ctx)
    key = f"{locale}:commands:{cog.qualified_name.lower()}:description"
    if ctx.bot.locale_cache.exists(key):
        string = ctx.bot.locale_cache.get(key).decode()
        if not kwargs:
            return string
        return string.format(**kwargs)
    else:
        return key


def translate_global(ctx: Context, key: str, **kwargs) -> str:
    return translate(ctx, f"global", key, **kwargs)
