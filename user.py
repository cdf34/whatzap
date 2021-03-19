from classes import Character
import utils

def get_author_character(state, context):
    return state.users.get(str(context.author))

async def send_as_self(state, context, message):
    character = get_author_character(state, context)
    if character:
        await context.delete()
        await character.send_as(context.channel, message)

async def set_name(state, context, name):
    character = get_author_character(state, context)
    if character:
        if await state.check_no_confusion(context, name, [character.name, character.alias]):
            old_name = character.name
            character.name = name
            state.save() 
            state.update_commands()
            await state.log(context, f"Changed {context.author}'s character name from {old_name} to {name}.")
    else:
        if await state.check_no_confusion(context, name):
            state.users[str(context.author)] = Character(name=name)
            state.save() 
            state.update_commands()
            await state.log(context, f"Created a character for {context.author} with name {name}.")

async def set_alias(state, context, alias):
    character = get_author_character(state, context)
    if character:
        if await state.check_no_confusion(context, alias, [character.name, character.alias]):
            character.alias = alias
            state.save()
            state.update_commands()
            await state.log(context, f"Changed {character.name}'s alias to {alias}.")
    else:
        await context.channel.send(f"User {context.author} does not have a character.")

async def set_avatar(state, context, message):
    character = get_author_character(state, context)
    if character:
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
    else:
        await context.channel.send(f"User {context.author} does not have a character.")

async def switch_avatar(state, context, key):
    character = get_author_character(state, context)
    if character:
        if key in character.avatars:
            character.avatar = key
            state.save() 
            await state.log(context, f"Switched {character.name}'s avatar to avatar with key {key}.")
        else:
            await context.channel.send(f"Key {key} does not appear in your list of avatars.")
    else:
        await context.channel.send(f"User {context.author} does not have a character.")

async def remove_avatar(state, context, key):
    character = get_author_character(state, context)
    if character:
        if key in character.avatars:
            del character.avatars[key]
            if key == character.avatar:
                character.avatar = None
            state.save() 
            await state.log(context, f"Removed {character.name}'s switchable avatar with key {key}.")
        else:
            await context.channel.send(f"Key {key} does not appear in your list of avatars.")
    else:
        await context.channel.send(f"User {context.author} does not have a character.")

async def avatar_list(state, context, message):
    character = get_author_character(state, context)
    if character:
        if character.avatars:
            await context.channel.send(f"Your list of avatars: " + ", ".join(character.avatars))
        else:
            await context.channel.send(f"You do not have any avatars you can switch to.")
    else:
        await context.channel.send(f"User {context.author} does not have a character.")

async def give_access(state, context, message):
    character = get_author_character(state, context)
    if character:
        character.permissions.append(message)
        state.save()
        await state.log(context, f"Gave sending permissions for {character.name} to {message}.")
    else:
        await context.channel.send(f"User {context.author} does not have a character.")

async def remove_access(state, context, message):
    character = get_author_character(state, context)
    if character:
        if message == str(context.author):
            await context.channel.send("You can't remove your permission to send as yourself!")
        else:
            try:
                character.permissions.remove(message)
                state.save()
                await state.log(context, f"Removed sending permissions for {character.name} from {message}.")
            except ValueError:
                await context.channel.send("That user already does not have permission to send as your character.")
    else:
        await context.channel.send(f"User {context.author} does not have a character.")

async def check_access(state, context, message):
    character = get_author_character(state, context)
    if character:
        to_send = f"Users that have permission to send as {character.name}: " + ", ".join(character.permissions)
        await context.channel.send(to_send)
    else:
        await context.channel.send(f"User {context.author} does not have a character.")
