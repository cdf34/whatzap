# todo: avatar error checking

from state import State
from commands import parse_command
import discord


states = {}
client = discord.Client()


@client.event
async def on_message(message):
    try:
        if message.guild.id not in states:
            states[message.guild.id] = State(message.guild.id, client)
        state = states[message.guild.id]
        await parse_command(state, message)
    except Exception:
        print(message)
        raise

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

with open('token') as f:
    token = f.readline()

client.run(token)
