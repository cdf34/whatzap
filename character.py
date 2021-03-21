from classes import NPC, Character
import utils

async def send_as_self(state, context, message):
    character = state.users.get(str(context.author))
    if character:
        await context.delete()
        await character.send_as(context, message)

async def pc_create(state, context, name):
    user = str(context.author)
    if user not in state.users:
        if await state.check_no_confusion(context, name):
            state.users[user] = Character(name=name)
            state.users[user].permissions = [user]
            state.save() 
            state.update_commands()
            await state.log(context, f"Created a character for {user} with name {name}.")
    else:
        await context.channel.send(f"You already have a character called {state.users[user].name}.")

async def npc_create(state, context, name):
    if await state.check_no_confusion(context, name):
        state.npcs.append(NPC(name=name))
        state.save()
        state.update_commands()
        await state.log(context, f"Created an NPC called {name}.")

async def rename(state, context, character, name):
    if await state.check_no_confusion(context, name, [character.name, character.alias]):
        old_name = character.name
        character.name = name
        state.save()
        state.update_commands()
        await state.log(context, f"Changed {old_name}'s name to {name}.")

async def set_alias(state, context, character, alias):
    if await state.check_no_confusion(context, alias, [character.name, character.alias]):
        character.alias = alias
        state.save()
        state.update_commands()            
        await state.log(context, f"Changed {character.name}'s alias to {alias}.")

async def set_avatar(state, context, character, message):
    if context.attachments:
        avatar = context.attachments[0].url
        key = message
    else:
        parts = message.split(" ")
        avatar = parts[-1]
        if not utils.check_avatar(avatar):
            await context.channel.send("That doesn't look like an avatar URL. If you think it does, report this to the developer.")
            return
        if len(parts) > 1:
            key = " ".join(parts)
        else:
            key = None
    if key:
        character.avatars[key] = avatar
        state.save() 
        await state.log(context, f"Set a switchable avatar with key {key}.")
    else:
        character.avatar = "default"
        character.avatars["default"] = avatar
        state.save() 
        await state.log(context, f"Changed {character.name}'s avatar.")


async def send_as(state, context, character, message):
    await context.delete()
    await character.send_as(context, message)


async def delete_character(state, context, character, args):
    if isinstance(character, NPC):
        state.npcs.remove(character)
        state.save()
        await state.log(context, f"Removed NPC {character.name}.")
    else:
        # todo
        await context.channel.send("You can't yet delete player characters.")


async def set_description(state, context, character, description):
    character.description = description
    state.save()
    await state.log(context, f"Set or updated {character.name}'s description.")

async def switch_avatar(state, context, character, key):
    if key in character.avatars:
        character.avatar = key
        state.save() 
        await state.log(context, f"Switched {character.name}'s avatar to avatar with key {key}.")
    else:
        await context.channel.send(f"Key {key} does not appear in {character.name}'s' list of avatars.")

async def remove_avatar(state, context, character, key):
    if key in character.avatars:
        del character.avatars[key]
        if key == character.avatar:
            character.avatar = None
        state.save() 
        await state.log(context, f"Removed {character.name}'s switchable avatar with key {key}.")
    else:
        await context.channel.send(f"Key {key} does not appear in {character.name}'s list of avatars.")

async def avatar_list(state, context, character, args):
    if character.avatars:
        await context.channel.send(f"{character.name}'s' list of avatars: " + ", ".join(character.avatars))
    else:
        await context.channel.send(f"{character.name} does not have any switchable avatars.")

async def give_access(state, context, character, message):
    character.permissions.append(message)
    state.save()
    await state.log(context, f"Gave sending permissions for {character.name} to {message}.")

async def remove_access(state, context, character, message):
    if message == str(context.author):
        await context.channel.send("You can't remove your permission to send as yourself!")
    else:
        try:
            character.permissions.remove(message)
            state.save()
            await state.log(context, f"Removed sending permissions for {character.name} from {message}.")
        except ValueError:
            await context.channel.send(f"User {message} already does not have permission to send as {character.name}.")

async def check_access(state, context, character, message):
    to_send = f"Users that have permission to send as {character.name}: " + ", ".join(character.permissions)
    await context.channel.send(to_send)
