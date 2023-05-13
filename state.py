import pickle
import discord
import time
import os.path
from collections import defaultdict

from commands import bot_commands


class State:
    def __init__(self, server_id, client):
        self.server_id = server_id
        self.client = client
        self.save_folder = os.path.join("save", str(server_id))

        self.users = {}
        self.npcs = []
        self.channels = defaultdict(set)
        self.channels["private-initiatives"] = dict()

        self.event = {"time": None, "reminders": []}

        if not os.path.isdir(self.save_folder):
            os.mkdir(self.save_folder)
            self.save()
        else:
            self.load()
            if isinstance(self.channels["automatic"], list):
                self.channels["automatic"] = set(self.channels["automatic"])
            if not isinstance(self.channels, defaultdict):
                temp = self.channels
                self.channels = defaultdict(set)
                self.channels.update(temp)

        self.channels["rolling-initiative"] = set()
        self.update_commands()
        
    def _load_if_exists(self, pname, attr):
        try:
            with open(os.path.join(self.save_folder, pname), "rb") as f:
                setattr(self, attr, pickle.load(f))
        except FileNotFoundError:
            pass
    
    def load(self):
        self._load_if_exists("users.p", "users")
        self._load_if_exists("npcs.p", "npcs")
        self._load_if_exists("channels.p", "channels")
        self._load_if_exists("event.p", "event")

    def save(self):
        with open(os.path.join(self.save_folder, "users.p"), "wb") as f:
            pickle.dump(self.users, f)
        with open(os.path.join(self.save_folder, "npcs.p"), "wb") as f:
            pickle.dump(self.npcs, f)
        with open(os.path.join(self.save_folder, "channels.p"), "wb") as f:
            pickle.dump(self.channels, f)
        with open(os.path.join(self.save_folder, "event.p"), "wb") as f:
            pickle.dump(self.event, f)

    def find_npc(self, message):
        print("Deprecated")
        lower = message.lower()
        return None, message

    async def fix_names_ids(self):
        server_obj = await self.client.fetch_guild(self.server_id)
        members_to_id = {}
        async for member in server_obj.fetch_members(limit=None):
            members_to_id[str(member)] = member.id
        strusers = [x for x in self.users if isinstance(x, str)]
        for namedisc in strusers:
            if namedisc in members_to_id:
                self.users[members_to_id[namedisc]] = self.users[namedisc]
            else:
                print("no", namedisc, self.server_id)

    async def find_character(self, context, message, error_on_not_found=True):
        lower = message.lower() + " "
        if lower.startswith("me "):
            character = self.users.get(context.author.id)
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
                character = self.users.get(context.mentions[0].id)
                if character:
                    return character, message[message.index(">") + 2:]
            else:
                id = message[2:message.index(">")]
                if id.startswith("!"):
                    id = id[1:]
                id = int(id)
                for user in context.mentions:
                    if user.id == id:
                        character = self.users.get(user.id)
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
