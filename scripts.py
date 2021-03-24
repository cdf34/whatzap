import os
from state import State


def add_attr(attr, default=lambda x: None):
    for file in os.listdir("save"):
        if os.path.isdir(os.path.join("save", file)):
            state = State(int(file), None)
            for c in state.npcs:
                if not hasattr(c, attr):
                    setattr(c, attr, default(c))
            for user, c in state.users.items():
                if not hasattr(c, attr):
                    setattr(c, attr, default(c))
            state.save()

add_attr("init_modifier") 

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

