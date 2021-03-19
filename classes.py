from utils import get_webhook

class Character:
    def __init__(self, name, avatar=None) -> None:
        self.name = name
        if avatar:
            self.avatar = "default"
            self.avatars = {"default": avatar}
        else:
            self.avatar = None
            self.avatars = {}
        self.description = None
        self.alias = name
        self.permissions = None
        self.messages_sent = 0

    async def send_as(self, channel, content, prefix=""):
        webhook = await get_webhook(channel)
        await webhook.send(content, username=prefix + self.name, avatar_url=self.get_avatar())
        self.messages_sent += 1

    async def send_as_command(self, state, context, message):
        if self.permissions is not None:
            if str(context.author) not in self.permissions:
                await context.channel.send("You do not have permission to send as that character.")
                return
        await context.delete()
        await self.send_as(context.channel, message)

    def get_avatar(self):
        return None if self.avatar is None else self.avatars[self.avatar]


class NPC(Character):
    pass

