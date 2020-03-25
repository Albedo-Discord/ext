import os
import logging

import discord
from discord.ext import commands

from my_utils.default import all_cases, get
from my_utils.data import Bot, HelpCommand
from my_utils.guildstate import state_instance

config = get("config.json")

command_prefix = all_cases(config.prefix)

def get_prefix(bot, message):
    gstate = state_instance.get_state(message.guild.id)
    return command_prefix + all_cases(gstate.bot_prefix) 

bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=False,
    command_attrs=dict(hidden=True),
    help_command=HelpCommand()
)

@bot.check
def check_availabilty(ctx):
    cmd = ctx.command
    
    state = state_instance.get_state(ctx.guild.id)
    if cmd.root_parent:
        cmd = cmd.root_parent
    
    if str(cmd) == "enable" or str(cmd) == "disable" or str(cmd) == "reboot":
        return True
    
    al = state.get_var("all")
    comd = state.get_var(str(cmd))
    tc = ctx.channel
    rol = ctx.author.top_role
    
    if str(tc) in al.channels:
        return comd.forced
    if str(rol) in al.roles:
        return comd.forced
    if str(tc) in comd.channels:
        return False
    if str(rol) in comd.roles:
        return False

    availability = comd.server_wide if al.server_wide else comd.forced
    return availability

for filename in os.listdir('cogs'):                                   #Loads all the cogs                  
    if filename.endswith('.py') and filename not in config.off_by_default:
        bot.load_extension(f'cogs.{filename[:-3]}')

def run():
    bot.run(config.token[1])
    

#logging setup
formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")


# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='albedo.log', encoding='utf-8', mode='w')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("albedo.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

run()
