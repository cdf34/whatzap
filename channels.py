channel_modes = ["automatic", "default"]

async def channel_mode(state, context, mode):
    if mode not in channel_modes:
        await context.channel.send(f"{mode} is not a valid channel mode.")
    else:
        channel_id = context.channel.id
        for cs in state.channels.values():
            cs.discard(channel_id)
        state.channels[mode].add(channel_id)
        state.save()
        await state.log(context, f"Changed mode of channel {context.channel} to {mode}.")