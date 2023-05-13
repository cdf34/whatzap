from utils import get_webhook

def parse_quote(message, sender):
    message = message.split("\n")
    message = [line for line in message if not line.startswith("> ")]
    message = "\n> ".join(message)
    return "> " + sender + " " + message


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
        self.init_modifier = None

    async def send_as(self, context, message):
        webhook = await get_webhook(context.channel)
        if context.reference is not None:
            replied = context.reference.resolved
            if replied.author.id != webhook.id:
                message = parse_quote(replied.content, replied.author.mention) + "\n" + message
            else:
                message = parse_quote(replied.content, "**" + replied.author.name + "**") + "\n" + message
        await webhook.send(message, username=self.name, avatar_url=self.get_avatar())
        self.messages_sent += 1

    async def send_as_command(self, state, context, message):
        if self.permissions is not None:
            if context.author.id not in self.permissions:
                await context.channel.send("You do not have permission to send as that character.")
                return          
        await context.delete()
        await self.send_as(context, message)

    def get_avatar(self):
        return None if self.avatar is None else self.avatars[self.avatar]


class NPC(Character):
    pass

