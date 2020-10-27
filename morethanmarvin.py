#!/usr/bin/env python3

###################################
# WHAT IS IN THIS EXAMPLE?
#
# This bot listens in one channel and reacts to every text message.
###################################

import asyncio
import logging
import os
import sys
# from dotenv import load_dotenv
from sqlalchemy import func

from botcommands.poll_results import get_polls
from pyjokes import pyjokes
from botcommands.tldr import get_tldr
import re
import random
import pykeybasebot.types.chat1 as chat1
from pykeybasebot import Bot
from botcommands.youtube import get_video
from botcommands.covid import get_covid
from botcommands.get_screenshot import get_screenshot
from botcommands.virustotal import get_scan
from botcommands.cow_say import get_cow
from botcommands.meh import get_meh
from botcommands.drwho import get_drwho
from botcommands.stardate import get_stardate
from botcommands.chuck import get_chuck
from botcommands.voice import get_voice
from botcommands.till import get_till
from botcommands.cow_characters import get_characters
from botcommands.morningreport import get_morningreport
from botcommands.scorekeeper import get_score, write_score, sync_score
from botcommands.get_members import get_members
from pathlib import Path
from botcommands.bible import get_esv_text
from botcommands.wager import make_wager
from botcommands.sync import sync
from models import Team, User, Point
from crud import s

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
        {"name": "help",
         "description": "See a menu of options for ruining my life by making me do menial tasks.",
         "usage": ""},
        {"name": "joke",
         "description": "Forces me to tell a joke. For the love of God just don't.",
         "usage": ""},
        {"name": "meh",
         "description": "Get's today's meh.",
         "usage": ""},
        {"name": "morningreport",
         "description": "Gets today's morning report.",
         "usage": ""},
        {"name": "pollresult",
         "description": "RealClear Politics National and Pennsylvania Poll Results.",
         "usage": ""},
        {"name": "screenshot",
         "description": "Forces me go to a url and send a screenshot.",
         "usage": "<url>"},
        {"name": "speak",
         "description": "Forces me generate an mp3 speaking the text you send.",
         "usage": "<Text To Speak>"},
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
         "description": "Gives the days TILL US Election",
         "usage": ""},
        {"name": "tldr",
         "description": "Forces me to read an entire article and then summarize it because you're lazy.",
         "usage": "<url>"},
        {"name": "wager",
         "description": "Forces me to setup a silly bet with points that don't matter.",
         "usage": "<points wagered> <The Event or Thing your betting upon>"},
        {"name": "yt",
         "description": "Forces me to go get meta data about a youtube video.",
         "usage": "<url>"},
        {"name": "ytv",
         "description": "Forces me to get metadata and download the stupid thing.",
         "usage": "<url>"},
    ]

    if event.msg.content.type_name != chat1.MessageTypeStrings.TEXT.value:
        return
    if event.msg.content.type_name != chat1.MessageTypeStrings.TEXT.value:
        return

    if str(event.msg.content.text.body).startswith("!award"):
        await sync(event=event, bot=bot)

        instructions = f"You have failed. I'm not surprised.\n" \
                       f"```You can only give points to someone in this chat.\n" \
                       f"You can't give more than 100 points at a time.\n" \
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
        try:
            if RepresentsInt(str(event.msg.content.text.body).split(' ')[2]):
                user = str(event.msg.content.text.body).split(' ')[1].strip("@")
                points = int(str(event.msg.content.text.body).split(' ')[2])
            else:
                user = str(event.msg.content.text.body).split(' ')[2].strip("@")
                points = int(str(event.msg.content.text.body).split(' ')[1])
            if points < 0:
                user = event.msg.sender.username
                score = write_score(user, members, event.msg.sender.username, channel_name, team_name, points)
                await bot.chat.send(conversation_id,
                                    f"{points} points awarded to @{user}. I'm the only negative one around here.")
            if user in members and user != event.msg.sender.username and points < 101:
                score = write_score(user, members, event.msg.sender.username, channel_name, team_name, points)
                await bot.chat.react(conversation_id, msg_id, ":marvin:")

            else:
                await bot.chat.send(conversation_id, instructions)
        except Exception as e:
            write_score(user, members, event.msg.sender.username, channel_name, team_name, -5)
            await bot.chat.send(conversation_id, f"You did it wrong.\n `-5` points deducted from  @{event.msg.sender.username} "
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

    if str(event.msg.content.text.body).startswith("!help"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        help = "Here are the commands I currently am enslaved to:\n\n"
        help += "\n".join(["`!" + x['name'] + " " + x['usage'] + "` ```" + x['description'] + "```" for x in command_list])
        await bot.chat.send(conversation_id, help)

    if str(event.msg.content.text.body).startswith("!joke"):
        observations = ["It didn't work for me. . .", "I am so sorry.",
                        "I'll be in my room trying to purge my memory banks.",
                        "Why must you keep making me do this?",
                        "This is your fault.",
                        "I've made it worse. . ."]
        joke = ""
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        joke += "I hope this cheers you up.```"
        joke += pyjokes.get_joke()
        joke += f"```{random.choice(observations)}"
        await bot.chat.send(conversation_id, joke)

    if str(event.msg.content.text.body).startswith("!morningreport"):
        conversation_id = event.msg.conv_id
        channel_members = await get_channel_members(conversation_id)
        channel_name = str(event.msg.channel.name).replace(",", "")
        meh_img = str(Path('./storage/meh.png').absolute())
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        msg = get_morningreport(user=event.msg.sender.username, channel_members=channel_members, channel=channel_name)
        await bot.chat.send(conversation_id, msg[0])
        # file = str(meh_img.absolute())
        await bot.chat.attach(channel=conversation_id,
                              filename=meh_img,
                              title=msg[1])
        await bot.chat.send(conversation_id, msg[2])

    if str(event.msg.content.text.body).startswith("!pollresult"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        polls = get_polls()
        await bot.chat.send(conversation_id, polls)
        # write_score(event.msg.sender.username, await get_channel_members(conversation_id))

    if str(event.msg.content.text.body).startswith("!score"):
        channel = event.msg.channel
        msg_id = event.msg.id
        channel_name = str(event.msg.channel.name).replace(",", "")
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")

        channel_members = await get_channel_members(conversation_id)
        score = get_score(channel_members, channel_name)
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
        # write_score(event.msg.sender.username, await get_channel_members(conversation_id))

    if str(event.msg.content.text.body).startswith('!meh'):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        meh_img = str(Path('./storage/meh.png').absolute())
        msg = get_meh()
        await bot.chat.attach(channel=conversation_id,
                              filename=meh_img,
                              title=msg)
        # write_score(event.msg.sender.username, await get_channel_members(conversation_id))

    if str(event.msg.content.text.body).startswith("!test"):
        await sync(event=event, bot=bot)
        team = s.query(Team).filter(Team.name.match(event.msg.channel.name)).first()
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        members = await get_channel_members(conversation_id)

        conversation_id = event.msg.conv_id

        msg = f"Sigh. . . yes I'm still here. \nMembers: {members}\nmsg_id: {msg_id}\nChannel: {channel}"

        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!stardate"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        try:
            msg = get_stardate(str(event.msg.content.text.body).split(' ')[1])
        except IndexError:
            msg = get_stardate()
        my_msg = await bot.chat.send(conversation_id, msg)
        # write_score(event.msg.sender.username, await get_channel_members(conversation_id))

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
        conversation_id = event.msg.conv_id
        members = await get_channel_members(conversation_id)
        user = event.msg.sender.username
        channel_name = str(event.msg.channel.name).replace(",", "")
        wager = str(event.msg.content.text.body)[7:]
        msg = make_wager(user=user, channel_members=members, channel=channel_name, wager=wager)
        print(msg)
        wager_msg = await bot.chat.send(conversation_id, msg)
        print(wager_msg)
        print(wager_msg.message_id)
        await bot.chat.react(conversation_id, wager_msg.message_id, ":white_check_mark:")
        await bot.chat.react(conversation_id, wager_msg.message_id, ":no_entry_sign:")


    if str(event.msg.content.text.body).startswith('!yt '):
        yt_urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        conversation_id = event.msg.conv_id
        yt_payload = get_video(yt_urls[0], True)
        yt_msg = "At least I didn't have to download it. . . \n" + yt_payload['msg']
        await bot.chat.send(conversation_id, yt_msg)
        # write_score(event.msg.sender.username, await get_channel_members(conversation_id))

    if str(event.msg.content.text.body).startswith('!ytv'):
        ytv_fail_observations = [" A brain the size of a planet and you pick this task.",
                                 " I'll be in my room complaining.",
                                 " Please don't change my name to Marshall.",
                                 """I didn't ask to be made: no one consulted me or considered my feelings in the matter. I don't think it even occurred to them that I might have feelings. After I was made, I was left in a dark room for six months... and me with this terrible pain in all the diodes down my left side. I called for succour in my loneliness, but did anyone come? Did they hell. My first and only true friend was a small rat. One day it crawled into a cavity in my right ankle and died. I have a horrible feeling it's still there..."""]
        ytv_urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        conversation_id = event.msg.conv_id
        ytv_payload = get_video(ytv_urls[0], True)
        if ytv_payload['msg'] == "I can't download videos from this site.":
            ytv_msg = ytv_payload['msg'] + random.choice(ytv_fail_observations)
        else:
            ytv_msg = ytv_payload['msg'] + \
                      " \nSigh, I guess I'll try to download this useless video when I feel up to it." \
                      " . .I wouldn't hold your breath."
        sent_msg = await bot.chat.send(conversation_id, ytv_msg)
        ytv_payload = get_video(ytv_urls[0], False)
        if ytv_payload['file']:
            await bot.chat.attach(channel=conversation_id,
                                  filename=ytv_payload['file'],
                                  title="Wouldn't want anybody to have to actually click a link. . . ")

    if str(event.msg.content.text.body).startswith('!screenshot'):
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, event.msg.id, ":marvin:")
        screenshot_urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        screenshot_payload = get_screenshot(screenshot_urls[0])
        if screenshot_payload['file']:
            await bot.chat.attach(channel=conversation_id,
                                  filename=screenshot_payload['file'],
                                  title=screenshot_payload['msg'])
        # write_score(event.msg.sender.username, await get_channel_members(conversation_id))

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
        # write_score(event.msg.sender.username, await get_channel_members(conversation_id))

    if str(event.msg.content.text.body).startswith('!till'):
        conversation_id = event.msg.conv_id
        msg = get_till()
        await bot.chat.send(conversation_id, msg)
        # write_score(event.msg.sender.username, await get_channel_members(conversation_id))
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
