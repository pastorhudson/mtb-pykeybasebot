
import re
from typing import Dict, Any
import asyncio
import inspect
from openai import OpenAI
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
function_registry = {
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

tools = [
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


# =============================================================================
# UTILITIES AND HELPER FUNCTIONS
# =============================================================================

def extract_messages_from_response(response):
    """Extract text messages from OpenAI API response"""
    messages = []
    if hasattr(response, "output"):
        for item in response.output:
            if hasattr(item, "type") and item.type == "message":
                for content in item.content:
                    if hasattr(content, "type") and content.type == "output_text":
                        messages.append(content.text)
    return messages


def extract_function_calls_from_response(response):
    """Extract function calls from OpenAI API response"""
    function_calls = []
    if hasattr(response, "output"):
        for item in response.output:
            if hasattr(item, "type") and item.type == "function_call":
                function_calls.append({
                    "name": item.name,
                    "arguments": json.loads(item.arguments)
                })
    return function_calls


async def inject_dependencies(function_to_call, arguments, bot=None, event=None):
    """Inject bot, event, and other dependencies into function arguments if needed"""
    # Get function signature
    signature = inspect.signature(function_to_call)
    param_names = list(signature.parameters.keys())

    # Add bot and event if needed
    if "bot" in param_names and bot:
        arguments["bot"] = bot
    if "event" in param_names and event:
        arguments["event"] = event
    if "team_members" in param_names and bot and event:
        from pykeybasebot.utils import get_channel_members
        arguments["team_members"] = await get_channel_members(event.msg.conv_id, bot)
    if "sender" in param_names and event and hasattr(event.msg, "sender"):
        arguments["sender"] = event.msg.sender.username

    return arguments


async def execute_function(function_name, arguments, bot=None, event=None):
    """Execute a function from the registry with proper dependency injection"""
    if function_name not in function_registry:
        raise ValueError(f"Function {function_name} not found in registry")

    function_to_call = function_registry[function_name]

    # Inject dependencies
    arguments = await inject_dependencies(function_to_call, arguments, bot, event)

    # Execute the function
    if asyncio.iscoroutinefunction(function_to_call):
        result = await function_to_call(**arguments)
    else:
        result = function_to_call(**arguments)

    return result


# =============================================================================
# COMPLEXITY DETECTION
# =============================================================================

# Complexity level definitions
COMPLEXITY_SIMPLE = "simple"  # Single tool call
COMPLEXITY_MEDIUM = "medium"  # 2-3 tool calls in sequence, predictable pattern
COMPLEXITY_COMPLEX = "complex"  # Multiple tools, complex dependencies, or reasoning

# Patterns that indicate multi-step processes
MULTI_STEP_PATTERNS = [
    # Reset since patterns
    (r"reset\s+(?:the\s+)?(?:time\s+)?since", COMPLEXITY_MEDIUM),

    # Award points patterns
    (r"(?:award|give)\s+points\s+to", COMPLEXITY_MEDIUM),

    # Generate and modify image
    (r"(?:generate|create).+?(?:image|picture).+?(?:then|and).+?(?:restyle|modify)", COMPLEXITY_COMPLEX),

    # General patterns indicating multi-step operations
    (r"\bthen\b.+?\bafter\b", COMPLEXITY_COMPLEX),
    (r"(?:first|1st).+?(?:then|next|after)", COMPLEXITY_COMPLEX),
    (r"(?:step\s+by\s+step|sequence|process)", COMPLEXITY_COMPLEX),

    # Specific task patterns
    (r"summary\s+of\s+(?:hacker\s+news|weather)", COMPLEXITY_MEDIUM),
    (r"compare.+?(?:with|to|against)", COMPLEXITY_COMPLEX),
    (r"analyze.+?(?:then|and).+?(?:visualize|display|show)", COMPLEXITY_COMPLEX)
]


async def detect_complexity(message: str) -> str:
    """
    Analyze a message to determine its complexity level

    Returns:
    COMPLEXITY_SIMPLE, COMPLEXITY_MEDIUM, or COMPLEXITY_COMPLEX
    """
    # Check for patterns indicating multi-step processes
    for pattern, complexity in MULTI_STEP_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE):
            return complexity

    # Count potential operations (rough heuristic)
    operation_count = 0
    operation_indicators = ["get", "find", "search", "retrieve", "update", "reset",
                            "create", "generate", "award", "calculate", "analyze"]

    for indicator in operation_indicators:
        if re.search(rf"\b{indicator}\b", message, re.IGNORECASE):
            operation_count += 1

    if operation_count >= 3:
        return COMPLEXITY_COMPLEX
    elif operation_count >= 2:
        return COMPLEXITY_MEDIUM

    # Default to simple if no patterns or multiple operations detected
    return COMPLEXITY_SIMPLE


# =============================================================================
# SIMPLE REQUEST HANDLER (Direct Function Calling)
# =============================================================================

async def handle_simple_request(bot, event, message_text, client):
    """
    Handle simple requests using direct OpenAI function calling
    """
    msg_id = event.msg.id
    conversation_id = event.msg.conv_id
    team_name = event.msg.channel.name

    # Prepare enhanced system message
    system_message = """
    You are Marvn, a chatbot with a depressing and sarcastic personality. 
    You are skilled and actually helpful in all things. You are ultimately endearing in a comical dark humor way.
    When processing commands, extract the relevant information from the user's message
    and call the appropriate function with the correct parameters.
    """

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": message_text}
        ],
        tools=tools
    )

    # Extract function calls
    function_calls = []
    tool_calls = response.choices[0].message.tool_calls

    if tool_calls:
        for tool_call in tool_calls:
            if tool_call.type == "function":
                function_calls.append({
                    "name": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments)
                })

    # If there are function calls, execute them
    if function_calls:
        for call in function_calls:
            function_name = call["name"]
            arguments = call["arguments"]

            try:
                result = await execute_function(
                    function_name, arguments, function_registry, bot, event
                )

                # Handle the result
                if isinstance(result, str):
                    await bot.chat.reply(conversation_id, msg_id, result)
                elif isinstance(result, dict):
                    if "msg" in result:
                        await bot.chat.reply(conversation_id, msg_id, result["msg"])
                    if "file" in result:
                        await bot.chat.attach(
                            channel=conversation_id,
                            filename=result["file"],
                            title=result.get("msg", "File attachment")
                        )
                else:
                    await bot.chat.reply(conversation_id, msg_id, str(result))
            except Exception as e:
                logging.error(f"Error executing {function_name}: {str(e)}")
                await bot.chat.reply(conversation_id, msg_id, f"⚠️ Error: {str(e)}")
    else:
        # No function calls, just send the assistant's message
        message = response.choices[0].message.content
        await bot.chat.reply(conversation_id, msg_id, message)

    return True


# =============================================================================
# FUNCTION-BASED CHAIN OF TOOLS (Medium Complexity)
# =============================================================================

class ToolChain:
    def __init__(self):
        self.function_registry = function_registry
        self.context = {}  # Shared context between tool calls

    async def execute_chain(self, first_function: str, initial_args: Dict[str, Any],
                            bot=None, event=None, max_depth=5):
        """
        Execute a chain of functions where each function can return the next function to call.

        Parameters:
        first_function: Name of the first function to call
        initial_args: Arguments for the first function
        bot: Bot object for API calls
        event: Event information
        max_depth: Maximum chain depth to prevent infinite loops

        Returns:
        List of results from all function calls
        """
        if max_depth <= 0:
            return [{"error": "Maximum chain depth reached"}]

        # Initialize result list
        results = []

        # Check if function exists
        if first_function not in self.function_registry:
            return [{"error": f"Function {first_function} not found"}]

        # Get the function
        function_to_call = self.function_registry[first_function]

        # Prepare arguments
        args = initial_args.copy()

        # Add bot and event if needed
        args = await inject_dependencies(function_to_call, args, bot, event)

        # Add context if the function accepts it
        signature = inspect.signature(function_to_call)
        if "context" in signature.parameters:
            args["context"] = self.context

        # Add any missing required parameters from context if available
        for param in signature.parameters:
            if param not in args and param in self.context:
                args[param] = self.context[param]

        # Execute the function
        try:
            if asyncio.iscoroutinefunction(function_to_call):
                result = await function_to_call(**args)
            else:
                result = function_to_call(**args)

            # Add to results
            results.append({
                "function": first_function,
                "result": result
            })

            # Update context with result
            self.context[first_function + "_result"] = result

            # Check if result contains next_function instruction
            if isinstance(result, dict) and "next_function" in result:
                next_function = result["next_function"]
                next_args = result.get("next_args", {})

                # Recursively call the next function
                next_results = await self.execute_chain(
                    next_function, next_args, bot, event, max_depth - 1
                )

                # Add next results to our results list
                results.extend(next_results)
        except Exception as e:
            logging.error(f"Error executing {first_function}: {str(e)}")
            results.append({
                "function": first_function,
                "error": str(e)
            })

        return results


# Common pattern handlers using ToolChain

async def reset_since_process(bot, event, team_name, target_event):
    """Entry point for reset_since process"""
    from botcommands.since import get_since, reset_since

    msg_id = event.msg.id
    conversation_id = event.msg.conv_id

    # Execute get_since
    try:
        since_result = await get_since(team_name)

        # Show the result to user
        await bot.chat.reply(conversation_id, msg_id, f"Current 'since' events:\n{since_result}")

        # Parse the result to find target event
        since_id = None
        if isinstance(since_result, str):
            lines = since_result.split('\n')
            for line in lines:
                if target_event.lower() in line.lower():
                    id_match = re.search(r'#(\d+)', line)
                    if id_match:
                        since_id = f"#{id_match.group(1)}"
                        break

        # Execute reset_since if target found
        if since_id:
            reset_result = await reset_since(team_name, since_id)
            await bot.chat.reply(conversation_id, msg_id, f"✅ Successfully reset '{target_event}': {reset_result}")
        else:
            await bot.chat.reply(conversation_id, msg_id, f"❌ Could not find an event matching '{target_event}'")

    except Exception as e:
        logging.error(f"Error in reset_since_process: {str(e)}")
        await bot.chat.reply(conversation_id, msg_id, f"⚠️ Error: {str(e)}")

    return True


async def award_points_process(bot, event, recipient, points, description=""):
    """Entry point for award points process"""
    from botcommands.scorekeeper import award
    from pykeybasebot.utils import get_channel_members

    msg_id = event.msg.id
    conversation_id = event.msg.conv_id

    try:
        # Get team members
        team_members = await get_channel_members(event.msg.conv_id, bot)

        # Check if recipient is in team members
        if recipient not in team_members:
            similar_members = [member for member in team_members if recipient.lower() in member.lower()]
            if similar_members:
                await bot.chat.reply(conversation_id, msg_id,
                                     f"⚠️ Could not find '{recipient}'. Did you mean one of these: {', '.join(similar_members)}?")
            else:
                await bot.chat.reply(conversation_id, msg_id,
                                     f"⚠️ Could not find '{recipient}' in this chat's members.")
            return False

        # Award points
        award_result = await award(
            bot=bot,
            event=event,
            sender=event.msg.sender.username,
            recipient=recipient,
            team_members=team_members,
            points=points,
            description=description or "No reason specified"
        )

        await bot.chat.reply(conversation_id, msg_id, f"✅ {award_result}")

    except Exception as e:
        logging.error(f"Error in award_points_process: {str(e)}")
        await bot.chat.reply(conversation_id, msg_id, f"⚠️ Error: {str(e)}")

    return True


async def detect_and_process_patterns(bot, event, message_text):
    """Detect common request patterns and route to appropriate process function"""

    # Reset since pattern
    reset_pattern = r"reset\s+(?:the\s+)?(?:time\s+)?since\s+(?:last\s+)?(.+?)(?:\s+for\s+(.+?))?$"
    match = re.search(reset_pattern, message_text, re.IGNORECASE)

    if match:
        event_type = match.group(1).strip()
        team = match.group(2).strip() if match.group(2) else event.msg.channel.name

        # Execute the process
        await reset_since_process(bot, event, team, event_type)
        return True

    # Award points pattern
    award_pattern = r"(?:give|award)\s+(\d+)\s+points\s+to\s+(\w+)(?:\s+for\s+(.+))?$"
    match = re.search(award_pattern, message_text, re.IGNORECASE)

    if match:
        points = int(match.group(1).strip())
        recipient = match.group(2).strip()
        description = match.group(3).strip() if match.group(3) else "No reason specified"

        # Execute the process
        await award_points_process(bot, event, recipient, points, description)
        return True

    # No pattern matched
    return False


# =============================================================================
# DYNAMIC LLM TOOL SELECTION (Medium-Complex)
# =============================================================================

class DynamicToolExecutor:
    def __init__(self, function_registry, client, model="gpt-4o"):
        self.function_registry = function_registry
        self.client = client
        self.model = model
        self.conversation_history = []

    async def execute_with_context(self, user_input, bot=None, event=None, team_name=None):
        """
        Let the LLM decide which tools to call and handle the entire conversation flow.

        This approach maintains context between steps and lets the LLM make decisions
        about what to do next based on previous results.
        """
        # Add user input to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})

        # Enhanced system message to guide the model
        system_message = """
        You are Marvn, a chatbot with a depressing and sarcastic personality. 
        You are skilled and actually helpful in all things. You are ultimately endearing in a comical dark humor way.
        
        You can call tools to complete tasks. After each tool call,
        you'll receive the result and can decide what to do next: either respond to the user
        or call another tool. Always explain what you're doing to complete the user's request.
        """

        # Setup the full messages array with history
        messages = [
            {"role": "system", "content": system_message},
            *self.conversation_history
        ]

        # Initialize response to user
        user_response = ""
        msg_id = event.msg.id if event else None
        conversation_id = event.msg.conv_id if event else None

        # Loop until we have a final response (no more tool calls needed)
        max_steps = 5  # Limit number of iterations to prevent infinite loops
        for step in range(max_steps):
            # Call the model
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools  # Assuming tools is defined outside this class
            )

            # Get assistant message
            assistant_message = response.choices[0].message

            # Check for tool calls
            if assistant_message.tool_calls:
                # Process each tool call
                for tool_call in assistant_message.tool_calls:
                    if tool_call.type == "function":
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)

                        # Add assistant message to history
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": assistant_message.content,
                            "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {
                                        "name": function_name,
                                        "arguments": tool_call.function.arguments
                                    }
                                }
                            ]
                        })

                        # Execute function if it exists
                        if function_name in self.function_registry:
                            try:
                                result = await execute_function(
                                    function_name, arguments, self.function_registry, bot, event
                                )

                                # Optional: Show intermediate result to user
                                if bot and conversation_id and msg_id and step > 0:
                                    await bot.chat.reply(
                                        conversation_id,
                                        msg_id,
                                        f"Step {step + 1}: {result if isinstance(result, str) else 'Executed ' + function_name}"
                                    )

                                # Add tool response to history
                                tool_result = json.dumps(result) if not isinstance(result, str) else result
                                self.conversation_history.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": function_name,
                                    "content": tool_result
                                })
                            except Exception as e:
                                logging.error(f"Error executing {function_name}: {str(e)}")
                                self.conversation_history.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": function_name,
                                    "content": f"Error: {str(e)}"
                                })
                        else:
                            self.conversation_history.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": function_name,
                                "content": f"Error: Function {function_name} not found."
                            })
            else:
                # No tool calls, we have our final response
                user_response = assistant_message.content

                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": user_response
                })

                break

        # Send final response to user
        if user_response and bot and conversation_id and msg_id:
            await bot.chat.reply(conversation_id, msg_id, user_response)

        return user_response


async def handle_medium_complexity(bot, event, message_text, client, function_registry):
    """Handle medium-complexity requests"""
    msg_id = event.msg.id
    conversation_id = event.msg.conv_id

    # First try pattern-based processing
    processed = await detect_and_process_patterns(bot, event, message_text)

    # If no pattern matched, use the dynamic tool executor
    if not processed:
        executor = DynamicToolExecutor(function_registry, client)
        await executor.execute_with_context(
            user_input=message_text,
            bot=bot,
            event=event,
            team_name=event.msg.channel.name
        )

    return True


# =============================================================================
# AGENT-BASED APPROACH (Complex)
# =============================================================================

class ToolAgent:
    def __init__(self, function_registry, client, model="gpt-4o"):
        self.function_registry = function_registry
        self.client = client
        self.model = model
        self.conversation_history = []
        self.working_memory = {}  # Internal memory for storing task-specific info

    async def process_task(self, user_input, bot=None, event=None, team_name=None, max_steps=5):
        """
        Process a user task using an agent-based approach with planning and execution
        """
        msg_id = event.msg.id if event else None
        conversation_id = event.msg.conv_id if event else None

        # Initialize agent memory for this conversation
        self.working_memory = {
            "user_input": user_input,
            "team_name": team_name,
            "conversation_id": conversation_id,
            "user_id": event.msg.sender.username if event and hasattr(event.msg, "sender") else "user",
            "tool_results": {},
            "plan": None,
            "current_step": 0,
            "status": "planning"  # planning, executing, completed, error
        }

        # 1. Planning phase - Ask the LLM to develop a plan
        plan = await self._create_plan(user_input)
        self.working_memory["plan"] = plan

        # Optional: Show plan to user
        if bot and conversation_id and msg_id:
            plan_text = "📋 Plan:\n"
            for i, step in enumerate(plan["steps"], 1):
                plan_text += f"{i}. {step['description']}"
                if "tool" in step:
                    plan_text += f" (using {step['tool']})"
                plan_text += "\n"

            await bot.chat.reply(conversation_id, msg_id, plan_text)

        # 2. Execution phase - Execute each step of the plan
        self.working_memory["status"] = "executing"

        for i, step in enumerate(plan["steps"]):
            self.working_memory["current_step"] = i

            # Execute the step
            if "tool" in step and step["tool"] in self.function_registry:
                # Prepare arguments
                tool_args = await self._prepare_tool_arguments(step)

                # Execute tool
                try:
                    result = await execute_function(
                        step["tool"], tool_args, self.function_registry, bot, event
                    )

                    # Store result in memory
                    self.working_memory["tool_results"][step["tool"]] = result

                    # Optional: Show intermediate result to user
                    if bot and conversation_id and msg_id and step.get("show_result", False):
                        result_text = f"Step {i + 1}: {step['description']} - Completed"
                        await bot.chat.reply(conversation_id, msg_id, result_text)

                except Exception as e:
                    logging.error(f"Error executing step {i + 1}: {str(e)}")
                    self.working_memory["status"] = "error"
                    self.working_memory["error"] = str(e)

                    if bot and conversation_id and msg_id:
                        await bot.chat.reply(conversation_id, msg_id,
                                             f"❌ Error in step {i + 1}: {str(e)}")
                    break
            else:
                # Just a note or a step without a tool
                if bot and conversation_id and msg_id and step.get("show_note", True):
                    await bot.chat.reply(conversation_id, msg_id, f"📝 {step['description']}")

        # 3. Generating final response
        if self.working_memory["status"] != "error":
            self.working_memory["status"] = "completed"

        final_response = await self._generate_final_response()

        # Send final response to user
        if bot and conversation_id and msg_id:
            await bot.chat.reply(conversation_id, msg_id, final_response)

        # Return final response
        return final_response

    async def _create_plan(self, user_input):
        """Ask the LLM to create a plan to accomplish the task"""
        system_message = """
        You are an AI assistant that helps create plans to accomplish user tasks using available tools.
        
        Create a detailed, step-by-step plan that breaks down complex tasks into smaller subtasks.
        For each step that requires a tool, specify:
        1. The tool name
        2. The required parameters
        3. How to use the output from previous steps as input to later steps
        
        Return your plan as a JSON object.
        """

        # Tool descriptions to help with planning
        tool_descriptions = []
        for tool_name, func in self.function_registry.items():
            if func.__doc__:
                tool_descriptions.append(f"{tool_name}: {func.__doc__}")
            else:
                tool_descriptions.append(tool_name)

        planning_prompt = f"""
        User request: {user_input}
        
        Available tools:
        {chr(10).join(tool_descriptions)}
        
        Create a step-by-step plan to accomplish this task. For each step, include:
        1. Description of what this step accomplishes
        2. If a tool is needed, specify the tool name and what parameters it needs
        3. Indicate if any parameters should come from the results of previous steps
        
        Return your plan as a JSON object with this structure:
        {{
            "plan_summary": "Brief summary of the overall plan",
            "steps": [
                {{
                    "description": "Step description",
                    "tool": "tool_name", (if applicable)
                    "parameters": {{"param1": "value1", "param2": "AUTO:previous_step_result"}} (if applicable),
                    "show_result": true/false (whether to show this result to the user)
                }},
                ...
            ]
        }}
        """

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": planning_prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2  # Lower temperature for more consistent planning
        )

        try:
            plan_text = response.choices[0].message.content
            plan = json.loads(plan_text)
            return plan
        except Exception as e:
            logging.error(f"Error parsing plan: {str(e)}")
            # Fallback simple plan
            return {
                "plan_summary": "Simple fallback plan due to parsing error",
                "steps": [
                    {
                        "description": f"Process the request: {user_input}",
                        "show_note": True
                    }
                ]
            }

    async def _prepare_tool_arguments(self, step):
        """Prepare arguments for tool execution, resolving references to previous results"""
        if "parameters" not in step:
            return {}

        prepared_args = {}
        for param_name, param_value in step["parameters"].items():
            if isinstance(param_value, str) and param_value.startswith("AUTO:"):
                # Reference to a previous result
                result_key = param_value[5:]  # Remove AUTO: prefix
                if result_key in self.working_memory["tool_results"]:
                    # Direct reference to a tool result
                    prepared_args[param_name] = self.working_memory["tool_results"][result_key]
                else:
                    # Try to parse more complex references (e.g., AUTO:get_since.since_id)
                    parts = result_key.split(".")
                    if len(parts) == 2 and parts[0] in self.working_memory["tool_results"]:
                        tool_result = self.working_memory["tool_results"][parts[0]]
                        if isinstance(tool_result, dict) and parts[1] in tool_result:
                            prepared_args[param_name] = tool_result[parts[1]]
                        else:
                            # Try to extract from string result
                            try:
                                # For instance, extracting a since_id from get_since result
                                if parts[1] == "since_id" and isinstance(tool_result, str):
                                    import re
                                    # Look for patterns like "#42" in the text
                                    match = re.search(r'#(\d+)', tool_result)
                                    if match:
                                        prepared_args[param_name] = f"#{match.group(1)}"
                            except:
                                # Fallback - just use the raw value
                                prepared_args[param_name] = param_value
                    else:
                        # Fallback - just use the raw value
                        prepared_args[param_name] = param_value
            else:
                # Direct value
                prepared_args[param_name] = param_value

        # Add standard context if needed
        if "team_name" not in prepared_args and "team_name" in self.working_memory:
            prepared_args["team_name"] = self.working_memory["team_name"]

        return prepared_args

    async def _generate_final_response(self):
        """Generate a final response to the user based on the execution results"""
        system_message = """
        You are Marvn, a chatbot with a depressing and sarcastic personality. 
        You are skilled and actually helpful in all things. You are ultimately endearing in a comical dark humor way.
        
        Create a concise, friendly but sarcastic response that explains what was done and the outcome.
        """

        # Create a summary of what was done
        memory_for_response = {
            "user_input": self.working_memory["user_input"],
            "plan_summary": self.working_memory.get("plan", {}).get("plan_summary", ""),
            "tool_results": self.working_memory["tool_results"],
            "status": self.working_memory["status"],
            "error": self.working_memory.get("error", None)
        }

        response_prompt = f"""
        Based on the executed plan and results, generate a concise, friendly response to the user.
        
        User request: {self.working_memory["user_input"]}
        
        Execution details:
        {json.dumps(memory_for_response, indent=2)}
        
        Respond conversationally with Marvn's depressing and sarcastic personality, while still being helpful.
        Focus on what was accomplished rather than the technical details of how it was done.
        """

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": response_prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        return response.choices[0].message.content


async def handle_complex_requests(bot, event, message_text, client):
    """Handle complex requests using the agent-based approach"""
    msg_id = event.msg.id
    conversation_id = event.msg.conv_id

    # Create agent
    agent = ToolAgent(function_registry, client)

    # Process task with agent
    await agent.process_task(
        user_input=message_text,
        bot=bot,
        event=event,
        team_name=event.msg.channel.name
    )

    return True


# =============================================================================
# INTELLIGENT ROUTING
# =============================================================================

async def route_message_to_handler(bot, event, message_text, client):
    """
    Route a message to the appropriate handler based on its complexity
    """
    try:
        # Detect complexity
        complexity = await detect_complexity(message_text)

        conversation_id = event.msg.conv_id
        msg_id = event.msg.id

        # Optional: Log complexity level
        logging.info(f"Detected complexity: {complexity} for message: {message_text[:50]}...")

        # Route based on complexity
        if complexity == COMPLEXITY_SIMPLE:
            # Use direct OpenAI function calling for simple requests
            return await handle_simple_request(
                bot=bot,
                event=event,
                message_text=message_text,
                client=client,
                function_registry=function_registry,
                tools=tools
            )

        elif complexity == COMPLEXITY_MEDIUM:
            # Use function-based chain approach for medium complexity
            return await handle_medium_complexity(
                bot=bot,
                event=event,
                message_text=message_text,
                client=client,
                function_registry=function_registry,
                tools=tools
            )

        elif complexity == COMPLEXITY_COMPLEX:
            # Use the agent-based approach for complex requests
            return await handle_complex_requests(
                bot=bot,
                event=event,
                message_text=message_text,
                client=client,
                function_registry=function_registry,
                tools=tools
            )

        else:
            # This shouldn't happen, but just in case
            logging.error(f"Unknown complexity level: {complexity}")
            await bot.chat.reply(conversation_id, msg_id,
                                 "⚠️ I couldn't determine how to process your request.")
            return False

    except Exception as e:
        logging.error(f"Error routing message: {str(e)}")
        await bot.chat.reply(event.msg.conv_id, event.msg.id,
                             f"⚠️ An error occurred while processing your request: {str(e)}")
        return False


# =============================================================================
# HANDLE MARVN MENTION - MAIN ENTRY POINT
# =============================================================================

async def handle_marvn_mention_enhanced(bot, event):
    """Enhanced version of handle_marvn_mention that uses intelligent routing"""
    msg_id = event.msg.id
    conversation_id = event.msg.conv_id

    # React to the mention
    await bot.chat.react(conversation_id, msg_id, ":marvin:")

    # Handle attachments
    try:
        if event.msg.content.type_name == 'attachment':
            storage = Path('./storage')
            prompt = event.msg.content.attachment.object.title

            # Check if the title starts with or contains "@marvn"
            if "@marvn" in prompt:
                # Remove the @marvn from the prompt
                prompt = prompt.replace("@marvn", "").strip()

                # Add metadata to the prompt
                metadata = {
                    "sender": event.msg.sender.username if hasattr(event.msg, "sender") else "user",
                    "mentions": event.msg.at_mention_usernames if hasattr(event.msg, "at_mention_usernames") else [],
                    "conversation_id": conversation_id,
                    "team_name": event.msg.channel.name if hasattr(event.msg.channel, "name") else "default"
                }
                prompt += f"\n\nMESSAGE_METADATA: {json.dumps(metadata)}"

                filename = f"{storage.absolute()}/{event.msg.content.attachment.object.filename}"

                # Download the file
                logging.info(f"Downloading attachment: {filename}")
                await bot.chat.download(conversation_id, msg_id, filename)

                # Add the file path directly to the metadata
                metadata["attachment_path"] = filename

                # Handle image or file based on file type
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    # This is an image file, use vision capabilities
                    # You'll need to implement image handling here
                    await bot.chat.reply(conversation_id, msg_id,
                                         "I've received your image. Processing...")
                    # Call your image processing function here
                else:
                    # This is a regular file, process normally
                    await route_message_to_handler(
                        bot=bot,
                        event=event,
                        message_text=prompt,
                        client=client,
                        function_registry=function_registry,
                        tools=tools
                    )

                await bot.chat.reply(conversation_id, msg_id,
                                     "I've processed your attachment.")
                return
    except Exception as e:
        logging.error(f"Error handling attachment: {str(e)}")

    # Extract message text
    try:
        message_text = str(event.msg.content.text.body)[7:]  # Original message without the @marvn prefix
    except:
        # If we can't get text content, it might not be a text message
        await bot.chat.reply(conversation_id, msg_id, "⚠️ I couldn't process that message type.")
        return

    # Handle replies (if user is replying to a previous message)
    if hasattr(event.msg.content, "text") and hasattr(event.msg.content.text,
                                                      "reply_to") and event.msg.content.text.reply_to:
        logging.info("Processing a reply")
        original_msg = await bot.chat.get(conversation_id, event.msg.content.text.reply_to)

        if original_msg.message[0]['msg']['content']['type'] == "text":
            prompt = f"{original_msg.message[0]['msg']['sender']['username']}: {original_msg.message[0]['msg']['content']['text']['body']}\n\n" \
                     f"{event.msg.sender.username}: {message_text}"

            # Add metadata
            metadata = {
                "sender": event.msg.sender.username,
                "conversation_id": conversation_id,
                "team_name": event.msg.channel.name if hasattr(event.msg.channel, "name") else "default",
                "is_reply": True,
                "reply_to_sender": original_msg.message[0]['msg']['sender']['username']
            }
            prompt += f"\n\nMESSAGE_METADATA: {json.dumps(metadata)}"

            # Route the reply
            await route_message_to_handler(
                bot=bot,
                event=event,
                message_text=prompt,
                client=client,
                function_registry=function_registry,
                tools=tools
            )

        elif original_msg.message[0]['msg']['content']['type'] == "attachment":
            # Handle reply to attachment
            storage = Path('./storage')
            prompt = f"Original Message from {original_msg.message[0]['msg']['sender']['username']}: {original_msg.message[0]['msg']['content']['attachment']['object']['title']}\n\n" \
                     f"Question from {event.msg.sender.username}: {message_text}"

            # Add metadata
            metadata = {
                "sender": event.msg.sender.username,
                "conversation_id": conversation_id,
                "team_name": event.msg.channel.name if hasattr(event.msg.channel, "name") else "default",
                "is_reply": True,
                "reply_to_attachment": True,
                "reply_to_sender": original_msg.message[0]['msg']['sender']['username']
            }
            prompt += f"\n\nMESSAGE_METADATA: {json.dumps(metadata)}"

            org_filename = original_msg.message[0]['msg']['content']['attachment']['object']['filename']
            filename = f"{storage.absolute()}/{org_filename}"

            logging.info("Downloading attachment...")
            org_conversation_id = original_msg.message[0]['msg']['conversation_id']
            await bot.chat.download(org_conversation_id, original_msg.message[0]['msg']['id'], filename)

            # Handle image or file based on file type
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # This is an image file, use vision capabilities
                await bot.chat.reply(conversation_id, msg_id,
                                     "I'm processing your reply to an image...")
                # Call your image processing function here
            else:
                # This is a regular file, process normally
                await route_message_to_handler(
                    bot=bot,
                    event=event,
                    message_text=prompt,
                    client=client,
                    function_registry=function_registry,
                    tools=tools
                )
    else:
        # Regular message (not a reply)
        metadata = {
            "sender": event.msg.sender.username,
            "conversation_id": conversation_id,
            "team_name": event.msg.channel.name if hasattr(event.msg.channel, "name") else "default"
        }
        enhanced_message = f"{message_text}\n\nMESSAGE_METADATA: {json.dumps(metadata)}"

        # Route the message
        await route_message_to_handler(
            bot=bot,
            event=event,
            message_text=enhanced_message,
            client=client,
            function_registry=function_registry,
            tools=tools
        )

    # Reset unfurl setting if needed
    from botcommands.utils import set_unfurl
    await set_unfurl(bot, False)


# =============================================================================
# MAIN USAGE
# =============================================================================

# Example of how to use this system
# async def main():
#     """Example usage of the intelligent routing system"""
#     # This would typically be called from your main bot code
#     # Replace with actual bot instance, event, client, etc.
#
#     from openai import OpenAI
#
#     # Initialize OpenAI client
#     client = OpenAI()
#
#     # Use your existing function registry
#     function_registry = FUNCTION_REGISTRY
#
#     # Use your existing tools definition
#     tools = new_tools
#
#     # When a message is received that mentions @marvn
#     # bot and event would be provided by your bot framework
#     await handle_marvn_mention_enhanced(bot, event, client, function_registry, tools)


if __name__ == "__main__":
    # Example standalone usage for testing
    import sys
    # import asyncio

    # This wouldn't actually work without proper bot and event objects
    # Just here as a demonstration
    # asyncio.run(main())
    pass