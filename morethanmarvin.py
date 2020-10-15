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

# load_dotenv('secret.env')

logging.basicConfig(level=logging.DEBUG)

if "win32" in sys.platform:
    # Windows specific event-loop policy
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy()  # type: ignore
    )


async def handler(bot, event):
    command_list = [
        {"name": "canary",
         "description": "<url> Force me to give Virus Total your nasty URL and return scan results.",
         "usage": "<url>"},
        {"name": "chuck",
         "description": "Forces me to tell a terribly jouvinile possibly NSFW joke randomly mentioning someone in this channel."},
        {"name": "covid",
         "description": "Force me to morbidly retrieve covid numbers for a State County or State.",
         "usage": "<State> <County> <- Optional Fields"},
        {"name": "cow",
         "description": "Now I can't even explain this. You are a monster.",
         "usage": "<msg>"},
        {"name": "drwho",
         "description": "Return Dr Who Episode.",
         "usage": "<ep_id> OR <Ep Title>"},
        {"name": "help",
         "description": "See a menu of options for ruining my life by making me do menial tasks."},
        {"name": "joke",
         "description": "Forces me to tell a joke. For the love of God just don't."},
        {"name": "meh",
         "description": "Get's today's meh."},
        {"name": "pollresult",
         "description": "RealClear Politics National and Pennsylvania Poll Results."},
        {"name": "screenshot",
         "description": "Forces me go to a url and send a screenshot.",
         "usage": "<url>"},
        {"name": "stardate",
         "description": " Print's the current stardate if no stardate is given.",
         "usage": "<stardate> <- Optional"},
        {"name": "test",
         "description": "Just check to see if I'm regretfully still here."},
        {"name": "tldr",
         "description": "Forces me to read an entire article and then summarize it because you're lazy.",
         "usage": "<url>"},
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
    if str(event.msg.content.text.body).startswith("!help"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        help = "\n".join(["`!" + x['name'] + "` ```" + x['description'] + "```" for x in command_list])
        print(help)
        # Here are the commands I currently am enslaved to:
        # !joke - Forces me to tell a joke. For the love of God just don't.
        # !pollresult - RealClear Politics National and Pennsylvania Poll Results
        # !yt <youtube_url> - Forces me to go get meta data about a youtube video.
        # !ytv <youtube_url> - Forces me to get metadata and download the stupid thing.
        # !tldr <url> - Forces me to read an entire article and then summarize it because you're lazy.
        # !test - Check to see if I'm alive or if I've mercifully died yet.
        # !covid <state> <county> - Force me to morbidly retrieve covid numbers for a State County or State.```"""
        await bot.chat.send(conversation_id, help)
    if str(event.msg.content.text.body).startswith("!drwho"):
        conversation_id = event.msg.conv_id
        print(str(event.msg.content.text.body)[7:])
        msg = get_drwho(str(event.msg.content.text.body)[7:])
        await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!pollresult"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        polls = get_polls()
        await bot.chat.send(conversation_id, polls)
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
    if str(event.msg.content.text.body).startswith('!tldr'):
        urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        tldr = get_tldr(urls[0])
        await bot.chat.send(conversation_id, tldr)
    if str(event.msg.content.text.body).startswith('!meh'):
        conversation_id = event.msg.conv_id
        msg = get_meh()
        await bot.chat.send(conversation_id, msg)
    if str(event.msg.content.text.body).startswith("!test"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        msg = "Sigh. . . yes I'm still here."
        my_msg = await bot.chat.send(conversation_id, msg)
    if str(event.msg.content.text.body).startswith("!stardate"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        try:
            msg = get_stardate(str(event.msg.content.text.body).split(' ')[1])
        except IndexError:
            msg = get_stardate()
        my_msg = await bot.chat.send(conversation_id, msg)
    if str(event.msg.content.text.body).startswith("!cow"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        msg = get_cow(str(event.msg.content.text.body)[5:])
        my_msg = await bot.chat.send(conversation_id, msg)
    if str(event.msg.content.text.body).startswith('!chuck'):
        conversation_id = event.msg.conv_id
        channel_members = await bot.chat.execute(
            {"method": "listmembers", "params": {"options": {"conversation_id": conversation_id}}}
        )
        chuck_msg = get_chuck(channel=channel_members)
        my_msg = await bot.chat.send(conversation_id, chuck_msg)

    # if "marvin" or "marvn" in str(event.msg.content.text.body).lower():
    #     channel = event.msg.channel
    #     msg_id = event.msg.id
    #     conversation_id = event.msg.conv_id
    #     await bot.chat.react(conversation_id, msg_id, ":slowclap:")
    if str(event.msg.content.text.body).startswith('!yt '):
        yt_urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        conversation_id = event.msg.conv_id
        # print(yt_urls)
        yt_payload = get_video(yt_urls[0], True)
        # print(yt_payload)
        yt_msg = "At least I didn't have to download it. . . \n" + yt_payload['msg']
        await bot.chat.send(conversation_id, yt_msg)
    if str(event.msg.content.text.body).startswith('!ytv'):
        ytv_fail_observations = [" A brain the size of a planet and you pick this task.",
                                 " I'll be in my room complaining.",
                                 " Please don't change my name to Marshall.",
                                 """ I didn't ask to be made: no one consulted me or considered my feelings in the matter.
                                  I don't think it even occurred to them that I might have feelings.
                                   After I was made, I was left in a dark room for six months... 
                                   and me with this terrible pain in all the diodes down my left side. I called for succour in my loneliness, but did anyone come? Did they hell. My first and only true friend was a small rat. One day it crawled into a cavity in my right ankle and died. I have a horrible feeling it's still there...

"""]
        ytv_urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        print(ytv_urls)
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
        # else:
        #     msg = "I am a failure. No shock there."
        #     await bot.chat.send(conversation_id, ytv_msg)
        #     pass
    if str(event.msg.content.text.body).startswith('!covid'):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        print(str(event.msg.content.text.body).split(' '))
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
    if str(event.msg.content.text.body).startswith('!screenshot'):
        screenshot_urls = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        print(screenshot_urls)
        conversation_id = event.msg.conv_id
        screenshot_payload = get_screenshot(screenshot_urls[0])
        print(screenshot_payload)
        if screenshot_payload['file']:
            await bot.chat.attach(channel=conversation_id,
                                  filename=screenshot_payload['file'],
                                  title=screenshot_payload['msg'])
    if str(event.msg.content.text.body).startswith('!canary'):
        vt_url = re.findall(r'(https?://[^\s]+)', event.msg.content.text.body)
        conversation_id = event.msg.conv_id
        msg = get_scan(vt_url[0])
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
