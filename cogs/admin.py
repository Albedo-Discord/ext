import time
import aiohttp
import discord
import importlib
import os
import sys
import requests
import asyncio
from io import BytesIO

from discord.ext import commands
from my_utils import permissions, default, dataIO
from my_utils.guildstate import state_instance


class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self._last_result = None

    @commands.command()
    @commands.check(permissions.is_owner)
    async def load(self, ctx, name: str):
        """ Loads an extension. """
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Loaded extension **{name}.py**")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def unload(self, ctx, name: str):
        """ Unloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Unloaded extension **{name}.py**")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def reload(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.reload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Reloaded extension **{name}.py**")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def reloadall(self, ctx):
        """ Reloads all extensions. """
        error_collection = []
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                try:
                    self.bot.reload_extension(f"cogs.{name}")
                except Exception as e:
                    error_collection.append(
                        [file, default.traceback_maker(e, advance=False)]
                    )

        if error_collection:
            output = "\n".join([f"**{g[0]}** ```diff\n- {g[1]}```" for g in error_collection])
            return await ctx.send(
                f"Attempted to reload all extensions, was able to reload, "
                f"however the following failed: \n\n{output}"
            )

        await ctx.send("Successfully reloaded all extensions")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def reloadutils(self, ctx, name: str):
        """ Reloads a utils module. """
        name_maker = f"utils_folder/{name}.py"
        try:
            module_name = importlib.import_module(f"utils_folder.{name}")
            importlib.reload(module_name)
        except ModuleNotFoundError:
            return await ctx.send(f"Couldn't find module named **{name_maker}**")
        except Exception as e:
            error = default.traceback_maker(e)
            return await ctx.send(f"Module **{name_maker}** returned error and was not reloaded...\n{error}")
        await ctx.send(f"Reloaded module **{name_maker}**")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def reboot(self, ctx):
        """ Reboot the bot """
        await ctx.send('Rebooting now...')
        time.sleep(1)
        dataIO.backup_states(state_instance)
        await self.bot.close()
        sys.exit()

    @commands.command()
    @commands.check(permissions.is_owner)
    async def dm(self, ctx, user_id: int, *, message: str):
        """ DM the user of your choice """
        user = self.bot.get_user(user_id)
        if not user:
            return await ctx.send(f"Could not find any UserID matching **{user_id}**")

        try:
            await user.send(message)
            await ctx.send(f"✉️ Sent a DM to **{user_id}**")
        except discord.Forbidden:
            await ctx.send("This user might be having DMs blocked or it's a bot account...")

    @commands.group()
    @commands.check(permissions.is_owner)
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @change.command(name="playing")
    @commands.check(permissions.is_owner)
    async def change_playing(self, ctx, *, playing: str):
        """ Change playing status. """
        if self.config.status_type == "idle":
            status_type = discord.Status.idle
        elif self.config.status_type == "dnd":
            status_type = discord.Status.dnd
        else:
            status_type = discord.Status.online

        if self.config.playing_type == "listening":
            playing_type = 2
        elif self.config.playing_type == "watching":
            playing_type = 3
        else:
            playing_type = 0

        try:
            await self.bot.change_presence(
                activity=discord.Activity(type=playing_type, name=playing),
                status=status_type
            )
            dataIO.change_value("config.json", "playing", playing)
            await ctx.send(f"Successfully changed playing status to **{playing}**")
        except discord.InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(e)

    @change.command(name="username")
    @commands.check(permissions.is_owner)
    async def change_username(self, ctx, *, name: str):
        """ Change username. """
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await ctx.send(err)

    @change.command(name="nickname")
    @commands.check(permissions.is_owner)
    async def change_nickname(self, ctx, *, name: str = None):
        """ Change nickname. """
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"Successfully changed nickname to **{name}**")
            else:
                await ctx.send("Successfully removed nickname")
        except Exception as err:
            await ctx.send(err)

    @change.command(name="avatar")
    @commands.check(permissions.is_owner)
    async def change_avatar(self, ctx, url: str = None):
        """ Change avatar. """
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip('<>') if url else None

        try:
            bio = requests.get(url).content
            await self.bot.user.edit(avatar=bio)
            await ctx.send(f"Successfully changed the avatar. Currently using:\n{url}")
        except aiohttp.InvalidURL:
            await ctx.send("The URL is invalid...")
        except discord.InvalidArgument:
            await ctx.send("This URL does not contain a useable image")
        except discord.HTTPException as err:
            await ctx.send(err)
        except TypeError:
            await ctx.send("You need to either provide an image URL or upload one with the command")

    @change.command(name="def_prefix")
    @commands.check(permissions.is_owner)
    async def change_default_prefix(self, ctx, prefix):
        """Changes the default premanent prefix"""
        dataIO.change_value("config.json", "prefix", prefix)
        await ctx.send(f"Successfully changed default prefix to **{prefix}**")

    @commands.command(aliases = ["api_for", "api"])
    @commands.check(permissions.is_owner)
    async def search_api(self, ctx, category = ""):
        """ Search for some apis """
        if category != "":
            your_api = requests.get(f"https://api.publicapis.org/entries?category={category.lower()}&https=true").json()
        elif category.lower() == "categories":
            your_api = requests.get(f"https://api.publicapis.org/categories").json()
        else:
            your_api = requests.get("https://api.publicapis.org/random?auth=null").json()
        if your_api['count'] == 0:
            return await ctx.send("No APIs found")
        apis = f"{your_api['entries'][0]['Category']} apis\n"
        def auth(index):
            if your_api['entries'][i]['Auth'] != None:
                return your_api['entries'][i]['Auth']
            return "None"

        for i in range(your_api["count"]):
            apis += f"**{i+1}**. {your_api['entries'][i]['API']} - {your_api['entries'][i]['Description']} | Auth: {auth(i)} | Cors: {your_api['entries'][i]['Cors']} | Link: {your_api['entries'][i]['Link']}\n"
        if len(str(apis)) > 1999:
            apis = apis[:2000][::-1]
            arr = apis.index(".")
            apis = apis[arr:][::-1]

        return await ctx.send(apis)

    @commands.group(aliases = ["file"])
    @commands.check(permissions.is_owner)
    async def fil(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @fil.group()
    @commands.check(permissions.is_owner)
    async def add(self, ctx, location = ""):
        if len(ctx.message.attachments) == 1 and location != "":
            try:
                await ctx.message.attachments[0].save(f"{location}\{ctx.message.attachments[0].filename}")
            except FileNotFoundError:
                await ctx.send("Directory not found. Creating directory...")
                os.makedirs(location)
                await ctx.message.attachments[0].save(f"{location}\{ctx.message.attachments[0].filename}")
        elif len(ctx.message.attachments) == 1 and location == "":
            await ctx.message.attachments[0].save(f"{ctx.message.attachments[0].filename}")
        else:
            return await ctx.send("Provide a file as an attachment")
        await ctx.message.delete(delay=1)
        return await ctx.send(f"The {ctx.message.attachments[0].filename} has been added")
    
    @fil.group()
    @commands.check(permissions.is_owner)
    async def remove(self, ctx, file_name_with_path):
        await ctx.send("Are you sure you want to remove the file. Please remember to unload if the file is and existing cog.\n(y/n)")
        def mcheck(message):
            if message.author == ctx.author:
                return True
            return False
        try:    
            answer = await self.bot.wait_for('message', timeout=20, check=mcheck)
        except asyncio.TimeoutError:
            return await ctx.send("You didn't respond in time")
        if answer.content == "y":
            pass
        else:
            return await ctx.send("As you wish, the file will not be removed")
        try:    
            default.delete(file_name_with_path)
            await ctx.send(f"Removed {file_name_with_path}")
        except Exception as e:
            await ctx.send(e)
        await ctx.message.delete(delay=1)

def setup(bot):
    bot.add_cog(admin(bot))