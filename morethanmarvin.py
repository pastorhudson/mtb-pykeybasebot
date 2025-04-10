#!/usr/bin/env python3
import asyncio
import logging
import os
import sys
from pprint import pprint
from string import punctuation
import json
from botcommands.morse import get_morse_code
from botcommands.natural_chat import get_chat, get_marvn_reaction, get_chat_with_image
from botcommands.jokes import get_joke
from botcommands.news import get_top_hacker_news
from botcommands.since import set_since, get_since, reset_since, reset_sign
# from botcommands.poll_results import get_poll_result
from botcommands.tldr import tldr_react, get_gpt_summary
import re
import random
import pykeybasebot.types.chat1 as chat1
from botcommands.utils import download_image
from botcommands.weather import get_weather
from pykeybasebot import Bot
from botcommands.youtube_dlp import get_mp3, get_mp4, get_meta
from urllib.parse import urlparse
from botcommands.covid import get_covid
from botcommands.get_screenshot import get_screenshot
from botcommands.cow_say import cowsay
from botcommands.meh import get_meh
from botcommands.draw_dallie import generate_dalle_image
from botcommands.drwho import get_drwho
from botcommands.stardate import get_stardate
from botcommands.chuck import get_new_chuck
from botcommands.till import get_till, set_till
from botcommands.cow_characters import get_characters
from botcommands.morningreport import get_morningreport
from botcommands.scorekeeper import get_score, write_score, sync_score
from botcommands.get_members import get_members
from pathlib import Path
from botcommands.bible import get_esv_text
from botcommands.wager import get_wagers, make_wager, make_bet, payout_wager
from botcommands.sync import sync
from models import Team, User, Point, Location, Wager, Message
from crud import s
from botcommands.get_grades import get_academic_snapshot
from botcommands.eyebleach import get_eyebleach
from botcommands.checkspeed import get_speed
from botcommands.poll import make_poll
# from botcommands.award_activity_points import award_activity_points
from botcommands.db_events import is_morning_report, write_morning_report_task
from botcommands.school_closings import get_school_closings
from botcommands.wordle import solve_wordle
from botcommands.send_queue import process_message_queue
from botcommands.curl_commands import get_curl, extract_message_sender
from pykeybasebot.types import chat1
from datetime import timedelta
from botcommands.open_ai_agent import handle_marvn_mention_with_context


logging.basicConfig(level=logging.DEBUG)


if "win32" in sys.platform:
    # Windows specific event-loop policy
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy()  # type: ignore
    )


async def get_channel_members(conversation_id):
    channel_members = await bot.chat.execute(
        {"method": "listmembers", "params": {"options": {"conversation_id": conversation_id}}}
    )
    members = get_members(channel_members)
    return members


async def set_unfurl(unfurl):
    if unfurl:
        furl = await bot.chat.execute(
            {"method": "setunfurlsettings",
             "params": {"options": {"mode": "always"}}})
    else:
        furl = await bot.chat.execute(
            {"method": "setunfurlsettings",
             "params": {"options": {"mode": "never"}}})
    return


def RepresentsInt(s):
    try:
        int(s)
        return True
    except Exception as e:
        return False


class Points(object):
    pass


async def handler(bot, event):
    command_list = [
        # {"name": "aoc",
        #  "description": "Make me solve the advent of code puzzle.",
        #  "usage": "<year> <day> <part>"},
        {"name": "award",
         "description": "Force me to give completely meaningless points to your comrades.",
         "usage": "<user> <points>"},
        {"name": "bible",
         "description": "Force me to lookup Bible txt.",
         "usage": "<reference> OR <search string>"},
        # {"name": "canary",
        #  "description": "Force me to give Virus Total your nasty URL and return scan results.",
        #  "usage": "<url>"},
        {"name": "chuck",
         "description": "Forces me to tell a terribly jouvinile possibly NSFW joke randomly mentioning someone in this channel.",
         "usage": "chuck"},
        # {"name": "covid",
        #  "description": "Force me to morbidly retrieve covid numbers for a State County or State.",
        #  "usage": "<State> <County> <- Optional Fields"},
        {"name": "cow",
         "description": f"Now I can't even explain this. You are a monster. Optional Characters: {get_characters()}",
         "usage": "<character> <msg>"},
        {"name": "draw",
         "description": "Forces me to draw a picture using dall-e-3.",
         "usage": "<prompt>"},
        {"name": "stabledraw",
         "description": "Forces me to draw a picture using stable diffusion.",
         "usage": "<prompt>"},
        {"name": "drwho",
         "description": "Return Dr Who Episode.",
         "usage": "<ep_id> OR <Ep Title>"},
        {"name": "eyebleach",
         "description": "Returns images from r/eyebleach. Default = 3",
         "usage": "<bleach_level> 1-11"},
        # {"name": "files",
        #  "description": "Returns list of files on marvin",
        #  "usage": ""},
        {"name": "grades",
         "description": "Retrieve current academic snapshot from pa-cyber.",
         "usage": "RESTRICTED"},
        {"name": "help",
         "description": "See a menu of options for ruining my life by making me do menial tasks.",
         "usage": ""},
        {"name": "joke",
         "description": "Forces me to tell a joke. For the love of God just don't.",
         "usage": ""},
        {"name": "meh",
         "description": "Get's today's meh.",
         "usage": ""},
        # {"name": "meet",
        #  "description": "Get video conference link.",
        #  "usage": "<Conference Name>"},
        # {"name": "morbidity",
        #  "description": "Return data about current mass shootings in the US.",
        #  "usage": ""},
        {"name": "morse",
         "description": "Translate morsecode to english.",
         "usage": ""},
        {"name": "morningreport",
         "description": "Gets today's morning report.",
         "usage": ""},
        {"name": "news",
         "description": "Gets the top x articles from hackernews.",
         "usage": "optional num of articles"},
        {"name": "poll",
         "description": "Start a poll",
         "usage": '"Should we deactivate our neural engines?" "Yes" "No"'},
        {"name": "payout",
         "description": "Pays out a wager.",
         "usage": "<#wager> <True/False>"},
        # {"name": "pollresult",
        #  "description": "RealClear Politics National and Pennsylvania Poll Results.",
        #  "usage": ""},
        {"name": "closings",
         "description": "Forces me go to get the SW PA school closings.",
         "usage": "Optional: <school name>, <school name>"},
        {"name": "screenshot",
         "description": "Forces me go to a url and send a screenshot.",
         "usage": "<url>"},
        {"name": "set",
         "description": "Admin command for setting various things",
         "usage": ""},
        {"name": "speed",
         "description": "Forces me check upload download speed.",
         "usage": ""},
        {"name": "score",
         "description": "Get the score for who abuses me the most.",
         "usage": ""},
        {"name": "since",
         "description": "Gives the days SINCE events.",
         "usage": "<name> -t <datetime> adds event. -r #number resets since. <no_arguments> lists all sinces."},
        {"name": "stardate",
         "description": " Print's the current stardate if no stardate is given.",
         "usage": "<stardate> <- Optional"},
        {"name": "test",
         "description": "Just check to see if I'm regretfully still here.",
         "usage": ""},
        {"name": "till",
         "description": "Gives the days TILL events.",
         "usage": "<event_name> -t <event_datetime> adds event.\n<no_arguments> lists all tills."},
        {"name": "tldr",
         "description": "Forces me to read an entire article and then summarize it because you're lazy.",
         "usage": "<url>"},
        # {"name": "vac",
        #  "description": "Get Vaccine Distributation data from health.pa.gov",
        #  "usage": ""},
        # {"name": "waffle",
        #  "description": "Get the currently closed Waffle Houses",
        #  "usage": "Optional <state>"},
        {"name": "wager",
         "description": "Forces me to setup a silly bet with points that don't matter.",
         "usage": "<points wagered> <The Event or Thing your betting upon>"},
        # {"name": "yt",
        #  "description": "Forces me to go get meta data about a youtube video.",
        #  "usage": "<url>"},
        {"name": "ytm",
         "description": "Forces me to get metadata and download the stupid thing as an mp3.",
         "usage": "<url>"},
        {"name": "ytv",
         "description": "Forces me to get metadata and download the stupid thing.",
         "usage": "<url>"},
        {"name": "wordle",
         "description": "Retrieve today's wordle to ensure you always win.",
         "usage": "optional <date>"},
        {"name": "transmit",
         "description": "Get curl command to send a message to the current chat conversation.",
         "usage": "<message> <optional> -sender <sender>"},
        {"name": "weather",
         "description": "Get Uniontown Weather.",
         "usage": ""}
    ]

    # If there's an attachment check if we send this to @marvn
    try:
        if event.msg.content.type_name == 'attachment':
            if str(event.msg.content.attachment.object.title).startswith("@marvn"):
                await sync(event=event, bot=bot)
                pprint(event.msg.content)

                await handle_marvn_mention_with_context(bot, event)
        elif str(event.msg.content.attachment.object.title).startswith("@marvn"):
            pprint(event.msg.content)
            logging.info(f"Sending attachment event to handle_marvn_mention_with_context")
            await handle_marvn_mention_with_context(bot, event)

    except Exception as e:
        logging.error(f"Error handling attachment: {str(e)}")
        logging.error(f"Type: {type(e)}")
        print("Not an attachment or error processing attachment")

    try:
        logging.info(f"event.msg.content.text.reply_to {event.msg.content.text.reply_to}")
        logging.info(event)

        if (hasattr(event.msg.content, 'text') and
                event.msg.content.text is not None and
                event.msg.content.text.reply_to):
            logging.info(f"I've identified a replyto")
            original_msg_info = await bot.chat.get(event.msg.conv_id, event.msg.content.text.reply_to)
            original_msg = original_msg_info.message[0]['msg']
            original_sender = original_msg.get('sender', {}).get('username', 'unknown')
            if original_sender == 'marvn':
                await sync(event=event, bot=bot)
                await handle_marvn_mention_with_context(bot, event)

            elif (str(event.msg.content.text.body).lower().startswith("@marvn") or
                  hasattr(event.msg.content, 'at_mention_usernames') and "marvn" in
                  event.msg.content.at_mention_usernames):
                await sync(event=event, bot=bot)
                await handle_marvn_mention_with_context(bot, event)

        elif (str(event.msg.content.text.body).lower().startswith("@marvn") or
              hasattr(event.msg.content, 'at_mention_usernames') and "marvn" in
              event.msg.content.at_mention_usernames):
            await sync(event=event, bot=bot)
            await handle_marvn_mention_with_context(bot, event)
    except Exception as e:
        logging.info(e)

    # logging.info(event.msg.content)

    if event.msg.content.type_name == 'reaction':
        if event.msg.content.reaction.body == ":white_check_mark:" or ':no_entry_sign:':
            if event.msg.sender.username != 'marvn' or event.msg.sender.username != 'morethanmarvin':

                try:
                    team_name = event.msg.channel.name
                    username = event.msg.sender.username
                    msg_id = event.msg.content.reaction.message_id
                    message = s.query(Message).filter_by(msg_id=str(msg_id)).first()

                    points = message.wager.points
                    wager_id = message.wager.id
                    if event.msg.content.reaction.body == ":white_check_mark:":
                        position = True
                    elif event.msg.content.reaction.body == ":no_entry_sign:":
                        position = False
                    else:
                        raise ValueError
                    msg = make_bet(team_name, username, points, position, wager_id)
                    await bot.chat.edit(event.msg.conv_id, msg_id, msg)
                except ValueError as e:
                    print(e)
                    print("ValueError")
                except AttributeError:
                    pass

    if event.msg.content.type_name == 'reaction':
        if event.msg.content.reaction.body == ":marvin:":
            if event.msg.sender.username != 'marvn' or event.msg.sender.username != 'morethanmarvin':

                msg = await bot.chat.get(event.msg.conv_id, event.msg.content.reaction.message_id)
                """Handle text on attachments"""
                try:
                    original_body = msg.message[0]['msg']['content']['text']['body']
                except KeyError:
                    original_body = msg.message[0]['msg']['content']['attachment']['object']['title']

                try:
                    username = event.msg.sender.username
                    conversation_id = event.msg.conv_id

                    msg = get_marvn_reaction(username, event.msg.content.text.body)
                    await bot.chat.send(conversation_id, msg)

                except ValueError as e:
                    print(e)
                    print("ValueError")
                except AttributeError:
                    pass

    if event.msg.content.type_name == 'reaction':
        if event.msg.content.reaction.body == ":tv:":
            if event.msg.sender.username != 'marvn' and event.msg.sender.username != 'morethanmarvin':
                conversation_id = event.msg.conv_id

                msg = await bot.chat.get(event.msg.conv_id, event.msg.content.reaction.message_id)
                try:
                    original_body = msg.message[0]['msg']['content']['text']['body']
                except KeyError:
                    original_body = msg.message[0]['msg']['content']['attachment']['object']['title']
                original_msg_id = msg.message[0]['msg']['id']
                reactions = msg.message[0]['msg']['reactions']
                reaction_list = []
                for key, value in reactions.items():
                    for k, v in value.items():
                        try:
                            if v['users']['marvn']:
                                reaction_list.append(k)
                        except KeyError:
                            pass
                if ':tv:' in reaction_list:
                    team_name = event.msg.channel.name
                    fail_msg = f"`-1000pts` awarded to @{event.msg.sender.username} for spamming :tv:"
                    score = write_score(event.msg.sender.username, 'marvn',
                                        team_name, -1000, description=fail_msg)
                    await bot.chat.send(conversation_id, fail_msg)

                else:
                    urls = re.findall(r'(https?://[^\s]+)', original_body)
                    await bot.chat.react(conversation_id, original_msg_id, ":tv:")
                    ytv_payload = await get_mp4(urls[0])
                    if ytv_payload['file']:
                        ytv_msg = ytv_payload['msg']
                        try:

                            await bot.chat.attach(channel=conversation_id,
                                                  filename=ytv_payload['file'],
                                                  title=ytv_msg)

                        except TimeoutError:
                            pass

    if event.msg.content.type_name == 'reaction':
        if event.msg.content.reaction.body == ":headphones:":
            if event.msg.sender.username != 'marvn' and event.msg.sender.username != 'morethanmarvin':
                conversation_id = event.msg.conv_id

                msg = await bot.chat.get(event.msg.conv_id, event.msg.content.reaction.message_id)
                """Handle text on attachments"""
                try:
                    original_body = msg.message[0]['msg']['content']['text']['body']
                except KeyError:
                    original_body = msg.message[0]['msg']['content']['attachment']['object']['title']
                original_msg_id = msg.message[0]['msg']['id']
                reactions = msg.message[0]['msg']['reactions']
                reaction_list = []
                for key, value in reactions.items():
                    for k, v in value.items():
                        try:
                            if v['users']['marvn']:
                                reaction_list.append(k)
                        except KeyError:
                            pass
                print(reaction_list)
                if ':headphones:' in reaction_list:
                    team_name = event.msg.channel.name
                    fail_msg = f"`-379pts` awarded to @{event.msg.sender.username} for spamming :headphones:"
                    score = write_score(event.msg.sender.username, 'marvn',
                                        team_name, -379, description=fail_msg)
                    await bot.chat.send(conversation_id, fail_msg)

                else:
                    urls = re.findall(r'(https?://[^\s]+)', original_body)
                    await bot.chat.react(conversation_id, original_msg_id, ":headphones:")
                    ytv_payload = get_mp3(urls[0])
                    if ytv_payload['file']:
                        ytv_msg = ytv_payload['msg']
                        try:

                            await bot.chat.attach(channel=conversation_id,
                                                  filename=ytv_payload['file'],
                                                  title=ytv_msg)

                        except TimeoutError:
                            pass

    if event.msg.content.type_name == 'reaction':
        if event.msg.content.reaction.body == ":camera:":
            if event.msg.sender.username != 'marvn' and event.msg.sender.username != 'morethanmarvin':
                conversation_id = event.msg.conv_id

                msg = await bot.chat.get(event.msg.conv_id, event.msg.content.reaction.message_id)

                try:
                    original_body = msg.message[0]['msg']['content']['text']['body']
                except KeyError:
                    original_body = msg.message[0]['msg']['content']['attachment']['object']['title']
                original_msg_id = msg.message[0]['msg']['id']
                reactions = msg.message[0]['msg']['reactions']
                reaction_list = []
                for key, value in reactions.items():
                    for k, v in value.items():
                        try:
                            if v['users']['marvn']:
                                reaction_list.append(k)
                        except KeyError:
                            pass
                if ':camera:' in reaction_list:
                    team_name = event.msg.channel.name
                    fail_msg = f"`-1200pts` awarded to @{event.msg.sender.username} for spamming :camera:"
                    score = write_score(event.msg.sender.username, 'marvn',
                                        team_name, -1200, description=fail_msg)
                    await bot.chat.send(conversation_id, fail_msg)

                else:

                    urls = re.findall(r'(https?://[^\s]+)', original_body)
                    await bot.chat.react(conversation_id, original_msg_id, ":camera:")
                    try:
                        screenshot_payload = get_screenshot(urls[0])
                        if screenshot_payload['file']:
                            await bot.chat.attach(channel=conversation_id,
                                                  filename=screenshot_payload['file'],
                                                  title=screenshot_payload['msg'])
                    except IndexError as e:
                        pass

    if event.msg.content.type_name == 'reaction':
        if event.msg.content.reaction.body == ":notebook:":
            tldr_length = 3

            await tldr_react(event, bot, tldr_length)

    if event.msg.content.type_name == 'reaction':
        team_name = event.msg.channel.name
        username = event.msg.sender.username
        if team_name == "morethanbits":
            if event.msg.content.reaction.body == ":tap-the-sign:":
                reset_sign(team_name, "#8", username)

    if event.msg.content.type_name == 'reaction':
        if event.msg.content.reaction.body in [":mag:", ":zuckerberg:" ]:
            conversation_id = event.msg.conv_id
            # await bot.chat.react(conversation_id, event.msg.id, ":mag:")
            # await bot.chat.react(conversation_id, event.msg.id, ":zuckerberg:")

            await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

            msg = await bot.chat.get(event.msg.conv_id, event.msg.content.reaction.message_id)
            original_body = msg.message[0]['msg']['content']['text']['body']
            url = re.findall(r'(https?://[^\s]+)', original_body)
            yt_urls = re.findall(r'(https?://[^\s]+)', original_body)
            conversation_id = event.msg.conv_id

            if 'youtube' in yt_urls[0] or 'youtu.be' in yt_urls[0]:
                try:
                    await set_unfurl(unfurl=False)
                except Exception as e:
                    logging.info(e)

                await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

                yt_payload = get_meta(yt_urls[0])
                yt_msg = yt_payload['msg']
                logging.info(yt_msg)
                await bot.chat.reply(conversation_id, event.msg.id, yt_msg)
                # await bot.chat.react(conversation_id, event.msg.id, ":vhs:")

            else:
                yt_payload = get_meta(yt_urls[0])
                yt_msg = yt_payload['msg']
                # if is_supported(yt_urls[0]):
                if "That video url didn't work." not in yt_msg:
                    await bot.chat.react(conversation_id, event.msg.id, ":no_entry_sign:")


    if event.msg.content.type_name != chat1.MessageTypeStrings.TEXT.value:
        return
    if event.msg.content.type_name != chat1.MessageTypeStrings.TEXT.value:
        return

    # context.add_message(event.msg.content.text.body)

    if str(event.msg.content.text.body).startswith("!award"):
        await sync(event=event, bot=bot)

        pts_max = 5000

        instructions = f"You have failed. I'm not surprised.\n" \
                       f"```You can only give points to someone in this chat.\n" \
                       f"You can't give more than {pts_max} points at a time.\n" \
                       f"You can't give negative points.\n" \
                       f"Points must be whole numbers.\n" \
                       f"No cutesy extra characters, or I'll deduct from your score.\n" \
                       f"You can't give points to yourself.```\n" \
                       f"Usage: `!award <@user> <points> <description>`"
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        members = await get_channel_members(conversation_id)
        channel_name = str(event.msg.channel.name).replace(",", "")
        team_name = event.msg.channel.name
        description = " ".join(str(event.msg.content.text.body).split(' ')[3:]).strip()
        try:
            user = None
            points = None
            for word in str(event.msg.content.text.body).split(' '):
                if RepresentsInt(word) and not points:
                    points = int(word.strip(punctuation))
                elif word.startswith('@') and not user:
                    user = str(word.strip("@").rstrip(punctuation))
            logging.info(f"{event.msg.sender.username} is trying to give {user} {points}pts.")
            if not points:
                await bot.chat.send(conversation_id, instructions)

            if points < 0 and event.msg.sender.username != 'pastorhudson':
                logging.info("Points are Negative!")
                user = event.msg.sender.username
                score = write_score(user, event.msg.sender.username, team_name, -500, description=description)
                await bot.chat.send(conversation_id,
                                    f"`-500` points awarded to @{user}. I'm the only negative one around here.")
            if user in members:
                logging.info("User is in members")
            if user != event.msg.sender.username:
                logging.info(f"{event.msg.sender.username} is not {user}")
            if points <= pts_max:
                logging.info(f"{points} is less than or equal to {pts_max}")
            if user in members and user != event.msg.sender.username and points <= pts_max:
                score = write_score(user, event.msg.sender.username, team_name, points, description=description)
                await bot.chat.react(conversation_id, msg_id, ":marvin:")

            else:
                await bot.chat.send(conversation_id, instructions)
        except Exception as e:
            write_score('marvn', event.msg.sender.username, team_name, -42, description=description)
            await bot.chat.send(conversation_id,
                                f"You did it wrong.\n `-42` points deducted from  @{event.msg.sender.username} "
                                f"for trying to be cute.\n{instructions}")



    if str(event.msg.content.text.body).startswith("!bible"):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        passage = str(event.msg.content.text.body)[7:]
        msg = get_esv_text(passage)
        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!biblemorse"):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        passage = str(event.msg.content.text.body)[7:]
        msg = get_morse_code(get_esv_text(passage, plain_txt=True))
        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith('!chuck'):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        channel_members = await get_channel_members(conversation_id)
        # try:
        #     name = str(event.msg.content.text.body)[7:]
        #     chuck_msg = get_chuck(name=name, channel_members=channel_members)
        # except:
        #     chuck_msg = get_chuck(channel_members=channel_members)
        chuck_msg = get_new_chuck()
        my_msg = await bot.chat.reply(conversation_id, event.msg.id, chuck_msg)

    if str(event.msg.content.text.body).startswith('!covid'):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        try:
            state = str(event.msg.content.text.body).split(' ')[1]
        except IndexError:
            state = None
        try:
            county = str(event.msg.content.text.body).split(' ')[2]
        except IndexError:
            county = None
        msg = get_covid(state, county)
        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!cow"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        msg = cowsay(str(event.msg.content.text.body)[5:])
        my_msg = await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith('!draw'):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        prompt = event.msg.content.text.body[6:]
        draw_payload = await generate_dalle_image(prompt)
        if draw_payload['file']:
            await bot.chat.react(conversation_id, event.msg.id, ":floppy_disk:")

            await bot.chat.attach(channel=conversation_id,
                                  filename=draw_payload['file'],
                                  title=draw_payload['msg'])
        else:
            await bot.chat.reply(conversation_id, event.msg.id, draw_payload['msg'])

    if str(event.msg.content.text.body).startswith("!drwho"):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        msg = get_drwho(str(event.msg.content.text.body)[7:])
        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!eyebleach"):
        try:
            await set_unfurl(unfurl=True)
        except Exception as e:
            logging.info(e)
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        try:
            bleach_level = str(event.msg.content.text.body).split(" ")[1]
            msg = get_eyebleach(int(bleach_level))

        except TypeError:
            msg = get_eyebleach()
            await bot.chat.send(conversation_id, msg)

        except ValueError:
            msg = get_eyebleach()

        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!grades"):
        conversation_id = event.msg.conv_id
        if event.msg.sender.username == 'pastorhudson' or event.msg.sender.username == 'sakanakami':
            await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
            grades = get_academic_snapshot()
            await bot.chat.send(conversation_id, grades)
        else:
            await bot.chat.send(conversation_id, "This is a private command.")

    if str(event.msg.content.text.body).startswith("!help"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        help = "Here are the commands I currently am enslaved to:\n\n"
        help += "\n".join(
            ["`!" + x['name'] + " " + x['usage'] + "` ```" + x['description'] + "```" for x in command_list])
        await bot.chat.send(conversation_id, help)

    if str(event.msg.content.text.body).startswith("!joke"):
        conversation_id = event.msg.conv_id

        joke = get_joke(observation=False)
        prompt = joke
        draw_payload = await generate_dalle_image(prompt)
        if draw_payload['file']:
            # await bot.chat.react(conversation_id, event.msg.id, ":floppy_disk:")

            await bot.chat.attach(channel=conversation_id,
                                  filename=draw_payload['file'],
                                  title=joke)
        else:
            await bot.chat.reply(conversation_id, event.msg.id, draw_payload['msg'])
        # await bot.chat.send(conversation_id, joke)


    if str(event.msg.content.text.body).startswith("!morningreport"):
        try:
            await set_unfurl(unfurl=False)
        except Exception as e:
            logging.info(e)
        await sync(event=event, bot=bot)
        conversation_id = event.msg.conv_id
        channel_name = str(event.msg.channel.name)
        channel_members = await get_channel_members(conversation_id)
        meh_img = str(Path('./storage/meh.png').absolute())
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        msg = await get_morningreport(channel=channel_name)

        await bot.chat.send(conversation_id, msg[0])
        # file = str(meh_img.absolute())
        await bot.chat.attach(channel=conversation_id,
                              filename=meh_img,
                              title=msg[1])
        joke = msg[3]
        prompt = joke
        draw_payload = await generate_dalle_image(prompt)
        if draw_payload['file']:
            # await bot.chat.react(conversation_id, event.msg.id, ":floppy_disk:")

            await bot.chat.attach(channel=conversation_id,
                                  filename=draw_payload['file'],
                                  title=joke)
        else:
            await bot.chat.reply(conversation_id, event.msg.id, draw_payload['msg'])
        await bot.chat.send(conversation_id, msg[2])
        await bot.chat.send(conversation_id, msg[4])
        await bot.chat.send(conversation_id, msg[5])


    if str(event.msg.content.text.body).startswith("!news"):
        try:
            await set_unfurl(unfurl=False)
        except Exception as e:
            logging.info(e)
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        try:
            news_level = str(event.msg.content.text.body).split(" ")[1]
            msg = get_top_hacker_news(num_articles=int(news_level))

        except TypeError:
            msg = get_top_hacker_news()
            await bot.chat.send(conversation_id, msg)

        except ValueError:
            msg = get_top_hacker_news()

        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith('!morse'):
        conversation_id = event.msg.conv_id

        morse_code = get_morse_code(event.msg.content.text.body[7:])

        await bot.chat.send(conversation_id, morse_code)

    if str(event.msg.content.text.body).startswith("!payout"):
        await sync(event=event, bot=bot)
        conversation_id = event.msg.conv_id
        username = event.msg.sender.username
        team_name = event.msg.channel.name
        payload = str(event.msg.content.text.body)[8:].split(" ")
        try:
            if payload[0][0] != '#':
                raise ValueError
            elif payload[1].lower() != "true" and payload[1].lower() != 'false':
                raise ValueError
            else:
                msg = await payout_wager(username=username, team_name=team_name, wager_id=int(payload[0][1:]),
                                         result=payload[1], bot=bot)

                await bot.chat.send(conversation_id, msg)

        except ValueError as e:
            print(e)
            await bot.chat.send(conversation_id, "This is a disaster. You've probably corrupted my database.\n"
                                                 "It's probably pointless to go on.\n"
                                                 "Usage: !payout <#wager> <True/False>\n"
                                                 "Example: `!payout #3 True`")
        except IndexError:
            await bot.chat.send(conversation_id, "This is a disaster. You've probably corrupted my database.\n"
                                                 "It's probably pointless to go on.\n"
                                                 "Usage: !payout <#wager> <True/False>\n"
                                                 "Example: `!payout #3 True`")

    # if str(event.msg.content.text.body).startswith("!pollresult"):
    #     channel = event.msg.channel.name
    #     msg_id = event.msg.id
    #     conversation_id = event.msg.conv_id
    #     await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
    #     polls = get_poll_result(channel)
    #     await bot.chat.send(conversation_id, polls)

    if str(event.msg.content.text.body).startswith("!poll"):
        await bot.chat.react(event.msg.conv_id, event.msg.id, ":marvin:")
        channel = event.msg.channel.name
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        poll = make_poll(event.msg.content.text.body)
        if not poll[1]:
            await bot.chat.send(conversation_id, poll[0])
        else:
            poll_msg = await bot.chat.send(conversation_id, poll[0])
            for emoji in poll[1]:
                await bot.chat.react(conversation_id, poll_msg.message_id, emoji)

    if str(event.msg.content.text.body).startswith("!set"):
        await bot.chat.react(event.msg.conv_id, event.msg.id, ":marvin:")
        if event.msg.sender.username != 'pastorhudson':
            await bot.chat.send(event.msg.conv_id, "These are not the commands you are looking for.")
        else:
            payload = str(event.msg.content.text.body).split(" ")
            try:
                if payload[1] == '':
                    raise IndexError
                if payload[1] == "local:add":
                    team = s.query(Team).filter_by(name=event.msg.channel.name).first()
                    new_local = Location(state=payload[2], county=payload[3])
                    team.location.append(new_local)
                    s.commit()
                    msg = team.location.all()
                    s.close()
                    await bot.chat.send(event.msg.conv_id, str(msg))
                if payload[1] == "local:del":
                    team = s.query(Team).filter_by(name=event.msg.channel.name).first()
                    index = int(payload[2])
                    del_loc = team.location.all()[index]
                    s.delete(del_loc)
                    s.commit()
                    msg = team.location.all()
                    s.close()
                    await bot.chat.send(event.msg.conv_id, str(msg))


            except IndexError:
                team = s.query(Team).filter_by(name=event.msg.channel.name).first()
                msg = "Current Settings:\n" \
                      f"```{team.location.all()}```"
                msg += "Set Commands:\n" \
                       "local:add <state> <county>\n" \
                       "wager:end <#wager> <datetime>\n" \
                       ""
                await bot.chat.send(event.msg.conv_id, msg)
            except AttributeError:
                msg = "Team not Sync'd I'll Sync it now. Try again in a little bit."
                await bot.chat.send(event.msg.conv_id, msg)
                await sync(event=event, bot=bot)

    if str(event.msg.content.text.body).startswith("!score"):
        await sync(event=event, bot=bot)

        channel = event.msg.channel
        msg_id = event.msg.id
        channel_name = str(event.msg.channel.name).replace(",", "")
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        channel_members = await get_channel_members(conversation_id)
        try:
            year = int(event.msg.content.text.body.split(' ')[1])
            score = get_score(channel_name=channel.name, year=year)
        except (ValueError, IndexError):
            score = get_score(channel_name=channel.name)
        await bot.chat.send(conversation_id, score)

    if str(event.msg.content.text.body).startswith("!teams"):
        if event.msg.sender.username == 'pastorhudson':
            t = s.query(Team).all()
            await bot.chat.send(event.msg.conv_id, str(t))

    if str(event.msg.content.text.body).startswith("!users"):
        if event.msg.sender.username == 'pastorhudson':
            u = s.query(User).all()
            await bot.chat.send(event.msg.conv_id, str(u))

    if str(event.msg.content.text.body).startswith("!points"):
        if event.msg.sender.username == 'pastorhudson':
            u = s.query(Point).all()
            await bot.chat.send(event.msg.conv_id, str(u))

    if str(event.msg.content.text.body).startswith("!syncscore"):
        await sync(event=event, bot=bot)
        if event.msg.sender.username == 'pastorhudson':
            sync_score(channel=event.msg.channel.name)
            msg = "Scyn'd csv score with DB"
        else:
            msg = "You're not authorized to run this command."
        await bot.chat.send(event.msg.conv_id, msg)

    if str(event.msg.content.text.body).startswith(":tap-the-sign:"):
        # channel = event.msg.channel
        # msg_id = event.msg.id
        # conversation_id = event.msg.conv_id

        team_name = event.msg.channel.name
        username = event.msg.sender.username
        reset_sign(team_name, "#8", username)

    if str(event.msg.content.text.body).startswith('!tldr'):
        urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        tldr = await get_gpt_summary(urls[0])
        if tldr:
            await bot.chat.reply(conversation_id, event.msg.id, tldr)
        else:
            await bot.chat.react(conversation_id, event.msg.id, ":no_entry:")
        await sync(event=event, bot=bot)



    if str(event.msg.content.text.body).startswith('!meh'):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        meh_img = str(Path('./storage/meh.png').absolute())
        msg = await get_meh()
        await bot.chat.attach(channel=conversation_id,
                              filename=meh_img,
                              title=msg)

    if str(event.msg.content.text.body).startswith("!transmit"):
        logging.info("Running msg")
        sender = None
        dm_channel = f'marvn,{event.msg.sender.username}'
        channel = chat1.ChatChannel(name=dm_channel)
        try:
            send_msg, sender = extract_message_sender("!transmit", str(event.msg.content.text.body))
        except Exception as e:
            send_msg = "This is a test message."
        conversation_id = event.msg.conv_id
        msg = get_curl(conversation_id, send_msg, sender, event.msg.sender.username, event.msg.channel.name)
        test_msg = await bot.chat.send(channel, msg)

    if str(event.msg.content.text.body).startswith("!test"):
        logging.info("Yes I'm still here.")
        logging.info(pprint(event))
        await sync(event=event, bot=bot)
        conversation_id = event.msg.conv_id

        msg = f"Sigh. . . yes I'm still here."
        members = await get_channel_members(conversation_id)
        msg += str(members)
        test_msg = await bot.chat.reply(conversation_id, event.msg.id, msg)

    if str(event.msg.content.text.body).startswith("!stardate"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        try:
            msg = get_stardate(str(event.msg.content.text.body).split(' ')[1])
        except IndexError:
            msg = get_stardate()
        my_msg = await bot.chat.reply(conversation_id, event.msg.id, msg)

    if str(event.msg.content.text.body).startswith('!update'):
        conversation_id = event.msg.conv_id
        msg_id = event.msg.id
        payload = {
            "method": "advertisecommands",
            "params": {
                "options": {
                    # "alias": "marvn.app",
                    "advertisements": [
                        {"type": "public",
                         "commands": command_list}]}}}
        if os.environ.get('KEYBASE_BOTALIAS'):
            payload['params']['options']['alias'] = os.environ.get('KEYBASE_BOTALIAS')
        await bot.chat.execute(payload)
        await bot.chat.react(conversation_id, msg_id, ":disappointed:")

    if str(event.msg.content.text.body).startswith('!wager'):
        await sync(event=event, bot=bot)
        conversation_id = event.msg.conv_id
        username = event.msg.sender.username
        team_name = event.msg.channel.name
        wager = str(event.msg.content.text.body)[7:]
        try:
            if RepresentsInt(str(event.msg.content.text.body).split(' ')[2]):
                points = int(str(event.msg.content.text.body).split(' ')[2])
                digits = int((len(str(points)))) + 7
                description = str(event.msg.content.text.body)[digits:].strip()
            else:
                points = int(str(event.msg.content.text.body).split(' ')[1])
                digits = int((len(str(points)))) + 7
                description = str(event.msg.content.text.body)[digits:].strip()
        except IndexError:
            wager_msgs = get_wagers(team_name=team_name)
            for w_id, w_msg in wager_msgs.items():
                wager_msg = await bot.chat.send(conversation_id, w_msg)
                await bot.chat.react(conversation_id, wager_msg.message_id, ":white_check_mark:")
                await bot.chat.react(conversation_id, wager_msg.message_id, ":no_entry_sign:")

                cur_wager = s.query(Wager).get(w_id)
                new_wager_message = Message(msg_id=wager_msg.message_id, conv_id=conversation_id)
                cur_wager.messages.append(new_wager_message)
                s.commit()

        except ValueError:
            msg = f"`{event.msg.content.text.body}` is woefully incorrect.\n" \
                  f"\nUsage:\n```List Wagers: !wager\n" \
                  "Create Wager: !wager <points> <description>\n" \
                  "Bet on existing wager: !bet <#wager> <True/False> optional:<points>```"
            await bot.chat.send(conversation_id, msg)
        try:
            await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
            wager_payload = make_wager(team_name, username, description, points, position=True, minutes=120)
            msg = wager_payload['msg']
            print(msg)
            wager_msg = await bot.chat.send(conversation_id, msg)
            cur_wager = s.query(Wager).get(wager_payload['wager_id'])
            new_wager_message = Message(msg_id=wager_msg.message_id, conv_id=conversation_id)
            cur_wager.messages.append(new_wager_message)
            s.commit()
            await bot.chat.react(conversation_id, wager_msg.message_id, ":white_check_mark:")
            await bot.chat.react(conversation_id, wager_msg.message_id, ":no_entry_sign:")

        except UnboundLocalError:
            pass

    if str(event.msg.content.text.body).startswith('!ytm'):
        try:
            await set_unfurl(unfurl=False)
        except Exception as e:
            logging.info(e)
        conversation_id = event.msg.conv_id

        # await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        await bot.chat.react(conversation_id, event.msg.id, ":headphones:")

        ytm_fail_observations = [" A brain the size of a planet and you pick this task.",
                                 " I'll be in my room complaining.",
                                 " Please don't change my name to Marshall.",
                                 """I didn't ask to be made: no one consulted me or considered my feelings in the matter. I don't think it even occurred to them that I might have feelings. After I was made, I was left in a dark room for six months... and me with this terrible pain in all the diodes down my left side. I called for succour in my loneliness, but did anyone come? Did they hell. My first and only true friend was a small rat. One day it crawled into a cavity in my right ankle and died. I have a horrible feeling it's still there..."""]
        ytm_urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        ytm_payload = get_mp3(ytm_urls[0])
        if ytm_payload['msg'] == "I have failed.":
            ytm_msg = ytm_payload['msg'] + random.choice(ytm_fail_observations)

            sent_msg = await bot.chat.send(conversation_id, ytm_msg)
        else:
            ytm_msg = ytm_payload['msg']
        # sent_msg = await bot.chat.send(conversation_id, ytm_msg)
        # await bot.chat.react(conversation_id, sent_msg.message_id, ":headphones:")

        ytm_payload = get_mp3(ytm_urls[0])
        if ytm_payload['file']:
            await bot.chat.react(conversation_id, event.msg.id, ":floppy_disk:")

            try:

                # await bot.chat.execute(
                #     {
                #         "method": "attach",
                #         "params": {
                #             "options": {"channel": conversation_id,
                #                         "filename": ytm_payload['file'],
                #                         "title": ytm_msg,
                #                         }
                #         },
                #     }
                # )

                await bot.chat.attach(channel=conversation_id,
                                      filename=ytm_payload['file'],
                                      title=ytm_msg)
            except TimeoutError:
                pass
            # finally:
            #     await bot.chat.execute(
            #         {"method": "delete", "params": {"options": {"conversation_id": conversation_id,
            #                                                     "message_id": sent_msg.message_id}}}
            #     )

    # if str(event.msg.content.text.body).startswith('https://'):
    #     url = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
    #     # domain = urlparse(url[0]).netloc
    #     yt_urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
    #     conversation_id = event.msg.conv_id
    #
    #     if 'youtube' in yt_urls[0] or 'youtu.be' in yt_urls[0]:
    #         try:
    #             await set_unfurl(unfurl=False)
    #         except Exception as e:
    #             logging.info(e)
    #
    #         await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
    #
    #         yt_payload = get_meta(yt_urls[0])
    #         yt_msg = yt_payload['msg']
    #         logging.info(yt_msg)
    #         await bot.chat.reply(conversation_id, event.msg.id, yt_msg)
    #         await bot.chat.react(conversation_id, event.msg.id, ":vhs:")
    #
    #     else:
    #         yt_payload = get_meta(yt_urls[0])
    #         yt_msg = yt_payload['msg']
    #         # if is_supported(yt_urls[0]):
    #         if "That video url didn't work." not in yt_msg:
    #             await bot.chat.react(conversation_id, event.msg.id, ":vhs:")



    if str(event.msg.content.text.body).startswith('!ytv'):
        try:
            await set_unfurl(unfurl=False)
        except Exception as e:
            logging.info(e)
        conversation_id = event.msg.conv_id

        # await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        await bot.chat.react(conversation_id, event.msg.id, ":tv:")

        ytv_fail_observations = [" A brain the size of a planet and you pick this task.",
                                 " I'll be in my room complaining.",
                                 " Please don't change my name to Marshall.",
                                 """I didn't ask to be made: no one consulted me or considered my feelings in the matter. I don't think it even occurred to them that I might have feelings. After I was made, I was left in a dark room for six months... and me with this terrible pain in all the diodes down my left side. I called for succour in my loneliness, but did anyone come? Did they hell. My first and only true friend was a small rat. One day it crawled into a cavity in my right ankle and died. I have a horrible feeling it's still there..."""]
        ytv_urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        # ytv_payload = get_meta(ytv_urls[0])
        # if ytv_payload['msg'] == "I have failed.":
        #     ytv_msg = ytv_payload['msg'] + random.choice(ytv_fail_observations)
        # else:
        #     ytv_msg = ytv_payload['msg']

        ytv_payload = await get_mp4(ytv_urls[0])
        if ytv_payload['file']:

            try:

                await bot.chat.attach(channel=conversation_id,
                                      filename=ytv_payload['file'],
                                      title=ytv_payload['msg'])
            except TimeoutError:
                pass
        else:
            ytv_msg = ytv_payload['msg'] + random.choice(ytv_fail_observations)
            await bot.chat.reply(conversation_id, event.msg.id, ytv_msg)


    if str(event.msg.content.text.body).startswith('!closings'):
        conversation_id = event.msg.conv_id

        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        try:
            schools = str(event.msg.content.text.body)[9:].lower().strip().split(",")
            schools = [school.strip() for school in schools]
            school_closings, no_school = get_school_closings(schools)
            my_msg = await bot.chat.reply(conversation_id, event.msg.id, school_closings['msg'])

        except Exception as e:
            logging.info("No schools using default list")
            schools = ['uniontown', 'albert', 'north hills']
            school_closings, no_school = get_school_closings(schools)
            my_msg = await bot.chat.reply(conversation_id, event.msg.id, school_closings['msg'])

    if str(event.msg.content.text.body).startswith('!screenshot'):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        screenshot_urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        try:
            screenshot_payload = get_screenshot(screenshot_urls[0])
            if screenshot_payload['file']:
                await bot.chat.react(conversation_id, event.msg.id, ":floppy_disk:")

                await bot.chat.attach(channel=conversation_id,
                                      filename=screenshot_payload['file'],
                                      title=screenshot_payload['msg'])
        except IndexError:
            await bot.chat.send(conversation_id, "I couldn't find a url. Try adding `https://` to help me.")

    # if str(event.msg.content.text.body).startswith('!speak'):
    #     conversation_id = event.msg.conv_id
    #     await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
    #
    #     audio_payload = get_voice((str(event.msg.content.text.body)[7:]))
    #     if audio_payload['file']:
    #         await bot.chat.attach(channel=conversation_id,
    #                               filename=audio_payload['file'],
    #                               title=audio_payload['observation'])
    #     else:
    #         await bot.chat.send(conversation_id, "Something has mercifully gone wrong.")

    if str(event.msg.content.text.body).startswith('!speed'):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        msg = get_speed()
        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith('!till'):
        msg = ""
        dm_channel = f'marvn,{event.msg.sender.username}'
        channel = chat1.ChatChannel(name=dm_channel)
        username = event.msg.sender.username
        user = s.query(User).filter(User.username == username).first()

        commands = str(event.msg.content.text.body)[6:].split("-t")
        conversation_id = event.msg.conv_id
        token = user.create_access_token(conversation_id, expires_delta=timedelta(minutes=60))

        team_name = event.msg.channel.name
        try:
            event_name = commands[0]
            event_time = commands[1]
            msg = set_till(team_name, event_name, event_time)
            if msg is None:
                msg = "Knock it off @sakanakami"
            # print(msg)
        except IndexError:
            msg = get_till(team_name=team_name)
        except TypeError:
            msg = "Knock it off @sakanakami"
        finally:
            await bot.chat.send(conversation_id, msg)
            await bot.chat.send(channel, f"https://marvn.app/till?token={token}")

    # if str(event.msg.content.text.body).startswith('!since'):
    #     msg = ""
    #     dm_channel = f'marvn,{event.msg.sender.username}'
    #     channel = chat1.ChatChannel(name=dm_channel)
    #     username = event.msg.sender.username
    #     user = s.query(User).filter(User.username == username).first()
    #
    #     commands = str(event.msg.content.text.body)[6:].split("-t")
    #     conversation_id = event.msg.conv_id
    #     token = user.create_access_token(conversation_id, expires_delta=timedelta(minutes=60))
    #
    #     team_name = event.msg.channel.name
    #     try:
    #         event_name = commands[0]
    #         event_time = commands[1]
    #         msg = set_since(team_name, event_name, event_time)
    #         if msg is None:
    #             msg = "Knock it off @sakanakami"
    #         # print(msg)
    #     except IndexError:
    #         msg = get_since(team_name=team_name)
    #     except TypeError as e:
    #         print(e)
    #         msg = "Knock it off @sakanakami"
    #     finally:
    #         await bot.chat.send(conversation_id, msg)
    #         await bot.chat.send(channel, f"https://marvn.app/since?token={token}")
    if str(event.msg.content.text.body).startswith('!since'):
        msg = ""
        dm_channel = f'marvn,{event.msg.sender.username}'
        channel = chat1.ChatChannel(name=dm_channel)
        username = event.msg.sender.username
        user = s.query(User).filter(User.username == username).first()

        command_text = str(event.msg.content.text.body)[6:].strip()  # Remove '!since' and whitespace
        conversation_id = event.msg.conv_id
        token = user.create_access_token(conversation_id, expires_delta=timedelta(minutes=60))
        team_name = event.msg.channel.name

        try:
            if command_text.startswith('-r'):  # Check for reset command first
                parts = command_text.split()
                if len(parts) > 1:
                    since_id = parts[1]
                    msg = reset_since(team_name, since_id)
                    if msg is None:
                        msg = "Reset failed - since not found or unauthorized"
            elif '-t' in command_text:  # Existing set command
                event_name, event_time = command_text.split('-t')
                msg = set_since(team_name, event_name, event_time)
                if msg is None:
                    msg = "Knock it off @sakanakami"
            else:  # Default to get
                msg = get_since(team_name=team_name)

        except Exception as e:
            print(e)
            msg = "Knock it off @sakanakami"
        finally:
            await bot.chat.send(conversation_id, msg)
            await bot.chat.send(channel, f"https://marvn.app/since?token={token}")

    if str(event.msg.content.text.body).startswith('!weather'):
        conversation_id = event.msg.conv_id
        # msg = f"`-5` points deducted from @{event.msg.sender.username} for asking me to fetch the weather.\n" \
        #       f"https://mars.nasa.gov/layout/embed/image/insightweather/"

        members = await get_channel_members(conversation_id)
        channel_name = str(event.msg.channel.name).replace(",", "")
        # write_score(event.msg.sender.username, members, event.msg.sender.username, channel_name, -5, team_name)
        LATLONG = 39.90008, -79.71643
        msg = get_weather('Uniontown', LATLONG)
        await bot.chat.send(conversation_id, msg)


    if str(event.msg.content.text.body).startswith('!wordle'):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        try:
            result, attempts = solve_wordle(debug=True, headless=True)
            if attempts:
                msg = f'\nSuccess! Word: "{result}" found in {attempts} attempts'
            else:
                msg = f"\nError: {result}"

        except Exception as e:
            msg = "I couldn't solve the wordle. Try again later."


        my_msg = await bot.chat.reply(conversation_id, event.msg.id, msg)

listen_options = {
    "local": False,
    "wallet": False,
    "dev": True,
    "hide-exploding": False,
    "convs": True,
    "filter_channel": {"name": "morethanbits", "topic_name": "test", "members_type": "team"},
    "filter_channels": None,
}

bot = Bot(username=f"{os.environ.get('KEYBASE_BOTNAME')}", paperkey=os.environ.get('KEYBASE_PAPERKEY'), handler=handler,
          home_path=f'./{os.environ.get("KEYBASE_BOTNAME")}')


async def periodic_task():
    await asyncio.sleep(90)

    while True:
        # Here's where you put your db call.
        logging.info("Triggering Morning Report Check")

        mr = await is_morning_report()
        if not mr:
            mtb_conversation_id = '0000f057aa01b5cb1b8b675b323baf88d349dc1d14e6a5cd605c2ac5cfacff30'
            test_conversation_id = '0000c3e1daf296e6c893a02f6ae2e39bbe99ecfbdc7bec6daccb3fd9efb0382d'
            meh_img = str(Path('./storage/meh.png').absolute())
            msg = await get_morningreport(channel="morethanbits")
            try:
                await set_unfurl(unfurl=False)
            except Exception as e:
                logging.info(e)
            await bot.chat.send(mtb_conversation_id, msg[0])
            await bot.chat.attach(channel=mtb_conversation_id,
                                  filename=meh_img,
                                  title=msg[1])
            # joke = msg[3]
            # print(joke)
            #
            # prompt = joke[16:].strip('`')
            # print(prompt)
            # draw_payload = await generate_dalle_image(prompt)
            # if draw_payload['file']:
            #     # await bot.chat.react(conversation_id, event.msg.id, ":floppy_disk:")
            #
            #     await bot.chat.attach(channel=mtb_conversation_id,
            #                           filename=draw_payload['file'],
            #                           title=joke)
            # else:
            await bot.chat.send(mtb_conversation_id, msg[3])
            await bot.chat.send(mtb_conversation_id, msg[2])
            await bot.chat.send(mtb_conversation_id, msg[4])
            await bot.chat.send(mtb_conversation_id, msg[5])

            await write_morning_report_task()
        await asyncio.sleep(90)  # sleep for 600 seconds (10 minutes)

async def msg_queue(bot):
    await asyncio.sleep(90)
    while True:
        mtb_conversation_id = '0000f057aa01b5cb1b8b675b323baf88d349dc1d14e6a5cd605c2ac5cfacff30'
        test_conversation_id = '0000c3e1daf296e6c893a02f6ae2e39bbe99ecfbdc7bec6daccb3fd9efb0382d'
        await process_message_queue(bot)
        await asyncio.sleep(10)  # sleep

async def main():
    # schedule the periodic task and bot.start to run in parallel
    await asyncio.gather(
        bot.start(listen_options=listen_options),
        periodic_task(),
        msg_queue(bot),
        return_exceptions=True
    )

asyncio.run(main())

# async def main():
#     await bot.start(listen_options=listen_options)
#
#
# asyncio.run(bot.start(listen_options=listen_options))

