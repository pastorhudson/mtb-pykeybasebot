import logging

from botcommands.scorekeeper import write_score

logging.basicConfig(level=logging.DEBUG)


async def award_activity_points(event):

    if event.msg.content.type_name == "text":
        team_name = event.msg.channel.name

        if str(event.msg.content.text.body).startswith("!"):
            score = write_score('@marvn', event.msg.sender.username, team_name, 3, description='sent msg')
        elif event.msg.sender.username != 'marvn':
            logging.info(f'Giving {event.msg.sender.username} {len(str(event.msg.content.text.body))}pts')
            score = write_score('@marvn', event.msg.sender.username, team_name, len(str(event.msg.content.text.body)), description='msg')
    if event.msg.content.type_name == 'reaction' and event.msg.sender.username != 'marvn':
        team_name = event.msg.channel.name
        logging.info(f'Giving {event.msg.sender.username} 4 pts')
        score = write_score('@marvn', event.msg.sender.username, team_name, 4, description='react')
    pass
