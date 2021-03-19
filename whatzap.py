# todo: avatar error checking

from state import State
import user
import npc
import info
import discord


states = {}
client = discord.Client()


@client.event
async def on_message(message):
    if message.guild.id not in states:
        states[message.guild.id] = State(message.guild.id)
    state = states[message.guild.id]
    commands_dict = state.commands
    if message.content.startswith(",,"):
        await user.send_as_self(state, message, message.content[2:])
    elif message.content.startswith(","):
        lower = message.content.lower()
        for c in commands_dict:
            if lower.startswith(c):
                await commands_dict[c](state, message, message.content[len(c) + 1:])
    elif message.channel.id in state.channels["automatic"]:
        await user.send_as_self(state, message, message.content)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

client.run('ODIxNzQzMjg5MjAyOTAxMDEy.YFIKEw.oi7IbqcR8CMng_V309ttt3p7D9E')

"https://discord.com/api/oauth2/authorize?client_id=821743289202901012&permissions=603990080&scope=bot"
"Should work to add the bot to other servers"