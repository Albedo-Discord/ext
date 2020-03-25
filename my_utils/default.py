import json
import os
import time
import traceback
from collections import namedtuple
from io import BytesIO

import discord
import timeago as timesince

from my_utils.guildstate import state_instance


def get(file):
    try:
        with open(file, encoding='utf8') as data:
            return json.load(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    except AttributeError:
        raise AttributeError("Unknown argument")
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")


def traceback_maker(err, advance: bool = True):
    _traceback = ''.join(traceback.format_tb(err.__traceback__))
    error = ('```py\n{1}{0}: {2}\n```').format(type(err).__name__, _traceback, err)
    return error if advance else f"{type(err).__name__}: {err}"


def timetext(name):
    return f"{name}_{int(time.time())}.txt"


def timeago(target):
    return timesince.format(target)


def date(target, clock=True):
    if clock is False:
        return target.strftime("%d %B %Y")
    return target.strftime("%d %B %Y, %H:%M")


def responsible(target, reason):
    responsible = f"[ {target} ]"
    if reason is None:
        return f"{responsible} no reason given..."
    return f"{responsible} {reason}"


def actionmessage(case, mass=False):
    output = f"**{case}** the user"

    if mass is True:
        output = f"**{case}** the IDs/Users"

    return f"✅ Successfully {output}"


async def prettyResults(ctx, filename: str = "Results", resultmsg: str = "Here's the results:", loop=None):
    if not loop:
        return await ctx.send("The result was empty...")

    pretty = "\r\n".join([f"[{str(num).zfill(2)}] {data}" for num, data in enumerate(loop, start=1)])

    if len(loop) < 15:
        return await ctx.send(f"{resultmsg}```ini\n{pretty}```")

    data = BytesIO(pretty.encode('utf-8'))
    await ctx.send(
        content=resultmsg,
        file=discord.File(data, filename=timetext(filename.title()))
    )

def intcheck(it):                                                       #Interger checker
    isit = True
    try:
        int(it)
    except:
        isit = False

    return isit

def all_cases(za_word):
    if len(za_word) == 1:
        if za_word.isalnum():
            return [za_word.lower(), za_word.upper()]
        else:
            return[za_word]
    else:
        output = []
        f = za_word[0]
        l = za_word[1:]
        for st in all_cases(l):
            if f.isalnum():
                output.append(f.lower() + st)
                output.append(f.upper() + st)
            else:
                output.append(f+st)
        return output

def save(jsonfile, data):
    with open(f"json/{jsonfile}", "w") as f:
      json.dump(data, f, indent=4)

def retrieve(jsonfile):
    with open(f"json/{jsonfile}", "r") as f:
       data = json.load(f)
    return data

def delete(file, jsonFile = None, keyName = None):
    os.remove(file)
    if jsonFile != None and keyName != None:   
        data = retrieve(jsonFile)
        data[keyName].remove(file)
        save(jsonFile, data)

def add_zero(var):
    if var < 10:
            return f"0{var}"
    else:
        return var

async def safe_send(ctx, txt, name, thumbnail):
    embed= discord.Embed(color = discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)
    embed.set_author(name=name, icon_url=ctx.me.avatar_url)
    embed.set_thumbnail(url=thumbnail)
    pg=0
    async def splitter(txt: str):    
        nonlocal pg
        l=5900
        embed.clear_fields()
        pg+=1
        i=0
        if len(txt)>l:
            txt2 = txt[:l]
            txt=txt[l:]
            txt2 = txt2.rsplit(' ', 1)
            txt =txt2[1] + txt
            txt2=txt2[0]
            embed.description = txt2[:2000].rsplit(' ', 1)[0]
            txt2 = txt2[:2000].rsplit(' ', 1)[1] + txt2[2000:]
            work_number = len(txt2)
            
            while i < work_number:
                big_chunk = txt2[:1000]
                big_chunk = big_chunk.rsplit(' ', 1) if len(big_chunk)>1000 else [big_chunk]
                chunk = big_chunk[0]
                embed.add_field(name=str("_ _"), value=chunk, inline=False)
                txt2 = txt2[1000:]
                txt2 = big_chunk[1] + txt2 if len(big_chunk)>1 else txt2
                i+=1000


            embed.set_footer(text=f"PAGE {pg}")
            await ctx.send(embed=embed)
            await splitter(txt)
        else:
            txt2=txt
            embed.description = txt2[:2000].rsplit(' ', 1)[0]
            txt2 = txt2[:2000].rsplit(' ', 1)[1] + txt2[2000:]
            work_number = len(txt2)
            while i <= work_number:
                big_chunk = txt2[:1000]
                big_chunk = big_chunk.rsplit(' ', 1) if len(big_chunk)>1000 else [big_chunk]
                chunk = big_chunk[0]
                embed.add_field(name=str("_ _"), value=chunk, inline=False)
                txt2 = txt2[1000:]
                txt2 = big_chunk[1] + txt2 if len(big_chunk)>1 else txt2
                i+=1000
            embed.set_footer(text=f"END")
            await ctx.send(embed=embed)
    await splitter(txt)
    

def implement_numeral(number):
    count = 0
    suffixes = {0: "", 1: "k", 2: "m", 3: "b", 4: "t"}
    formatted = ""
    def process(number):
        nonlocal count
        nonlocal formatted   
        if number > 99:
            number = number/1000
            number = round(number, 1)
            count += 1
            if number > 99:
                process(number)
            elif number < 99:
                formatted = f"{number}{suffixes[count]}"
        else:
            formatted = f"{number}{suffixes[count]}"
    
    process(number)
    return formatted

def format_seconds(time_seconds, output_type=0):
    """Formats some number of seconds into a string of format d days, x hours, y minutes, z seconds"""
    seconds = time_seconds
    hours = 0
    minutes = 0
    days = 0
    while seconds >= 60:
        if seconds >= 60 * 60 * 24:
            seconds -= 60 * 60 * 24
            days += 1
        elif seconds >= 60 * 60:
            seconds -= 60 * 60
            hours += 1
        elif seconds >= 60:
            seconds -= 60
            minutes += 1
    seconds = int(seconds)
    if output_type == 0:
        if days != 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours != 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes != 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    else:
        seconds = add_zero(seconds)
        if days != 0:
            hours = add_zero(hours)
            minutes = add_zero(minutes)
            return f"{days}:{hours}:{minutes}:{seconds}"
        elif hours != 0:
            minutes = add_zero(minutes)
            return f"{hours}:{minutes}:{seconds}"
        elif minutes != 0:
            return f"{minutes}:{seconds}"
        else:
            return f"0:{seconds}"

def to_seconds(time):
    try:    
        components = time.split(":")
        seconds = 0
        for index, value in enumerate(components[::-1]):
            seconds += int(value)*(60**index)
        if seconds < 0:
            return False    
        return seconds
    except:
        return False


