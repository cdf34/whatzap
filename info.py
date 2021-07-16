import discord
import os

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
    field_count = 0
    
    async def add_field(name, value):
        # maximum field count in an embed is 25, so we have to send the message if we hit 25
        nonlocal embed
        nonlocal field_count
        embed.add_field(name=name, value=value, inline=False)
        field_count += 1
        if field_count == 25:    
            await context.channel.send(embed=embed)
            embed = discord.Embed()
            field_count = 0
    
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
            await add_field(name=name, value=npc.description)
        else:
            await add_field(name=name, value="_ _")
    await context.channel.send(embed=embed)

async def list_npcs(state, context, message):
    await _list_npcs(state, context, False)

async def list_npcs_full(state, context, message):
    await _list_npcs(state, context, True)

async def _help(state, context, file, reverse):
    files = sorted(list(os.listdir("docs/")), key=lambda x:int(x.split("-")[0]))
    file_dict = {}
    for f in files:
        middle = (f.split("-")[1]).split(".")[0]
        file_dict[middle] = f
    if file in file_dict:
        with open(os.path.join("docs", file_dict[file])) as f:
            embed = discord.Embed()
            name = None
            value = ""
            for j, line in enumerate(f):
                if not j:
                    embed.description = line.strip()
                    continue
                if file in ["quickstart", "syntax"]: # fix this
                    embed.description += "\n" + line.strip()
                    continue
                if line.startswith(" "):
                    value += line
                else:
                    if name is not None:
                        if reverse:
                            name = name[::-1]
                            value = value[::-1]
                        embed.add_field(name=name, value=value, inline=False)
                    name = line.strip()
                    value = ""
            if name is not None:
                if reverse:
                    name = name[::-1]
                    value = value[::-1]
                embed.add_field(name=name, value=value, inline=False)
        await context.channel.send(embed=embed)
    else:

        embed = discord.Embed()
        text = "The help is split into several sections. Send `help $section` to get that section. Possible sections:"
        for desc, filename in file_dict.items():
            with open(os.path.join("docs", filename)) as f:
                line = f.readline().strip()
                text += f"\n**{desc}**: {line}"
        if reverse:
            text = text[::-1]
        embed.description = text
        await context.channel.send(embed=embed)


async def help(state, context, file):
    await _help(state, context, file, reverse=False)

async def hguolp(state, context, file):
    await _help(state, context, file, reverse=True)



async def commands(state, context, filter_text):
    if filter_text == "":
        await context.channel.send("Try `,help` if you want all the commands.")
        return
    embed = discord.Embed()
    field_count = 0
    blank_before = True

    async def add_field(name, value):
        # maximum field count in an embed is 25, so we have to send the message if we hit 25
        nonlocal embed
        nonlocal field_count
        nonlocal blank_before
        if blank_before:
            embed.add_field(name='\u200B', value='\u200B', inline=False)
            blank_before = False
            field_count += 1
            if field_count == 25:    
                await context.channel.send(embed=embed)
                embed = discord.Embed()
                field_count = 0
        embed.add_field(name=name, value=value, inline=False)
        field_count += 1
        if field_count == 25:    
            await context.channel.send(embed=embed)
            embed = discord.Embed()
            field_count = 0

    for i, file in enumerate(sorted(list(os.listdir("docs/")), key=lambda x:int(x.split("-")[0]))):
        with open(os.path.join("docs", file)) as f:
            if i == 0:
                continue
            elif i == 1:
                embed.description = "".join(f.readlines())
                embed.description += "\nShowing all commands"
                if filter_text:
                    embed.description += f" containing {filter_text}"
                embed.description += "."
                continue
            name = None
            value = ""
            for j, line in enumerate(f):
                if not j:
                    continue
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

    await context.channel.send(embed=embed)
            
async def whois(state, context, character, args):
    description = character.description if character.description is not None else f"{character.name} does not have a description set."
    title = character.name
    if character.alias != character.name:
        title += f" (alias {character.alias})"
    embed = discord.Embed(title=title, description=description)
    avatar = character.get_avatar()
    if avatar is not None:
        if "whois" in character.avatars:
            avatar = character.avatars["whois"]
        embed.set_thumbnail(url=avatar)
    
    footer_parts = []
    for user, pc in state.users.items():
        if pc is character:
            footer_parts.append(f"Player character for {user}")
    footer_parts.append(f"Messages sent: {character.messages_sent}")
    embed.set_footer(text=" -- ".join(footer_parts))
    await context.channel.send(embed=embed)
