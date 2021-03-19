from classes import NPC

async def npc_create(state, context, name):
    npc, _ = state.find_npc(name)
    if npc:
        await context.channel.send(f"There is already an NPC called {name}.")
    else:
        for character in state.users.values():
            if character.name == name:
                await context.channel.send(f"There is already a character called {name}.")
                break
        else:
            if await state.check_no_confusion(context, name):
                state.npcs.append(NPC(name=name))
                state.save()
                state.update_commands()
                await state.log(context, f"Created an NPC called {name}.")

async def npc_rename(state, context, args):
    npc, name = state.find_npc(args)
    if npc:
        if await state.check_no_confusion(context, name, [npc.name, npc.alias]):
            old_name = npc.name
            npc.name = name
            state.save()
            state.update_commands()
            await state.log(context, f"Changed NPC {old_name}'s name to {name}.")
    else:
        await context.channel.send(f"There is no NPC called that.")

async def npc_alias(state, context, args):
    npc, alias = state.find_npc(args)
    if npc:
        if await state.check_no_confusion(context, alias, [npc.name, npc.alias]):
            npc.alias = alias
            state.save()
            state.update_commands()            
            await state.log(context, f"Changed NPC {npc.name}'s alias to {alias}.")
    else:
        await context.channel.send(f"There is no NPC called that.")


async def npc_avatar(state, context, args):
    npc, avatar = state.find_npc(args)
    if npc:
        if context.attachments:
            avatar = context.attachments[0].url
        npc.avatar = avatar
        state.save()
        await state.log(context, f"Changed {npc.name}'s avatar.")
    else:
        await context.channel.send(f"There is no NPC called that.")


async def npc_send(state, context, args):
    npc, to_send = state.find_npc(args)
    if npc:
        await context.delete()
        await npc.send_as(context.channel, to_send)
    else:
        await context.channel.send(f"There is no NPC called that.")        


async def npc_delete(state, context, args):
    npc, _ = state.find_npc(args)
    if npc:
        state.npcs.remove(npc)
        state.save()
        await state.log(context, f"Removed NPC {npc.name}.")
    else:
        await context.channel.send(f"There is no NPC called {args}.")


async def set_description(state, context, args):
    npc, description = state.find_npc(args)
    if npc:
        npc.description = description
        state.save()
        await state.log(context, f"Set or updated {npc.name}'s description.")
    else:
        character = state.users.get(str(context.author))
        if character:
            if args.startswith(character.name):
                description = args[len(str(character.name)) + 1:]
                character.description = description
                state.save()
                await state.log(context, f"Set or updated {character.name}'s description.")
            elif args.startswith(character.alias):
                description = args[len(str(character.alias)) + 1:]
                character.description = description
                state.save()
                await state.log(context, f"Set or updated {character.name}'s description.")
            elif args.startswith("me"):
                description = args[3:]
                character.description = description
                state.save()
                await state.log(context, f"Set or updated {character.name}'s description.")
