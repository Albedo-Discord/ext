from discord.ext import commands
import discord
import asyncio
import youtube_dl
import logging
import math
import random
from collections import namedtuple
import requests
from bs4 import BeautifulSoup
from urllib import request
from my_utils.video import Video
from my_utils import permissions
from my_utils.default import format_seconds, to_seconds, safe_send, intcheck

def get_song(query, item):

    url = "https://genius.p.rapidapi.com/search"
    song = namedtuple("song", ["title", "path", "image"])
    querystring = {"q":query}
    
    headers = {
        'x-rapidapi-host': "genius.p.rapidapi.com",
        'x-rapidapi-key': "1adab39b32msh3ace9d305db7522p133436jsn292ad15e4db3"
        }
    
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    lyrics = song((response['response']['hits'][item]['result']['full_title']),
                    str(response['response']['hits'][0]['result']['url']), str(response['response']['hits'][item]['result']['song_art_image_url']))
    return lyrics

async def audio_playing(ctx):
    """Checks that audio is currently playing before continuing."""
    client = ctx.guild.voice_client
    if client and client.channel and client.source:
        return True
    else:
        #await ctx.send("Not currently playing any audio.")
        return False


async def in_voice_channel(ctx):
    """Checks that the command sender is in the same voice channel as the bot."""
    voice = ctx.author.voice
    bot_voice = ctx.guild.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    else:
        #await ctx.send("You need to be in the channel to do that.")
        return False


async def is_audio_requester(ctx):
    """Checks that the command sender is the song requester."""
    music = ctx.bot.get_cog("music")
    state = music.get_state(ctx.guild)
    try:    
        if await permissions.check_permissions(ctx, {"perms": "administrator"}) or state.is_requester(ctx.author):
            return True
        else:
            #await ctx.send("You need to be the song requester to do that.")
            return False
    except:
        return False


class music(commands.Cog):
    """Bot commands to help play music."""

    def __init__(self, bot):
        self.bot = bot
        self.config = {"max_volume" : 250, "vote_skip" : True, "vote_skip_ratio" : 0.5}  # retrieve module name, find config entry
        self.states = {}

    def get_state(self, guild):
        """Gets the state for `guild`, creating it if it does not exist."""
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState()
            return self.states[guild.id]

    @commands.command(aliases=["stop"])
    @commands.guild_only()
    @permissions.has_permissions(perms = "administrator")
    async def leave(self, ctx):
        """Leaves the voice channel, if currently in one."""
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        
        if client and client.channel:
            await self._leave(client, state)
        else:
            await ctx.send("Not in a voice channel")

    async def _leave(self, client, state):
        asyncio.run_coroutine_threadsafe(client.disconnect(),self.bot.loop)
        state.playlist = []
        state.skip_votes = set()
        state.now_playing = None
        state.last_audio = None
        state.loop = False
        state.loop_queue = False
    
    @commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    async def shuffle(self, ctx):
        """Shuffles the queue"""
        state = self.get_state(ctx.guild)
        self._shuffle(state)
        await ctx.send(self._queue_text(state.playlist))

    def _shuffle(self, state):
        """Handles the shuffling of queue"""
        old_queue = state.playlist
        random.shuffle(old_queue)
        state.playlist = old_queue

    @commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    @commands.check(is_audio_requester)
    async def seek(self, ctx: commands.Context, time):
        """Seek the audio to a given time. Example: seek 6:09"""
        
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        time = to_seconds(time)
        if not time:
            return await ctx.send("Invalid input. The input should only contain `:` and numbers. There should be no blank spaces after `:`")
        song = state.now_playing
        if time > song.duration:
            return await ctx.send(f"The song is only {format_seconds(song.duration)} long")
        client.source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(song.stream_url, before_options=f" -ss {time} -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"), volume=state.volume)
        await ctx.send(f"Seeked to {format_seconds(time)}")

    @commands.command(aliases=["resume", "p"])
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    @commands.check(is_audio_requester)
    async def pause(self, ctx):
        """Pauses any currently playing audio."""
        client = ctx.guild.voice_client
        self._pause_audio(client)

    def _pause_audio(self, client):
        if client.is_paused():
            client.resume()
        else:
            client.pause()

    @commands.group(aliases=["repeat"], invoke_without_command = True)
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    async def loop(self, ctx):
        """loops any currently playing audio."""

        reply = self._loop(ctx)
        await ctx.send(reply)
    
    @loop.command(aliases = ["full"])
    async def all(self, ctx):
        """loops the queue"""
        
        state = self.get_state(ctx.guild)

        state.loop = False
        state.loop_queue = True
        await ctx.send("Looping the queue")

    @loop.command()
    async def off(self, ctx):
        """Disable looping of any type"""

        state = self.get_state(ctx.guild)

        state.loop = False
        state.loop_queue = False
        await ctx.send("Looping Disabeld")

    def _loop(self, ctx):
        state = self.get_state(ctx.guild)
        reply = ""
        if state.loop == False:
            state.loop = True
            state.loop_queue = False
            reply = "Looping current song"
        elif state.loop == True or state.loop_queue == True:
            state.loop = False
            state.loop_queue = False
            reply = "Looping disabled"
        
        return reply

    @commands.command(aliases=["vol", "v"])
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    @commands.check(is_audio_requester)
    async def volume(self, ctx, volume: int):
        """Change the volume of currently playing audio (values 0-250)."""
        state = self.get_state(ctx.guild)

        # make sure volume is nonnegative
        if volume < 0:
            volume = 0

        max_vol = self.config["max_volume"]
        if max_vol > -1:  # check if max volume is set
            # clamp volume to [0, max_vol]
            if volume > max_vol:
                volume = max_vol

        client = ctx.guild.voice_client

        state.volume = float(volume) / 100.0
        client.source.volume = state.volume  # update the AudioSource's volume to match

    @commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    async def skip(self, ctx):
        """Skips the currently playing song, or votes to skip it."""
        state = self.get_state(ctx.guild)
        client = ctx.guild.voice_client
        if await permissions.check_permissions(ctx, {"perms": "administrator"}) or state.is_requester(ctx.author):
            # immediately skip if requester or admin
            state.loop = False
            state.loop_queue = False
            client.stop()
        elif self.config["vote_skip"]:
            # vote to skip song
            channel = client.channel
            self._vote_skip(channel, ctx.author)
            # announce vote
            users_in_channel = len([
                member for member in channel.members if not member.bot
            ])  # don't count bots
            required_votes = math.ceil(
                self.config["vote_skip_ratio"] * users_in_channel)
            await ctx.send(
                f"{ctx.author.mention} voted to skip ({len(state.skip_votes)}/{required_votes} votes)"
            )
        else:
            raise commands.CommandError("Sorry, vote skipping is disabled.")

    def _vote_skip(self, channel, member):
        """Register a vote for `member` to skip the song playing."""
        logging.info(f"{member.name} votes to skip")
        state = self.get_state(channel.guild)
        state.skip_votes.add(member)
        users_in_channel = len([member for member in channel.members if not member.bot]) # don't count bots
        
        if (float(len(state.skip_votes))/users_in_channel) >= self.config["vote_skip_ratio"]:  # enough members have voted to skip, so skip the song
            state.loop = False
            state.loop_queue = False
            channel.guild.voice_client.stop()

    def _play_song(self, client, state, song):
        state.now_playing = song
        state.skip_votes = set()  # clear skip votes
            
        source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(song.stream_url, before_options=" -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"), volume=state.volume)

        def after_playing(err):
            try:
                if state.loop == True:
                    self._play_song(client, state, state.now_playing)
                elif state.loop_queue == True and len(state.playlist) > 0:
                    if state.last_audio == state.playlist[0]:
                        state.last_audio = None
                    else:
                        state.last_audio = state.now_playing
                    next_song = state.playlist.pop(0)
                    if state.last_audio:    
                        state.playlist.append(state.now_playing)
                    self._play_song(client, state, next_song)
                elif len(state.playlist) > 0:
                    if state.last_audio == state.playlist[0]:
                        state.last_audio = None
                    else:
                        state.last_audio = state.now_playing
                    next_song = state.playlist.pop(0)
                    self._play_song(client, state, next_song)
                else:
                    asyncio.run_coroutine_threadsafe(client.disconnect(),self.bot.loop)
            except Exception as e:
                asyncio.run_coroutine_threadsafe(client.disconnect(),self.bot.loop)
                #raise e

        client.play(source, after=after_playing)

    @commands.command(aliases=["np"])
    @commands.guild_only()
    @commands.check(audio_playing)
    async def nowplaying(self, ctx):
        """Displays information about the current song."""
        state = self.get_state(ctx.guild)
        message = await ctx.send("", embed=state.now_playing.get_embed())
        await self._add_reaction_controls(message)

    @commands.command(aliases=["q", "playlist"])
    @commands.guild_only()
    @commands.check(audio_playing)
    async def queue(self, ctx):
        """Display the current play queue."""
        state = self.get_state(ctx.guild)
        await ctx.send(self._queue_text(state.playlist))

    def _queue_text(self, queue):
        """Returns a block of text describing a given song queue."""
        if len(queue) > 0:
            message = [f"{len(queue)} songs in queue:"]
            message += [
                f"  {index+1}. **{song.title}** (requested by **{song.requested_by.name}**) - [{format_seconds(song.duration, 1)}]"
                for (index, song) in enumerate(queue)
            ]  # add individual songs
            return "\n".join(message)
        else:
            return "The play queue is empty."

    @commands.command(aliases=["cq"])
    @commands.guild_only()
    @commands.check(audio_playing)
    @permissions.has_permissions(perms = "administrator")
    async def clearqueue(self, ctx):
        """Clears the play queue without leaving the channel."""
        state = self.get_state(ctx.guild)
        state.playlist = []

    @commands.command(aliases=["jq"])
    @commands.guild_only()
    @commands.check(audio_playing)
    # @permissions.has_permissions(perms = "administrator")                  #! decide if this should be uncommented
    async def jumpqueue(self, ctx, song: int, new_index: int):
        """Moves song at an index to a new index in queue."""
        
        state = self.get_state(ctx.guild)  # get state for this guild
        if 1 <= song <= len(state.playlist) and 1 <= new_index:
            song = state.playlist.pop(song-1)  # take song at index...
            state.playlist.insert(new_index-1, song)  # and insert it.

            await ctx.send(self._queue_text(state.playlist))
        else:
            await ctx.send("You must use a valid index.")
    
    @commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    # @permissions.has_permissions(perms = "administrator")                  #! decide if this should be uncommented
    async def remove(self, ctx, index: int):
        """Remove a song at the given index in the queue"""
        state = self.get_state(ctx.guild)  # get state for this guild
        
        if 1 <= index <= len(state.playlist):
            song = state.playlist[index-1]
            if ctx.author.id == song.requested_by.id or permissions.check_permissions(ctx, {"perms" : "administrator"}):    
                song = state.playlist.pop(index-1)  # remove song at index...
        
                await ctx.send(f"Removed **{song.title}**")
        else:
            await ctx.send("You must use a valid index.")

    @commands.command()
    async def lyrics(self, ctx, *, query:str =None):
        state = self.get_state(ctx.guild)

        if await audio_playing(ctx) and query == None:
            async with ctx.channel.typing():
                query = state.now_playing.clean_title
                song = get_song(query, 0)
                source = requests.get(song.path).text
                soup = BeautifulSoup(source, 'lxml')
                tags = soup.find(class_="lyrics")
                lyrics = tags.text.strip()
                lyrics = lyrics.replace("[", "**_").replace("]", "_**")

                return await safe_send(ctx, lyrics, song.title, song.image)

        if query == None:
            raise commands.errors.MissingRequiredArgument(query)

        async with ctx.channel.typing():
            txt = "**Please select a track from the following results by responding with `1 - 5`:**\n"
            max_ind = 0
            for i in range(5):
                try: 
                    txt += f"**{i+1}**. {get_song(query, i).title}\n"
                    max_ind += 1
                except IndexError:
                    break
            await ctx.send(txt)

        def mcheck(message):
            if message.author == ctx.author and message.channel == ctx.channel:
                return True
            return False
        try:
            answer = await self.bot.wait_for('message', timeout=20, check=mcheck)
        except asyncio.TimeoutError:
            return await ctx.send("You didn't respond in time.")
        content = answer.content.strip()
        if not content.isnumeric():
            return await ctx.send("Respond with an integer")
        if intcheck(content) and int(content) <= max_ind and int(content) > 0:
            async with ctx.channel.typing():
                song = get_song(query, int(content)-1)
                source = requests.get(song.path).text
                soup = BeautifulSoup(source, 'lxml')
                tags = soup.find(class_="lyrics")
                lyrics = tags.text.strip()
                lyrics = lyrics.replace("[", "**_").replace("]", "_**")
                
                return await safe_send(ctx, lyrics, song.title, song.image)
        else:
            return await ctx.send("You are proving me stupid for letting you use my commands")
        
    @commands.command(brief="Plays audio from <url>.")
    @commands.guild_only()
    async def play(self, ctx, *, url):
        """Plays audio hosted at <url> (or performs a search for <url> and plays the first result)."""

        client = ctx.guild.voice_client
        req_voice = ctx.author.voice
        state = self.get_state(ctx.guild)  # get the guild's state

        if client and client.channel and req_voice != None:
            if req_voice.channel != client.channel:
                users_in_channel = len([member for member in client.channel.members if not member.bot])
                if users_in_channel:
                    return await ctx.send("Someone else is listening to me right now, sad")
                await client.move_to(req_voice.channel)

            async with ctx.channel.typing():
                try:
                    video = Video(url, ctx.author)
                except youtube_dl.DownloadError as e:
                    logging.warn(f"Error downloading video: {e}")
                    print(f"Error downloading video: {e}")
                    await ctx.send(
                        "There was an error downloading your video, sorry.")
                    return
                state.playlist.append(video)
                message = await ctx.send(f"Added to queue at index {len(state.playlist)}", embed=video.get_embed())
            await self._add_reaction_controls(message)
        else:
            if req_voice != None:
                async with ctx.channel.typing():    
                    channel = req_voice.channel
                    try:
                        video = Video(url, ctx.author)
                    except youtube_dl.DownloadError as e:
                        logging.warn(f"Error downloading video: {e}")
                        await ctx.send(
                            "There was an error downloading your video, sorry.")
                        return
                    client = await channel.connect()
                    self._play_song(client, state, video)
                    message = await ctx.send("", embed=video.get_embed())
                await self._add_reaction_controls(message)
            else:
                # await ctx.send("Are you just stupid or retarded, which vc am i supposed to join if you are not even in one")
                await ctx.send("Join a voice channel.")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Respods to reactions added to the bot's messages, allowing reactions to control playback."""
        message = reaction.message
        
        if user != self.bot.user and message.author == self.bot.user:
            await message.remove_reaction(reaction, user)
            
            if message.guild and message.guild.voice_client:
                user_in_channel = user.voice and user.voice.channel and user.voice.channel == message.guild.voice_client.channel
                guild = message.guild
                perms = message.channel.permissions_for(user)
                state = self.get_state(guild)
                client = message.guild.voice_client
                
                if perms.administrator or state.is_requester(user) or permissions.is_owner(user=user) and user_in_channel:                  
                    
                    if reaction.emoji == "⏯":
                        # pause audio
                        self._pause_audio(client)
                    
                    elif reaction.emoji == "⏭":
                        # skip audio
                        state.loop = False
                        state.loop_queue = False
                        client.stop()
                    
                    elif reaction.emoji == "⏮":
                        if state.last_audio == None:    # if its the first song, restart it
                            if state.loop == True:
                                client.stop()
                            else:
                                state.playlist.insert(0, state.now_playing)  # insert current song at beginning of playlist
                                client.stop()
                        else:                           # else play the last audio
                            state.loop = False
                            state.playlist.insert(0, state.last_audio)
                            state.playlist.insert(1, state.now_playing)  # insert current song at beginning of playlist
                            client.stop()

                    elif reaction.emoji == "⏹":
                        # disconnect bot
                        await self._leave(client, state)
                    
                    elif reaction.emoji == "🔁":
                        # loop/repeat the current audio or queue
                        if state.loop == True:
                            state.loop, state.loop_queue = False, True
                            await message.channel.send("Looping the queue")
                        elif state.loop_queue == True:
                            state.loop_queue = False
                            await message.channel.send("Looping disabled")
                        else:
                            state.loop = True
                            await message.channel.send("Looping current audio")

                    elif reaction.emoji == "🔀":
                        # shuffle the queue
                        self._shuffle(state)
 
                elif user_in_channel and client and client.channel:
                    # ensure that the user is in the channel, and that the bot is in a voice channel
                    voice_channel = client.channel
                    if reaction.emoji == "⏭" and self.config["vote_skip"]:
                        # ensure that skip was pressed, that vote skipping is enabled
                        self._vote_skip(voice_channel, user)
                        # announce vote
                        channel = message.channel
                        users_in_channel = len([member for member in voice_channel.members if not member.bot])  # don't count bots
                        required_votes = math.ceil(self.config["vote_skip_ratio"] * users_in_channel)
                        await channel.send( f"{user.mention} voted to skip ({len(state.skip_votes)}/{required_votes} votes)")
                    
                    elif reaction.emoji == "🔁":
                        # loop/repeat the current audio or queue
                        if state.loop == True:
                            state.loop, state.loop_queue = False, True
                            await message.channel.send("Looping the queue", delete_after=2)
                        elif state.loop_queue == True:
                            state.loop_queue = False
                            await message.channel.send("Looping disabled", delete_after=2)
                        else:
                            state.loop = True
                            await message.channel.send("Looping current audio", delete_after=2)

                    elif reaction.emoji == "🔀":
                        # shuffle the queue
                        self._shuffle(state)
                        await message.channel.send("Shuffled the queue", delete_after=2)

    async def _add_reaction_controls(self, message):
        """Adds a 'control-panel' of reactions to a message that can be used to control the bot."""
        CONTROLS = ["⏹","⏮", "⏯", "⏭","🔁","🔀"]
        for control in CONTROLS:
            await message.add_reaction(control)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, user, before, after):
        client = user.guild.voice_client

        if not client:
            return

        state = self.get_state(user.guild)
        left_channel = before.channel and before.channel == client.channel and before.channel != after.channel or user == self.bot.user and before.channel != after.channel  # check if the member was in the voice channel of client
        
        def vcheck(user, before, after):
            nonlocal client
            joined_channel = after.channel and after.channel == client.channel and before.channel != client.channel or user == self.bot.user and before.channel != client.channel
            if joined_channel:
                return True
            return False
            

        if left_channel:
            users_in_channel = len([member for member in client.channel.members if not member.bot])
            if users_in_channel == 0:
                if not client.is_paused():
                    client.pause()

                try:
                    user, before, after = await self.bot.wait_for('voice_state_update', timeout=300, check=vcheck)  # checks message reactions
                except asyncio.TimeoutError:
                    await self._leave(client, state)
                else:
                    if client.is_paused():
                        client.resume()



class GuildState:
    """Helper class managing per-guild state."""
    __slots__=('volume', 'playlist', 'skip_votes', 'now_playing', 'loop', 'loop_queue', 'last_audio')
    def __init__(self):
        self.volume = 1.00
        self.playlist = []
        self.skip_votes = set()
        self.now_playing = None
        self.last_audio = None
        self.loop = False
        self.loop_queue = False

    def is_requester(self, user):
        try:
            return self.now_playing.requested_by == user
        except:
            return False
    
    def is_song_requester(self, user, index):
        try:    
            return self.playlist[index].requested_by == user
        except:
            return False

    def get_var(self, variable):
        var = getattr(self, variable)
        return var

def setup(bot):
    bot.add_cog(music(bot))
