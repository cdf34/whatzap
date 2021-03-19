import pickle
import time
import os.path
from collections import defaultdict

from commands import bot_commands

class State:
    def __init__(self, server_id):
        self.server_id = server_id
        self.save_folder = os.path.join("save", str(server_id))
        if not os.path.isdir(self.save_folder):
            os.mkdir(self.save_folder)
            self.users = {}
            self.npcs = []
            self.channels = {}
            self.save()
        else:
            self.load()
        self.update_commands()
        
    def load(self):
        with open(os.path.join(self.save_folder, "users.p"), "rb") as f:
            self.users = pickle.load(f)
        with open(os.path.join(self.save_folder, "npcs.p"), "rb") as f:
            self.npcs = pickle.load(f)
        with open(os.path.join(self.save_folder, "channels.p"), "rb") as f:
            self.channels = pickle.load(f)
            if isinstance(self.channels, list):
                self.channels = defaultdict(set)

    def save(self):
        with open(os.path.join(self.save_folder, "users.p"), "wb") as f:
            pickle.dump(self.users, f)
        with open(os.path.join(self.save_folder, "npcs.p"), "wb") as f:
            pickle.dump(self.npcs, f)
        with open(os.path.join(self.save_folder, "channels.p"), "wb") as f:
            pickle.dump(self.channels, f)

    def find_npc(self, message):
        lower = message.lower()
        for npc in self.npcs:
            if lower.startswith(npc.name.lower()):
                return npc, message[len(npc.name) + 1:]
            elif lower.startswith(npc.alias.lower()):
                return npc, message[len(npc.alias) + 1:]
        return None, message

    def find_character(self, message):
        npc, message = self.find_npc(message)
        if npc:
            return npc, message
        for character in self.users.values():
            lower = message.lower()
            if lower.startswith(character.name.lower()):
                return character, message[len(character.name) + 1:]
            elif lower.startswith(character.alias.lower()):
                return character, message[len(character.alias) + 1:]
        return None, message

    async def log(self, message, text_to_log):
        with open(os.path.join(self.save_folder, "log.txt"), "a") as f:
            f.write(time.strftime("%a, %d %b %Y %H:%M:%S: ", time.localtime()))
            f.write(f"{str(message.author)}: {text_to_log}\n")
        await message.channel.send(text_to_log)

    def update_commands(self):
        commands = {}
        commands.update(bot_commands)
        for npc_object in self.npcs:
            commands["," + npc_object.name.lower()] = npc_object.send_as_command
            commands["," + npc_object.alias.lower()] = npc_object.send_as_command
        for pc_object in self.users.values():
            commands["," + pc_object.name.lower()] = pc_object.send_as_command
            commands["," + pc_object.alias.lower()] = pc_object.send_as_command
        self.commands = commands

    async def check_no_confusion(self, context, new_command, exceptions=None):
        if exceptions is None:
            exceptions = []
        else:
            exceptions = ["," + e.lower() for e in exceptions]
        commands = self.commands
        lower = "," + new_command.lower()
        for c in commands:
            if c in exceptions:
                continue
            if c.startswith(lower) or lower.startswith(c):
                if c in bot_commands:
                    await context.channel.send(f"Unfortunately {new_command} could be confused with {c} so is not valid for whatever you're trying to do.")
                else:
                    await context.channel.send(f"Unfortunately {new_command.lower()} could be confused with {c[1:]} so is not valid for whatever you're trying to do.")
                return False
        return True
