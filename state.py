import pickle
import time
import os.path
from collections import defaultdict

from commands import bot_commands

class State:
    def __init__(self, server_id, client):
        self.server_id = server_id
        self.client = client
        self.save_folder = os.path.join("save", str(server_id))
        if not os.path.isdir(self.save_folder):
            os.mkdir(self.save_folder)
            self.users = {}
            self.npcs = []
            self.channels = defaultdict(set)
            self.channels["private-initiatives"] = dict()
            self.save()
        else:
            self.load()
            self.channels["rolling-initiative"] = set()
            if isinstance(self.channels["automatic"], list):
                self.channels["automatic"] = set(self.channels["automatic"])
            if not isinstance(self.channels, defaultdict):
                temp = self.channels
                self.channels = defaultdict(set)
                self.channels.update(temp)

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
        print("Deprecated")
        lower = message.lower()
        return None, message

    async def find_character(self, context, message, error_on_not_found=True):
        lower = message.lower() + " "
        if lower.startswith("me "):
            character = self.users.get(str(context.author))
            if character:
                return character, message[3:]
            await context.channel.send("You do not yet have a character. Create one with `,create-pc character-name`.")
            return None, message
        for character in self.users.values():
            if lower.startswith(character.name.lower() + " "):
                return character, message[len(character.name) + 1:]
            elif lower.startswith(character.alias.lower() + " "):
                return character, message[len(character.alias) + 1:]
        for npc in self.npcs:
            if lower.startswith(npc.name.lower() + " "):
                return npc, message[len(npc.name) + 1:]
            elif lower.startswith(npc.alias.lower() + " "):
                return npc, message[len(npc.alias) + 1:]
        if message.startswith("<@") and len(context.mentions) > 0:
            if len(context.mentions) == 1:
                character = self.users.get(str(context.mentions[0]))
                if character:
                    return character, message[message.index(">") + 2:]
            else:
                id = message[2:message.index(">")]
                if id.startswith("!"):
                    id = id[1:]
                id = int(id)
                for user in context.mentions:
                    if user.id == id:
                        character = self.users.get(str(user))
                        if character:
                            return character, message[message.index(">") + 2:]

        if error_on_not_found:
            await context.channel.send("That character does not appear to exist.")
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
