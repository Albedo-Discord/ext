from my_utils.dataIO import recover_states
from collections import namedtuple
class _states:
    ''' contains the states for an instance of bot '''
    def __init__(self):
        self.states = {}

    def get_state(self, guild_id):
        """Gets the state for `guild`, creating it if it does not exist."""
        if guild_id in self.states:
            return self.states[guild_id]
        else:
            self.states[guild_id] = GuildState()
            return self.states[guild_id]

    def delete_state(self, guild_id):
        """Delete the state of a guild"""
        del self.states[guild_id]
        
    def all_states(self):
        return self.states

class GuildState:
    ''' This class manages per-guild states '''
    
    def __init__(self):
        self.command = namedtuple("command", ["server_wide", "channels", "roles", "forced"])
        self.bot_prefix = "/"
        self.mute_exists = False
        self.debugmode = False
        self.all = self.command(True, set(),set(), False)
        self.desc = self.command(True, set(), set(), False)
        self.ping = self.command(True, set(), set(), False)

    def get_var(self, variable):
        try:    
            var = getattr(self, variable)
            return var
        except:
            return self.command(True, set(),set(), False)
    
    def get_commands(self):
        cmds = dir(self)
        not_cmds = ("command", "bot_prefix", "mute_exists", "get_var", "get_commands", "set_var", "debugmode")
        return [cmd for cmd in cmds if cmd not in not_cmds and not cmd.startswith("__")]

    def set_var(self, variable, value):
        setattr(self, variable, value)
        return

state_instance = _states()
recover_states(state_instance)