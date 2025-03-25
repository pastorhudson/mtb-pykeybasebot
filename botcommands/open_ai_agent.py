from openai import OpenAI
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, ResponseOutputText
import logging
from pathlib import Path
import json

# Bot Command Imports
from botcommands.morse import get_morse_code
# from botcommands.natural_chat import get_chat, get_marvn_reaction, get_chat_with_image
from botcommands.jokes import get_joke
from botcommands.news import get_top_hacker_news
from botcommands.since import set_since, get_since, reset_since, reset_sign
from botcommands.tldr import tldr_react, get_gpt_summary
from botcommands.weather import get_weather
from botcommands.youtube_dlp import get_mp3, get_mp4, get_meta
from botcommands.covid import get_covid
from botcommands.get_screenshot import get_screenshot
from botcommands.cow_say import get_cow
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
from botcommands.bible import get_esv_text
from botcommands.wager import get_wagers, make_wager, make_bet, payout_wager
from botcommands.sync import sync
# from botcommands.get_grades import get_academic_snapshot
from botcommands.eyebleach import get_eyebleach
from botcommands.checkspeed import get_speed
from botcommands.poll import make_poll
from botcommands.award_activity_points import award_activity_points
from botcommands.db_events import is_morning_report, write_morning_report_task
from botcommands.school_closings import get_school_closings
from botcommands.wordle import solve_wordle
from botcommands.send_queue import process_message_queue
# from botcommands.curl_commands import get_curl, extract_message_sender

# Initialize OpenAI client
client = OpenAI()

# Define function registry (mapping function names to actual implementations)
# Function Registry: Maps command names to their respective functions
FUNCTION_REGISTRY = {
    "get_esv_text": get_esv_text,
    "get_morse_code": get_morse_code,
    "get_new_chuck": get_new_chuck,
    "get_cow": get_cow,
    "generate_dalle_image": generate_dalle_image,
    "get_drwho": get_drwho,
    "get_eyebleach": get_eyebleach,
    # "get_academic_snapshot": get_academic_snapshot,
    "get_joke": get_joke,
    "get_meh": get_meh,
    "get_top_hacker_news": get_top_hacker_news,
    "make_poll": make_poll,
    "get_school_closings": get_school_closings,
    "get_screenshot": get_screenshot,
    "get_speed": get_speed,
    "get_stardate": get_stardate,
    "solve_wordle": solve_wordle,
    "get_weather": get_weather,
    "get_mp3": get_mp3,
    "get_mp4": get_mp4,
    "get_meta": get_meta,
    "get_till": get_till,
    "set_till": set_till,
    "get_wagers": get_wagers,
    "make_wager": make_wager,
    "make_bet": make_bet,
    "payout_wager": payout_wager,
    "sync": sync,
    "award_activity_points": award_activity_points,
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
    "write_score": write_score,
    "sync_score": sync_score,
    "get_members": get_members,
}

new_tools = [
    {
        "name": "award_activity_points",
        "type": "function",
        "description": "Award points based on user activity.",
        "parameters": {
            "type": "object",
            "required": ["event"],
            "properties": {
                "event": {"type": "object", "description": "The event triggering the point award."}
            }
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
        "name": "get_cow",
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
        "name": "get_drwho",
        "type": "function",
        "description": "Retrieve information about a Doctor Who episode.",
        "parameters": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string", "description": "Episode title or ID to search for."}
            }
        }
    },
    {
        "name": "get_eyebleach",
        "type": "function",
        "description": "Fetch images from r/eyebleach to improve mood.",
        "parameters": {
            "type": "object",
            "required": ["bleach_level"],
            "properties": {
                "bleach_level": {
                    "type": "integer",
                    "description": "Number of images to retrieve (1-11)."
                }
            }
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
                }
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
            "required": ["date"],
            "properties": {
                "date": {"type": "string", "description": "Date to convert (optional)."}
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
        "description": "Download YouTube video as MP3.",
        "parameters": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "YouTube video URL."}
            }
        }
    },
    {
        "name": "get_mp4",
        "type": "function",
        "description": "Download YouTube video as MP4.",
        "parameters": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "YouTube video URL."}
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

# Define available tools
# tools = [{
#     "name": "get_esv_text",
#     "type": "function",
#     "description": "Fetches the text of a specified Bible passage from the ESV API.",
#     "strict": True,
#     "parameters": {
#         "type": "object",
#         "required": ["passage", "plain_txt"],
#         "properties": {
#             "passage": {"type": "string", "description": "The Bible reference (e.g., 'john 3:16')."},
#             "plain_txt": {"type": "boolean", "description": "If true, returns text without formatting."}
#         },
#         "additionalProperties": False
#     }
# },
#     {"type": "web_search_preview"},
#     {
#         "name": "generate_dalle_image",
#         "type": "function",
#         "description": "Generates an image using DALL-E.",
#         "parameters": {
#             "type": "object",
#             "required": ["prompt"],
#             "properties": {
#                 "prompt": {"type": "string", "description": "Text describing the image to generate."}
#             }
#         }
#     }]


def get_ai_response(user_input: str):
    """Handles OpenAI response and returns text instead of printing."""

    response = client.responses.create(
        model="gpt-4o",
        tools=new_tools,
        input=user_input,
        instructions='"Marvn" is a chatbot with a depressing and sarcastic personality. He is skilled and actually helpful in all things. He is ultimately endearing in a comical dark humor way.'
    )


    if response.output:
        for item in response.output:
            if isinstance(item, ResponseFunctionToolCall) and item.type == "function_call":
                function_name = item.name
                arguments = json.loads(item.arguments)

                if function_name in FUNCTION_REGISTRY:
                    function_to_call = FUNCTION_REGISTRY[function_name]
                    result = function_to_call(**arguments)
                    return {"type": "text", "content": result}

                return {"type": "error", "content": f"⚠️ No registered function found for `{function_name}`."}

            elif isinstance(item, ResponseOutputMessage) and item.type == "message":
                for content in item.content:
                    if isinstance(content, ResponseOutputText) and content.type == "output_text":
                        return {"type": "text", "content": content.text}

            elif isinstance(item, ResponseOutputMessage) and item.type == "image":
                for content in item.content:
                    if content.type == "image":
                        return {"type": "image", "url": content.url}

    return {"type": "error", "content": "⚠️ No valid response received from OpenAI."}


async def handle_marvn_mention(bot, event):
    """Handles @Marvn mentions and responds using AI."""
    msg_id = event.msg.id
    team_name = event.msg.channel.name
    conversation_id = event.msg.conv_id

    # React to the mention
    await bot.chat.react(conversation_id, msg_id, ":marvin:")

    # Handle replies (if user is replying to a previous message)
    if event.msg.content.text.reply_to:
        logging.info("Processing a reply")
        original_msg = await bot.chat.get(conversation_id, event.msg.content.text.reply_to)

        if original_msg.message[0]['msg']['content']['type'] == "text":
            prompt = f"{original_msg.message[0]['msg']['sender']['username']}: {original_msg.message[0]['msg']['content']['text']['body']}\n\n" \
                     f"{event.msg.sender.username}: {str(event.msg.content.text.body)[7:]}"
            response = get_ai_response(prompt)

        elif original_msg.message[0]['msg']['content']['type'] == "attachment":
            storage = Path('./storage')
            prompt = f"Original Message from {original_msg.message[0]['msg']['sender']['username']}: {original_msg.message[0]['msg']['content']['attachment']['object']['title']}\n\n" \
                     f"Question from {event.msg.sender.username}: {str(event.msg.content.text.body)[7:]}"
            org_filename = original_msg.message[0]['msg']['content']['attachment']['object']['filename']
            filename = f"{storage.absolute()}/{org_filename}"

            logging.info("Downloading attachment...")
            org_conversation_id = original_msg.message[0]['msg']['conversation_id']
            await bot.chat.download(org_conversation_id, original_msg.message[0]['msg']['id'], filename)

            response = get_ai_response(f"{prompt} (Image: {filename})")

    else:
        response = get_ai_response(str(event.msg.content.text.body)[7:])

    # **Fix the TypeError by checking response type**
    if isinstance(response, dict) and "type" in response:
        if response["type"] == "text":
            await bot.chat.reply(conversation_id, msg_id, response["content"])
        elif response["type"] == "image":
            await bot.chat.attach(channel=conversation_id, filename=response["url"], title="Here’s your image!")
        else:
            await bot.chat.reply(conversation_id, msg_id, "⚠️ Unknown response type.")
    else:
        await bot.chat.reply(conversation_id, msg_id, "⚠️ Error: Response format invalid.")


# Example usage:
result = get_ai_response("tell me a joke")
print(result)  # You can replace this with any return logic needed
