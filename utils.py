import asyncio


saved_webhooks = dict()


async def get_webhook(channel):
    if channel in saved_webhooks:
        return saved_webhooks[channel]
    webhooks = await channel.webhooks()
    for hook in webhooks:
        if hook.name == "WhatZap":
            saved_webhooks[channel] = hook
            return hook
    else:
        print("Creating webhook")
        hook = await channel.create_webhook(name="WhatZap")
        saved_webhooks[channel] = hook
        return hook

def check_avatar(url):
    return url.endswith(".png") or url.endswith(".jpg") or url.endswith(".gif") or url.endswith(".jpeg")

async def confirm(state, message, user):
    original_content = message.content
    thumbs_up = "👍"
    thumbs_down = "👎"
    await message.edit(content=original_content + f"\nWaiting for confirmation: react {thumbs_up} to confirm or {thumbs_down} to cancel.")
    await message.add_reaction(thumbs_up)
    await message.add_reaction(thumbs_down)

    possibles = [thumbs_up, thumbs_down]
    def check(reaction, reactor):
        return reaction.emoji in possibles and reactor == user and reaction.message == message

    try:
        reaction, _ = await state.client.wait_for('reaction_add', timeout=60.0, check=check)
        await message.edit(content=original_content)
        answer = reaction.emoji == thumbs_up
        await message.clear_reaction(thumbs_up)
        await message.clear_reaction(thumbs_down)
        return answer
    except asyncio.TimeoutError:
        await message.edit(content=original_content)
        await message.channel.send("Timed out waiting for confirmation.")
        await message.clear_reaction(thumbs_up)
        await message.clear_reaction(thumbs_down)
        return False
