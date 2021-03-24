from utils import confirm, ask
import random

NOT_VALID = 0
SCORE = 1
ROLL = 2

CHARACTER = 5
AUTHOR = 6

class InitiativeState:
    def __init__(self, context) -> None:
        self.initiatives = {}
        self.order = []
        self.current_index = None
        self.current_character = None
        self.channel = context.channel
        self.set_modifier_warning = False

    async def setup(self):
        self.message = await self.channel.send(self.to_message())

    def to_message(self):
        this = "▶️"
        not_this = "⬛"
        text = "**Initiative**"
        for i, name in enumerate(self.order):
            text += "\n"
            if i == self.current_index:
                text += this
            else:
                text += not_this
            text += f" {self.initiatives[name]}: {name}"
        if self.set_modifier_warning:
            text += "\nSet your initiative modifier using `,init-modifier me $value` before using the 🎲 react to roll."
        return text

    async def update(self):
        await self.message.edit(content=self.to_message())

    async def start(self):
        if self.order:
            self.current_index = 0
            self.current_character = self.order[self.current_index]
            await self.update()
            return True
        return False

    async def backward(self):
        self.current_index -= 1
        self.current_index += len(self.order)
        self.current_index %= len(self.order)
        self.current_character = self.order[self.current_index]
        await self.update()

    async def forward(self):
        self.current_index += 1
        self.current_index %= len(self.order)
        self.current_character = self.order[self.current_index]
        await self.update()

    async def fast_backward(self):
        self.current_index = 0
        self.current_character = self.order[self.current_index]
        await self.update()

    async def add_character(self, name, initiative):
        self.initiatives[name] = initiative
        self.order.append(name)        
        self.order = sorted(self.order, key=lambda name: self.initiatives[name], reverse=True)
        if self.current_character is not None:
            self.current_index = self.order.index(self.current_character)
        await self.update()

    async def change_initiative(self, name, initiative):
        self.initiatives[name] = initiative
        self.order = sorted(self.order, key=lambda name: self.initiatives[name], reverse=True)
        if self.current_character is not None:
            self.current_index = self.order.index(self.current_character)
        await self.update()

    async def add_full(self, state, channel, author, command, value, name, loud):
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
            question  = f"You are already in the initiative order in this channel with initiative {self.initiatives[name]}. Replace this initiative? "
            if await ask(state, channel, question, author):
                await self.change_initiative(name, initiative)
                
        else:
            await self.add_character(name, initiative)

        if roll_msg is not None:
            await roll_msg.delete(delay=20)
        return True
    
    async def add_modifier_warning(self):
        self.set_modifier_warning = True
        await self.update()



channel_initiatives = {}


async def initiative_start(state, context, args):
    if context.channel.id in channel_initiatives:
        await context.channel.send("This channel is already in initiative.")
        return
    me = state.client.user
    init_state = InitiativeState(context)
    await init_state.setup()
    channel_initiatives[context.channel.id] = init_state
    state.channels["rolling-initiative"].add(context.channel.id)
    left = "⬅️"
    fast_left = "⏮️"
    right = "➡️"
    blank = "⬛"
    dice = "🎲"
    cross = "❎"
    start = "▶️"
    possibles_rolling = [start, dice, cross]
    await init_state.message.add_reaction(dice)
    await init_state.message.add_reaction(start)
    await init_state.message.add_reaction(blank)
    await init_state.message.add_reaction(cross)

    def check(reaction, user):
        return reaction.emoji in possibles_rolling and user != me and reaction.message == init_state.message

    while True:
        reaction, user = await state.client.wait_for('reaction_add', check=check)
        if reaction.emoji == dice:
            character = state.users.get(str(user))
            if character is not None and character.init_modifier is not None:
                await init_state.add_full(state, context.channel, user, ROLL, character.init_modifier, character.name, True)
            else:
                await init_state.add_modifier_warning()
                await init_state.message.remove_reaction(dice, user)
        elif user == context.author:
            if reaction.emoji == start:
                if await init_state.start():
                    await init_state.message.clear_reaction(start)
                    await init_state.message.clear_reaction(blank)
                    await init_state.message.clear_reaction(cross)
                    break
                else:
                    await init_state.message.remove_reaction(start, user)
            elif reaction.emoji == cross:
                if await confirm(state, init_state.message, user):
                    await init_state.message.clear_reactions()

                    await context.channel.send("Done with initiative.")
                    state.channels["rolling-initiative"].remove(context.channel.id)
                    del channel_initiatives[context.channel.id]
                    return
                else:
                    await init_state.message.remove_reaction(cross, user)
        else:
            await init_state.message.remove_reaction(reaction.emoji, user)

    state.channels["rolling-initiative"].remove(context.channel.id)

    await init_state.message.add_reaction(fast_left)
    await init_state.message.add_reaction(left)
    await init_state.message.add_reaction(right)
    await init_state.message.add_reaction(blank)
    await init_state.message.add_reaction(cross)

                
    possibles_playing = [left, right, dice, cross, fast_left]
    
    def check(reaction, user):
        return reaction.emoji in possibles_playing and user != me and reaction.message == init_state.message

    while True:
        reaction, user = await state.client.wait_for('reaction_add', check=check)
        if reaction.emoji == dice:
            character = state.users.get(str(user))
            if character is not None and character.init_modifier is not None:
                await init_state.add_full(state, context.channel, user, ROLL, character.init_modifier, character.name, True)
            else:
                await init_state.add_modifier_warning()
                await init_state.message.remove_reaction(dice, user)
        elif user == context.author:
            if reaction.emoji == left:
                await init_state.message.remove_reaction(left, user)
                await init_state.backward()
            elif reaction.emoji == right:
                await init_state.message.remove_reaction(right, user)
                await init_state.forward()
            elif reaction.emoji == fast_left:
                await init_state.message.remove_reaction(fast_left, user)
                await init_state.fast_backward()
            elif reaction.emoji == cross:
                if await confirm(state, init_state.message, user):
                    await init_state.message.clear_reactions()

                    await context.channel.send("Done with initiative.")
                    del channel_initiatives[context.channel.id]
                    return
                else:
                    await init_state.message.remove_reaction(cross, user)
        else:
            await init_state.message.remove_reaction(reaction.emoji, user)


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
    roll_msg = None
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
    success = await init_state.add_full(state, context.channel, context.author, command, value, name, loud)
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
