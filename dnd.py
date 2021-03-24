from utils import confirm
import random

class InitiativeState:
    def __init__(self, context) -> None:
        self.initiatives = []
        self.current = 0
        self.channel = context.channel

    async def setup(self):
        self.message = await self.channel.send(self.to_message())

    def to_message(self):
        this = "▶️"
        not_this = "⬛"
        text = "**Initiative**"
        for i, pair in enumerate(self.initiatives):
            text += "\n"
            if i == self.current:
                text += this
            else:
                text += not_this
            init, name = pair
            text += f" {init}: {name}"
        return text

    async def update(self):
        await self.message.edit(content=self.to_message())

    async def backward(self):
        self.current -= 1
        self.current += len(self.initiatives)
        self.current %= len(self.initiatives)
        await self.update()

    async def forward(self):
        self.current += 1
        self.current %= len(self.initiatives)
        await self.update()

    async def add_character(self, name, initiative):
        self.initiatives.append((name, initiative))        
        if initiative > self.initiatives[self.current][1]:
            self.current += 1
        self.initiatives = sorted(self.initiatives, key=lambda pair: pair[1], reverse=True)
        await self.update()


channel_initiatives = {}


async def initiative_start(state, context, args):
    me = state.client.user
    init_state = InitiativeState(context)
    await init_state.setup()
    channel_initiatives[context.channel.id] = init_state
    left = "⬅️"
    right = "➡️"
    blank = "⬛"
    cross = "❎"
    possibles = [left, right, cross]
    await init_state.message.add_reaction(left)
    await init_state.message.add_reaction(right)
    await init_state.message.add_reaction(blank)
    await init_state.message.add_reaction(cross)

    def check(reaction, user):
        return reaction.emoji in possibles and user != me and reaction.message == init_state.message

    while True:
        reaction, user = await state.client.wait_for('reaction_add', check=check)
        if reaction.emoji == left:
            await init_state.message.remove_reaction(left, user)
            await init_state.backward()
        elif reaction.emoji == right:
            await init_state.message.remove_reaction(right, user)
            await init_state.forward()
        elif reaction.emoji == cross:
            if await confirm(state, init_state.message, user):
                await init_state.message.clear_reactions()

                await context.channel.send("Done with initiative.")
                del channel_initiatives[context.channel.id]
                break
            else:
                await init_state.message.remove_reaction(cross, user)


async def initiative_add(state, context, character, args):
    if context.channel.id in channel_initiatives:
        initiative = None
        try:
            initiative = int(args)
        except ValueError:
            try:
                command, modifier = args.split(" ")
                if command == "roll":
                    modifier = int(modifier)
                    initiative = random.randint(1, 20) + modifier
            except:
                await context.channel.send("That does not look like an initiative.")
        if initiative is not None:
            await channel_initiatives[context.channel.id].add_character(character.name, int(initiative))
    else:
        await context.channel.send("This channel is not currently in initiative.")