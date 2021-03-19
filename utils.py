saved_webhooks = dict()


async def get_webhook(channel):
    if channel in saved_webhooks:
        return saved_webhooks[channel]
    webhooks = await channel.webhooks()
    for hook in webhooks:
        if hook.name == "WhatZap":
            saved_webhooks[channel] = hook
            return hook
    else:
        print("Creating webhook")
        hook = await channel.create_webhook(name="WhatZap")
        saved_webhooks[channel] = hook
        return hook

def check_avatar(url):
    return url.endswith(".png") or url.endswith(".jpg") or url.endswith(".gif") or url.endswith(".jpeg")