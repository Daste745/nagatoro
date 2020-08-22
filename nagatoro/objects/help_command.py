from discord import Color
from discord.ext.commands import MinimalHelpCommand as BaseHelpCommand
from nagatoro.objects import Embed


class HelpCommand(BaseHelpCommand):
    def __init__(self):
        super(HelpCommand, self).__init__()

    def get_opening_note(self, description: str = None) -> str:
        prefix = self.clean_prefix
        help_name = self.invoked_with

        return (
            f"Use `{prefix}{help_name} [command]` for info about a command.\n"
            f"Use `{prefix}{help_name} [category]` for info about a category."
            f"\n\n{description if description else ''}"
        )

    def get_help_embed(self, title: str, description: str = None) -> Embed:
        return Embed(
            self.context,
            title=title,
            description=self.get_opening_note(description),
            color=Color.blue(),
        )

    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = self.get_help_embed("Commands")

        for cog, commands in mapping.items():
            if not cog:
                # Don't show commands without a cog (e.g. the help command)
                continue

            category_name = cog.qualified_name
            filtered_commands = await self.filter_commands(commands)

            embed.add_field(
                name=category_name,
                value=", ".join(i.name for i in filtered_commands),
                inline=False,
            )

        await ctx.send(embed=embed)

    async def send_cog_help(self, cog):
        ctx = self.context
        embed = self.get_help_embed(f"{cog.qualified_name} Commands", cog.description)

        commands = []
        for command in cog.get_commands():
            commands.append(
                f"**{self.clean_prefix}{command.qualified_name}** - "
                f"{command.short_doc}"
            )

        embed.add_field(name="Commands", value="\n".join(commands))

        await ctx.send(embed=embed)

    async def send_group_help(self, group):
        ...

    async def send_command_help(self, command):
        ...
