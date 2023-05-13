import character
import dnd
import info
import channels
import schedule
from classes import NPC

def default_permissions(state, character, author):
    return isinstance(character, NPC) or state.users.get(author) is character

def send_permissions(state, character, author):
    return isinstance(character, NPC) or author in character.permissions

def access_permissions(state, character, author):
    return state.users.get(author) is character

def whois_permissions(state, character, author):
    return True

class CharacterCommand:
    def __init__(self, func, permissions_func=default_permissions) -> None:
        self.func = func
        if permissions_func is None:
            self.permissions_func = lambda s, c, a: True
        else:
            self.permissions_func = permissions_func

    async def __call__(self, state, context, args):
        character, args = await state.find_character(context, args)
        if character:
            if self.permissions_func(state, character, context.author.id):
                await self.func(state, context, character, args)
            else:
                await context.channel.send(f"You do not have permission to do that to {character.name}.")

class OptionalCharacterCommand(CharacterCommand):
    async def __call__(self, state, context, args):
        character, args = await state.find_character(context, args, error_on_not_found=False)
        if character is None or self.permissions_func(state, character, context.author.id):
            return await self.func(state, context, character, args)
        else:
            await context.channel.send(f"You do not have permission to do that to {character.name}.")
            return False

bot_commands = {
    ",create-pc": character.pc_create,
    ",create-npc": character.npc_create,
    ",rename": CharacterCommand(character.rename),
    ",set-alias": CharacterCommand(character.set_alias),
    ",send-as": CharacterCommand(character.send_as, permissions_func=send_permissions),
    ",remove-npc": CharacterCommand(character.delete_character),
    ",set-description": CharacterCommand(character.set_description),
    ",set-avatar": CharacterCommand(character.set_avatar),
    ",switch-avatar": CharacterCommand(character.switch_avatar),
    ",list-avatars": CharacterCommand(character.avatar_list),
    ",remove-avatar": CharacterCommand(character.remove_avatar),

    ",give-access": CharacterCommand(character.give_access, permissions_func=access_permissions),
    ",remove-access": CharacterCommand(character.remove_access, permissions_func=access_permissions),
    ",check-access": CharacterCommand(character.check_access, permissions_func=access_permissions),

    ",channel-mode": channels.channel_mode,
    ",help": info.help,
    ",hguolp": info.hguolp,
    ",commands": info.commands,
    ",list-pcs": info.list_pcs,
    ",list-pcs-full": info.list_pcs_full,
    ",list-npcs": info.list_npcs,
    ",list-npcs-full": info.list_npcs_full,
    ",whois": CharacterCommand(info.whois, permissions_func=whois_permissions),
    ",who-is": CharacterCommand(info.whois, permissions_func=whois_permissions),

    ",init-start": dnd.initiative_start,
    ",initiative-start": dnd.initiative_start,
    ",init-add": OptionalCharacterCommand(dnd.initiative_add_loud, permissions_func=whois_permissions),
    ",initiative-add": dnd.initiative_start,
    ",init-modifier": CharacterCommand(dnd.initiative_modifier),
    ",initiative-modifier": dnd.initiative_start,

    ",schedule": schedule.schedule,
    ",schedule-reminders": schedule.schedule_reminders,
    ",reminder-channel": schedule.reminder_channel,
}

auto_init = OptionalCharacterCommand(dnd.initiative_add_quiet, permissions_func=whois_permissions)

async def parse_command(state, message):
    commands_dict = state.commands
    if message.content.startswith(",,"):
        await character.send_as_self(state, message, message.content[2:])
    elif message.content.startswith(","):
        lower = message.content.lower()
        for c in commands_dict:
            if lower.startswith(c):
                content = message.content[len(c):]
                if not content or content[0] == " ":
                    await commands_dict[c](state, message, content[1:])
    elif message.channel.id in state.channels["rolling-initiative"] and len(message.content) and await auto_init(state, message, message.content):
        pass
    elif message.channel.id in state.channels["automatic"]:
        await character.send_as_self(state, message, message.content)
