import discord
import os
from discord.ext import commands, tasks
import random
import urllib
import aiohttp
import requests
import asyncio
import logging

from io import BytesIO
from my_utils import lists, permissions, default, argparser

def intcheck(it):                                                       #Interger checker
    isit = True
    try:
        int(it)
    except:
        isit = False

    return isit

class fun(commands.Cog):
    """Commands for fun, yup that's it"""

    def __init__(self, bot):
        self.bot = bot
    
    async def randomimageapi(self, ctx, url, endpoint):
        try:
            r = requests.get(url).json()
        except aiohttp.ClientConnectorError:
            return await ctx.send("The API seems to be down...")
        except aiohttp.ContentTypeError:
            return await ctx.send("The API returned an error or didn't return JSON...")

        # response = requests.get(r[endpoint])
        # with open("animals.png", "wb") as f:
        #     f.write(response.content)
        embed = discord.Embed(
            color = discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)
        embed.set_author(name=f"Here, take some {ctx.invoked_with}s")
        embed.set_image(url=r[endpoint])
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    async def api_img_creator(self, ctx, url, filename, content=None):
        async with ctx.channel.typing():
            req = requests.get(url)

            if req.content is None:
                return await ctx.send("I couldn't create the image ;-;")

            img = BytesIO(req.content)
            img.seek(0)
            await ctx.send(content=content, file=discord.File(img, filename=filename))

    @commands.command(aliases=["question", "ask", "8ball"])
    async def ceist(self, ctx, *,question: commands.clean_content(fix_channel_mentions=True)):
        """Ask me any question and I'll answer it."""                                     #CEIST function
        answer = random.choice(lists.ballresponse)
        embed = discord.Embed(colour=discord.Colour.from_rgb(0,250,141), timestamp=ctx.message.created_at)
        embed.set_author(name="Here's what I think")
        embed.add_field(name="Question\t",value=f"{question}")
        embed.add_field(name="Answer",value=f"{answer}")
        await ctx.send(embed=embed)

    @commands.command(aliases = ['emo', 'emoji'])                    # EMOTE function
    async def emote(self, ctx, type, emo_amount):
        """Wanna print some emotes?"""

        if intcheck(emo_amount):
            emo_amount = int(emo_amount)
            if emo_amount > 0 and emo_amount < 201:
                await ctx.send(f':{type}:'*emo_amount)
            elif emo_amount < 0 and emo_amount > -201:
                emo_amount *= -1
                await ctx.send(f':{type}:\n'* (emo_amount))
            else:
                await ctx.send(f'|emoji amount| too big')
        else:
            emo_amount = 1
            await ctx.send(f':{type}:'* emo_amount)

    @commands.command()                                                       #%DED function
    async def ded(self, ctx, member:discord.Member = None):
        """Find out how dead you're inside."""

        member = ctx.author if not member else member
        saddy = random.randrange(1, 100)
        embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at)
        embed.add_field(name="Bruh",value=f"You are {saddy}% dead inside :skull:.")
        await ctx.send(embed=embed)

    @commands.command()                                                       #SIZE fucntion
    async def dicc(self, ctx):
        """pp long? pp short? no pp? find out here."""

        random_p = random.randrange(1, 10)
        dicc_string = random_p*"="
        await ctx.send(f">>> Your dicc is 8{dicc_string}D long")

    @commands.command()
    async def f(self, ctx, *, text: commands.clean_content = None):
        """ Press F to pay respect """
        hearts = ['❤', '💛', '💚', '💙', '💜', '🖤', '💜', '💔', '💝', '💖', '💗', '💓', '💟']
        reason = f"for **{text}** " if text else ""
        await ctx.send(f"**{ctx.author.name}** has paid their respect {reason}{random.choice(hearts)}")

    @commands.command(aliases = ['kat', 'pussy', 'neko'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def cat(self, ctx):
        """ Posts a random cat """
        await self.randomimageapi(ctx, 'https://api.alexflipnote.dev/cats', 'file')

    @commands.command(aliases = ['doge', 'doggo'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def dog(self, ctx):
        """ Posts a random dog """
        await self.randomimageapi(ctx, 'https://api.alexflipnote.dev/dogs', 'file')

    @commands.command(aliases=["bird"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def birb(self, ctx):
        """ Posts a random birb """
        await self.randomimageapi(ctx, 'https://api.alexflipnote.dev/birb', 'file')

    @commands.command(aliases = ['ducc'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def duck(self, ctx):
        """ Posts a random duck """
        await self.randomimageapi(ctx, 'https://random-d.uk/api/v1/random', 'url')
    
    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def urban(self, ctx, *, search: str):
        """ Find the 'best' definition to your words """
        async with ctx.channel.typing():
            url = requests.get(f'https://api.urbandictionary.com/v0/define?term={search}').json()

            if url is None:
                return await ctx.send("I think the API broke...")

            if not len(url['list']):
                return await ctx.send("Couldn't find your search in the dictionary...")

            result = sorted(url['list'], reverse=True, key=lambda g: int(g["thumbs_up"]))[0]

            definition = result['definition']
            definition = definition.replace("[", "**").replace("]", "**")
            if len(definition) >= 1500:
                definition = definition[:1500]
                definition = definition.rsplit(' ', 1)[0]
                definition += '...'
            

            embed = discord.Embed(
                title = "📚 Urban Dictionary 📚",
                color = discord.Colour.from_rgb(0,250,141), timestamp=ctx.message.created_at)
            
            embed.add_field(name="**Definitions for {}**".format(result['word']), value=f"\n{definition}")
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(aliases=['noticemesenpai'])
    async def noticeme(self, ctx):
        """ Notice me senpai! owo """
        if not permissions.can_upload(ctx):
            return await ctx.send("I cannot send images here ;-;")

        response = requests.get("https://i.alexflipnote.dev/500ce4.gif")
        with open("noticeme.gif", "wb") as f:
            f.write(response.content)


    @commands.command(aliases=['jokes', 'funny'])
    async def joke(self, ctx, nsfw: str = "true"):
        """Random Joke"""
         
        buttons = ["<:al_up:681864791555440681>", "<:al_down:681864001948614684>"]
        url = "https://joke3.p.rapidapi.com/v1/joke"
        if nsfw.lower() == "false":
            nsfw = False
        else:
            nsfw = True
        querystring = {"nsfw": nsfw}

        headers = {
            'x-rapidapi-host': "joke3.p.rapidapi.com",
            'x-rapidapi-key': "1adab39b32msh3ace9d305db7522p133436jsn292ad15e4db3"
            }

        joke = requests.request("GET", url, headers=headers, params=querystring).json()
        message = await ctx.send(f"{joke['content']}\n> <:al_up:681864791555440681>: {joke['upvotes']} <:al_down:681864001948614684>: {joke['downvotes']}")
        for button in buttons:    
            await message.add_reaction(button)
        reacted = [self.bot.user]
        def rcheck(reaction, user):
            if reaction.message.content == message.content and user not in reacted:
                reacted.append(user)
                return True
            return False
        
        while 1:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=rcheck)  # checks message reactions
            except asyncio.TimeoutError:  # session has timed out what a fucking nerd
                try:
                    await message.clear_reactions()
                except discord.errors.Forbidden:
                    pass
                break
            if str(reaction.emoji) == '<:al_up:681864791555440681>':
                upvote = requests.request("POST", f"https://joke3.p.rapidapi.com/v1/joke/{joke['id']}/upvote", headers=headers).json()
                await message.edit(content=f"{upvote['content']}\n> <:al_up:681864791555440681>: {upvote['upvotes']} <:al_down:681864001948614684>: {upvote['downvotes']}")
            elif str(reaction.emoji) == '<:al_down:681864001948614684>':
                downvote = requests.request("POST", f"https://joke3.p.rapidapi.com/v1/joke/{joke['id']}/downvote", headers=headers).json()
                await message.edit(content=f"{downvote['content']}\n> <:al_up:681864791555440681>: {downvote['upvotes']} <:al_down:681864001948614684>: {downvote['downvotes']}")

    @commands.command(aliases=['quote'])
    async def quotes(self, ctx):
        url = "https://quotes15.p.rapidapi.com/quotes/random/"

        querystring = {"language_code":"en"}

        headers = {
            'x-rapidapi-host': "quotes15.p.rapidapi.com",
            'x-rapidapi-key': "1adab39b32msh3ace9d305db7522p133436jsn292ad15e4db3"
            }

        response = requests.request("GET", url, headers=headers, params=querystring).json()
        await ctx.send(f"_{response['content']}_\n- {response['originator']['name']}")

    @commands.command(aliases=['randomimage','wikihow'])
    async def wiki(self, ctx):
        try:
            url = "https://hargrimm-wikihow-v1.p.rapidapi.com/images"
            querystring = {"count":"1"}

            headers = {
                'x-rapidapi-host': "hargrimm-wikihow-v1.p.rapidapi.com",
                'x-rapidapi-key': "1adab39b32msh3ace9d305db7522p133436jsn292ad15e4db3"
                }

            response = requests.request("GET", url, headers=headers, params=querystring).json()
            embed = discord.Embed(
                color = discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)
            embed.set_author(name=f"Totally random wikihow images")
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            embed.set_image(url=response['1'])
            await ctx.send(embed=embed)
        except Exception as e:
            raise commands.errors.CommandInvokeError(e)

def setup(bot):
    bot.add_cog(fun(bot))

