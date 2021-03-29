import discord
from discord import user
from utils import confirm, ask
import random

NOT_VALID = 0
SCORE = 1
ROLL = 2

CHARACTER = 5
AUTHOR = 6

async def private_channel(state, channel: discord.TextChannel):
    guild = channel.guild
    if channel.id in state.channels["private-initiatives"]:
        return guild.get_channel(state.channels["private-initiatives"][channel.id])
    new_channel = await channel.guild.create_text_channel(name=channel.name + "-private", category=channel.category, position=channel.position + 1)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
    }
    await new_channel.edit(overwrites=overwrites)
    await new_channel.edit(position=channel.position + 1)
    state.channels["private-initiatives"][channel.id] = new_channel.id
    state.save()
    return new_channel

class InitiativeState:
    def __init__(self, state, context, me) -> None:
        self.game_state = state
        self.initiatives = {}
        self.privacies = {}
        self.order = []
        self.current_index = None
        self.current_public_index = None
        self.current_character = None
        self.channel = context.channel
        self.user = context.author
        self.me = me
        self.set_modifier_warning = False

    async def setup(self):
        self.message = await self.channel.send(self.to_message(private=False))
        # self.messages = {self.message: False}
        self.private_channel = await private_channel(self.game_state, self.channel)
        guild = self.private_channel.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            self.user: discord.PermissionOverwrite(read_messages=True),
        }
        await self.private_channel.edit(overwrites=overwrites)
        self.private_message = await self.private_channel.send(self.to_message(private=True))
        self.messages = {self.message: False, self.private_message: True}

    def to_message(self, private):
        this = "▶️"
        not_this = "⬛"
        text = "**Initiative**"
        for i, name in enumerate(self.order):
            if not private and self.privacies[name]:
                continue
            text += "\n"
            if (private and i == self.current_index) or (not private and i == self.current_public_index):
                text += this
            else:
                text += not_this
            text += f" {self.initiatives[name]}: {name}"
        if self.set_modifier_warning:
            text += "\nSet your initiative modifier using `,init-modifier me $value` before using the 🎲 react to roll."
        return text

    async def update(self):
        for message, privacy in self.messages.items():
            await message.edit(content=self.to_message(private=privacy))

    async def start(self):
        if self.order:
            self.current_index = 0
            self.update_currents()
            await self.update()
            return True
        return False

    def update_currents(self):
        self.current_character = self.order[self.current_index]
        self.current_public_index = self.current_index
        if self.privacies[self.order[self.current_index]]:
            while self.privacies[self.order[self.current_public_index]]:
                self.current_public_index += 1
                self.current_public_index %= len(self.order)

    async def backward(self):
        self.current_index -= 1
        self.current_index += len(self.order)
        self.current_index %= len(self.order)
        self.update_currents()
        await self.update()

    async def forward(self):
        self.current_index += 1
        self.current_index %= len(self.order)
        self.update_currents()
        await self.update()

    async def fast_backward(self):
        self.current_index = 0
        self.update_currents()
        await self.update()

    async def add_character(self, name, initiative, private):
        self.initiatives[name] = initiative
        self.privacies[name] = private
        self.order.append(name)        
        self.order = sorted(self.order, key=lambda name: self.initiatives[name], reverse=True)
        if self.current_character is not None:
            self.current_index = self.order.index(self.current_character)
            self.update_currents()
        await self.update()

    async def change_initiative(self, name, initiative):
        self.initiatives[name] = initiative
        self.order = sorted(self.order, key=lambda name: self.initiatives[name], reverse=True)
        if self.current_character is not None:
            self.current_index = self.order.index(self.current_character)
            self.update_currents()
        await self.update()

    async def add_full(self, state, channel, author, command, value, name, loud, private):
        if command == ROLL:
            initiative = random.randint(1, 20) 
            roll_msg = await channel.send(f"Rolled {initiative}, {'+' if value >= 0 else ''}{value} = {initiative + value}, for {name}.")
            initiative += value
        elif command == SCORE:
            initiative = value
            roll_msg = None
        else:
            return False            

        if name in self.initiatives:
            question  = f"{name} is already in the initiative order in this channel with initiative {self.initiatives[name]}. Replace this initiative? "
            if await ask(state, channel, question, author):
                await self.change_initiative(name, initiative)
                
        else:
            await self.add_character(name, initiative, private)

        if roll_msg is not None:
            await roll_msg.delete(delay=20)
        return True
    
    async def add_modifier_warning(self):
        self.set_modifier_warning = True
        await self.update()

    async def maybe_end(self, state, reaction, user):
        if await confirm(state, reaction.message, user):
            for message in self.messages:
                await message.clear_reactions()
            for message, private in self.messages.items():
                if private:
                    await message.delete()
                else:
                    await message.channel.send("Done with initiative.")
            for message in self.messages:
                state.channels["rolling-initiative"].discard(message.channel.id)
            guild = self.private_channel.guild
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
            }
            await self.private_channel.edit(overwrites=overwrites)
            del channel_initiatives[self.channel.id]
            del privacies[self.channel.id]
            return True
        else:
            await reaction.remove(user)

    async def run_auto_initiative(self, state, context):
        for message in self.messages:
            state.channels["rolling-initiative"].add(message.channel.id)
        blank = "⬛"
        dice = "🎲"
        cross = "❎"
        start = "▶️"
        possibles_rolling = [start, dice, cross]
        for message in self.messages:
            await message.add_reaction(dice)
            await message.add_reaction(start)
            await message.add_reaction(blank)
            await message.add_reaction(cross)

        def check(reaction, user):
            return reaction.emoji in possibles_rolling and user != self.me and reaction.message in self.messages

        while True:
            reaction, user = await state.client.wait_for('reaction_add', check=check)
            if reaction.emoji == dice:
                character = state.users.get(str(user))
                if character is not None and character.init_modifier is not None:
                    await self.add_full(state, context.channel, user, ROLL, character.init_modifier, character.name, True, False)
                else:
                    await self.add_modifier_warning()
                    await reaction.remove(user)
            elif user == self.user:
                if reaction.emoji == start:
                    if await self.start():
                        for message in self.messages:
                            await message.clear_reaction(start)
                            await message.clear_reaction(blank)
                            await message.clear_reaction(cross)
                        for message in self.messages:
                            state.channels["rolling-initiative"].discard(message.channel.id)
                        return True
                    else:
                        await reaction.remove(user)
                elif reaction.emoji == cross:
                    if await self.maybe_end(state, reaction, user):
                        return False
            else:
                await reaction.remove(user)

    async def run_tracker(self, state, context):
        left = "⬅️"
        fast_left = "⏮️"
        right = "➡️"
        blank = "⬛"
        dice = "🎲"
        cross = "❎"

        for message in self.messages:
            await message.add_reaction(fast_left)
            await message.add_reaction(left)
            await message.add_reaction(right)
            await message.add_reaction(blank)
            await message.add_reaction(cross)

                    
        possibles_playing = [left, right, dice, cross, fast_left]
        
        def check(reaction, user):
            return reaction.emoji in possibles_playing and user != self.me and reaction.message in self.messages

        while True:
            reaction, user = await state.client.wait_for('reaction_add', check=check)
            if reaction.emoji == dice:
                character = state.users.get(str(user))
                if character is not None and character.init_modifier is not None:
                    await self.add_full(state, reaction.message.channel, user, ROLL, character.init_modifier, character.name, True, self.messages[reaction.message])
                else:
                    await self.add_modifier_warning()
                    await reaction.remove(user)
            elif user == context.author:
                if reaction.emoji == left:
                    await self.backward()
                    await reaction.remove(user)
                elif reaction.emoji == right:
                    await self.forward()
                    await reaction.remove(user)
                elif reaction.emoji == fast_left:
                    await self.fast_backward()
                    await reaction.remove(user)
                elif reaction.emoji == cross:
                    if await self.maybe_end(state, reaction, user):
                        return False
            else:
                await reaction.remove(user)


channel_initiatives = {}
privacies = {}

async def initiative_start(state, context, args):
    if context.channel.id in channel_initiatives:
        await context.channel.send("This channel is already in initiative.")
        return
    init_state = InitiativeState(state, context, state.client.user)
    await init_state.setup()
    for message, privacy in init_state.messages.items():
        channel_initiatives[message.channel.id] = init_state
        privacies[message.channel.id] = privacy
    
    if await init_state.run_auto_initiative(state, context):
        await init_state.run_tracker(state, context)


def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def initiative_parse(args, character: bool, modifier):
    # modifier is the character's modifier if we're given one and the author's if not
    if args:
        words = args.split(" ")
    else:
        words = []
    try:
        if character:
            if len(words) == 0 and modifier is not None:
                return ROLL, modifier, CHARACTER
            elif len(words) == 0 and modifier is None:
                return NOT_VALID, None, None
            elif len(words) == 1 and args == "roll" and modifier is not None:
                return ROLL, modifier, CHARACTER
            elif len(words) == 1:
                return SCORE, int(words[0]), CHARACTER
            elif len(words) == 2 and words[0] == "roll":
                return ROLL, int(words[1]), CHARACTER
            else:
                return NOT_VALID, None, None
        else:
            if len(words) == 0 and modifier is not None:
                return ROLL, modifier, AUTHOR
            elif len(words) == 0:
                return NOT_VALID, None, None
            elif len(words) == 1 and args == "roll" and modifier is not None:
                return ROLL, modifier, AUTHOR
            elif len(words) == 1:
                return SCORE, int(args), AUTHOR
            elif words[-2] == "roll":
                if len(words) == 2:
                    name = AUTHOR
                else:
                    name = " ".join(words[:-2])
                return ROLL, int(words[-1]), name
            else:
                return SCORE, int(words[-1]), " ".join(words[:-1])
    except ValueError:
        return NOT_VALID, None, None
            

async def initiative_add(state, context, character, args, loud):
    if character is None:
        author_character = state.users.get(str(context.author))
        if author_character is not None:
            modifier = author_character.init_modifier
        else:
            modifier = None
    else:
        modifier = character.init_modifier
    command, value, name = initiative_parse(args, character is not None, modifier)

    if name == AUTHOR:
        if author_character is None:
            if loud:
                await context.channel.send("That does not look like an initiative.")
            return
        else:
            name = author_character.name
    elif name == CHARACTER:
        name = character.name

    init_state = channel_initiatives[context.channel.id]
    success = await init_state.add_full(state, context.channel, context.author, command, value, name, loud, privacies[context.channel.id])
    if success:    
        await context.delete()
    else:
        if loud:
            await context.channel.send("That does not look like an initiative; perhaps you need to set your initiative modifier with `,init-modifier`?")
    return success


async def initiative_add_loud(state, context, character, args):
    if context.channel.id in channel_initiatives:
        await initiative_add(state, context, character, args, True)
    else:
        await context.channel.send("This channel is not currently in initiative.")

async def initiative_add_quiet(state, context, character, args):
    return await initiative_add(state, context, character, args, False)

async def initiative_modifier(state, context, character, init_modifier):
    try:
        init_modifier = int(init_modifier)
    except ValueError:
        if character.init_modifier is not None:
            current = f"{'+' if character.init_modifier >= 0 else ''}{character.init_modifier}"
        else:
            current = "not set"
        await context.channel.send(f"Your initiative modifier is currently {current}.")
        return
    character.init_modifier = init_modifier
    state.save()
    await state.log(context, f"Set {character.name}'s initiative modifier to {init_modifier}.")
