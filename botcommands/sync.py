from models import User, Team
from crud import s
from botcommands.get_members import get_members


async def get_channel_members(conversation_id, bot):
    channel_members = await bot.chat.execute(
        {"method": "listmembers", "params": {"options": {"conversation_id": conversation_id}}}
    )
    members = get_members(channel_members)
    return members


async def sync(event, bot):
    conv_id = event.msg.conv_id
    channel = event.msg.channel.name
    members = await get_channel_members(conv_id, bot)

    team = s.query(Team).filter(Team.name.match(channel)).first()
    if not team:
        new_team = Team(name=channel)
        s.add(new_team)

    for member in members:
        user = s.query(User).filter(User.username.match(member)).first()
        if not user:
            new_user = User(username=member)
            team = s.query(Team).filter(Team.name.match(channel)).first()
            new_user.teams = [team]
            s.add(new_user)
    await bot.chat.react(conv_id, event.msg.id, ":arrows_clockwise:")
    s.commit()
    s.close()
