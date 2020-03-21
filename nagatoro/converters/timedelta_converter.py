import re
from datetime import timedelta
from discord.ext.commands import Converter, Context, BadArgument

timedelta_regex = r"^(((?P<weeks>\d+)w)|((?P<days>\d+)d)|((?P<hours>\d+)h)" \
                  r"|((?P<minutes>\d+)m)|((?P<seconds>\d+)s))+$"


class Timedelta(Converter):
    async def convert(self, ctx: Context, argument: str) -> timedelta:
        match = re.match(timedelta_regex, argument)
        if not match:
            raise BadArgument("Given time is wrong.")

        return timedelta(
            int(match.group("days") or 0),
            int(match.group("seconds") or 0),
            0,
            0,
            int(match.group("minutes") or 0),
            int(match.group("hours") or 0),
            int(match.group("weeks") or 0)
        )
