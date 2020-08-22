from discord import Color
from discord.ext.commands import HelpCommand as BaseHelpCommand
from nagatoro.objects import Embed


class HelpCommand(BaseHelpCommand):
    def __init__(self):
        super(HelpCommand, self).__init__(verify_checks=False)

    def get_opening_note(self):
        prefix = self.clean_prefix
        command_name = self.invoked_with

        return (
            f"Use `{prefix}{command_name} [command]` for info about a command.\n"
            f"Use `{prefix}{command_name} [category]` for info about a category."
        )

    def get_command_signature(self, command):
        if command.aliases:
            aliases = "|".join(i for i in command.aliases)
            name = f"[{command.name}|{aliases}]"
        else:
            name = command.name

        if command.full_parent_name:
            name = f"{command.full_parent_name} {name}"

        return f"{self.clean_prefix}{name}" + (
            f" {command.signature}" if command.signature else ""
        )

    def get_formatted_commands(self, commands):
        return (
            f"`{self.clean_prefix}{i.qualified_name}` - {i.short_doc}" for i in commands
        )

    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = Embed(
            ctx,
            title="Commands",
            description=self.get_opening_note(),
            color=Color.blue(),
        )

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
        embed = Embed(
            ctx,
            title=f"{cog.qualified_name} Commands",
            description=cog.description,
            color=Color.blue(),
        )

        commands = self.get_formatted_commands(
            await self.filter_commands(cog.get_commands())
        )
        embed.add_field(name="Commands", value="\n".join(commands))

        await ctx.send(embed=embed)

    async def send_group_help(self, group):
        ctx = self.context
        embed = Embed(
            ctx,
            title=f"`{self.get_command_signature(group)}`",
            description=group.help,
            color=Color.blue(),
        )

        commands = self.get_formatted_commands(
            await self.filter_commands(group.commands)
        )
        embed.add_field(name="Commands", value="\n".join(commands))

        await ctx.send(embed=embed)

    async def send_command_help(self, command):
        ctx = self.context
        embed = Embed(
            ctx,
            title=f"`{self.get_command_signature(command)}`",
            description=command.help,
            color=Color.blue(),
        )

        await ctx.send(embed=embed)
