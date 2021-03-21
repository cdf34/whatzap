import discord

async def _list_pcs(state, context, full):
    embed = discord.Embed()
    embed.description = "List of player characters:"
    for user, character in state.users.items():
        name = f"\n{user}: {character.name}"
        if character.alias != character.name:
            name += f" (alias {character.alias})"
        if full and character.description is not None:
            embed.add_field(name=name, value=character.description, inline=False)
        else:
            embed.add_field(name=name, value="_ _", inline=False)
    await context.channel.send(embed=embed)

async def list_pcs(state, context, message):
    await _list_pcs(state, context, False)

async def list_pcs_full(state, context, message):
    await _list_pcs(state, context, True)

def _npc_key(npc):
    score = npc.messages_sent
    if npc.avatar is not None:
        score += 20
    if npc.description is not None:
        score += 30
    return score

async def _list_npcs(state, context, full):
    embed = discord.Embed()
    embed.description = "Current list of NPCs:\n"
    embed.description += "📝 indicates they have a description, 🖼 indicates they have an avatar"
    for npc in sorted(state.npcs, key=_npc_key, reverse=True):
        name = ""
        if npc.description is not None:
            name += "📝"
        if npc.avatar is not None:
            name += "🖼"
        name += npc.name
        if npc.alias != npc.name:
            name += f" (alias {npc.alias})"
        if full and npc.description is not None:
            embed.add_field(name=name, value=npc.description, inline=False)
        else:
            embed.add_field(name=name, value="_ _", inline=False)
    await context.channel.send(embed=embed)

async def list_npcs(state, context, message):
    await _list_npcs(state, context, False)

async def list_npcs_full(state, context, message):
    await _list_npcs(state, context, True)

async def help(state, context, message):
    with open("docs/help.txt") as f:
        to_send = "".join(f.readlines())
    await context.channel.send(to_send)

async def commands(state, context, filter_text):
    embeds = []
    embed_count = 0
    embeds.append(discord.Embed())
    field_count = 0
    blank_before = True

    async def add_field(name, value):
        # maximum field count in an embed is 25
        # maximum embed count in a message is 10,
        # so we have to send the message if we hit 10
        nonlocal embeds
        nonlocal field_count
        nonlocal embed_count
        nonlocal blank_before
        if blank_before:
            embeds[embed_count].add_field(name='\u200B', value='\u200B', inline=False)
            blank_before = False
            field_count += 1
            if field_count == 25:
                embed_count += 1
                embeds.append(discord.Embed())
                field_count = 0
            if embed_count == 10:
                await context.channel.send(embeds=embeds)
                field_count = 0
                embeds.clear()
                embed_count = 0
        embeds[embed_count].add_field(name=name, value=value, inline=False)
        field_count += 1
        if field_count == 25:
            embed_count += 1
            embeds.append(discord.Embed())
            field_count = 0
        if embed_count == 10:
            await context.channel.send(embeds=embeds)
            field_count = 0
            embeds.clear()
            embed_count = 0

    for i in range(8):
        with open(f"docs/commands-{i}.txt") as f:
            if not i:
                embeds[embed_count].description = "".join(f.readlines())
                embeds[embed_count].description += "\nShowing all commands"
                if filter_text:
                    embeds[embed_count].description += f" containing {filter_text}"
                embeds[embed_count].description += "."
                continue
            name = None
            value = ""
            for line in f:
                if line.startswith(" "):
                    value += line
                else:
                    if name is not None and filter_text in name:
                        await add_field(name=name, value=value)
                    name = line.strip()
                    value = ""
            if name is not None and filter_text in name:
                await add_field(name=name, value=value)
            blank_before = True

    await context.channel.send(embeds=embeds)

async def whois(state, context, target):
    character, _ = state.find_character(target)

    if character:
        description = character.description if character.description is not None else f"{character.name} does not have a description set."
        title = character.name
        if character.alias != character.name:
            title += f" (alias {character.alias})"
        embed = discord.Embed(title=title, description=description)
        if character.get_avatar() is not None:
            embed.set_thumbnail(url=character.get_avatar())
        await context.channel.send(embed=embed)
    else:
        await context.channel.send(f"Cannot find character {target}.")
