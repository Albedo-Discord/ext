from discord.ext import commands

class doujinshi(commands.Cog):
    """Commands for reading doujinshis straight from nhentai"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases = ['rand'], brief="Get random doujinshi", usage="<ID of doujinshi>")
    async def random(self, ctx):
        """Get random doujinshi straight from nhentai.
        Caution: might give doujinshi with shit tags"""
        pass

    @commands.command(usage="<ID of doujinshi>")
    async def read(self, ctx, ID):
        """Read doujinshi by the Id you provided"""
        pass

    @commands.command(aliases = ['dl'], brief="Download doujinshi by the Id you provided", usage="<ID of doujinshi>")
    async def download(self, ctx, ID):
        """Get a doujinshi from nhentai by the Id you provided so that you can read it in a public washroom where internet is not available"""
        pass

    @commands.command(aliases = ['lang'], brief="Get random doujinshi by the language", usage="<ch|en|jp>")
    async def language(self, ctx, language):
        """Get random doujinshi by the language.
        Languages are chinese, japanese, english. You can either directly use languages or use their aliases"""
        pass

    @commands.command(aliases = ['par'], usage="<parody name> <chinese|english|japenese>")
    async def parody(self, ctx, name, language):
        """Get random doujin by the name and language you provide"""
        pass


def setup(bot):
    bot.add_cog(doujinshi(bot))