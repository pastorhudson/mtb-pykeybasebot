from botcommands.get_members import get_members


async def get_channel_members(conversation_id, bot):
    channel_members = await bot.chat.execute(
        {"method": "listmembers", "params": {"options": {"conversation_id": conversation_id}}}
    )
    members = get_members(channel_members)
    return members