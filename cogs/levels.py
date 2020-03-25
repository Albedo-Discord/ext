import random
import re
from datetime import datetime, timedelta
import io
import urllib
import os

import discord
import requests
from dateutil.parser import parse
from discord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont, ImageOps

from my_utils import default as d, permissions

def _exist(user_id):
    profiles = d.retrieve("profile.json")
    if user_id in profiles["id"]:
        return True
    return False

def _get_rank(guild_id : str, user_id : str):
    levels = d.retrieve("levels.json")
    if user_id in levels[guild_id].keys():
        return levels[guild_id][user_id]["rank"]
    else:
        return False

def _get_total_exp(guild_id : str, user_id : str):
    levels = d.retrieve("levels.json")
    if user_id in levels[guild_id].keys():
        return levels[guild_id][user_id]["total experience"]

def _get_level(guild_id : str, user_id : str):
    levels = d.retrieve("levels.json")
    if user_id in levels[guild_id].keys():
        return levels[guild_id][user_id]["level"]

def _get_current_exp(guild_id : str, user_id : str):
    levels = d.retrieve("levels.json")
    if user_id in levels[guild_id].keys():
        return levels[guild_id][user_id]["current experience"]

def _initialise(user_id, force_initialise = False, index = 0):
    if _exist(user_id) is False or force_initialise is True:
        profiles = d.retrieve("profile.json")
        if force_initialise is True:
            for colors in profiles.keys():
                del profiles[colors][index]
        profiles["id"] += [user_id]
        profiles["arc color"] += ["#00adb5"]
        profiles["bg color"] += ["#303841"]
        profiles["text color"] += ["#eeeeee"]
        profiles["banner"] += ["#3a4750"]
        profiles["number color"] += ["#00adb5"]
        profiles["ranker color"] += ["#eeeeee"]
        profiles["arc path color"] += ["#bbbcbd"]
        d.save("profile.json", profiles)

def _get_index(user):
    profiles = d.retrieve("profile.json")
    if _exist(user) is True:
        return profiles["id"].index(user)
    else:
        _initialise(user, True)

def _get_color(index, location):
    profiles = d.retrieve("profile.json")
    return profiles[location][index]

def _change_color(index, color, location):
    profiles = d.retrieve("profile.json")
    profiles[location][index] = color
    d.save("profile.json", profiles)

class levels(commands.Cog):
    """This is only for debugging purposes"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        exp = random.randint(15, 25)
        levels = d.retrieve("levels.json")
        
        if str(message.guild.id) in levels.keys():
            pass #users = levels[message.guild]
        else:
            levels[str(message.guild.id)] = {}
            
        users = levels[str(message.guild.id)]

        users = await self._initialise_data(users, message.author)
        await self._add_exp(users, message.author, exp)
        await self._level_up(users, message.author, message.channel)

        levels[str(message.guild.id)]
        d.save("levels.json", levels)
    
    async def _initialise_data(self, users, user):
        if not str(user.id) in users:
            user_number = len(list(users.keys())) + 1
            users[str(user.id)] = {
                "total experience": 0,
                "current experience": 0,
                "level": 1,
                "last message": "696-06-09 06:09:06.9696969",
                "rank": user_number
            }
        return users

    async def _add_exp(self, users, user, exp):
        last = parse(users[str(user.id)]['last message'])
        after_cooldown = last + timedelta(minutes=1)
        rank = 1
        if datetime.now() > after_cooldown:    
            users[str(user.id)]['total experience'] += exp
            users[str(user.id)]['current experience'] += exp
            users[str(user.id)]['last message'] = str(datetime.now())
            previous_rank = users[str(user.id)]["rank"]
            for other_user in users.keys():
                if users[other_user]["total experience"] > users[str(user.id)]['total experience'] and other_user != str(user.id):
                    rank += 1
            users[str(user.id)]["rank"] = rank
            for other_user in users.keys():
                if users[other_user]["rank"] <= users[str(user.id)]['rank'] and previous_rank <= users[other_user]["rank"] and other_user != str(user.id):
                    users[other_user]["rank"] += 1
        return

    async def _level_up(self, users, user, channel):
        current_exp = users[str(user.id)]["current experience"]
        lvl = users[str(user.id)]["level"]
        exp_for_levelup = 50*lvl**2 + 50*lvl + 100
        if current_exp > exp_for_levelup:
            await channel.send(f":tada:  Congratulations! You leveled up to **Level {lvl+1}** {user.mention}  :tada:")
            users[str(user.id)]["current experience"] = 0
            users[str(user.id)]["level"] += 1
        return

    @commands.group(aliases = ["c"], invoke_without_command = True)
    async def customize(self, ctx):
        """Customize your profile"""

        _initialise(str(ctx.author.id), False)

        await ctx.send("Nope, no category like dat found")

    @customize.command()
    async def arc(self, ctx, color):
        """Change the color of arc"""

        _initialise(str(ctx.author.id), False)
        try:
            Image.new("RGB", (700, 1100), color = color)
        except:
            return await ctx.send("Invalid colors, baka")
        ind = _get_index(str(ctx.author.id))
        ind = _get_index(str(ctx.author.id))
        _change_color(ind, color, "arc color")
        await ctx.send(f"Arc color changed to `{color}`")
    
    @customize.command(aliases = ["bg"])
    async def background(self, ctx, color):
        """Change the color of the background"""

        _initialise(str(ctx.author.id), False)
        try:
            Image.new("RGB", (700, 1100), color = color)
        except:
            return await ctx.send("Invalid colors, baka")
        ind = _get_index(str(ctx.author.id))
        _change_color(ind, color, "bg color")
        await ctx.send(f"Background color changed to `{color}`")

    @customize.command(aliases = ["bn"], brief="Change the banner", usage="<color|url|attachment>")
    async def banner(self, ctx, color = None):
        """Change the image or the color of the banner"""

        _initialise(str(ctx.author.id), False)
        ind = _get_index(str(ctx.author.id))
        banner = _get_color(ind, "banner")
        if color != None:
            color = color.strip('<>')
            if color == banner:
                pass
            else:
                try:
                    Image.new("RGB", (700, 1100), color = color)
                except ValueError:
                    try:
                        response = requests.get(color)
                        if response.content == None:
                            return await ctx.send("The url doesn't contain an image. Send a valid image url")
                        with open(f"banners/{ctx.author.id}", "wb") as f:
                            f.write(response.content)
                        color = f"{ctx.author.id}"
                    except:
                        return await ctx.send("Invalid colors, baka")
        else:
            if len(ctx.message.attachments) == 1:
                await ctx.message.attachments[0].save(f"banners\{ctx.author.id}")
                color = f"{ctx.author.id}"
            else:
                return await ctx.send("Atleast provide an attachment")
    
        ind = _get_index(str(ctx.author.id))
        _change_color(ind, color, "banner")
        await ctx.send(f"Banner color changed to `{color}`")

    @customize.command(aliases = ["tc"])
    async def textcolor(self, ctx, color):
        """Change the text color"""

        _initialise(str(ctx.author.id), False)
        try:
            Image.new("RGB", (700, 1100), color = color)
        except:
            return await ctx.send("Invalid colors, baka")
        ind = _get_index(str(ctx.author.id))
        _change_color(ind, color, "text color")
        await ctx.send(f"Text color changed to `{color}`")
    
    @customize.command(aliases = ["nc"])
    async def numbercolor(self, ctx, color):
        """Change the color of numbers"""

        _initialise(str(ctx.author.id))
        try:
            Image.new("RGB", (700, 1100), color = color)
        except:
            return await ctx.send("Invalid colors, baka")
        ind = _get_index(str(ctx.author.id))
        _change_color(ind, color, "number color")
        await ctx.send(f"Number color changed to `{color}`")

    @customize.command(aliases = ["rc"], brief="Change the ranker color")
    async def rankercolor(self, ctx, color):
        """Change the ranker color, the number at the top left."""

        _initialise(str(ctx.author.id))
        try:
            Image.new("RGB", (700, 1100), color = color)
        except:
            return await ctx.send("Invalid colors, baka")
        ind = _get_index(str(ctx.author.id))
        _change_color(ind, color, "ranker color")
        await ctx.send(f"Ranker color changed to `{color}`")

    @customize.command(aliases = ["apc"], brief="Change the arc path color")
    async def arcpathcolor(self, ctx, color):
        """Change the color of the path of the arc"""

        _initialise(str(ctx.author.id))
        try:
            Image.new("RGB", (700, 1100), color = color)
        except:
            return await ctx.send("Invalid colors, baka")
        ind = _get_index(str(ctx.author.id))
        _change_color(ind, color, "arc path color")
        await ctx.send(f"arc path color changed to `{color}`")

    @customize.command(usage="<light|dark|default>")
    async def mode(self, ctx, mode):
        """These are some preset themes for you"""

        _initialise(str(ctx.author.id), False)
        ind = _get_index(str(ctx.author.id))
        if mode == "light":    
            _change_color(ind, "#7289DA", "arc color")
            _change_color(ind, "#8E9FDD", "bg color")  
            _change_color(ind, "white", "text color")
            _change_color(ind, "#FAFAFA", "banner")
            _change_color(ind, "white", "number color")
            _change_color(ind, "#7289DA", "ranker color")
            _change_color(ind, "white", "arc path color")
            await ctx.send("Light theme active.")

        elif mode == "dark":
            _change_color(ind, "#5c5470", "arc color")
            _change_color(ind, "#2a2438", "bg color")
            _change_color(ind, "#dbd8e3", "text color")
            _change_color(ind, "#352f44", "banner")
            _change_color(ind, "#dbd8e3", "number color")
            await ctx.send("Dark theme active.")

        elif mode == "default":
            _initialise(str(ctx.author.id), True, ind)
            await ctx.send("Default theme active.")
        
        else:
            await ctx.send("I feel emptiness somewhere. Yeah got it, your head, its so empty even Null is afraid of you")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def show(self, ctx, member: discord.Member = None):
        """Shows the profile color set"""

        member = ctx.author if not member else member
        _initialise(str(member.id), False)
        ind = _get_index(str(member.id))
        profiles = d.retrieve("profile.json")

        arc = profiles["arc color"][ind]
        bg = profiles["bg color"][ind]
        text = profiles["text color"][ind]
        number = profiles["number color"][ind]
        banner = profiles["banner"][ind]
        arcpathc = profiles["arc path color"][ind]
        ranker = profiles["ranker color"][ind]

        d.save("profile.json", profiles)
        
        await ctx.send(f"Profile colors of **{str(member)[:-5]}**\n\n**Arc color** `{arc}`\n**Arc path color** `{arcpathc}`\n**Background color** `{bg}`\n**Text color** `{text}`\n**Number color** `{number}`\n**Banner color** `{banner}`\n**#Rank color** `{ranker}`\n")


    @commands.command(aliases = ["rank"])
    async def profile(self, ctx, member: discord.Member = None):
        r"""Shows the profile \-\_\-"""

        member = ctx.author if not member else member
        _initialise(str(member.id), False)
        profiles = d.retrieve("profile.json")
        ind = _get_index(str(member.id))

        # VARIABLES
        member_rank = _get_rank(str(ctx.guild.id), str(member.id))
        if member_rank == False:
            return await ctx.send(f"**{member.name}** has not messaged yet, so their profile doesn't exist.")
        
        member_total_exp = _get_total_exp(str(ctx.guild.id), str(member.id))
        member_current_exp = _get_current_exp(str(ctx.guild.id), str(member.id))
        member_level = _get_level(str(ctx.guild.id), str(member.id)) 
        exp_for_levelup = 50*member_level**2 + 50*member_level + 100
        arc_end = (member_current_exp/exp_for_levelup)*360 - 90
        bgc = _get_color(ind, "bg color")
        banner_id = _get_color(ind, "banner") 
        numberc = _get_color(ind, "number color")
        textc = _get_color(ind, "text color")
        arcc = _get_color(ind, "arc color")
        rankerc = _get_color(ind, "ranker color")
        arcpathc = _get_color(ind, "arc path color")

        # PROCESSING THE VARIABLES
        for image in os.listdir('banners'):     # process the banner of the user based on the color, url or the downloaded file
            if str(banner_id) == image.split(".")[0]:
                bannerc = image
                break
            else:
                bannerc = banner_id

        member_total_exp = d.implement_numeral(member_total_exp)    #Adds, k, m, etc.


        try:
        # LOADING THE AVATAR AND BANNER            
            response = requests.get(member.avatar_url)
            im = Image.open(io.BytesIO(response.content))

            try:
                banner = Image.new("RGB", (700, 280), color = bannerc)
            except:
                try:    
                    response = requests.get(bannerc)
                    banner = Image.open(io.BytesIO(response.content))
                except:
                    banner = Image.open(f"banners\{bannerc}")
            
            banner = banner.resize((700, 280))

        # MASK FOR AVATAR

            im = im.resize((300, 300))
            bigsize = (im.size[0] * 4, im.size[1] * 4)
            mask = Image.new('L', bigsize, 0)
            draw = ImageDraw.Draw(mask) 
            draw.ellipse((0, 0) + bigsize, fill=255)
            mask = mask.resize(im.size, Image.ANTIALIAS)
            im.putalpha(mask)

            output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)
            output.save('output.png')

            w, h = 350, 350
            shape = [(0, 0), (w, h)]

        # CREATING IMAGES
            background = Image.new("RGB", (700, 1100), color = "white")
            small_bg = Image.new("RGB", (700, 820), color=bgc)
            small_circle_img = Image.new("RGB", (w, h))
            small_circle = ImageDraw.Draw(small_circle_img)
            small_circle.ellipse(shape, fill=bgc)

        # MASK FOR SMALL CIRCLE
            im2 = im.resize((350, 350))
            bigsize2 = (im2.size[0] * 4, im2.size[1] * 4)
            mask2 = Image.new('L', bigsize2, 0)
            draw2 = ImageDraw.Draw(mask2) 
            try:    
                draw2.ellipse((0, 0) + bigsize2, fill=bannerc)
            except:
                draw2.ellipse((0, 0) + bigsize2, fill=bgc)
            mask2 = mask2.resize(im2.size, Image.ANTIALIAS)
            small_circle_img.putalpha(mask2)

        # TEXT
            # text = str(member)
            text = str(member)[:11]+"...#"+member.discriminator if len(str(member)) > 18 else str(member)
            font_size = 70
            font = ImageFont.truetype('fonts/monofonto.ttf', font_size)
            text_draw = ImageDraw.Draw(small_bg)
            w1, h1 = font.getsize(text)
            text_draw.text(((700-w1)/2, (230-h1)/2), text, font=font, fill=numberc)
        # RANK, LEVEL, EXP TEXT
            font_size2 = 45
            font2 = ImageFont.truetype('fonts/soloist1.ttf', font_size2)
            rank_draw = ImageDraw.Draw(background)
        # MAIN TEXT
            font_size3 = 90
            # font3 = ImageFont.truetype('fonts/Fragmentcore.ttf', font_size3)
            number_draw = ImageDraw.Draw(background)
            font3 = ImageFont.truetype('fonts/NewAthleticM54-31vz.ttf', font_size3)
        # TOP LEFT RANK
            font_size4 = 130
            font4 = ImageFont.truetype('fonts/ROBOTECH_GP.ttf', font_size4)
            ranker = ImageDraw.Draw(background)

        # PASTING

            background.paste(small_bg, (0,280))
            background.paste(banner, (0, 0))
            background.paste(small_circle_img, (175, 5), im2)
            background.paste(im, (200, 30), im)

        # ARC
            arc_draw = ImageDraw.Draw(background)
            #             x0  y0  x1   y1      
        # GREY EXP ARC    
            arc_draw.arc((190, 700, 510, 1030), start = -90, end = 270, fill=arcpathc, width = 7)     
            
        # EXP ARC 
            arc_draw.arc((190, 700, 510, 1030), start = -90, end = arc_end, fill = arcc, width = 12)

        # OUTER GREY CIRCLE
            arc_draw.arc((165, 675, 535, 1055), start = -90, end = 270, fill = arcc, width = 1)       

        # TEXT FOR RANK & LEVEL
            rw = font2.getsize("Rank")[0]
            lw = font2.getsize("Level")[0]
            ew = font2.getsize("Exp")[0]
            rank_draw.text(((700-rw)/2, 770), "Rank", font=font2, fill=textc)
            rank_draw.text(((500-lw)/4, 500), "Level", font=font2, fill=textc)
            rank_draw.text((3*(750-ew)/4, 500), "Exp", font=font2, fill=textc)

        # TEXT FOR NUMBER

            rnw = font3.getsize(str(member_rank))[0]
            lnw = font3.getsize(str(member_level))[0]
            enw = font3.getsize(str(member_total_exp))[0]
            number_draw.text(((700-rnw)/2, 840), str(d.implement_numeral(member_rank)), font=font3, fill=numberc)
            number_draw.text(((540-lnw)/4, 565), str(d.implement_numeral(member_level)), font=font3, fill=numberc)
            number_draw.text((3*(750-enw)/4, 565), str(member_total_exp), font=font3, fill=numberc)

            if member_rank < 10:    
                ranker.text((30,0), f"#{str(member_rank)}", font=font4, fill=rankerc)
            background.save('overlap.png')
            d.save("profile.json", profiles)
            await ctx.send(file=discord.File('overlap.png'))

        except ValueError:
            await ctx.send("Invalid colors, setting to default.")
            _initialise(member.id, True, ind)

def setup(bot):
 bot.add_cog(levels(bot))
