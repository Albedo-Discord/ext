import logging
import os
import traceback
from datetime import datetime

import discord
import psutil
from discord.ext import commands
from discord.ext.commands import errors

from my_utils import default
from my_utils.guildstate import state_instance
from my_utils.permissions import has_permissions


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if hasattr(ctx.command, "on_error"):
            return  # Don't interfere with custom error handlers
        
        gstate = state_instance.get_state(ctx.guild.id)
        
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await ctx.send_help(helper)

        elif isinstance(err, errors.CommandInvokeError):
            error = default.traceback_maker(err.original)

            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send(
                    f"You attempted to make the command display more than 2,000 characters...\n"
                    f"Both error and command will be ignored."
                )

            await ctx.send(f"There was an error processing the command ;-;\n{error}")
            logging.error("Ignoring exception in command {}:".format(ctx.command))
            logging.error("\n" + "".join(traceback.format_exception(type(error), err, err.__traceback__)))

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.CommandOnCooldown):
            embed = discord.Embed(title="Cooldown", color=discord.Colour.from_rgb(0,250,141), 
            description="**This command is on cooldown... try again in {}**".format(default.format_seconds(err.retry_after)), 
            timestamp=ctx.message.created_at)

            await ctx.send(embed=embed)

        if isinstance(err, commands.CommandNotFound):
            if not gstate.debugmode:
                return
            await ctx.send(f'>>> No command "{ctx.invoked_with}" found.', delete_after = 5)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        
        state_instance.get_state(guild.id)

        if not self.config.join_message:
            return

        try:
            to_send = sorted([chan for chan in guild.channels if chan.permissions_for(guild.me).send_messages and isinstance(chan, discord.TextChannel)], key=lambda x: x.position)[0]
        except IndexError:
            pass
        else:
            await to_send.send(self.config.join_message)
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        state_instance.delete_state(guild.id)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        try:
            logging.info(f"{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content}")
        except AttributeError:
            logging.info(f"Private message > {ctx.author} > {ctx.message.clean_content}")

    @commands.Cog.listener()
    async def on_ready(self):
        """ The function that actiavtes when boot was completed """
        if not hasattr(self.bot, 'uptime'):
            self.bot.uptime = datetime.utcnow()

        # Check if user desires to have something other than online
        if self.config.status_type == "idle":
            status_type = discord.Status.idle
        elif self.config.status_type == "dnd":
            status_type = discord.Status.dnd
        else:
            status_type = discord.Status.online

        # Check if user desires to have a different type of playing status
        if self.config.playing_type == "listening":
            playing_type = 2
        elif self.config.playing_type == "watching":
            playing_type = 3
        else:
            playing_type = 0

        await self.bot.change_presence(
            activity=discord.Activity(type=playing_type, name=self.config.playing),
            status=status_type
        )
        print("ready")
        logging.info(f"Logged in as {self.bot.user.name}")
        print(f'{self.bot.user} is in service| Servers: {len(self.bot.guilds)}')


def setup(bot):
    bot.add_cog(events(bot))
