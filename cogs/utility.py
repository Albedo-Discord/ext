import discord
import os
from discord.ext import commands, tasks

class utility(commands.Cog):    
    """Some utility commands for you guys, might be able to help in whatever you are trying to do"""

    @commands.command(aliases = ['av'])
    async def avatar(self, ctx, member: discord.Member = None):
        """Get all avatar of the mentioned user or yourself(by not mentioning anyone)"""
        
        member = ctx.author if not member else member
        embed = discord.Embed(timestamp=ctx.message.created_at)

        embed.set_author(name=f"Avatar of {member}")
        embed.set_image(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(aliases = ['ui'])
    async def userinfo(self, ctx, member: discord.Member = None):
        """Gets you all the info for a perticular user, or yourself(don't mention anyone)"""
        
        if member == None:
            member = ctx.author

        roles = [role for role in member.roles]
        embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at)
        embed.set_author(name=f"User info of {member}")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="ID",value=member.id)
        embed.add_field(name="Guild name",value=member.guild)
        embed.add_field(name="Created at",value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name="Joined at",value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name=f"Roles ({len(roles)-1})",value="\n".join([role.mention for role in roles[1::1]]))
        embed.add_field(name="Top role",value=member.top_role.mention)
    
        await ctx.send(embed=embed)

    @commands.command(aliases = ['cc', 'copyback'])
    async def copycat(self, ctx, *, arg: commands.clean_content(fix_channel_mentions=True)):
        """Just re-sends the text you sent"""
        
        await ctx.send(arg)

    @commands.command(hidden = True)
    async def server(self, ctx):
        """Sends the server you are currently in"""

        await ctx.send(str(ctx.author.guild))

def setup(bot):
    bot.add_cog(utility(bot))