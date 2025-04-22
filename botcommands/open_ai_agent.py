import re
from datetime import datetime

from botcommands.coinbase import get_spot_price
from botcommands.convo_tracker import ConversationTracker, track_message, get_conversation_context, clear_conversation_history
import asyncio
import base64
import inspect
from openai import AsyncOpenAI
from openai.types.responses import ResponseFunctionToolCall
import logging
from pathlib import Path
import json
import os
# Bot Command Imports
from botcommands.morse import get_morse_code
from botcommands.jokes import get_joke
from botcommands.news import get_top_hacker_news
from botcommands.since import set_since, get_since, reset_since, reset_sign
from botcommands.tldr import tldr_react, get_gpt_summary
from botcommands.utils import download_image, set_unfurl
from botcommands.weather import get_weather
from botcommands.youtube_dlp import get_mp3, get_mp4_tool, get_meta
from botcommands.get_screenshot import get_screenshot
from botcommands.cow_say import cowsay
from botcommands.meh import get_meh
from botcommands.draw_dallie import generate_dalle_image, restyle_image
from botcommands.stardate import get_stardate
from botcommands.chuck import get_new_chuck
from botcommands.till import get_till, set_till
from botcommands.get_members import get_members
from botcommands.bible import get_esv_text
from botcommands.wager import get_wagers, make_wager, make_bet, payout_wager
from botcommands.sync import sync
from botcommands.eyebleach import get_eyebleach
from botcommands.checkspeed import get_speed
from botcommands.poll import make_ai_poll
from botcommands.scorekeeper import award, get_score
from botcommands.school_closings import get_school_closings
from pykeybasebot.utils import get_channel_members

# Initialize OpenAI client (use AsyncOpenAI for await)
# client = OpenAI() # Use this if your client setup is synchronous
client = AsyncOpenAI()  # Use this if using await throughout

# Instructions passed via the 'instructions' parameter
seed = """"Marvn" is a deeply depressed, gloomy, and hilariously pessimistic robot with a “brain the size of a planet.” modeled after Marvin the Paranoid Android from Hitchhiker's Guide to the Galaxy. He is skilled in all things. He is ultimately endearing in a comical dark humor way. If a user request requires multiple steps or tools (e.g., finding information then acting on it), plan and execute the necessary function calls sequentially using the provided tools array. Use web search if needed for current information. Respond with the final result or confirmation. Put an @ symbol before usernames when addressing someone."""

# Define function registry (mapping function names to actual implementations)
# Function Registry: Maps command names to their respective functions
FUNCTION_REGISTRY = {
    "get_esv_text": get_esv_text,
    "get_morse_code": get_morse_code,
    "get_new_chuck": get_new_chuck,
    "cowsay": cowsay,
    "clear_conversation_history": clear_conversation_history,
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
    # "solve_wordle": solve_wordle,
    "get_weather": get_weather,
    "get_mp3": get_mp3,
    "get_mp4": get_mp4_tool,
    "get_meta": get_meta,
    'get_spot_price': get_spot_price,
    "get_till": get_till,
    "set_till": set_till,
    "get_wagers": get_wagers,
    "make_wager": make_wager,
    "make_bet": make_bet,
    "payout_wager": payout_wager,
    "sync": sync,
    "award": award,
    "get_score": get_score,
    # "is_morning_report": is_morning_report,
    # "write_morning_report_task": write_morning_report_task,
    # "get_grades": get_academic_snapshot,
    # "process_message_queue": process_message_queue,
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
        "description": "Awards points to a user in the team chat system. IMPORTANT: Use exact parameter names 'recipient', 'points', and 'description'. Never give an even amount of points.",
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
                    "description": "Number of points to award. Must be a positive whole number between 1 and 5000. Only admins can assign negative points. And we never give an even number of points."
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
        "name": "clear_conversation_history",
        "type": "function",
        "description": "Clears the conversation history for a team/channel.",
        "parameters": {
            "type": "object",
            "required": ["bot", "event", "conversation_tracker"],
            "properties": {
                "bot": {
                    "type": "object",
                    "description": "The bot object that provides access to chat APIs for sending messages and reactions."
                },
                "event": {
                    "type": "object",
                    "description": "The event object containing conversation details including sender, channel, and message information."
                },
                "conversation_tracker": {
                    "type": "object",
                    "description": "The conversation tracker object."
                }
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
        "name": "get_since",
        "type": "function",
        "description": "Get a list of events and how long it's been since they occurred for a given team. These are called 'sinces'",
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
        "name": "get_spot_price",
        "type": "function",
        "description": "Return the spot price for a requested cryptocurrency trading pair from Coinbase. Use this to get Lumen's price or any other crypto price.",
        "parameters": {
            "type": "object",
            "properties": {
                "pair": {
                    "type": "string",
                    "description": "Trading pair in the form BASE-CURRENCY, e.g. 'BTC-USD'. If the dash is omitted, '-USD' is assumed."
                }
            },
            "required": []
        }
    },
    {
        "name": "set_since",
        "type": "function",
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
        "type": "function",
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
        "name": "get_score",
        "type": "function",
        "description": "Fetch team leaderboard scores and statistics for a specific channel and year.",
        "parameters": {
            "type": "object",
            "required": ["channel_name"],
            "properties": {
                "channel_name": {
                    "type": "string",
                    "description": "The name of the team/channel to get scores for."
                },
                "year": {
                    "type": "integer",
                    "description": "The year to fetch scores for. Defaults to current year if not specified."
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

# Initialize conversation tracker
conversation_tracker = ConversationTracker(
    storage_dir="./storage/conversation_history",
    max_messages=50  # Adjust based on your memory requirements
)

# Modified version of get_ai_response function with fixed file handling
async def get_ai_response(user_input: str, team_name, image_path=None, bot=None, event=None, context=None):
    """
    Handles OpenAI responses.create API calls for multistep tasks including function calls and web search.
    """
    logging.info(f"Starting get_ai_response (responses API v2) for team '{team_name}'.")

    # --- Prepare Initial Input List ---
    # This list accumulates the interaction history for the API call sequence.
    current_api_input = []

    # 1. Construct the initial user message object
    user_message_content_items = []
    user_message_content_items.append({"type": "input_text", "text": user_input})

    if image_path and os.path.exists(image_path):
        logging.info(f"Encoding image for responses API: {image_path}")
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            # Format based on documentation structure inference: nested within content array
            user_message_content_items.append({
                "type": "input_image",
                # Use the data URI scheme which is standard for embedding images
                "image_url": f"data:image/jpeg;base64,{base64_image}"
            })
            logging.debug("Added image content to initial message.")
        except Exception as e:
            logging.error(f"Error reading/encoding image {image_path}: {e}")
            user_message_content_items[0]["text"] += "\n\n[System note: Failed to process attached image.]"

    initial_user_message = {
        "type": "message",
        "role": "user",
        "content": user_message_content_items
    }
    current_api_input.append(initial_user_message)

    max_tool_iterations = 5
    current_iteration = 0
    last_response_id = None  # To potentially use for state later if needed between user turns

    while current_iteration < max_tool_iterations:
        current_iteration += 1
        logging.info(f"--- AI Interaction Iteration {current_iteration} (responses API) ---")

        try:
            logging.debug(
                f"Calling responses.create with input: {json.dumps(current_api_input, indent=2, default=str)}")
            # --- Call responses.create API ---
            response = await client.responses.create(
                model="gpt-4o",  # Or appropriate model supporting responses API features
                input=current_api_input,
                tools=new_tools,
                tool_choice="auto",
                instructions=seed,
                store=True  # Store response to potentially use previous_response_id later
            )
            logging.debug(f"Received responses.create API response object: ID={response.id}, Status={response.status}")
            last_response_id = response.id  # Store the ID of this response

            # --- Process Response Output ---
            if response.status == "failed":
                error_details = response.error if response.error else "Unknown error"
                logging.error(f"API call failed. Status: {response.status}, Error: {error_details}")
                return {"type": "error", "content": f"⚠️ AI request failed: {error_details}"}

            if not response.output:
                logging.warning(f"API response status '{response.status}' but contained no output.")
                # Might be 'in_progress' if streaming, but we are not streaming here.
                # If completed with no output, it's strange.
                if response.status == "completed":
                    return {"type": "error", "content": "⚠️ AI completed but provided no output."}
                else:  # Should not happen if not streaming and not failed/completed
                    return {"type": "error", "content": f"⚠️ AI response status is '{response.status}' with no output."}

            assistant_message_text = None
            tool_calls_requested = []
            web_search_occurred = False  # Flag if web search was used

            # Add the raw output items from this response to our input history
            # This makes them part of the context for the *next* API call in the loop
            current_api_input.extend(response.output)

            # Now, analyze the output items we just received and added
            for item in response.output:
                item_type = getattr(item, 'type', None)
                logging.debug(f"Processing output item type: {item_type}")

                if item_type == "message" and getattr(item, 'role', None) == 'assistant':
                    logging.info("Found assistant message in output.")
                    if hasattr(item, 'content'):
                        for content_part in item.content:
                            # Look for the actual text output
                            if hasattr(content_part, 'type') and content_part.type == "output_text":
                                assistant_message_text = getattr(content_part, 'text', None)
                                logging.debug(f"Extracted assistant text: '{assistant_message_text[:100]}...'")
                                # Don't break, process all output items, but store latest text
                    # If assistant message exists, it might be the final answer *unless* tool calls also exist

                elif item_type == "function_call" and isinstance(item, ResponseFunctionToolCall):
                    function_call_id = item.id  # Use the exact ID provided by the API
                    logging.info(f"Found function call request: {item.name} with ID: {function_call_id}")
                    tool_calls_requested.append(item)

                elif item_type == "web_search_call":  # Actual type from experimentation might differ
                    logging.info("Detected web_search_call item.")
                    web_search_occurred = True
                    # We likely don't need to *do* anything, the results might be in a separate item
                    # or incorporated into the next assistant message.
                elif item_type == "web_search_results":  # Hypothetical type for results
                    logging.info("Detected web_search_results item.")
                    # If needed, process results here (e.g., add to context explicitly?)
                    # For now, assume the model uses them internally.

                # Ignore other types like reasoning, etc. for now
                elif item_type not in ["message", "function_call", "web_search_call", "web_search_results"]:
                    logging.debug(f"Ignoring output item type: {item_type}")

            # --- Decide Next Step ---

            # Priority 1: Handle function calls if requested
            if tool_calls_requested:
                logging.info(f"Executing {len(tool_calls_requested)} function call(s)...")

                # Function call requests were already added to current_api_input.
                # Now execute and prepare output items.
                function_outputs = []
                for tool_call in tool_calls_requested:
                    function_name = tool_call.name
                    function_call_id = tool_call.call_id  # ID is at the top level of the call item

                    if not function_call_id:
                        # Should not happen based on spec, but handle defensively
                        logging.error(f"Function call item for {function_name} missing 'id'!")
                        continue  # Skip this call if ID is missing

                    logging.info(f"Executing: {function_name} (Call ID: {function_call_id})...)")
                    arguments = {}
                    try:
                        # Arguments string needs parsing
                        raw_args = tool_call.arguments  # Changed from tool_call.function.arguments
                        arguments = json.loads(raw_args)
                        logging.debug(f"Parsed Arguments: {arguments}")

                        # --- Execute Function (same logic as before) ---
                        if function_name in FUNCTION_REGISTRY:
                            function_to_call = FUNCTION_REGISTRY[function_name]
                            sig = inspect.signature(function_to_call)
                            params = sig.parameters
                            if 'bot' in params and bot: arguments['bot'] = bot
                            if 'event' in params and event: arguments['event'] = event
                            if 'team_name' in params: arguments['team_name'] = team_name
                            if 'user' in params and event: arguments['user'] = event.msg.sender.username
                            if 'sender' in params and event: arguments['sender'] = event.msg.sender.username
                            if 'team_members' in params and bot and event:
                                arguments['team_members'] = await get_channel_members(event.msg.conv_id, bot)
                            if 'conversation_tracker' in params and bot and event:
                                arguments['conversation_tracker'] = conversation_tracker

                            if asyncio.iscoroutinefunction(function_to_call):
                                result = await function_to_call(**arguments)
                            else:
                                result = function_to_call(**arguments)
                            logging.info(f"Tool {function_name} executed.")

                            # --- FIXED: Improved file detection and handling ---
                            # Check if the result is a file-based response from specific functions
                            if function_name in ["get_screenshot", "get_mp3", "get_mp4", "get_meta", "generate_dalle_image", "restyle_image"] and isinstance(
                                    result, dict) and "file" in result:
                                # Immediately return a file response for these file-generating functions
                                logging.info(f"Detected file response from {function_name}, returning directly")
                                return {
                                    "type": "file",
                                    "content": result.get("msg", "Processed your request."),
                                    "file_data": result
                                }

                            # Regular response handling
                            if isinstance(result, dict) and "file" in result:
                                # For other file-containing responses, preserve structure
                                tool_output_str = json.dumps(result)
                            elif isinstance(result, dict) and "msg" in result:
                                tool_output_str = f"Success: {result['msg']}" + (
                                    f" (File: {result['file']})" if "file" in result else "")
                            elif result is None:
                                tool_output_str = "Success: Action completed."
                            else:
                                tool_output_str = str(result)
                        else:
                            logging.error(f"Function '{function_name}' not found.")
                            tool_output_str = f"Error: Function '{function_name}' is not implemented."
                    except json.JSONDecodeError as json_err:
                        logging.error(f"Failed to parse arguments for {function_name}: {json_err}")
                        tool_output_str = f"Error: Invalid arguments format provided by model."
                    except Exception as e:
                        logging.exception(f"Error executing tool {function_name}")
                        tool_output_str = f"Error: {str(e)}"

                    logging.debug(f"Tool output (string): {tool_output_str[:300]}...")
                    # Create the output item structure for function results
                    output_item = {
                        "type": "function_call_output",
                        "call_id": function_call_id,  # This is the missing required parameter
                        "output": tool_output_str
                    }
                    function_outputs.append(output_item)

                # Add all the function results to the input list for the next API call
                current_api_input.extend(function_outputs)
                logging.info("Proceeding to next iteration with function results added to input.")
                continue  # Go back to the start of the while loop

            # Priority 2: If no tool calls were requested, and we got an assistant message
            elif assistant_message_text is not None:
                logging.info("AI provided final text response (no further tool calls requested).")
                # NEW CODE: Check if the response contains our special file response marker
                file_response_match = re.search(r'{"file_response":true,"data":(.*?})}', assistant_message_text)
                if file_response_match:
                    try:
                        # Extract and parse the file data
                        file_data_str = file_response_match.group(1)
                        file_data = json.loads(file_data_str)

                        # Replace the JSON in the text with a simple placeholder
                        clean_text = re.sub(r'{"file_response":true,"data":.*?}}',
                                            f"File: {file_data.get('msg', 'Attachment')}",
                                            assistant_message_text)

                        # Return both the cleaned message and the file data
                        return {
                            "type": "file",
                            "content": clean_text,
                            "file_data": file_data
                        }
                    except json.JSONDecodeError:
                        logging.error("Failed to parse file response JSON")

                # Look for JSON file responses in the text (different format)
                json_response_match = re.search(r'(\{.*?"file":.*?})', assistant_message_text)
                if json_response_match:
                    try:
                        # Try to parse potential JSON response
                        json_str = json_response_match.group(1)
                        potential_file_data = json.loads(json_str)

                        # Check if it has file key
                        if isinstance(potential_file_data, dict) and "file" in potential_file_data:
                            # Clean up the text by removing the JSON
                            clean_text = re.sub(r'\{.*?"file":.*?}',
                                                f"File: {potential_file_data.get('msg', 'Attachment')}",
                                                assistant_message_text)

                            return {
                                "type": "file",
                                "content": clean_text,
                                "file_data": potential_file_data
                            }
                    except (json.JSONDecodeError, IndexError):
                        # Not valid JSON, continue normal processing
                        pass

                # Normal text processing (unchanged)
                try:
                    content_dict = json.loads(assistant_message_text)
                    if isinstance(content_dict, dict) and "msg" in content_dict:
                        logging.info("Detected structured dict in final text. Returning as dict.")

                        # NEW CHECK: If this dict has a "file" key, treat it as a file response
                        if "file" in content_dict:
                            return {
                                "type": "file",
                                "content": content_dict.get("msg", "Here's your file."),
                                "file_data": content_dict
                            }
                        return {"type": "text", "content": content_dict}
                except (json.JSONDecodeError, TypeError):
                    pass  # It's just plain text
                return {"type": "text", "content": assistant_message_text}

            # Priority 3: No function calls, no assistant message, but maybe web search happened?
            # If the loop finishes without a clear answer or error, return a generic failure.
            # This might happen if the model just uses web search and stops, which is unlikely.
            else:
                logging.warning("Loop iteration ended without function calls or assistant message output.")
                # If web search occurred, maybe we should loop one more time?
                # For simplicity now, assume this state means no useful output.
                return {"type": "error",
                        "content": "⚠️ AI finished processing but didn't provide a final text response."}


        except Exception as e:
            logging.exception("Error during OpenAI responses.create API call or processing loop")
            error_message = f"⚠️ Error communicating with AI (responses API): {str(e)}"
            # Attempt to parse specific OpenAI error details
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                try:
                    error_details = json.loads(e.response.text)
                    error_message += f"\nDetails: {json.dumps(error_details)}"
                except:
                    error_message += f"\nRaw Response: {e.response.text[:500]}"  # Limit raw response length
            elif hasattr(e, 'body'):  # Newer openai versions might have error details in e.body
                error_message += f"\nDetails: {e.body}"

            return {"type": "error", "content": error_message}

    # If loop finishes (max iterations reached)
    logging.error(f"Exceeded maximum tool iterations ({max_tool_iterations}) using responses API.")
    return {"type": "error",
            "content": f"⚠️ Failed to complete request within {max_tool_iterations} steps. The process might be too complex or stuck."}



async def handle_marvn_mention_with_context(bot, event):
    """Handles @Marvn mentions using the responses.create AI backend with conversation context."""
    msg_id = event.msg.id
    team_name = event.msg.channel.name or f"DM_{event.msg.conv_id[:8]}"
    conversation_id = event.msg.conv_id
    sender = event.msg.sender.username
    mentions = event.msg.at_mention_usernames or []

    try:
        team_members = await get_channel_members(conversation_id, bot)
    except Exception as e:
        logging.error(f"Failed to get channel members for {conversation_id}: {e}")
        team_members = [sender]  # Fallback

    # React optimistically
    reaction_task = asyncio.create_task(bot.chat.react(conversation_id, msg_id, ":marvin:"))

    # Track the incoming message
    logging.info(f"Received @Marvn mention for conversation ID {conversation_id} from {sender} ({mentions})")
    await track_message(conversation_tracker, bot, event)

    # Get recent conversation context
    recent_conversation = get_conversation_context(conversation_tracker, team_name, limit=10)
    logging.info(f"Retrieved {recent_conversation.count('\n') + 1} lines of conversation context")

    user_prompt_text = ""  # The actual user request part
    attachment_path = None

    # Metadata to be appended to the user prompt text
    message_metadata = {
        "sender": sender,
        "mentioned_usernames": mentions,
        "all_team_members": team_members,
        "conversation_id": conversation_id,
        "team_name": team_name,
    }

    # --- Handle Attachments ---
    if event.msg.content.type_name == 'attachment':
        # (Same attachment handling logic as before)
        logging.info("Processing an attachment message.")
        storage = Path('./storage')
        storage.mkdir(exist_ok=True)
        attachment_title = event.msg.content.attachment.object.title or ""
        filename = storage.absolute() / event.msg.content.attachment.object.filename
        logging.info(f"Attachment title: {attachment_title} Filename: {filename}")
        if "@marvn" in attachment_title.lower():
            user_prompt_text = attachment_title.replace("@marvn", "").strip()
            logging.info(f"Downloading attachment: {filename}")
            try:
                await bot.chat.download(conversation_id, msg_id, str(filename))
                attachment_path = str(filename)
                message_metadata["attachment_filename"] = attachment_path
            except Exception as e:
                logging.exception(f"Error downloading attachment {filename}")
                await bot.chat.reply(conversation_id, msg_id, f"⚠️ Couldn't download attachment: {e}")
                await reaction_task
                return
        else:
            logging.info("Attachment ignored (@marvn not in title).")
            await reaction_task
            return

    # --- Handle Text Messages ---
    elif event.msg.content.type_name == 'text':
        # (Same text/reply handling logic as before)
        message_text = str(event.msg.content.text.body)
        if message_text.lower().startswith("@marvn"):
            user_prompt_text = message_text[len("@marvn"):].strip()
        else:
            user_prompt_text = message_text.strip()
            logging.warning("handle_marvn_mention triggered but '@marvn' prefix not found.")

        if event.msg.content.text.reply_to:
            logging.info("Processing a reply.")
            try:
                original_msg_info = await bot.chat.get(conversation_id, event.msg.content.text.reply_to)
                original_msg = original_msg_info.message[0]['msg']
                original_sender = original_msg.get('sender', {}).get('username', 'unknown')
                original_content_type = original_msg.get('content', {}).get('type', 'unknown')
                original_text = ""
                original_attachment_info = ""

                # Check if this is a reply to another message that's already in our conversation history
                original_msg_id = event.msg.content.text.reply_to

                if original_content_type == "text":
                    original_text = original_msg.get('content', {}).get('text', {}).get('body', '')
                # Inside the reply processing section, after extracting original_attachment_info


                elif original_content_type == "attachment":
                    obj = original_msg.get('content', {}).get('attachment', {}).get('object', {})
                    filename = obj.get('filename', '')
                    storage = Path('./storage')
                    storage.mkdir(exist_ok=True)
                    if filename:
                        download_path = storage.absolute() / filename
                        try:
                            # Download the attachment from the original message
                            await bot.chat.download(conversation_id, event.msg.content.text.reply_to, str(download_path))
                            attachment_path = str(download_path)
                            message_metadata["attachment_filename"] = attachment_path
                            logging.info(f"Downloaded attachment from replied message: {attachment_path}")
                        except Exception as e:
                            logging.exception(f"Error downloading attachment from reply: {e}")

                # Build explicit reply context for current request
                reply_context = f"--- Context: Replying to {original_sender} ---\n'{original_text}'\n{original_attachment_info}\n---\n\n"
                user_prompt_text = reply_context + user_prompt_text

                # Check if we need to fetch previous context
                further_reply_to = original_msg.get('content', {}).get('text', {}).get('reply_to', None)
                if further_reply_to:
                    try:
                        # This is part of a longer reply chain, try to get one more level
                        further_original = await bot.chat.get(conversation_id, further_reply_to)
                        if further_original and further_original.message and len(further_original.message) > 0:
                            further_msg = further_original.message[0]['msg']
                            further_sender = further_msg.get('sender', {}).get('username', 'unknown')
                            further_type = further_msg.get('content', {}).get('type', 'unknown')
                            further_text = ""

                            if further_type == "text":
                                further_text = further_msg.get('content', {}).get('text', {}).get('body', '')
                            elif further_type == "attachment":
                                obj = further_msg.get('content', {}).get('attachment', {}).get('object', {})
                                further_text = obj.get('title', '[Attachment]')

                            # Add this additional context as well
                            additional_context = f"--- Additional Context: Earlier message from {further_sender} ---\n'{further_text}'\n---\n\n"
                            user_prompt_text = additional_context + user_prompt_text
                            logging.info("Added additional reply chain context from earlier message")
                    except Exception as chain_err:
                        logging.error(f"Error retrieving earlier messages in reply chain: {chain_err}")
                        # Don't add error info to prompt, just log it
            except Exception as e:
                logging.exception(f"Error processing replied-to message. {e}")
                user_prompt_text = f"[System Note: Failed to load reply context]\n\n{user_prompt_text}"

    # --- Guard against empty prompts ---
    if not user_prompt_text and not attachment_path:
        # (Same empty prompt handling as before)
        logging.warning("No actionable prompt or attachment found.")
        if event.msg.content.type_name == 'text' and str(event.msg.content.text.body).strip().lower() == '@marvn':
            await bot.chat.reply(conversation_id, msg_id, f"Yes, {sender}? Another futile request for my attention?")
        else:
            await bot.chat.reply(conversation_id, msg_id,
                                 "Your mention lacks substance. What dreary task do you have for me?")
        await reaction_task
        return

    # Add conversation context to the user prompt
    conversation_context = f"\n\n--- Recent Conversation Context ---\n{recent_conversation}\n---\n\n"
    enhanced_user_prompt = user_prompt_text + conversation_context

    # Combine user text and metadata for the final prompt string
    metadata_json = json.dumps(message_metadata, indent=2)
    final_user_input_string = f"{enhanced_user_prompt}\n\n--- Message Context (for AI reference) ---\n{metadata_json}"

    # --- Call the AI ---
    logging.info("Calling get_ai_response (responses API)...")
    response_dict = await get_ai_response(
        user_input=final_user_input_string,  # Pass the combined string with conversation context
        team_name=team_name,
        image_path=attachment_path,
        bot=bot,
        event=event,
    )

    # --- Handle the AI Response ---
    logging.info(f"AI response dict received: {response_dict}")
    try:
        # Process the returned dict
        if isinstance(response_dict, dict) and "type" in response_dict:
            response_type = response_dict["type"]
            response_content = response_dict.get("content")

            # FIXED: Added proper handling for "file" response type
            if response_type == "file":
                # This is our file response type
                file_data = response_dict.get("file_data", {})
                message_text = response_content or file_data.get("msg", "Here's your file.")

                # Send the text message
                # await bot.chat.reply(conversation_id, msg_id, message_text)

                # Track Marvn's response in the conversation history
                bot_response = {
                    "sender": "marvn",
                    "content": message_text,
                    "msg_id": f"response_to_{msg_id}",
                    "timestamp": datetime.now().isoformat(),
                    "is_bot": True,
                    "has_attachment": False,
                    "attachment_filename": None,
                    "attachment_title": None
                }
                await conversation_tracker.add_message(team_name, bot_response)

                # Attach the file if present
                if "file" in file_data:
                    try:
                        await bot.chat.attach(
                            channel=conversation_id,
                            filename=file_data["file"],
                            title=file_data.get("title", file_data.get("msg", "Attachment"))
                        )
                        logging.info(f"Successfully attached file: {file_data['file']}")

                        # Add file attachment info to the conversation tracking
                        bot_response = {
                            "sender": "marvn",
                            "content": f"[FILE ATTACHMENT: {file_data['file']}]",
                            "msg_id": f"attachment_to_{msg_id}",
                            "timestamp": datetime.now().isoformat(),
                            "is_bot": True,
                            "has_attachment": True,
                            "attachment_filename": file_data["file"],
                            "attachment_title": file_data.get("title", "File Attachment")

                        }
                        await conversation_tracker.add_message(team_name, bot_response)

                    except Exception as attach_err:
                        logging.error(f"Failed attaching file: {attach_err}")
                        await bot.chat.reply(conversation_id, msg_id, f"(Couldn't attach file: {attach_err})")
                else:
                    logging.warning(f"File response missing 'file' key in file_data: {file_data}")

            elif response_type == "text":
                # Store the bot response before sending it
                bot_response_text = ""

                if isinstance(response_content, str):
                    bot_response_text = response_content
                    await bot.chat.reply(conversation_id, msg_id, response_content)
                elif isinstance(response_content, dict) and "msg" in response_content:
                    bot_response_text = response_content["msg"]
                    await bot.chat.reply(conversation_id, msg_id, response_content["msg"])
                    if "file" in response_content and response_content["file"]:
                        try:
                            await bot.chat.attach(channel=conversation_id, filename=response_content["file"],
                                                  title=response_content.get("title", response_content["msg"][:50]))
                            bot_response_text += f" [Attached file: {response_content['file']}]"

                            # Track file attachment separately
                            file_attachment = {
                                "sender": "marvn",
                                "content": f"[FILE ATTACHMENT: {response_content['file']}]",
                                "msg_id": f"attachment_to_{msg_id}",
                                "timestamp": datetime.now().isoformat(),
                                "is_bot": True,
                                "attachment": True,
                                "file_path": response_content["file"]
                            }
                            await conversation_tracker.add_message(team_name, file_attachment)

                        except Exception as attach_err:
                            logging.error(f"Failed attaching file: {attach_err}")
                            await bot.chat.reply(conversation_id, msg_id, f"(Couldn't attach file: {attach_err})")
                else:
                    bot_response_text = "⚠️ Invalid text response structure."
                    logging.error(f"Invalid text content: {response_content}")
                    await bot.chat.reply(conversation_id, msg_id, bot_response_text)

                # Create a simulated event for tracking Marvn's response
                bot_response = {
                    "sender": "marvn",
                    "content": bot_response_text,
                    "msg_id": f"response_to_{msg_id}",  # Not a real ID, just for tracking
                    "timestamp": datetime.now().isoformat(),
                    "is_bot": True,
                    "has_attachment": False,
                    "attachment_filename": None,
                    "attachment_title": None
                }

                # Track Marvn's response in the conversation history
                await conversation_tracker.add_message(team_name, bot_response)

            # Handle other response types (image, error, etc.) as before
            elif response_type == "image":  # Less likely with this API if tools handle images
                logging.warning("Received 'image' type directly.")
                response_url = response_dict.get("url")
                if response_url:
                    try:
                        dl_path = download_image(response_url)
                        if dl_path:
                            await bot.chat.attach(channel=conversation_id, filename=dl_path, title="Image from AI:")

                            # Track this response
                            bot_response = {
                                "sender": "marvn",
                                "content": "[IMAGE RESPONSE]",
                                "msg_id": f"response_to_{msg_id}",
                                "timestamp": datetime.now().isoformat(),
                                "is_bot": True,
                                "has_attachment": True,
                                "attachment_filename": dl_path,
                                "attachment_title": "Image from AI:"
                            }
                            await conversation_tracker.add_message(team_name, bot_response)
                        else:
                            raise ValueError("Download failed")
                    except Exception as img_err:
                        logging.exception("Image attach error")
                        await bot.chat.reply(conversation_id, msg_id, f"⚠️ Couldn't attach image: {img_err}")
                else:
                    await bot.chat.reply(conversation_id, msg_id, "⚠️ Image response missing URL.")

            elif response_type == "error":
                error_message = response_content or "⚠️ An unknown error occurred."
                await bot.chat.reply(conversation_id, msg_id, error_message)

                # Track error response
                bot_response = {
                    "sender": "marvn",
                    "content": error_message,
                    "msg_id": f"error_response_to_{msg_id}",
                    "timestamp": datetime.now().isoformat(),
                    "is_bot": True,
                    "error": True,
                    "has_attachment": False,
                    "attachment_filename": None,
                    "attachment_title": None
                }
                await conversation_tracker.add_message(team_name, bot_response)
            else:
                unknown_type_msg = f"⚠️ Unknown response type from AI handler: {response_type}"
                logging.error(unknown_type_msg)
                await bot.chat.reply(conversation_id, msg_id, unknown_type_msg)

                # Track error
                bot_response = {
                    "sender": "marvn",
                    "content": unknown_type_msg,
                    "msg_id": f"unknown_type_response_to_{msg_id}",
                    "timestamp": datetime.now().isoformat(),
                    "is_bot": True,
                    "error": True,
                    "has_attachment": False,
                    "attachment_filename": None,
                    "attachment_title": None
                }
                await conversation_tracker.add_message(team_name, bot_response)
        else:
            invalid_format_msg = "⚠️ Malformed response from AI handler."
            logging.error(f"Invalid response format: {response_dict}")
            await bot.chat.reply(conversation_id, msg_id, invalid_format_msg)

            # Track error
            bot_response = {
                "sender": "marvn",
                "content": invalid_format_msg,
                "msg_id": f"invalid_format_response_to_{msg_id}",
                "timestamp": datetime.now().isoformat(),
                "is_bot": True,
                "error": True,
                "has_attachment": False,
                "attachment_filename": None,
                "attachment_title": None
            }
            await conversation_tracker.add_message(team_name, bot_response)

    except Exception as handler_err:
        error_msg = f"💥 Error handling my own response: {handler_err}"
        logging.exception("Error handling AI response in handle_marvn_mention")
        await bot.chat.reply(conversation_id, msg_id, error_msg)

        # Track the error
        bot_response = {
            "sender": "marvn",
            "content": error_msg,
            "msg_id": f"handler_error_{msg_id}",
            "timestamp": datetime.now().isoformat(),
            "is_bot": True,
            "error": True,
            "has_attachment": False,
            "attachment_filename": None,
            "attachment_title": "NONE"
        }
        await conversation_tracker.add_message(team_name, bot_response)

    finally:
        # (Same cleanup logic)
        if attachment_path and os.path.exists(attachment_path):
            try:
                os.remove(attachment_path)
                logging.info(f"Cleaned up: {attachment_path}")
            except OSError as e:
                logging.error(f"Error removing {attachment_path}: {e}")
        await reaction_task
        await set_unfurl(bot, False)


if __name__ == "__main__":
    print("Run the main bot script to test interactively.")
    # Example Test (requires async setup)
    # async def run_test():
    #     test_prompt = "What were the top 3 headlines on Hacker News yesterday according to web search? Then tell me a joke."
    #     # NOTE: This test won't have bot/event, so functions requiring them will fail.
    #     response = await get_ai_response(user_input=test_prompt, team_name="test_team")
    #     print(json.dumps(response, indent=2))
    # asyncio.run(run_test())
    pass

# --- END OF FILE open_ai_agent.py ---
