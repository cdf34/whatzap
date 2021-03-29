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

# add_attr("init_modifier") 

def avatar_manage(c):
    print(c, c.avatar if hasattr(c, "avatar") else "undef", c.avatars if hasattr(c, "avatars") else "undef")
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
                    if value == c.avatar or key == c.avatar:
                        c.avatar = key
                        break
                else:
                    c.avatars["default"] = c.avatar
                    c.avatar = "default"
    print(c, c.avatar if hasattr(c, "avatar") else "undef", c.avatars if hasattr(c, "avatars") else "undef")
    print()


def avatars_manage():
    state = State(690249317646073856, None)
    for c in state.npcs:
        avatar_manage(c)
    for user, c in state.users.items():
        avatar_manage(c)
    state.save()


def state_update():
    for file in os.listdir("save"):
        if os.path.isdir(os.path.join("save", file)):
            state = State(int(file), None)
            state.channels["private-initiatives"] = dict()
            state.save()

state_update()
# avatars_manage()