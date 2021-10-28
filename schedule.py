import datetime
import discord
from discord.ext import tasks
import dateparser
import pytz

bst = pytz.timezone("Europe/London")

def reminders_update(state):
    if state.event["time"] is None:
        return
    now = bst.fromutc(datetime.datetime.utcnow())
    for pair in state.event["reminders"]:
        delta = pair[0]
        if state.event["time"] - delta < now:
            pair[1] = True
        else:
            pair[1] = False
    state.save()

async def schedule(state, context, message):
    time = dateparser.parse(message)
    state.event["time"] = bst.localize(time)
    reminders_update(state)
    await state.log(context, f"Scheduled event for {time.strftime('%H:%M on %d/%m/%Y')} BST/GMT.")

async def schedule_reminders(state, context, message):
    state.event["reminders"] = []
    for r in message.split(","):
        r = r.strip()
        try:
            val = int(r[:-1])
        except ValueError:
            continue
        if r[-1] == "h":
            state.event["reminders"].append([datetime.timedelta(hours=val), False, f"{val} hours"])        
        elif r[-1] == "m":
            state.event["reminders"].append([datetime.timedelta(minutes=val), False, f"{val} minutes"])
    reminders_update(state)
    await state.log(context, f"Set reminders for events to be {', '.join(x[2] for x in state.event['reminders'])} before the event.")

async def reminder_channel(state, context, message):
    if message == "on":
        state.channels["reminder"].add(context.channel.id)
        state.save()
        await state.log(context, f"Event reminders turned on in {context.channel}.")
    elif message == "off":
        state.channels["reminder"].discard(context.channel.id)
        state.save()
        await state.log(context, f"Event reminders turned off in {context.channel}.")
    else:
        await context.channel.send("Try either `,reminder-channel on` or `,reminder-channel off`.")

@tasks.loop(minutes=1)
async def schedule_loop(states):
    now = bst.fromutc(datetime.datetime.utcnow())
    for state in states.values():
        if state.event["time"] is None:
            continue
        for delta, used, text in state.event["reminders"]:
            if used:
                continue
            if state.event["time"] - delta < now:
                for channel in state.channels["reminder"]:
                    await state.client.get_channel(channel).send(f"@everyone D&D in {text}!", allowed_mentions=discord.AllowedMentions(everyone = True))
        reminders_update(state)

