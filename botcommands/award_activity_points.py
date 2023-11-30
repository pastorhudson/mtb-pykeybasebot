from botcommands.scorekeeper import write_score
from botcommands.sync import sync


async def award_activity_points(event, bot):
    await sync(event=event, bot=bot)

    # msg_id = event.msg.id
    conversation_id = event.msg.conv_id
    # members = await get_channel_members(conversation_id. bot)
    # channel_name = str(event.msg.channel.name).replace(",", "")
    team_name = event.msg.channel.name
    score = write_score(event.msg.sender.username, '@marvn', team_name, 11, description='sent msg')
    pass

# def award(event):
#     if str(event.msg.content.text.body).startswith("!award"):
#         await sync(event=event, bot=bot)
#
#         pts_max = 5000
#
#         instructions = f"You have failed. I'm not surprised.\n" \
#                        f"```You can only give points to someone in this chat.\n" \
#                        f"You can't give more than {pts_max} points at a time.\n" \
#                        f"You can't give negative points.\n" \
#                        f"Points must be whole numbers.\n" \
#                        f"No cutesy extra characters, or I'll deduct from your score.\n" \
#                        f"You can't give points to yourself.```\n" \
#                        f"Usage: `!award <@user> <points> <description>`"
#         msg_id = event.msg.id
#         conversation_id = event.msg.conv_id
#         members = await get_channel_members(conversation_id)
#         channel_name = str(event.msg.channel.name).replace(",", "")
#         team_name = event.msg.channel.name
#         description = " ".join(str(event.msg.content.text.body).split(' ')[3:]).strip()
#         try:
#             user = None
#             points = None
#             for word in str(event.msg.content.text.body).split(' '):
#                 if RepresentsInt(word) and not points:
#                     points = int(word.strip(punctuation))
#                 elif word.startswith('@') and not user:
#                     user = str(word.strip("@").rstrip(punctuation))
#             logging.info(f"{event.msg.sender.username} is trying to give {user} {points}pts.")
#             if not points:
#                 await bot.chat.send(conversation_id, instructions)
#
#             if points < 0 and event.msg.sender.username != 'pastorhudson':
#                 logging.info("Points are Negative!")
#                 user = event.msg.sender.username
#                 score = write_score(user, event.msg.sender.username, team_name, -500, description=description)
#                 await bot.chat.send(conversation_id,
#                                     f"`-500` points awarded to @{user}. I'm the only negative one around here.")
#             if user in members:
#                 logging.info("User is in members")
#             if user != event.msg.sender.username:
#                 logging.info(f"{event.msg.sender.username} is not {user}")
#             if points <= pts_max:
#                 logging.info(f"{points} is less than or equal to {pts_max}")
#             if user in members and user != event.msg.sender.username and points <= pts_max:
#                 score = write_score(user, event.msg.sender.username, team_name, points, description=description)
#                 await bot.chat.react(conversation_id, msg_id, ":marvin:")
#
#             else:
#                 await bot.chat.send(conversation_id, instructions)
#         except Exception as e:
#             write_score('marvn', event.msg.sender.username, team_name, -5, description=description)
#             await bot.chat.send(conversation_id,
#                                 f"You did it wrong.\n `-5` points deducted from  @{event.msg.sender.username} "
#                                 f"for trying to be cute.\n{instructions}")
