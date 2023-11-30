import logging

from botcommands.scorekeeper import write_score

logging.basicConfig(level=logging.DEBUG)


async def award_activity_points(event):
    # await sync(event=event, bot=bot)
    # msg_id = event.msg.id
    # conversation_id = event.msg.conv_id
    # members = await get_channel_members(conversation_id. bot)
    # channel_name = str(event.msg.channel.name).replace(",", "")
    if event.msg.content.type_name == "text":

        team_name = event.msg.channel.name
        logging.info(f'Giving {event.msg.sender.username} 11 pts')
        score = write_score(event.msg.sender.username, '@marvn', team_name, 11, description='sent msg')
    if event.msg.content.type_name == 'reaction':
        team_name = event.msg.channel.name
        logging.info(f'Giving {event.msg.sender.username} 4 pts')
        score = write_score(event.msg.sender.username, '@marvn', team_name, 4, description='sent msg')
    pass
