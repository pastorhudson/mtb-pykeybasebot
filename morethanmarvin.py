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
from dotenv import load_dotenv
from botcommands.poll_results import get_polls
from pyjokes import pyjokes
from botcommands.tldr import get_tldr
import re
import random


load_dotenv('secret.env')

import pykeybasebot.types.chat1 as chat1
from pykeybasebot import Bot

logging.basicConfig(level=logging.DEBUG)

if "win32" in sys.platform:
    # Windows specific event-loop policy
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy()  # type: ignore
    )


async def handler(bot, event):
    if event.msg.content.type_name != chat1.MessageTypeStrings.TEXT.value:
        return
    if event.msg.content.type_name != chat1.MessageTypeStrings.TEXT.value:
        return
    if event.msg.content.text.body == "!pollresult":
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        polls = get_polls()
        await bot.chat.send(conversation_id, polls)
    if event.msg.content.text.body == "!joke" or event.msg.content.text.body == "!Joke":
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
    if event.msg.content.text.body == "!test":
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        msg = 'PASS!'
        await bot.chat.send(conversation_id, msg)
    # channel = event.msg.channel
    # msg_id = event.msg.id
    # await bot.chat.react(channel, msg_id, ":clap:")

listen_options = {
    "local": False,
    "wallet": False,
    "dev": False,
    "hide-exploding": False,
    "convs": True,
    "filter_channel": {"name": "morethanbits", "topic_name": "test", "members_type": "team"},
    "filter_channels": None,
}

bot = Bot(username="morethanmarvin", paperkey=os.environ.get('KEYBASE_PAPERKEY'), handler=handler, home_path='./morethanmarvin')


asyncio.run(bot.start(listen_options=listen_options))