import re
from datetime import timedelta

from discord.ext.commands import Converter, Context, BadArgument


time_regex = (
    r"^(?:(?P<days>\d+)(d|days?))?"
    r"(?:(?P<hours>\d+)(h|hours?))?"
    r"(?:(?P<minutes>\d+)(m|minutes?))?"
    r"(?:(?P<seconds>\d+)(s|seconds?))?$"
)


class Timedelta(Converter):
    async def convert(self, ctx: Context, argument: str) -> timedelta:
        if not (match := re.match(time_regex, argument, flags=re.IGNORECASE)):
            raise BadArgument("Invalid time.")

        date_values = {k: int(v or "0") for k, v in match.groupdict().items()}

        if any(i > 999999999 for i in date_values.values()):
            raise BadArgument(
                "Some time values are too big. Please use smaller values."
            )

        return timedelta(**date_values)
