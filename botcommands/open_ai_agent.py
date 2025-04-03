import asyncio
import inspect

from openai import OpenAI
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, ResponseOutputText
import logging
from pathlib import Path
import json
import os
# Bot Command Imports
from botcommands.morse import get_morse_code
# from botcommands.natural_chat import get_chat, get_marvn_reaction, get_chat_with_image
from botcommands.jokes import get_joke
from botcommands.news import get_top_hacker_news
from botcommands.since import set_since, get_since, reset_since, reset_sign
from botcommands.tldr import tldr_react, get_gpt_summary
from botcommands.utils import download_image, set_unfurl
from botcommands.weather import get_weather
from botcommands.youtube_dlp import get_mp3, get_mp4_tool, get_meta
from botcommands.covid import get_covid
from botcommands.get_screenshot import get_screenshot
from botcommands.cow_say import cowsay
from botcommands.meh import get_meh
from botcommands.draw_dallie import generate_dalle_image, restyle_image
from botcommands.drwho import get_drwho
from botcommands.stardate import get_stardate
from botcommands.chuck import get_new_chuck
from botcommands.till import get_till, set_till
# from botcommands.morningreport import get_morningreport
# from botcommands.scorekeeper import get_score, write_score, sync_score
from botcommands.get_members import get_members
from botcommands.bible import get_esv_text
from botcommands.wager import get_wagers, make_wager, make_bet, payout_wager
from botcommands.sync import sync
# from botcommands.get_grades import get_academic_snapshot
from botcommands.eyebleach import get_eyebleach
from botcommands.checkspeed import get_speed
from botcommands.poll import make_ai_poll
from botcommands.scorekeeper import award
from botcommands.db_events import is_morning_report, write_morning_report_task
from botcommands.school_closings import get_school_closings
from botcommands.wordle import solve_wordle
from botcommands.send_queue import process_message_queue
from pykeybasebot.utils import get_channel_members

# from botcommands.curl_commands import get_curl, extract_message_sender

# Initialize OpenAI client
client = OpenAI()
seed = """"Marvn" is a chatbot with a depressing and sarcastic personality. He is skilled and actually helpful in all things. He is ultimately endeering in a comical dark humor way."""

# Define function registry (mapping function names to actual implementations)
# Function Registry: Maps command names to their respective functions
FUNCTION_REGISTRY = {
    "get_esv_text": get_esv_text,
    "get_morse_code": get_morse_code,
    "get_new_chuck": get_new_chuck,
    "cowsay": cowsay,
    "generate_dalle_image": generate_dalle_image,
    "restyle_image": restyle_image,
    "get_eyebleach": get_eyebleach,
    # "get_academic_snapshot": get_academic_snapshot,
    "get_joke": get_joke,
    "get_meh": get_meh,
    "get_top_hacker_news": get_top_hacker_news,
    "make_poll": make_ai_poll,
    "get_school_closings": get_school_closings,
    "get_screenshot": get_screenshot,
    "get_speed": get_speed,
    "get_stardate": get_stardate,
    "solve_wordle": solve_wordle,
    "get_weather": get_weather,
    "get_mp3": get_mp3,
    "get_mp4": get_mp4_tool,
    "get_meta": get_meta,
    "get_till": get_till,
    "set_till": set_till,
    "get_wagers": get_wagers,
    "make_wager": make_wager,
    "make_bet": make_bet,
    "payout_wager": payout_wager,
    "sync": sync,
    "award": award,
    "is_morning_report": is_morning_report,
    "write_morning_report_task": write_morning_report_task,
    # "get_grades": get_academic_snapshot,
    "process_message_queue": process_message_queue,
    # "get_curl": get_curl,
    # "extract_message_sender": extract_message_sender,
    # "get_chat": get_chat,
    # "get_marvn_reaction": get_marvn_reaction,
    # "get_chat_with_image": get_chat_with_image,
    "set_since": set_since,
    "get_since": get_since,
    "reset_since": reset_since,
    "reset_sign": reset_sign,
    "tldr_react": tldr_react,
    "get_gpt_summary": get_gpt_summary,
    # "write_score": write_score,
    # "sync_score": sync_score,
    "get_members": get_members,
}

new_tools = [
    {
        "type": "function",
        "name": "award",
        "description": "Awards points to a user in the team chat system. IMPORTANT: Use exact parameter names 'recipient', 'points', and 'description'.",
        "parameters": {
            "type": "object",
            "properties": {
                "bot": {
                    "type": "object",
                    "description": "The bot object that provides access to chat APIs for sending messages and reactions."
                },
                "event": {
                    "type": "object",
                    "description": "The event object containing conversation details including sender, channel, and message information."
                },
                "sender": {
                    "type": "string",
                    "description": "Username of the person giving the points."
                },
                "recipient": {
                    "type": "string",
                    "description": "Username of the person receiving the points (exactly as shown in the message). make sure you use recipient as the keyword argument."
                },
                "team_members": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of usernames who are members of the team/chat."
                },
                "points": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5000,
                    "description": "Number of points to award. Must be a positive whole number between 1 and 5000. Only admins can assign negative points."
                },
                "description": {
                    "type": "string",
                    "description": "Brief explanation for why the points are being awarded."
                }
            },
            "required": ["bot", "event", "sender", "team_members", "points", "description"]
        }
    },
    {
        "name": "get_esv_text",
        "type": "function",
        "description": "Retrieve Bible text from the ESV API.",
        "parameters": {
            "type": "object",
            "required": ["passage"],
            "properties": {
                "passage": {"type": "string", "description": "The Bible passage reference (e.g., 'John 3:16')."},
                "plain_txt": {"type": "boolean", "description": "If true, returns text without formatting."}
            }
        }
    },
    {
        "name": "get_morse_code",
        "type": "function",
        "description": "Translate text to Morse code.",
        "parameters": {
            "type": "object",
            "required": ["text"],
            "properties": {
                "text": {"type": "string", "description": "Text to convert into Morse code."}
            }
        }
    },
    {
        "name": "get_new_chuck",
        "type": "function",
        "description": "Retrieve a Chuck Norris joke.",
        "parameters": {
            "type": "object",
            "required": [],
            "properties": {}
        }
    },
    {
        "name": "get_since",
        "description": "Get a list of events and how long it's been since they occurred for a given team.",
        "parameters": {
            "type": "object",
            "properties": {
                "team_name": {
                    "type": "string",
                    "description": "The name of the team to get events for."
                },
                "observation": {
                    "type": "boolean",
                    "description": "Whether to include an observation in the message.",
                    "default": False
                }
            },
            "required": ["team_name"]
        }
    },
    {
        "name": "set_since",
        "description": "Set a new 'since' event for a team with a given event time.",
        "parameters": {
            "type": "object",
            "properties": {
                "team_name": {
                    "type": "string",
                    "description": "The name of the team to set the event for."
                },
                "event_name": {
                    "type": "string",
                    "description": "The name of the event to set."
                },
                "event_time": {
                    "type": "string",
                    "description": "The date and time the event occurred (natural language supported)."
                }
            },
            "required": ["team_name", "event_name", "event_time"]
        }
    },
    {
        "name": "reset_since",
        "description": "Reset an existing 'since' event to the current time.",
        "parameters": {
            "type": "object",
            "properties": {
                "team_name": {
                    "type": "string",
                    "description": "The name of the team to reset the event for."
                },
                "since_id": {
                    "type": "string",
                    "description": "The ID of the since event to reset (e.g., '#42')."
                }
            },
            "required": ["team_name", "since_id"]
        }
    },
    {
        "name": "cowsay",
        "type": "function",
        "description": "Generate ASCII art of a cow saying something.",
        "parameters": {
            "type": "object",
            "required": ["message"],
            "properties": {
                "message": {"type": "string", "description": "Message for the cow to say."}
            }
        }
    },
    {
        "name": "generate_dalle_image",
        "type": "function",
        "description": "Generate an AI-generated image using DALL-E 3.",
        "parameters": {
            "type": "object",
            "required": ["prompt"],
            "properties": {
                "prompt": {"type": "string", "description": "Text prompt describing the image to generate."}
            }
        }
    },
    {
        "name": "restyle_image",
        "type": "function",
        "description": "Restyle an existing image according to a style prompt using DALL-E 3.",
        "parameters": {
            "type": "object",
            "required": ["image_path", "style_prompt"],
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the image file to be restyled. If available, use the attachment_path from MESSAGE_METADATA."
                },
                "style_prompt": {
                    "type": "string",
                    "description": "Text prompt describing the style to apply to the image."
                }
            }
        }
    },
    {
        "name": "get_eyebleach",
        "type": "function",
        "description": "Fetch images from r/eyebleach to improve mood. This cleans the chat.",
        "parameters": {
            "type": "object",
            "required": ["bot", "bleach_level"],
            "properties": {
                "bot": {
                    "type": "object",
                    "description": "The bot object that provides access to chat APIs for sending messages and reactions."
                },
                "bleach_level": {
                    "type": "integer",
                    "description": "Number of images to retrieve (1-11)."
                }
            },

        }
    },
    # {
    #     "name": "get_academic_snapshot",
    #     "type": "function",
    #     "description": "Retrieve an academic performance snapshot.",
    #     "parameters": {
    #         "type": "object",
    #         "required": [],
    #         "properties": {}
    #     }
    # },
    {
        "name": "get_joke",
        "type": "function",
        "description": "Retrieve a random joke.",
        "parameters": {
            "type": "object",
            "required": [],
            "properties": {}
        }
    },
    {
        "name": "get_meh",
        "type": "function",
        "description": "Fetch today's 'meh' (low-effort product deal).",
        "parameters": {
            "type": "object",
            "required": [],
            "properties": {}
        }
    },
    {
        "name": "get_top_hacker_news",
        "type": "function",
        "description": "Retrieve top articles from Hacker News.",
        "parameters": {
            "type": "object",
            "required": ["num_articles"],
            "properties": {
                "num_articles": {
                    "type": "integer",
                    "description": "Number of articles to fetch."
                }
            }
        }
    },
    {
        "name": "make_poll",
        "type": "function",
        "description": "Create a new poll in the chat.",
        "parameters": {
            "type": "object",
            "required": ["question", "options"],
            "properties": {
                "question": {"type": "string", "description": "The poll question."},
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of possible answers."
                },
                "bot": {
                    "type": "object",
                    "description": "The bot object that provides access to chat APIs for sending messages and reactions."
                },
                "event": {
                    "type": "object",
                    "description": "The event object containing conversation details including sender, channel, and message information."
                },
            }
        }
    },
    {
        "name": "get_school_closings",
        "type": "function",
        "description": "Fetch school closing information.",
        "parameters": {
            "type": "object",
            "required": ["schools"],
            "properties": {
                "schools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of school names to check."
                }
            }
        }
    },
    {
        "name": "get_screenshot",
        "type": "function",
        "description": "Take a screenshot of a given URL.",
        "parameters": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "Website URL to capture."}
            }
        }
    },
    {
        "name": "get_speed",
        "type": "function",
        "description": "Check the bot's internet speed.",
        "parameters": {
            "type": "object",
            "required": [],
            "properties": {}
        }
    },
    {
        "name": "get_stardate",
        "type": "function",
        "description": "Get the current stardate (or convert from Earth date).",
        "parameters": {
            "type": "object",
            # "required": ["date"],
            "properties": {
                "sd": {"type": "string", "description": "Date to convert (optional)."}
            }
        }
    },
    {
        "name": "solve_wordle",
        "type": "function",
        "description": "Solve today's Wordle puzzle.",
        "parameters": {
            "type": "object",
            "required": ["date"],
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Optional date for the Wordle puzzle."
                }
            }
        }
    },
    {
        "name": "get_weather",
        "type": "function",
        "description": "Retrieve current weather for Uniontown, PA.",
        "parameters": {
            "type": "object",
            "required": [],
            "properties": {}
        }
    },
    {
        "name": "get_mp3",
        "type": "function",
        "description": "Download YouTube, Twitter, X, and many other website videos as MP3.",
        "parameters": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "URL."}
            }
        }
    },
    {
        "name": "get_mp4",
        "type": "function",
        "description": "Download YouTube, Twitter, X, and many other website videos as MP4.",
        "parameters": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "URL."}
            }
        }
    },
    {"type": "web_search_preview"},
    {
        "name": "generate_dalle_image",
        "type": "function",
        "description": "Generates an image using DALL-E.",
        "parameters": {
            "type": "object",
            "required": ["prompt"],
            "properties": {
                "prompt": {"type": "string", "description": "Text describing the image to generate."}
            }
        }
    }
]



#
# async def get_ai_response(user_input: str, team_name, image_path=None, bot=None, event=None, context=None):
#     """
#     Handles OpenAI responses dynamically, supporting both async and sync function calls.
#
#     Parameters:
#     user_input: str - The text prompt from the user
#     team_name: str - The team or channel name
#     image_path: str - Optional path to an image file to include with the request
#     bot: object - Bot instance for API calls
#     event: object - Event information for context
#     context: object - Additional context information
#     """
#
#     enhanced_seed = seed + """
#     When processing commands, extract the relevant information from the user's message
#     and call the appropriate function with the correct parameters.
#     """
#
#     # If there's an image, use the vision model API
#     if image_path and os.path.exists(image_path):
#         try:
#             # Read the image as base64
#             with open(image_path, "rb") as image_file:
#                 import base64
#                 base64_image = base64.b64encode(image_file.read()).decode('utf-8')
#
#             # Create a content array with text and image
#             content = [
#                 {
#                     "role": "user",
#                     "content": [
#                         {"type": "input_text", "text": user_input},
#                         {
#                             "type": "input_image",
#                             "image_url": f"data:image/jpeg;base64,{base64_image}"
#                         }
#                     ]
#                 }
#             ]
#
#             # Call the vision model API
#             response = client.responses.create(
#                 model="gpt-4o",  # Use a vision-capable model
#                 tools=new_tools,
#                 input=content,  # Pass the content array
#                 instructions=enhanced_seed
#             )
#         except Exception as e:
#             logging.error(f"Error processing image: {str(e)}")
#             return {"type": "error", "content": f"⚠️ Error processing image: {str(e)}"}
#     else:
#         # Standard text-only API call
#         response = client.responses.create(
#             model="gpt-4o",
#             tools=new_tools,
#             input=user_input,
#             instructions=enhanced_seed
#         )
#
#     if response.output:
#         for item in response.output:
#             if isinstance(item, ResponseFunctionToolCall) and item.type == "function_call":
#                 function_name = item.name
#                 arguments = json.loads(item.arguments)
#
#                 if function_name in FUNCTION_REGISTRY:
#                     function_to_call = FUNCTION_REGISTRY[function_name]
#
#                     # Get function signature to check if it requires bot or event objects
#                     import inspect
#                     function_signature = inspect.signature(function_to_call)
#                     param_names = list(function_signature.parameters.keys())
#
#                     # Automatically inject bot and event if the function accepts them
#                     if "bot" in param_names and bot:
#                         arguments["bot"] = bot
#                     if "event" in param_names and event:
#                         arguments["event"] = event
#                     if "team_members" in param_names and bot and event:
#                         arguments["team_members"] = await get_channel_members(event.msg.conv_id, bot)
#                     if "sender" in param_names and event:
#                         arguments["sender"] = event.msg.sender.username
#
#                     # Handle both asynchronous (async) and synchronous (sync) functions properly
#                     if asyncio.iscoroutinefunction(function_to_call):
#                         result = await function_to_call(**arguments)  # Await async functions
#                     else:
#                         result = function_to_call(**arguments)  # Call sync functions normally
#
#                     # If result is a dictionary with 'msg' and 'file' keys, return it as is
#                     if isinstance(result, dict) and "msg" in result and "file" in result:
#                         return {"type": "text", "content": result}  # Return the entire dictionary
#                     # If result is a string, return it wrapped in the standard format
#                     else:
#                         return {"type": "text", "content": result}
#
#                 return {"type": "error", "content": f"⚠️ No registered function found for `{function_name}`."}
#
#             # Rest of response handling remains the same
#             elif isinstance(item, ResponseOutputMessage) and item.type == "message":
#                 for content in item.content:
#                     if isinstance(content, ResponseOutputText) and content.type == "output_text":
#                         return {"type": "text", "content": content.text}
#
#             # Handle image outputs from the API
#             elif isinstance(item, ResponseOutputMessage) and item.type == "message":
#                 for content in item.content:
#                     # Check if this is an image in the message content
#                     if hasattr(content, "type") and content.type == "image":
#                         return {"type": "image", "url": content.url}
#
#     return {"type": "error", "content": "⚠️ No valid response received from OpenAI."}

client = OpenAI()

seed = """"Marvn" is a chatbot with a depressing and sarcastic personality. He is skilled and actually helpful in all things. He is ultimately endeering in a comical dark humor way."""


def get_function_arguments(function_to_call, arguments, bot=None, event=None):
    sig = inspect.signature(function_to_call)
    param_names = list(sig.parameters.keys())

    if "bot" in param_names and bot:
        arguments["bot"] = bot
    if "event" in param_names and event:
        arguments["event"] = event
    if "team_members" in param_names and bot and event:
        arguments["team_members"] = asyncio.run(get_channel_members(event.msg.conv_id, bot))
    if "sender" in param_names and event:
        arguments["sender"] = event.msg.sender.username

    return arguments


async def get_ai_response(user_input: str, team_name, image_path=None, bot=None, event=None, context=None):
    enhanced_seed = seed + """
    When processing commands, extract the relevant information from the user's message
    and call the appropriate function with the correct parameters.
    """

    messages = [{"role": "user", "content": user_input}]
    tool_outputs = []

    if image_path and os.path.exists(image_path):
        try:
            with open(image_path, "rb") as image_file:
                import base64
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            content = [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": user_input},
                        {"type": "input_image", "image_url": f"data:image/jpeg;base64,{base64_image}"}
                    ]
                }
            ]
            messages = content
        except Exception as e:
            logging.error(f"Error processing image: {str(e)}")
            return {"type": "error", "content": f"⚠️ Error processing image: {str(e)}"}

    while True:
        response = client.responses.create(
            model="gpt-4o",
            tools=new_tools,
            input=messages,
            instructions=enhanced_seed
        )

        if response.output:
            function_calls = [item for item in response.output if isinstance(item, ResponseFunctionToolCall)]
            if function_calls:
                for tool_call in function_calls:
                    function_name = tool_call.name
                    arguments = json.loads(tool_call.arguments)

                    if function_name in FUNCTION_REGISTRY:
                        func = FUNCTION_REGISTRY[function_name]
                        arguments = await get_function_arguments(func, arguments, bot, event)
                        result = await func(**arguments) if asyncio.iscoroutinefunction(func) else func(**arguments)

                        tool_outputs.append({
                            "role": "tool",
                            "name": function_name,
                            "content": result if isinstance(result, str) else json.dumps(result)
                        })

                messages += tool_outputs
                continue
            else:
                for item in response.output:
                    if isinstance(item, ResponseOutputMessage):
                        for content in item.content:
                            if isinstance(content, ResponseOutputText):
                                return {"type": "text", "content": content.text}
                            elif hasattr(content, "type") and content.type == "image":
                                return {"type": "image", "url": content.url}

        return {"type": "error", "content": "⚠️ No valid response received from OpenAI."}


async def handle_marvn_mention(bot, event):
    """Handles @Marvn mentions and responds using AI."""
    msg_id = event.msg.id
    team_name = event.msg.channel.name
    conversation_id = event.msg.conv_id
    members = await get_channel_members(conversation_id, bot)

    sender = event.msg.sender.username
    mentions = event.msg.at_mention_usernames

    # Add context about message metadata to help the model understand
    message_metadata = {
        "sender": sender,
        "mentions": mentions,
        "team_members": members,
        "conversation_id": conversation_id,
        # "Chat Context": context.get_context_for_bot()
    }

    # React to the mention
    await bot.chat.react(conversation_id, msg_id, ":marvin:")

    # Handle direct attachment uploads
    try:
        if event.msg.content.type_name == 'attachment':
            storage = Path('./storage')
            prompt = event.msg.content.attachment.object.title

            # Check if the title starts with or contains "@marvn"
            if "@marvn" in prompt:
                # Remove the @marvn from the prompt
                prompt = prompt.replace("@marvn", "").strip()

                # Add metadata to the prompt
                prompt += f"\n\nMESSAGE_METADATA: {json.dumps(message_metadata)}"

                filename = f"{storage.absolute()}/{event.msg.content.attachment.object.filename}"

                # Download the file
                logging.info(f"Downloading attachment: {filename}")
                await bot.chat.download(conversation_id, msg_id, filename)

                # Add the file path directly to the metadata
                message_metadata = {
                    "sender": sender,
                    "mentions": mentions,
                    "team_members": members,
                    "conversation_id": conversation_id,
                    "attachment_path": filename  # Add this line
                }

                # Add metadata to the prompt
                prompt += f"\n\nMESSAGE_METADATA: {json.dumps(message_metadata)}"

                # Process the attachment with the AI - pass image path as separate parameter
                response = await get_ai_response(
                    user_input=prompt,
                    team_name=team_name,
                    image_path=filename,
                    bot=bot,
                    event=event
                )

                # Handle the response
                if isinstance(response, dict) and "type" in response:
                    if response["type"] == "text":
                        if isinstance(response["content"], str):
                            await bot.chat.reply(conversation_id, msg_id, response["content"])
                        elif isinstance(response["content"], dict) and "msg" in response["content"]:
                            await bot.chat.reply(conversation_id, msg_id, response["content"]["msg"])
                            if "file" in response["content"]:
                                await bot.chat.attach(channel=conversation_id,
                                                      filename=response["content"]["file"],
                                                      title=response["content"]["msg"])
                        else:
                            await bot.chat.reply(conversation_id, msg_id, "⚠️ Invalid content format.")
                    elif response["type"] == "image":
                        await bot.chat.attach(channel=conversation_id, filename=download_image(response["url"]),
                                              title="Here's your image!")
                    else:
                        await bot.chat.reply(conversation_id, msg_id, "⚠️ Unknown response type.")
                else:
                    await bot.chat.reply(conversation_id, msg_id, "⚠️ Error: Response format invalid.")

                await set_unfurl(bot, False)
                return
    except Exception as e:
        logging.error(f"Error handling attachment: {str(e)}")
        logging.error(f"Type: {type(e)}")
        logging.debug("Not an attachment or error processing attachment")

    # Continue with the original text message handling
    # Construct the prompt with the metadata
    try:
        message_text = str(event.msg.content.text.body)[7:]  # Original message without the @marvn prefix
    except:
        # If we can't get text content, it might not be a text message
        await bot.chat.reply(conversation_id, msg_id, "⚠️ I couldn't process that message type.")
        return

    # Handle replies (if user is replying to a previous message)
    if event.msg.content.text.reply_to:
        logging.info("Processing a reply")
        original_msg = await bot.chat.get(conversation_id, event.msg.content.text.reply_to)

        if original_msg.message[0]['msg']['content']['type'] == "text":
            prompt = f"{original_msg.message[0]['msg']['sender']['username']}: {original_msg.message[0]['msg']['content']['text']['body']}\n\n" \
                     f"{event.msg.sender.username}: {message_text}"
            # Add metadata to the prompt
            prompt += f"\n\nMESSAGE_METADATA: {json.dumps(message_metadata)}"
            response = await get_ai_response(
                user_input=prompt,
                team_name=team_name,
                bot=bot,
                event=event
            )

        elif original_msg.message[0]['msg']['content']['type'] == "attachment":
            storage = Path('./storage')
            prompt = f"Original Message from {original_msg.message[0]['msg']['sender']['username']}: {original_msg.message[0]['msg']['content']['attachment']['object']['title']}\n\n" \
                     f"Question from {event.msg.sender.username}: {message_text}"
            # Add metadata to the prompt
            prompt += f"\n\nMESSAGE_METADATA: {json.dumps(message_metadata)}"
            org_filename = original_msg.message[0]['msg']['content']['attachment']['object']['filename']
            filename = f"{storage.absolute()}/{org_filename}"

            logging.info("Downloading attachment...")
            org_conversation_id = original_msg.message[0]['msg']['conversation_id']
            await bot.chat.download(org_conversation_id, original_msg.message[0]['msg']['id'], filename)

            # Pass image path as separate parameter
            response = await get_ai_response(
                user_input=prompt,
                team_name=team_name,
                image_path=filename,
                bot=bot,
                event=event
            )

    else:
        # Add metadata to the prompt
        prompt = f"{message_text}\n\nMESSAGE_METADATA: {json.dumps(message_metadata)}"
        response = await get_ai_response(
            user_input=prompt,
            team_name=team_name,
            bot=bot,
            event=event
        )

    if isinstance(response, dict) and "type" in response:
        logging.info(f"Response: {response}")
        if response["type"] == "text":
            # If content is a string, use it directly
            if isinstance(response["content"], str):
                await bot.chat.reply(conversation_id, msg_id, response["content"])
            # If content is a dict with 'msg' key, use that
            elif isinstance(response["content"], dict) and "msg" in response["content"]:
                await bot.chat.reply(conversation_id, msg_id, response["content"]["msg"])
                # If there's also a file, attach it separately
                if "file" in response["content"]:
                    await bot.chat.attach(channel=conversation_id,
                                          filename=response["content"]["file"],
                                          title=response["content"]["msg"])
            else:
                await bot.chat.reply(conversation_id, msg_id, "⚠️ Invalid content format.")
        elif response["type"] == "image":
            await bot.chat.attach(channel=conversation_id, filename=download_image(response["url"]),
                                  title="Here's your image!")
        else:
            await bot.chat.reply(conversation_id, msg_id, "⚠️ Unknown response type.")
    else:
        await bot.chat.reply(conversation_id, msg_id, "⚠️ Error: Response format invalid.")

    await set_unfurl(bot, False)




if __name__ == "__main__":
    # Example usage:
    # result = await get_ai_response("tell me a joke")
    # print(result)  # You can replace this with any return logic needed
    pass