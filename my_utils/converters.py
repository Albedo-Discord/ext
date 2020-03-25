from discord.ext import commands
import discord

class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
        else:
            return m.id


class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = argument

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret

class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        ban_list = await ctx.guild.bans()
        try:
            member_id = int(argument, base=10)
            entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
        except ValueError:
            entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument("Not a valid previously-banned member.")
        return entity

class ComCog(commands.Converter):
    async def convert(self, ctx, argument):
        if argument.lower() == "all":   
            dargument = "all"
        else:   
            dargument = ctx.bot.get_command(argument.lower())
            if not dargument:
                await ctx.send(f'No command {argument} found!')
                raise commands.errors.CheckFailure("Just another day of the survey corps")
            
            if dargument.root_parent:
                dargument = dargument.root_parent
        
        return (argument, dargument)