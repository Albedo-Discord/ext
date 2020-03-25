import discord

from my_utils import permissions, default as d
from discord.ext.commands import AutoShardedBot, DefaultHelpCommand
import os

Hidden_cogs = ["memberlog", "events"]

class Bot(AutoShardedBot):
    def __init__(self, *args, prefix=None, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_message(self, msg: discord.Message):
        if not self.is_ready() or msg.author.bot or not permissions.can_send(msg):
            return
        
        await self.process_commands(msg)


class HelpCommand(DefaultHelpCommand):
    
    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = discord.Embed(title = "ALBEDO COMMAND LIST", 
        description = "Albedo has a huge variety of commands. You can use the help command to navigate through them. ",
        color = discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)
        
        for cog in mapping.keys():
            if cog != None:    
                if len(cog.get_commands()) != 0:
                    if not permissions.is_owner(ctx):
                        if cog.qualified_name == "admin":
                            continue
                    embed.add_field(name = "**{}**".format(cog.qualified_name.upper()), value = f"`{self.clean_prefix}help {cog.qualified_name}`\n", inline= False)

        await ctx.send(embed = embed)

    async def send_command_help(self, command):
        ctx = self.context

        embed = discord.Embed(
            description=command.help if command.help else "Gonna write dis shit later boya",
            color=discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)

        signature = self.get_command_signature(command)
        embed.set_author(name=f"{signature}")

        await ctx.send(embed = embed)

    async def send_group_help(self, group):
        ctx = self.context
        signature = self.get_command_signature(group)

        embed = discord.Embed(
            description = group.help if group.help else "", 
            color = discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)
        embed.set_author(name=signature)
        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        for command in filtered:
            halp = command.brief if command.brief else command.help
            embed.add_field(name = f"**{command.name}**", value = "_{}_".format(halp if halp else "Crap, forgot to write this shit"), inline=False)

        await ctx.send(embed = embed)

    async def send_cog_help(self, cog):
        ctx = self.context
        if len(cog.get_commands()) == 0:
            return await ctx.send(f'No command "{cog.qualified_name}" found.')
        
        embed = discord.Embed(
            title = cog.qualified_name.upper(),
            description = cog.description if cog.description else "", 
            color = discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)

        filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
        
        for command in filtered:
            halp = command.brief if command.brief else command.help
            embed.add_field(name = f"**{command.name}**", value = "_{}_".format(halp if halp else "Crap, forgot to write this shit"), inline=False)

        return await ctx.send(embed = embed)

class HelpFormat(DefaultHelpCommand):
    def get_destination(self, no_pm: bool = False):
        if no_pm:
            return self.context.channel
        else:
            return self.context.author

    async def send_error_message(self, error):
        destination = self.get_destination(no_pm=True)
        await destination.send(error)

    async def send_command_help(self, command):
        self.add_command_formatting(command)
        self.paginator.close_page()
        await self.send_pages(no_pm=True)

    async def send_pages(self, no_pm: bool = False):
        try:
            if permissions.can_react(self.context):
                await self.context.message.add_reaction(chr(0x2709))
        except discord.Forbidden:
            pass

        try:
            destination = self.get_destination(no_pm=no_pm)
            for page in self.paginator.pages:
                await destination.send(page)
        except discord.Forbidden:
            destination = self.get_destination(no_pm=True)
            await destination.send("Couldn't send help to you due to blocked DMs...")

