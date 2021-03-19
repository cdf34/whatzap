from state import State


def add_attr(attr, default=lambda x: None):
    state = State()
    state.load()
    for npc in state.npcs:
        if not hasattr(npc, attr):
            setattr(npc, attr, default(npc))
    for user, pc in state.users.items():
        if not hasattr(pc, attr):
            setattr(pc, attr, default(pc))
    state.save()

#  add_attr("avatars", default=lambda x: dict())

def avatars_manage():
    state = State(690249317646073856)
    for c in state.npcs:
        if not hasattr(c, "avatar"):
            c.avatar = None
            if not hasattr(c, "avatars"):
                c.avatars = {}
        else:
            if c.avatar is None:
                if not hasattr(c, "avatars"):
                    c.avatars = {}
            else:
                if not hasattr(c, "avatars"):
                    c.avatars = {"default": c.avatar}
                    c.avatar = "default"
                else:
                    for key, value in c.avatars.items():
                        if value == c.avatar:
                            c.avatar = key
                            break
                    else:
                        c.avatar = "default"
    for user, c in state.users.items():
        if not hasattr(c, "avatar"):
            c.avatar = None
            if not hasattr(c, "avatars"):
                c.avatars = {}
        else:
            if c.avatar is None:
                if not hasattr(c, "avatars"):
                    c.avatars = {}
            else:
                if not hasattr(c, "avatars"):
                    c.avatars = {"default": c.avatar}
                    c.avatar = "default"
                else:
                    for key, value in c.avatars.items():
                        if value == c.avatar:
                            c.avatar = key
                            break
                    else:
                        c.avatar = "default"
    state.save()

avatars_manage()