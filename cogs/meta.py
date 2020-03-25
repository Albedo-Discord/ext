import os
import typing

import discord
from discord.ext import commands, tasks
from discord.utils import oauth_url

from my_utils import default as d, permissions
from my_utils.guildstate import state_instance
from my_utils.converters import ComCog

config = d.get("config.json")

al_admins = config.almins

class meta(commands.Cog):    
    """Contains the general commands or the commands related to the bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @permissions.has_permissions(perms = "administrator")
    async def prefix(self, ctx, *, prefix = None):
        """Gets the current prefix or changes the prefix"""

        embed = discord.Embed(color = discord.Colour.from_rgb(0, 0, 0), timestamp = ctx.message.created_at)
        state = state_instance.get_state(ctx.guild.id)
        if prefix == None:
                embed.add_field(name="Current Prefix", value=f"Current prefix `{state.bot_prefix}`", inline=False)
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        elif prefix != None:
            if ctx.message.author.id in al_admins:
                state.bot_prefix = prefix
                embed.add_field(name="Prefix", value=f"Prefix changed to `{state.bot_prefix}`", inline=False)
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                print("prefix changed to {} in {}".format(prefix,ctx.guild.id))
            else:
                embed = discord.Embed(title="You thought you could do that, how gae.", timestamp = ctx.message.created_at)
    
        await ctx.send(embed=embed)

    @commands.command()
    async def botinvite(self, ctx):
        """Sends the invite link of the bot"""

        await ctx.send(oauth_url(self.bot.user.id, permissions=discord.Permissions(permissions=8), guild=None, redirect_uri=None))

    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(color = discord.Colour.from_rgb(0,250,141), timestamp=ctx.message.created_at)
        embed.add_field(name="Bot ping",value=f"{round(self.bot.latency*1000)}ms")
        await ctx.send(embed=embed)

    @commands.command()                                                      #Description command
    async def desc(self, ctx, *, random_stuff = None):
        """Description of the bot."""

        await ctx.send(">>> I love Ainz sama")

    @commands.group(invoke_without_command = True, usage="<command> [channel|role]")
    @permissions.has_permissions(perms = "manage_server")
    async def enable(self, ctx, command:ComCog, role_chan: typing.Union[discord.TextChannel, discord.Role, str] = None):
        """Enables a given command"""
        
        command, cmd = command
            
        state = state_instance.get_state(ctx.guild.id)
        comd = state.get_var(str(cmd))
        if isinstance(role_chan, discord.TextChannel):
            chann = comd.channels
            chann.discard(str(role_chan))
            val = state.command(comd.server_wide, chann, comd.roles, False) if str(role_chan) not in state.get_var("all").channels else state.command(comd.server_wide, chann, comd.roles, True)
            await ctx.send(f"Enabled `{command}` in {role_chan.mention}")
        elif isinstance(role_chan, discord.Role):
            rol = comd.roles
            rol.discard(str(role_chan))
            val = state.command(comd.server_wide, comd.channels, rol, False) if str(role_chan) not in state.get_var("all").roles else state.command(comd.server_wide, comd.channels, rol, True)
            await ctx.send(f"Enabled `{command}` for {role_chan.mention}")
        elif role_chan != None:
            raise commands.errors.BadArgument()
        else:
            if command != "all":
                all_cmds=state.get_var("all")
                val = state.command(True, set(), set(), False) if all_cmds.server_wide else state.command(True, set(), set(), True)
            else:
                val = state.command(True, set(), set(), False)
            await ctx.send(f"Enabled `{command}` server-wide")
        state.set_var(str(cmd), val)

    @enable.command(name="list", brief="Commands which are overriding disable rules")
    async def enable_list(self, ctx):
        """Get the commands which are overrirding the disable all rules for channels or roles"""

        state = state_instance.get_state(ctx.guild.id)
        cmds = state.get_commands()
        
        en_cmds = ""
        for cmd in cmds:
            comd = state.get_var(cmd)
            if comd.forced:
                en_cmds += f"\t`{cmd}` forced enabled\n"
        
        if en_cmds == "":
            return await ctx.send("Looks like someone is obedient towards the rules, no commands are overriding any roles(¬‿¬)")

        elist = discord.Embed(
            title = "Forced enabled Commands",
            description = en_cmds, 
            color = discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)

        elist.set_author(name="Note: Overridded rules don't have rules for channels or roles, These are overriding only `all disabled` rule")
        
        elist.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url)

        await ctx.send(embed = elist)

    @enable.command(name="debugmode")
    @commands.check(permissions.is_owner)
    async def enable_debugmode(self, ctx):
        """Enable debugmode"""

        state = state_instance.get_state(ctx.guild.id)
        state.set_var("debugmode", True)

        await ctx.send("Enabled debugmode...")

    @commands.group(invoke_without_command=True, usage="<command> [channel|role]", brief="disables a given command")
    @permissions.has_permissions(perms = "manage_server")
    async def disable(self, ctx, command:ComCog, role_chan: typing.Union[discord.TextChannel, discord.Role, str] = None):
        """You can provide a command to be disabled in a channel, for a particular role or server wide(don't pass anything)"""
        
        command, cmd = command

        state = state_instance.get_state(ctx.guild.id)
        comd = state.get_var(str(cmd))
        if isinstance(role_chan, discord.TextChannel):
            chann = comd.channels
            chann.add(str(role_chan))
            val = state.command(comd.server_wide, chann, comd.roles, False)
            await ctx.send(f"Disabled `{command}` in {role_chan.mention}")
        elif isinstance(role_chan, discord.Role):
            rol = comd.roles
            rol.add(str(role_chan))
            val = state.command(comd.server_wide, comd.channels, rol, False)
            await ctx.send(f"Disabled `{command}` for {role_chan.mention}")
        elif role_chan != None:
            raise commands.errors.BadArgument()
        else:
            val = state.command(False, set(), set(), False)
            if command == "all":    
                self.unforce(state)
            await ctx.send(f"Disabled `{command}` server-wide")
        state.set_var(str(cmd), val)

    def unforce(self, state):
        for command_name in state.get_commands():
            command_obj = state.get_var(command_name)
            if command_obj.forced:
                value = (state.command(command_obj.server_wide, command_obj.channels, command_obj.roles, False))
                state.set_var(str(command_name), value)

    @disable.command(name="debugmode")
    @commands.check(permissions.is_owner)
    async def disable_debugmode(self, ctx):
        """Disable debugmode"""

        state = state_instance.get_state(ctx.guild.id)
        state.set_var("debugmode", True)

        await ctx.send("Disabled debugmode...")
    
    @disable.command(name = "list")
    async def disable_list(self, ctx):
        """List of disabled commands"""

        state = state_instance.get_state(ctx.guild.id)
        cmds = state.get_commands()
        
        dis_cmds = ""
        for cmd in cmds:
            comd = state.get_var(cmd)
            if comd.server_wide == False:
                dis_cmds += f"`{cmd}` disabled server-wide\n"
            if len(comd.channels) > 0:
                dis_cmds += f"`{cmd}` disabled in channels {str(comd.channels).strip('{}')}\n"
            if len(comd.roles) > 0:
                dis_cmds += f"`{cmd}` disabled for roles {str(comd.roles).strip('{}')}\n"
        
        if dis_cmds == "":
            return await ctx.send("Disabled command list is empty, darkness is its only friend now")

        dlist = discord.Embed(
            title = "Disabled Commands",
            description = dis_cmds, 
            color = discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)

        dlist.set_author(name = "Note: Disabling all commands server-wide will override all rules of other commands. Also, disabling for roles checks if the member has that role as the toprole. IQ is required to use these command")
        
        dlist.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url)

        await ctx.send(embed = dlist)

def setup(bot):
    bot.add_cog(meta(bot))
