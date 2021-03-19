import user
import npc
import info
import channels

bot_commands = {
    ",name": user.set_name,
    ",avatar": user.set_avatar,
    ",switch-avatar": user.switch_avatar,
    ",list-avatars": user.avatar_list,
    ",remove-avatar": user.remove_avatar,
    ",alias": user.set_alias,
    ",give-access": user.give_access,
    ",remove-access": user.remove_access,
    ",check-access": user.check_access,
    ",npc-create": npc.npc_create,
    ",npc-avatar": npc.npc_avatar,
    ",npc-alias": npc.npc_alias,
    ",npc-remove": npc.npc_delete,
    ",npc-delete": npc.npc_delete,
    ",npc-send": npc.npc_send,
    ",npc-rename": npc.npc_rename,
    ",set-description": npc.set_description,
    ",channel-mode": channels.channel_mode,
    ",help": info.help,
    ",commands": info.commands,
    ",list-pcs": info.list_pcs,
    ",list-pcs-full": info.list_pcs_full,
    ",list-npcs": info.list_npcs,
    ",list-npcs-full": info.list_npcs_full,
    ",whois": info.whois,
    ",who-is": info.whois,
}
