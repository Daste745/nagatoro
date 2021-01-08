import os
import logging

import yaml
from redis import Redis
from discord.ext.commands import Context


LOCALE_PATH = "locale/"

log = logging.getLogger(__name__)


def load_locale(path: str, cache: Redis) -> None:
    with open(path) as f:
        data = yaml.safe_load(f)

    locale: str = data["locale"]
    cached_strings: int = 0

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


def translate(ctx: Context, key: str, item: str, **kwargs) -> str:
    locale = (
        ctx.bot.cache.get(f"{ctx.guild.id}:locale")
        if ctx.bot.cache.exists(f"{ctx.guild.id}:locale")
        else ctx.bot.config.locale
    ).decode()

    if ctx.bot.locale_cache.hexists(f"{locale}:{key}", item):
        string = ctx.bot.locale_cache.hget(f"{locale}:{key}", item).decode()
        if not kwargs:
            return string
        return string.format(**kwargs)
    else:
        return f"{locale}:{key}:{item}"


def translate_command(ctx: Context, key: str, **kwargs) -> str:
    return translate(
        ctx,
        f"commands:{ctx.cog.qualified_name.lower()}:{ctx.command.name}",
        key,
        **kwargs,
    )
