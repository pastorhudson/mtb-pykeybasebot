import logging

from botcommands.scorekeeper import write_score

logging.basicConfig(level=logging.DEBUG)



async def award_activity_points(event, command_list):
    # await sync(event=event, bot=bot)
    # msg_id = event.msg.id
    # conversation_id = event.msg.conv_id
    # members = await get_channel_members(conversation_id. bot)
    # channel_name = str(event.msg.channel.name).replace(",", "")
    if event.msg.content.type_name == "text":

        team_name = event.msg.channel.name
        logging.info(f'Giving {event.msg.sender.username} 11 pts')
        if str(event.msg.content.text.body).startswith("!"):
            score = write_score('@marvn', event.msg.sender.username, team_name, 3, description='sent msg')
        else:
            score = write_score('@marvn', event.msg.sender.username, team_name, len(str(event.msg.content.text.body)), description='sent msg')
    if event.msg.content.type_name == 'reaction' and event.msg.sender.username != '@marvn':
        team_name = event.msg.channel.name
        logging.info(f'Giving {event.msg.sender.username} 4 pts')
        score = write_score('@marvn', event.msg.sender.username, team_name, 4, description='sent msg')
    pass
