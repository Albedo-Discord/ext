import discord
import random
from discord.ext import commands
from my_utils import default as d


def _exists(a_id):
    bet = d.retrieve("bet.json")
    if a_id in bet["id"]:
        return True
    return False


def _initalise(user_id, force_initialise):
    if _exists(user_id) is False or force_initialise is True:
        bet = d.retrieve("bet.json")    
        bet["id"] += [user_id]
        bet["wallet"] += [500]
        bet["bank"] += [1000]
        d.save("bet.json", bet)


def _get_index(user):
    bet = d.retrieve("bet.json")
    return bet["id"].index(user)


def _steal():
    chance = random.randrange(1, 100)
    if chance < 45:
        return True
    else:
        return False


def _get_dollars(index, location):
    bet = d.retrieve("bet.json")
    return bet[location][index]


def _add_dollars(index, amount, location):
    bet = d.retrieve("bet.json")
    bet[location][index] += amount
    d.save("bet.json", bet)


def _remove_dollars(index, amount, location):
    bet = d.retrieve("bet.json")
    bet[location][index] -= amount
    d.save("bet.json", bet)


#def _check_errors(ctx):
    #try 


class currency(commands.Cog):
    """Commands related to our currency system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.ind = None
        self.member_ind = None

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def flip(self, ctx, amount: int, guess: str):
        """Flips a coin. If your guess is correct, you win the amount you bet. Or you lose them"""
        
        _initalise(str(ctx.author.id), False)
        sliced_author = str(ctx.author)[:-5]
        self.ind = _get_index(str(ctx.author.id))
        balance = _get_dollars(self.ind, "wallet")
        guesses = ('heads', 'tails')
        result = random.choice(guesses)
        guess = guess.lower()
        if guess not in guesses:
            await ctx.send("Invalid guess.")
            raise commands.CommandError("invalid guess")

        elif amount <= 0:
            await ctx.send("clearly your pp and bren smol")
            raise commands.CommandError("invalid amount")
        
        elif balance < amount: 
            await ctx.send(f"You don't have that much money.\nYour balance is ${balance}.")
            raise commands.CommandError("balance < amount")
            
        elif result == guess:
            _add_dollars(self.ind, amount, "wallet")
            embed = discord.Embed(title=f"{sliced_author}'s gambling game",description = "You won!", timestamp = ctx.message.created_at)
            
            embed.add_field(name=f"You tossed a coin.\nIt was {result}!", value = f"```diff\n+You got ${amount}\n```\nYour balance: ${_get_dollars(self.ind, 'wallet')}")
            await ctx.send(embed=embed)
            
        else:
            _remove_dollars(self.ind, amount, "wallet")
            embed = discord.Embed(title=f"{sliced_author}'s gambling game",timestamp = ctx.message.created_at, description = "You lost.")

            embed.add_field(name=f"You tossed a coin.\nIt was {result}.", value = f"```diff\n-You lost ${amount}\n```\nYour balance: ${_get_dollars(self.ind, 'wallet')}")
            await ctx.send(embed=embed)
            
    @commands.command(aliases = ["bal"])
    async def balance(self, ctx, member: discord.Member = None):
        """Shows the balance of a user, if mentioned or your balance."""
        
        if member == None:
            member = ctx.author
        _initalise(str(member.id), False)            
        sliced_author = str(member)[:-5]
        self.ind = _get_index(str(member.id))
        embed = discord.Embed(title=f"{sliced_author}'s profile",timestamp = ctx.message.created_at, description = f"Wallet: ${_get_dollars(self.ind, 'wallet')}\nBank: ${_get_dollars(self.ind, 'bank')}")  
        await ctx.send(embed=embed)
        
    @commands.command(aliases = ["dep"])
    async def deposit(self, ctx, amount):
        """Deposits the amount from your wallet to your bank."""

        _initalise(str(ctx.author.id), False)
        self.ind = _get_index(str(ctx.author.id))
        if str(amount) == "all":
            if _get_dollars(self.ind, 'wallet') != 0:
                await ctx.send(f"Deposited ${_get_dollars(self.ind, 'wallet')}.")
                _add_dollars(self.ind, _get_dollars(self.ind, 'wallet'), "bank")
                _remove_dollars(self.ind, _get_dollars(self.ind, 'wallet'), 'wallet')
            else:
                await ctx.send("You don't have any money to deposit, you dumb schmuck")
            
        elif int(amount) <= 0 or int(amount) > _get_dollars(self.ind, 'wallet'):
            await ctx.send("Ah, vary smol bren")
        else:
            self.ind = _get_index(str(ctx.author.id))
            _remove_dollars(self.ind, int(amount), "wallet")
            _add_dollars(self.ind, int(amount), "bank")
            return await ctx.send(f"Deposited ${int(amount)}.")

    @commands.command(aliases = ["with"])
    async def withdraw(self, ctx, amount):
        """Withdraws the amount from your bank to your wallet."""

        _initalise(str(ctx.author.id), False)
        self.ind = _get_index(str(ctx.author.id))
        if str(amount) == "all":
            if _get_dollars(self.ind, 'bank') != 0:
                await ctx.send(f"Withdrew ${_get_dollars(self.ind, 'bank')}.")
                _add_dollars(self.ind, _get_dollars(self.ind, 'bank'), "wallet")
                _remove_dollars(self.ind, _get_dollars(self.ind, 'bank'), "bank")
            else:
                await ctx.send("You don't have any money to withdraw, you dumb schmuck.")

        elif int(amount) <= 0 or int(amount) > _get_dollars(self.ind, 'bank'):
            await ctx.send("why are u tan? frickun' invalid amount")
        else:
            self.ind = _get_index(str(ctx.author.id))
            _remove_dollars(self.ind, int(amount), "bank")
            _add_dollars(self.ind, int(amount), "wallet")
            return await ctx.send(f"Withdrew ${int(amount)}.")

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def beg(self, ctx):
        """Short on coins. Just become what you really are! A beggar!"""

        _initalise(str(ctx.author.id), False)
        msg_list = [
            "Your mom donated you ",
            "Thanos donated you ",
            "Blon de man donated you ",
            "Tan de gae donated you ",
            "A Random stranger donated you ",
            "Me me me donated you ",
            "Aqua donated you ",
            "God donated you ",
            "A Phuccing degenarate donated you "
        ]
        self.ind = _get_index(str(ctx.author.id))
        beg_amount = random.randrange(1,70)
        _add_dollars(self.ind, beg_amount, "wallet")
        return await ctx.send(f"{random.choice(msg_list)}${beg_amount}.")

    # @beg.error
    # async def beg_error(self, ctx, error):
    #     embed = discord.Embed(title="Don't be so greedy", description = "**Consider it a blessing to be able to beg, try again in {:.2f}s**".format(error.retry_after), timestamp = ctx.message.created_at)
    #     if isinstance(error, commands.CommandOnCooldown): 
    #         await ctx.send(embed=embed)
    #     else:
    #         raise error

    @commands.command()
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def steal(self, ctx, member: discord.Member):
        """Time to steal! If you get lucky, you get a huge payload."""

        _initalise(str(ctx.author.id), False)
        _initalise(str(member.id), False)
        self.ind = _get_index(str(ctx.author.id))
        self.member_ind = _get_index(str(member.id))
        get_member_wallet = _get_dollars(self.member_ind, 'wallet')
        steal_amount_probability = {"1" : 3, "0.75" : 10, "0.50" : 17, "0.25" : 30, "0.10" : 40}
        prob = random.randint(1, 100)
        if prob <= steal_amount_probability["1"]:
            steal_amount = 1
        elif prob <= (steal_amount_probability["0.75"] + steal_amount_probability["1"]):
            steal_amount = 0.75
        elif prob <= (steal_amount_probability["0.50"] + steal_amount_probability["0.75"] + steal_amount_probability["1"]):
            steal_amount = 0.50
        elif prob <= (steal_amount_probability["0.25"] + steal_amount_probability["0.50"] + steal_amount_probability["0.75"] + steal_amount_probability["1"]):
            steal_amount = 0.25
        elif prob <= (steal_amount_probability["0.10"] + steal_amount_probability["0.25"] + steal_amount_probability["0.50"] + steal_amount_probability["0.75"] + steal_amount_probability["1"]):
            steal_amount = 0.10

        if _get_dollars(self.ind, 'wallet') >= 1000:
            if _get_dollars(self.member_ind, 'wallet') >= 1000:

                if _steal() == True:
                    _remove_dollars(self.member_ind, int(get_member_wallet*steal_amount), 'wallet')
                    _add_dollars(self.ind, int(get_member_wallet*steal_amount), 'wallet')
                    await ctx.send(f"You stole ${int(get_member_wallet*steal_amount)} from {member}.")

                elif _steal() == False:
                    _remove_dollars(self.ind, 1000, 'wallet')
                    _add_dollars(self.member_ind, 1000, 'wallet')
                    await ctx.send(f"You were caught stealing {member}\nYou paid them $1000.")
                    
            else:
                await ctx.send(f"{member} is too poor, leave them alone and don't be a cunt.")
        else:
            await ctx.send(f"You're too poor, very sed.")
        
    # @steal.error
    # async def steal_error(self, ctx, error):
    #     embed = discord.Embed(title="Take a break bruh", description = f"**Don't be so hasty, succes takes time .Try again in {int(error.retry_after/60)}m and {str(error.retry_after/60)[2:4]}s**", timestamp = ctx.message.created_at)
    #     if isinstance(error, commands.CommandOnCooldown): 
    #         await ctx.send(embed=embed)
    #     else:
    #         raise error


def setup(bot):
    bot.add_cog(currency(bot))