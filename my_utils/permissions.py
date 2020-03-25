import discord

from my_utils import default
from discord.ext import commands

almins = default.get("config.json").almins


def is_owner(ctx = None, user =  None):
    if user == None:
        return ctx.author.id in almins
    elif ctx == None:   
        return user.id in almins


async def check_permissions(ctx, perms, *, check=all):
    if ctx.author.id in almins:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_permissions(*, check=all, **perms):
    async def pred(ctx):
        return await check_permissions(ctx, perms, check=check)
    return commands.check(pred)


async def check_priv(ctx, member):
    try:
        # Self checks
        if member == ctx.author:
            return await ctx.send(f"You can't {ctx.command.name} yourself, although I want to")
        if member.id == ctx.bot.user.id:
            return await ctx.send("So that's what you think of me huh..? You pathetic humans")

        # Protect the almins
        if member.id in almins:
            if ctx.author.id not in almins:
                return await ctx.send(f"You dare {ctx.command.name} my lords (●'◡'●)")
            else:
                return await ctx.send(f"I am sorry, i cannot betray either of my lords")

        # Check if user bypasses
        if ctx.author.id == ctx.guild.owner.id:
            return False

        # Now permission check
        if member.id == ctx.guild.owner.id:
            return await ctx.send(f"Even if i tried, i will not be able to {ctx.command.name} the server owner, sed")
        if ctx.author.top_role == member.top_role:
            return await ctx.send(f"You can't {ctx.command.name} someone who has the same permissions as you...")
        if ctx.author.top_role < member.top_role:
            return await ctx.send(f"Nope, you can't {ctx.command.name} someone higher than yourself.")
    except Exception:
        return False


def can_send(ctx):
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.permissions_for(ctx.guild.me).send_messages


def can_embed(ctx):
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.permissions_for(ctx.guild.me).embed_links


def can_upload(ctx):
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.permissions_for(ctx.guild.me).attach_files


def can_react(ctx):
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.permissions_for(ctx.guild.me).add_reactions


def is_nsfw(ctx):
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.is_nsfw()
