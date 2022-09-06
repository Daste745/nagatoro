from discord import Color
from discord.ext.commands import HelpCommand as BaseHelpCommand
from nagatoro.objects import Embed
from nagatoro.utils import t, tc


class HelpCommand(BaseHelpCommand):
    def __init__(self):
        super(HelpCommand, self).__init__(verify_checks=False)

    def get_opening_note(self):
        prefix = self.clean_prefix
        command_name = self.invoked_with

        return t(
            self.context,
            "opening_note",
            prefix=prefix,
            command_name=command_name,
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
        def short_doc(command):
            return t(self.context, "description", command).split("\n")[0]

        return (
            f"`{self.clean_prefix}{i.qualified_name}` - {short_doc(i)}"
            for i in commands
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
            title=t(ctx, "cog_commands", cog=cog.qualified_name),
            description=tc(ctx, cog),
            color=Color.blue(),
        )

        commands = self.get_formatted_commands(
            await self.filter_commands(cog.get_commands())
        )
        embed.add_field(name=t(ctx, "commands"), value="\n".join(commands))

        await ctx.send(embed=embed)

    async def send_group_help(self, group):
        ctx = self.context
        embed = Embed(
            ctx,
            title=f"`{self.get_command_signature(group)}`",
            description=t(ctx, "description", group),
            color=Color.blue(),
        )

        commands = self.get_formatted_commands(
            await self.filter_commands(group.commands)
        )
        embed.add_field(name=t(ctx, "commands"), value="\n".join(commands))

        await ctx.send(embed=embed)

    async def send_command_help(self, command):
        ctx = self.context
        embed = Embed(
            ctx,
            title=f"`{self.get_command_signature(command)}`",
            description=t(ctx, "description", command),
            color=Color.blue(),
        )

        await ctx.send(embed=embed)
