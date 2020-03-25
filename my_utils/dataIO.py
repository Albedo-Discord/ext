import json


def change_value(file: str, value: str, changeto: str):
    try:
        with open(file, "r") as jsonFile:
            data = json.load(jsonFile)
    except FileNotFoundError:
        raise FileNotFoundError("The file you tried to get does not exist...")

    data[value] = changeto
    with open(file, "w") as jsonFile:
        json.dump(data, jsonFile, indent=2)


def append_value(file: str, value: str, addition: str):
    try:
        with open(file, "r") as jsonFile:
            data = json.load(jsonFile)
    except FileNotFoundError:
        raise FileNotFoundError("The file you tried to get does not exist...")

    data[value].append(addition)
    with open(file, "w") as jsonFile:
        json.dump(data, jsonFile, indent=2)

def encode(obj):
    try:
        dic = obj.__dict__
    except AttributeError:
        if isinstance(obj, set):
            dic = list(obj)
        else:
            dic = ["server_wide", "channels", "roles"]
    return dic

def backup_states(state_instance):
    D = json.dumps(state_instance, default=encode)
    with open('json/states.json', "w") as f:
        json.dump(D, f)

def recover_states(state_instance):
    try:    
        with open(f"json/states.json") as f:
                D = json.load(f)
    except:
        return

    D = json.loads(D)
    for guild_id, settings in D.get("states").items():
        guild = state_instance.get_state(int(guild_id))
        for setting, value in settings.items():
            if setting == "bot_prefix" or setting == "mute_exists":    
                guild.set_var(setting, value)
            elif setting != "command" and setting != "debugmode":
                value=guild.command(value[0], set(value[1]), set(value[2]), value[3])
                guild.set_var(setting, value)
            else:
                pass
