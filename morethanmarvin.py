#!/usr/bin/env python3
import asyncio
import logging
import os
import sys
# from dotenv import load_dotenv
from pprint import pprint
from urllib.parse import urlparse

from sqlalchemy import func

from botcommands.poll_results import get_poll_result
from botcommands.jokes import get_joke
from botcommands.tldr import get_tldr
import re
import random
import pykeybasebot.types.chat1 as chat1
from pykeybasebot import Bot
from botcommands.youtube import get_video, get_mp3, get_domain
from botcommands.youtube_dlp import get_mp3, get_mp4, get_meta, is_supported
from botcommands.covid import get_covid
from botcommands.get_screenshot import get_screenshot
from botcommands.virustotal import get_scan
from botcommands.cow_say import get_cow
from botcommands.meh import get_meh
from botcommands.drwho import get_drwho
from botcommands.stardate import get_stardate
from botcommands.chuck import get_chuck
from botcommands.voice import get_voice
from botcommands.till import get_till, set_till
from botcommands.cow_characters import get_characters
from botcommands.morningreport import get_morningreport
from botcommands.scorekeeper import get_score, write_score, sync_score
from botcommands.get_members import get_members
from pathlib import Path
from botcommands.bible import get_esv_text
from botcommands.wager import get_wagers, make_wager, make_bet, get_bets, payout_wager
from botcommands.sync import sync
from models import Team, User, Point, Location, Wager, Message
from crud import s
from botcommands.jitsi import get_jitsi_link
from botcommands.pacyber import get_academic_snapshot
from botcommands.update_vaccine import get_vaccine_data
# from botcommands.morbidity import get_morbid
from botcommands.eyebleach import get_eyebleach
from botcommands.checkspeed import get_speed
from botcommands.files import get_files
# import webhooks

# from botcommands.rickroll import get_rickroll

# load_dotenv('secret.env')

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


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class Points(object):
    pass


async def handler(bot, event):
    command_list = [
        {"name": "award",
         "description": "Force me to give completely meaningless points to your comrades.",
         "usage": "<user> <points>"},
        {"name": "bible",
         "description": "Force me to lookup Bible txt.",
         "usage": "<reference> OR <search string>"},
        {"name": "canary",
         "description": "Force me to give Virus Total your nasty URL and return scan results.",
         "usage": "<url>"},
        {"name": "chuck",
         "description": "Forces me to tell a terribly jouvinile possibly NSFW joke randomly mentioning someone in this channel.",
         "usage": "Optional: <name> OR bomb if nothing is given a member of this channel will be selected at random."},
        {"name": "covid",
         "description": "Force me to morbidly retrieve covid numbers for a State County or State.",
         "usage": "<State> <County> <- Optional Fields"},
        {"name": "cow",
         "description": f"Now I can't even explain this. You are a monster. Optional Characters: {get_characters()}",
         "usage": "<character> <msg>"},
        {"name": "drwho",
         "description": "Return Dr Who Episode.",
         "usage": "<ep_id> OR <Ep Title>"},
        {"name": "eyebleach",
         "description": "Returns images from r/eyebleach. Default = 3",
         "usage": "<bleach_level> 1-11"},
        {"name": "files",
         "description": "Returns list of files on marvin",
         "usage": ""},
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
        {"name": "meet",
         "description": "Get video conference link.",
         "usage": "<Conference Name>"},
        # {"name": "morbidity",
        #  "description": "Return data about current mass shootings in the US.",
        #  "usage": ""},
        {"name": "morningreport",
         "description": "Gets today's morning report.",
         "usage": ""},
        {"name": "payout",
         "description": "Pays out a wager.",
         "usage": "<#wager> <True/False>"},
        {"name": "pollresult",
         "description": "RealClear Politics National and Pennsylvania Poll Results.",
         "usage": ""},
        {"name": "screenshot",
         "description": "Forces me go to a url and send a screenshot.",
         "usage": "<url>"},
        {"name": "set",
         "description": "Admin command for setting various things",
         "usage": ""},
        {"name": "speak",
         "description": "Forces me generate an mp3 speaking the text you send.",
         "usage": "<Text To Speak>"},
        {"name": "speed",
         "description": "Forces me check upload download speed.",
         "usage": ""},
        {"name": "score",
         "description": "Get the score for who abuses me the most.",
         "usage": ""},
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
        {"name": "vac",
         "description": "Get Vaccine Distributation data from health.pa.gov",
         "usage": ""},
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
    ]

    if event.msg.content.type_name == 'reaction':
        if event.msg.content.reaction.body == ":white_check_mark:" or ':no_entry_sign:':
            if event.msg.sender.username == 'marvn' or event.msg.sender.username == 'morethanmarvin':
                return
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
        if event.msg.content.reaction.body == ":tv:":
            if event.msg.sender.username == 'marvn' or event.msg.sender.username == 'morethanmarvin':
                return
            else:
                conversation_id = event.msg.conv_id

                msg = await bot.chat.get(event.msg.conv_id, event.msg.content.reaction.message_id)
                # pprint(msg.message[0]['msg']['reactions'])
                original_body = msg.message[0]['msg']['content']['text']['body']
                original_msg_id =msg.message[0]['msg']['id']
                reactions = msg.message[0]['msg']['reactions']
                reaction_list = []
                for key, value in reactions.items():
                    for k, v in value.items():
                        try:
                            if v['users']['morethanmarvin']:
                                reaction_list.append(k)
                        except KeyError:
                            pass
                if ':floppy_disk:' in reaction_list:
                    team_name = event.msg.channel.name
                    # print("found floppy")
                    fail_msg = f"`-10pts` awarded to @{event.msg.sender.username} for spamming :tv:"
                    score = write_score(event.msg.sender.username, 'marvn',
                                        team_name, -10, description=fail_msg)
                    await bot.chat.send(conversation_id, fail_msg)

                else:
                    urls = re.findall(r'(https?://[^\s]+)', original_body)
                    await bot.chat.react(conversation_id, original_msg_id, ":floppy_disk:")
                    ytv_payload = get_mp4(urls[0])
                    if ytv_payload['file']:
                        ytv_msg = ytv_payload['msg']
                        try:

                            await bot.chat.attach(channel=conversation_id,
                                                  filename=ytv_payload['file'],
                                                  title=ytv_msg)
                            # await bot.chat.delete(conversation_id, original_msg_id)

                        except TimeoutError:
                            pass

    if event.msg.content.type_name == 'reaction':
        if event.msg.content.reaction.body == ":camera:":
            if event.msg.sender.username == 'marvn' or event.msg.sender.username == 'morethanmarvin':
                return
            else:
                conversation_id = event.msg.conv_id

                msg = await bot.chat.get(event.msg.conv_id, event.msg.content.reaction.message_id)
                # pprint(msg.message[0]['msg']['reactions'])
                original_body = msg.message[0]['msg']['content']['text']['body']
                original_msg_id = msg.message[0]['msg']['id']
                reactions = msg.message[0]['msg']['reactions']
                reaction_list = []
                for key, value in reactions.items():
                    for k, v in value.items():
                        # print(v)
                        try:
                            if v['users']['morethanmarvin']:

                        # print(v.get('users')['morethanmarvin'])
                                reaction_list.append(k)
                        except KeyError:
                            pass
                if ':floppy_disk:' in reaction_list:
                    team_name = event.msg.channel.name
                    # print("found floppy")
                    fail_msg = f"`-10pts` awarded to @{event.msg.sender.username} for spamming :camera:"
                    score = write_score(event.msg.sender.username, 'marvn',
                                        team_name, -10, description=fail_msg)
                    await bot.chat.send(conversation_id, fail_msg)

                else:
                    print('Still going')

                    urls = re.findall(r'(https?://[^\s]+)', original_body)
                    await bot.chat.react(conversation_id, original_msg_id, ":floppy_disk:")
                    try:
                        screenshot_payload = get_screenshot(urls[0])
                        if screenshot_payload['file']:
                            await bot.chat.attach(channel=conversation_id,
                                                  filename=screenshot_payload['file'],
                                                  title=screenshot_payload['msg'])
                    except IndexError as e:
                        pass


    if event.msg.content.type_name != chat1.MessageTypeStrings.TEXT.value:
        return
    if event.msg.content.type_name != chat1.MessageTypeStrings.TEXT.value:
        return

    if str(event.msg.content.text.body).startswith("!award"):
        await sync(event=event, bot=bot)

        pts_max = 500

        instructions = f"You have failed. I'm not surprised.\n" \
                       f"```You can only give points to someone in this chat.\n" \
                       f"You can't give more than {pts_max} points at a time.\n" \
                       f"You can't give negative points.\n" \
                       f"Points must be whole numbers.\n" \
                       f"No cutesy extra characters, or I'll deduct from your score.\n" \
                       f"You can't give points to yourself.```\n" \
                       f"Usage: `!award <user> <points>`"
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        members = await get_channel_members(conversation_id)
        channel_name = str(event.msg.channel.name).replace(",", "")
        team_name = event.msg.channel.name
        description = " ".join(str(event.msg.content.text.body).split(' ')[3:]).strip()
        try:
            if RepresentsInt(str(event.msg.content.text.body).split(' ')[2]):
                user = str(event.msg.content.text.body).split(' ')[1].strip("@")
                points = int(str(event.msg.content.text.body).split(' ')[2])
            else:
                user = str(event.msg.content.text.body).split(' ')[2].strip("@")
                points = int(str(event.msg.content.text.body).split(' ')[1])

            if points < 0 and event.msg.sender.username != 'pastorhudson':
                user = event.msg.sender.username
                score = write_score(user, event.msg.sender.username, team_name, -5, description=description)
                await bot.chat.send(conversation_id,
                                    f"`-5` points awarded to @{user}. I'm the only negative one around here.")
            if user in members and user != event.msg.sender.username and points <= pts_max or event.msg.sender.username == 'pastorhudson' or user == 'pastorhudson':
                score = write_score(user, event.msg.sender.username, team_name, points, description=description)
                await bot.chat.react(conversation_id, msg_id, ":marvin:")

            else:
                await bot.chat.send(conversation_id, instructions)
        except Exception as e:
            write_score('marvn', event.msg.sender.username, team_name, -5, description=description)
            await bot.chat.send(conversation_id,
                                f"You did it wrong.\n `-5` points deducted from  @{event.msg.sender.username} "
                                f"for trying to be cute.\n{instructions}")

    if str(event.msg.content.text.body).startswith("!bible"):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        passage = str(event.msg.content.text.body)[7:]
        msg = get_esv_text(passage)
        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith('!canary'):
        vt_url = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        msg = get_scan(vt_url[0])
        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith('!chuck'):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        channel_members = await get_channel_members(conversation_id)
        try:
            name = str(event.msg.content.text.body)[7:]
            chuck_msg = get_chuck(name=name, channel_members=channel_members)
        except:
            chuck_msg = get_chuck(channel_members=channel_members)
        my_msg = await bot.chat.send(conversation_id, chuck_msg)

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

        msg = get_cow(str(event.msg.content.text.body)[5:])
        my_msg = await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!drwho"):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        msg = get_drwho(str(event.msg.content.text.body)[7:])
        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!eyebleach"):
        await set_unfurl(True)
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

    if str(event.msg.content.text.body).startswith("!files"):
        conversation_id = event.msg.conv_id
        team_name = event.msg.channel.name
        if team_name in ['morethanbits', 'growinlove'] or event.msg.sender == 'pastorhudson':
            msg = get_files()
        else:
            msg = "No Files."
        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!grades"):
        conversation_id = event.msg.conv_id
        if event.msg.sender.username == 'pastorhudson' or event.msg.sender.username == 'sakanakami':
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
        joke = get_joke()

        conversation_id = event.msg.conv_id
        await bot.chat.send(conversation_id, joke)

    # if str(event.msg.content.text.body).startswith("!morbidity"):
    #     conversation_id = event.msg.conv_id
    #     msg = get_morbid()
    #     members = await get_channel_members(conversation_id)
    #     morbid_msg = await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!morningreport"):
        await sync(event=event, bot=bot)
        conversation_id = event.msg.conv_id
        channel_members = await get_channel_members(conversation_id)
        channel_name = str(event.msg.channel.name)
        meh_img = str(Path('./storage/meh.png').absolute())
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        msg = get_morningreport(channel=channel_name)
        await bot.chat.send(conversation_id, msg[0])
        # file = str(meh_img.absolute())
        await bot.chat.attach(channel=conversation_id,
                              filename=meh_img,
                              title=msg[1])
        await bot.chat.send(conversation_id, msg[2])
        await bot.chat.send(conversation_id, msg[3])

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

    if str(event.msg.content.text.body).startswith("!pollresult"):
        channel = event.msg.channel.name
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        polls = get_poll_result(channel)
        await bot.chat.send(conversation_id, polls)

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

    if str(event.msg.content.text.body).startswith('!tldr'):
        urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        tldr = get_tldr(urls[0])
        await bot.chat.send(conversation_id, tldr)

        ytv_payload = get_mp4(urls[0])
        if ytv_payload['file']:
            await bot.chat.react(conversation_id, event.msg.id, ":tv:")

    if str(event.msg.content.text.body).startswith('!vac'):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        vac_data = get_vaccine_data()
        await bot.chat.send(conversation_id, vac_data)

    if str(event.msg.content.text.body).startswith('!meh'):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        meh_img = str(Path('./storage/meh.png').absolute())
        msg = get_meh()
        await bot.chat.attach(channel=conversation_id,
                              filename=meh_img,
                              title=msg)

    if str(event.msg.content.text.body).startswith('!meet'):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        room = str(event.msg.content.text.body)[6:]
        msg = get_jitsi_link(room)
        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!test"):
        conversation_id = event.msg.conv_id
        msg = f"Sigh. . . yes I'm still here."
        members = await get_channel_members(conversation_id)
        msg += str(members)
        test_msg = await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!stardate"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        try:
            msg = get_stardate(str(event.msg.content.text.body).split(' ')[1])
        except IndexError:
            msg = get_stardate()
        my_msg = await bot.chat.send(conversation_id, msg)

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
        await set_unfurl(unfurl=False)
        conversation_id = event.msg.conv_id

        # await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        await bot.chat.react(conversation_id, event.msg.id, ":headphones:")

        ytm_fail_observations = [" A brain the size of a planet and you pick this task.",
                                 " I'll be in my room complaining.",
                                 " Please don't change my name to Marshall.",
                                 """I didn't ask to be made: no one consulted me or considered my feelings in the matter. I don't think it even occurred to them that I might have feelings. After I was made, I was left in a dark room for six months... and me with this terrible pain in all the diodes down my left side. I called for succour in my loneliness, but did anyone come? Did they hell. My first and only true friend was a small rat. One day it crawled into a cavity in my right ankle and died. I have a horrible feeling it's still there..."""]
        ytm_urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        ytm_payload = get_mp3(ytm_urls[0], True)
        if ytm_payload['msg'] == "I have failed.":
            ytm_msg = ytm_payload['msg'] + random.choice(ytm_fail_observations)

            sent_msg = await bot.chat.send(conversation_id, ytm_msg)
        else:
            ytm_msg = ytm_payload['msg']
        # sent_msg = await bot.chat.send(conversation_id, ytm_msg)
        # await bot.chat.react(conversation_id, sent_msg.message_id, ":headphones:")

        ytm_payload = get_mp3(ytm_urls[0], False)
        if ytm_payload['file']:

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

    if str(event.msg.content.text.body).startswith('https://'):
        url = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        domain = get_domain(url[0])
        yt_urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        conversation_id = event.msg.conv_id

        if 'youtube' in yt_urls[0] or 'youtu.be' in yt_urls[0]:
            await set_unfurl(unfurl=False)

            await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

            yt_payload = get_meta(yt_urls[0])
            yt_msg = yt_payload['msg']

            await bot.chat.reply(conversation_id, event.msg.id, yt_msg)
            await bot.chat.react(conversation_id, event.msg.id, ":tv:")

        else:
            yt_payload = get_meta(yt_urls[0])
            yt_msg = yt_payload['msg']
            # if is_supported(yt_urls[0]):
            if "That video url didn't work." not in yt_msg:
                await bot.chat.react(conversation_id, event.msg.id, ":tv:")

    if str(event.msg.content.text.body).startswith('!ytv'):
        await set_unfurl(unfurl=False)
        conversation_id = event.msg.conv_id

        # await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        await bot.chat.react(conversation_id, event.msg.id, ":floppy_disk:")

        ytv_fail_observations = [" A brain the size of a planet and you pick this task.",
                                 " I'll be in my room complaining.",
                                 " Please don't change my name to Marshall.",
                                 """I didn't ask to be made: no one consulted me or considered my feelings in the matter. I don't think it even occurred to them that I might have feelings. After I was made, I was left in a dark room for six months... and me with this terrible pain in all the diodes down my left side. I called for succour in my loneliness, but did anyone come? Did they hell. My first and only true friend was a small rat. One day it crawled into a cavity in my right ankle and died. I have a horrible feeling it's still there..."""]
        ytv_urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        ytv_payload = get_meta(ytv_urls[0])
        if ytv_payload['msg'] == "I have failed.":
            ytv_msg = ytv_payload['msg'] + random.choice(ytv_fail_observations)
        else:
            ytv_msg = ytv_payload['msg']

        ytv_payload = get_mp4(ytv_urls[0])
        if ytv_payload['file']:

            try:

                await bot.chat.attach(channel=conversation_id,
                                      filename=ytv_payload['file'],
                                      title=ytv_msg)
            except TimeoutError:
                pass

    if str(event.msg.content.text.body).startswith('!screenshot'):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        screenshot_urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        screenshot_payload = get_screenshot(screenshot_urls[0])
        if screenshot_payload['file']:
            await bot.chat.react(conversation_id, event.msg.id, ":floppy_disk:")

            await bot.chat.attach(channel=conversation_id,
                                  filename=screenshot_payload['file'],
                                  title=screenshot_payload['msg'])

    if str(event.msg.content.text.body).startswith('!speak'):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        audio_payload = get_voice((str(event.msg.content.text.body)[7:]))
        if audio_payload['file']:
            await bot.chat.attach(channel=conversation_id,
                                  filename=audio_payload['file'],
                                  title=audio_payload['observation'])
        else:
            await bot.chat.send(conversation_id, "Something has mercifully gone wrong.")

    if str(event.msg.content.text.body).startswith('!speed'):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        msg = get_speed()
        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith('!till'):
        msg = ""
        commands = str(event.msg.content.text.body)[6:].split("-t")
        conversation_id = event.msg.conv_id
        team_name = event.msg.channel.name
        try:
            event_name = commands[0]
            event_time = commands[1]
            msg = set_till(team_name, event_name, event_time)
            # print(msg)
        except IndexError:
            msg = get_till(team_name=team_name)
        finally:
            await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith('!weather'):
        conversation_id = event.msg.conv_id
        msg = f"`-5` points deducted from @{event.msg.sender.username} for asking me to fetch the weather.\n" \
              f"https://mars.nasa.gov/layout/embed/image/insightweather/"
        members = await get_channel_members(conversation_id)
        channel_name = str(event.msg.channel.name).replace(",", "")
        write_score(event.msg.sender.username, members, event.msg.sender.username, channel_name, -5, team_name)
        await bot.chat.send(conversation_id, msg)


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

asyncio.run(bot.start(listen_options=listen_options))
