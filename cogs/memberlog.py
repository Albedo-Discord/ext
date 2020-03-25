from discord.ext import commands

class memberlog(commands.Cog):
    """Logs if anyone joins or leave your server"""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, ctx, member):
       await ctx.send(f'{member} has joined the server.')

    @commands.Cog.listener()                                                   
    async def on_member_remove(self, ctx, member):
        await ctx.send(f'{member} has left the server.')

def setup(bot):
    bot.add_cog(memberlog(bot))
