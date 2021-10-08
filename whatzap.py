# todo: avatar error checking
from collections import defaultdict
import os

import discord

from state import State
from commands import parse_command
import schedule

states = defaultdict(lambda id: State(id, client))
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

for str_id in os.listdir("save"):
    id = int(str_id)
    states[id] = State(id, client)

@client.event
async def on_message(message):
    try:
        state = states[message.guild.id]
        await parse_command(state, message)
    except Exception as e:
        print(message, e)
        raise

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

with open('token') as f:
    token = f.readline()

schedule.schedule_loop.start(states)
client.run(token)
