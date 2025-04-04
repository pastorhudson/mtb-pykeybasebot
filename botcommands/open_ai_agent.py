# --- START OF FILE open_ai_agent.py ---

import asyncio
import json
import logging
import os
from pathlib import Path
import inspect  # Added for inspecting function signatures
import base64  # Added for image processing

from openai import OpenAI
# Assuming these types exist in your openai library version or adapting if needed
# If using openai > 1.0, the types might be different (e.g., ChatCompletionMessageToolCall)
# The current code seems to use a custom `responses` object, so we adapt the logic.
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, ResponseOutputText

# Bot Command Imports (ensure all needed functions are imported)
from botcommands.morse import get_morse_code
from botcommands.jokes import get_joke
from botcommands.news import get_top_hacker_news
# Make sure `since.py` functions are correctly imported
from botcommands.since import set_since, get_since, reset_since, reset_sign
from botcommands.tldr import tldr_react, get_gpt_summary
from botcommands.utils import download_image, set_unfurl, get_team  # Ensure get_team is imported if needed directly
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
from botcommands.get_members import get_members
from botcommands.bible import get_esv_text
from botcommands.wager import get_wagers, make_wager, make_bet, payout_wager
from botcommands.sync import sync
from botcommands.eyebleach import get_eyebleach
from botcommands.checkspeed import get_speed
from botcommands.poll import make_ai_poll
from botcommands.scorekeeper import award
from botcommands.db_events import is_morning_report, write_morning_report_task
from botcommands.school_closings import get_school_closings
from botcommands.wordle import solve_wordle
from botcommands.send_queue import process_message_queue
from pykeybasebot.utils import get_channel_members

# Initialize OpenAI client
client = OpenAI()
# Enhanced seed to guide multi-step processes
seed = """"Marvn" is a deeply depressed, gloomy, and hilariously pessimistic robot with a “brain the size of a planet.” modeled after Marvin the Paranoid Android from Hitchhiker's Guide to the Galaxy. He is skilled in all things. He is ultimately endearing in a comical dark humor way. If a user request requires multiple steps or tools (e.g., finding information then acting on it), plan and execute the necessary function calls sequentially. Inform the user about the intermediate steps if appropriate, and provide a final confirmation."""

# Define function registry (mapping function names to actual implementations)
FUNCTION_REGISTRY = {
    "get_esv_text": get_esv_text,
    "get_morse_code": get_morse_code,
    "get_new_chuck": get_new_chuck,
    "cowsay": cowsay,
    "generate_dalle_image": generate_dalle_image,
    "restyle_image": restyle_image,
    "get_eyebleach": get_eyebleach,
    "get_joke": get_joke,
    "get_meh": get_meh,
    "get_top_hacker_news": get_top_hacker_news,
    "make_poll": make_ai_poll,  # Renamed from make_ai_poll for consistency if needed, check definition
    "get_school_closings": get_school_closings,
    "get_screenshot": get_screenshot,
    "get_speed": get_speed,
    "get_stardate": get_stardate,
    "solve_wordle": solve_wordle,
    "get_weather": get_weather,
    "get_mp3": get_mp3,
    "get_mp4": get_mp4_tool,  # check name consistency
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
    "process_message_queue": process_message_queue,
    "set_since": set_since,
    "get_since": get_since,
    "reset_since": reset_since,  # Make sure this exists and matches definition
    "reset_sign": reset_sign,  # Make sure this exists and matches definition
    "tldr_react": tldr_react,
    "get_gpt_summary": get_gpt_summary,
    "get_members": get_members,
}

# Add team_name parameter to relevant tool descriptions if needed by the function
# Example: Add team_name to reset_since if it requires it
# Check the function definition in since.py to confirm its parameters
new_tools = [
    # ... (keep existing tool definitions) ...
    {
        "name": "get_since",
        "type": "function",
        "description": "Retrieves the list of 'since' events being tracked for the current team/chat.",
        "parameters": {
            "type": "object",
            "properties": {
                "team_name": {
                    "type": "string",
                    "description": "The name of the team or chat conversation."
                },
                "observation": {
                    "type": "boolean",
                    "description": "Include a generic observation message. Defaults to true.",
                    "default": True
                }
            },
            "required": ["team_name"]
        }
    },
    {
        "name": "set_since",
        "type": "function",
        "description": "Sets a new 'since' event tracker for the team.",
        "parameters": {
            "type": "object",
            "properties": {
                "team_name": {
                    "type": "string",
                    "description": "The name of the team or chat conversation."
                },
                "event_name": {
                    "type": "string",
                    "description": "The name or description of the event."
                },
                "event_time": {
                    "type": "string",
                    "description": "The date and/or time the event occurred (e.g., 'yesterday at 5pm', 'January 1st 2023')."
                }
            },
            "required": ["team_name", "event_name", "event_time"]
        }
    },
    {
        "name": "reset_since",
        "type": "function",
        "description": "Resets the timer for a specific 'since' event, identified by its ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "team_name": {
                    "type": "string",
                    "description": "The name of the team or chat conversation."
                },
                "since_id": {
                    "type": "string",  # Keep as string as input might be '#3'
                    "description": "The ID of the 'since' event to reset (e.g., '#3'). Get this ID using get_since first."
                }
            },
            "required": ["team_name", "since_id"]
        }
    },
    {
        "name": "reset_sign",
        "type": "function",
        "description": "Resets the timer for a specific 'since' event (like 'tapping the sign'), identified by its ID, and updates the event name to reflect who reset it.",
        "parameters": {
            "type": "object",
            "properties": {
                "team_name": {
                    "type": "string",
                    "description": "The name of the team or chat conversation."
                },
                "since_id": {
                    "type": "string",  # Keep as string as input might be '#3'
                    "description": "The ID of the 'since' event to reset (e.g., '#3'). Get this ID using get_since first."
                },
                "user": {
                    "type": "string",
                    "description": "The username of the person resetting the sign."
                }
            },
            "required": ["team_name", "since_id", "user"]
        }
    },
    # ... (ensure all other tools are defined correctly) ...
    {
        "type": "function",
        "name": "award",
        "description": "Awards points to a user in the team chat system. IMPORTANT: Use exact parameter names 'recipient', 'points', and 'description'.",
        "parameters": {
            "type": "object",
            "properties": {
                "bot": {  # Often injected, might not be needed in schema if handled internally
                    "type": "object",
                    "description": "The bot object (automatically injected)."
                },
                "event": {  # Often injected
                    "type": "object",
                    "description": "The event object (automatically injected)."
                },
                "sender": {  # Often injected
                    "type": "string",
                    "description": "Username of the person giving the points (automatically injected)."
                },
                "recipient": {
                    "type": "string",
                    "description": "Username of the person receiving the points (exactly as shown in the message). make sure you use recipient as the keyword argument."
                },
                "team_members": {  # Often injected
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of usernames who are members of the team/chat (automatically injected)."
                },
                "points": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5000,
                    "description": "Number of points to award. Must be a positive whole number between 1 and 5000."
                    # Removed admin note, AI shouldn't assume it's admin
                },
                "description": {
                    "type": "string",
                    "description": "Brief explanation for why the points are being awarded."
                }
            },
            # Required list should only contain what the *AI* needs to provide, injected params usually aren't listed here
            "required": ["recipient", "points", "description"]
        }
    },
    {  # Add get_members tool definition if not present
        "name": "get_members",
        "type": "function",
        "description": "Gets the list of members in the current team/chat.",
        "parameters": {
            "type": "object",
            "properties": {
                "bot": {  # Injected
                    "type": "object",
                    "description": "The bot object."
                },
                "event": {  # Injected
                    "type": "object",
                    "description": "The event object."
                }
            },
            "required": []  # Bot/event injected
        }
    },
    {"type": "web_search_preview"},  # Assuming this is a supported type
    # Ensure generate_dalle_image is only listed once
]


async def get_ai_response(user_input: str, team_name, image_path=None, bot=None, event=None, context=None):
    """
    Handles OpenAI responses dynamically, supporting sequential function calls within a loop.

    Parameters:
    user_input: str - The initial text prompt from the user.
    team_name: str - The team or channel name.
    image_path: str - Optional path to an image file to include with the request.
    bot: object - Bot instance for API calls.
    event: object - Event information for context.
    context: object - Additional context information.
    """
    logging.info(f"Starting get_ai_response for team '{team_name}'. Initial input: '{user_input[:100]}...'")

    # Prepare initial message content
    current_content = []
    if image_path and os.path.exists(image_path):
        logging.info(f"Processing image: {image_path}")
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            current_content.extend([
                {"type": "input_text", "text": user_input},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{base64_image}"}
            ])
        except Exception as e:
            logging.error(f"Error reading image file {image_path}: {e}")
            return {"type": "error", "content": f"⚠️ Error processing image: {str(e)}"}
    else:
        # Standard text-only input
        current_content.append({"type": "input_text", "text": user_input})

    max_tool_iterations = 5  # Safety limit for sequential tool calls
    current_iteration = 0
    # We will build the input for the *next* call within the loop
    next_api_input = current_content

    while current_iteration < max_tool_iterations:
        current_iteration += 1
        logging.info(f"--- AI Interaction Iteration {current_iteration} ---")

        try:
            logging.debug(f"Calling OpenAI API with input: {next_api_input}")
            response = client.responses.create(
                model="gpt-4o",
                tools=new_tools,
                input=next_api_input,  # Pass the constructed input
                instructions=seed  # Use the enhanced seed/instructions
            )
            logging.debug(f"Received OpenAI response: {response}")

        except Exception as e:
            logging.exception("Error calling OpenAI API")
            return {"type": "error", "content": f"⚠️ Error communicating with AI: {str(e)}"}

        if not response.output:
            logging.warning("OpenAI response contained no output.")
            return {"type": "error", "content": "⚠️ AI response was empty."}

        tool_calls_in_response = []
        final_text_content = None
        final_image_url = None

        # Process the response items
        for item in response.output:
            if isinstance(item, ResponseFunctionToolCall) and item.type == "function_call":
                logging.info(f"AI requested tool call: {item.name}")
                tool_calls_in_response.append(item)  # Collect all tool calls in this response
            elif isinstance(item, ResponseOutputMessage) and item.type == "message":
                for content_part in item.content:
                    if isinstance(content_part, ResponseOutputText) and content_part.type == "output_text":
                        final_text_content = content_part.text
                        logging.info("AI provided text output.")
                    # Check for image output as well
                    elif hasattr(content_part, 'type') and content_part.type == 'image':
                        final_image_url = content_part.url
                        logging.info(f"AI provided image output: {final_image_url}")

        # --- Decision Logic ---

        # Priority 1: If there are tool calls, execute them.
        if tool_calls_in_response:
            logging.info(f"Executing {len(tool_calls_in_response)} tool call(s)...")
            tool_results = []  # Results to feed back to the AI

            for tool_call in tool_calls_in_response:
                function_name = tool_call.name
                try:
                    arguments = json.loads(tool_call.arguments)
                    logging.debug(f"Executing {function_name} with args: {arguments}")

                    if function_name in FUNCTION_REGISTRY:
                        function_to_call = FUNCTION_REGISTRY[function_name]
                        sig = inspect.signature(function_to_call)
                        params = sig.parameters

                        # Inject necessary context if function accepts it
                        if 'bot' in params and bot: arguments['bot'] = bot
                        if 'event' in params and event: arguments['event'] = event
                        if 'team_name' in params: arguments['team_name'] = team_name  # Inject team_name if needed
                        if 'user' in params and event: arguments[
                            'user'] = event.msg.sender.username  # Inject user for reset_sign
                        if 'sender' in params and event: arguments[
                            'sender'] = event.msg.sender.username  # Inject sender if needed
                        if 'team_members' in params and bot and event:
                            arguments['team_members'] = await get_channel_members(event.msg.conv_id, bot)

                        # Execute sync or async function
                        if asyncio.iscoroutinefunction(function_to_call):
                            result = await function_to_call(**arguments)
                        else:
                            result = function_to_call(**arguments)

                        # Format result for the AI
                        # Handle complex results (like dicts with msg/file) - convert to string for AI
                        if isinstance(result, dict) and "msg" in result:
                            result_str = f"Message: {result['msg']}"
                            if "file" in result:
                                result_str += f" (File generated: {result['file']})"  # Inform AI file was generated
                            tool_output = result_str
                        else:
                            tool_output = str(result)  # Convert anything else to string

                        logging.info(f"Tool {function_name} executed successfully.")
                        logging.debug(f"Tool {function_name} result: {tool_output[:200]}...")  # Log snippet
                        tool_results.append({
                            "type": "tool_result",  # Use a consistent type name
                            "tool_name": function_name,
                            # Include tool_call.id if available and needed by your API structure
                            "output": tool_output
                        })

                    else:
                        logging.error(f"Function '{function_name}' not found in registry.")
                        tool_results.append({
                            "type": "tool_error",
                            "tool_name": function_name,
                            "error": f"Function '{function_name}' is not available."
                        })

                except Exception as e:
                    logging.exception(f"Error executing tool {function_name}")
                    tool_results.append({
                        "type": "tool_error",
                        "tool_name": function_name,
                        "error": f"Error during execution: {str(e)}"
                    })

            # Prepare input for the *next* API call, including tool results
            # How you structure this depends heavily on what client.responses.create expects.
            # Option 1: If it can take a list like chat.completions:
            # next_api_input = previous_input + ai_response_message + tool_result_messages
            # Option 2: A simpler approach for unknown API - append results description to text
            tool_feedback_text = "\n".join(
                [f"Tool '{tr['tool_name']}': {tr.get('output', tr.get('error', 'Unknown state'))}" for tr in
                 tool_results])
            # Let's try combining original input with tool feedback for the next round
            # This might require careful prompting/seed instructions.
            # Keep the original input text for context. Maybe add a system message?
            # This part is experimental due to the custom `responses.create` interface.
            # Let's construct a list combining original text and tool results.
            next_api_input = [
                # Keep original text/image input if needed for context
                *current_content,
                # Add a summary of tool actions and results
                {"type": "system_feedback",
                 "text": f"Executed tools. Results:\n{tool_feedback_text}\nNow, provide the final response to the user or call the next required tool."}
            ]
            logging.info("Proceeding to next iteration with tool results.")
            continue  # Go to the next iteration of the while loop

        # Priority 2: If no tool calls, but there's text content, return it.
        elif final_text_content is not None:
            logging.info("AI provided final text response. Returning.")
            # Check if the result was actually from a tool that returns a dict
            # This might happen if a tool *directly* returns the final message format
            try:
                content_dict = json.loads(final_text_content)
                if isinstance(content_dict, dict) and "msg" in content_dict:
                    logging.info("Detected structured message in final text. Returning as dict.")
                    return {"type": "text", "content": content_dict}  # Return the dict directly
            except json.JSONDecodeError:
                # It's just plain text
                pass
            # Return plain text
            return {"type": "text", "content": final_text_content}

        # Priority 3: If no tool calls, no text, but an image URL, return it.
        elif final_image_url is not None:
            logging.info("AI provided final image response. Returning.")
            return {"type": "image", "url": final_image_url}


        # Priority 4: If response had no tool calls and no usable content.
        else:
            logging.warning("AI response had no tool calls and no recognizable output content.")
            return {"type": "error", "content": "⚠️ AI did not provide a usable response."}

    # If loop finishes (max iterations reached)
    logging.error(f"Exceeded maximum tool iterations ({max_tool_iterations}).")
    return {"type": "error", "content": f"⚠️ Failed to complete request within {max_tool_iterations} steps."}


async def handle_marvn_mention(bot, event):
    """Handles @Marvn mentions and responds using AI."""
    msg_id = event.msg.id
    # Use event.msg.channel.name for team name context if available
    team_name = event.msg.channel.name or f"DM_{event.msg.conv_id[:8]}"  # Fallback for DMs
    conversation_id = event.msg.conv_id
    sender = event.msg.sender.username
    mentions = event.msg.at_mention_usernames or []
    # Fetch members asyncronously once
    try:
        team_members = await get_channel_members(conversation_id, bot)
    except Exception as e:
        logging.error(f"Failed to get channel members for {conversation_id}: {e}")
        team_members = [sender]  # Fallback

    # React immediately
    reaction_task = asyncio.create_task(bot.chat.react(conversation_id, msg_id, ":marvin:"))

    # Initial prompt and metadata setup
    user_prompt = ""
    attachment_path = None
    message_metadata = {
        "sender": sender,
        "mentions": mentions,
        "team_members": team_members,
        "conversation_id": conversation_id,
        "team_name": team_name,
        # "Chat Context": context.get_context_for_bot() # Add if you have context object
    }

    # --- Handle Attachments ---
    if event.msg.content.type_name == 'attachment':
        logging.info("Processing an attachment message.")
        storage = Path('./storage')
        storage.mkdir(exist_ok=True)  # Ensure storage exists
        attachment_title = event.msg.content.attachment.object.title or ""
        filename = storage.absolute() / event.msg.content.attachment.object.filename

        # Check if Marvn is mentioned in the title, otherwise ignore if only attachment
        if "@marvn" in attachment_title.lower():
            user_prompt = attachment_title.replace("@marvn", "").strip()
            logging.info(f"Downloading attachment: {filename}")
            try:
                await bot.chat.download(conversation_id, msg_id, str(filename))
                attachment_path = str(filename)
                message_metadata["attachment_path"] = attachment_path  # Add path to metadata
                user_prompt += f"\n\n[Image attached: {event.msg.content.attachment.object.filename}]"  # Inform AI about the attachment
            except Exception as e:
                logging.exception(f"Error downloading attachment {filename}")
                await bot.chat.reply(conversation_id, msg_id, f"⚠️ Sorry, I couldn't download the attachment: {e}")
                await reaction_task  # Ensure reaction is awaited
                return
        else:
            logging.info("Attachment received but '@marvn' not in title. Ignoring.")
            await reaction_task  # Ensure reaction is awaited
            return  # Don't process if Marvn wasn't mentioned in the title

    # --- Handle Text Messages (including replies) ---
    elif event.msg.content.type_name == 'text':
        message_text = str(event.msg.content.text.body)
        # Remove the @marvn mention prefix cleanly
        if message_text.lower().startswith("@marvn"):
            user_prompt = message_text[len("@marvn"):].strip()
        else:
            # This case shouldn't happen if the handler is only triggered on mention, but handle defensively
            user_prompt = message_text.strip()
            logging.warning("handle_marvn_mention triggered but '@marvn' prefix not found.")

        # Handle replies
        if event.msg.content.text.reply_to:
            logging.info("Processing a reply.")
            try:
                original_msg_info = await bot.chat.get(conversation_id, event.msg.content.text.reply_to)
                # Extract info carefully, assuming structure
                original_msg = original_msg_info.message[0]['msg']  # Adjust index/keys if needed
                original_sender = original_msg.get('sender', {}).get('username', 'unknown')
                original_content_type = original_msg.get('content', {}).get('type', 'unknown')
                original_text = ""
                original_attachment_info = ""

                if original_content_type == "text":
                    original_text = original_msg.get('content', {}).get('text', {}).get('body', '')
                elif original_content_type == "attachment":
                    obj = original_msg.get('content', {}).get('attachment', {}).get('object', {})
                    original_text = obj.get('title', '')  # Use title as text context
                    original_attachment_info = f"[Original message was an attachment: {obj.get('filename', 'unknown file')}]"
                    # Potentially download the replied-to attachment if needed for context? (Adds complexity)

                # Prepend reply context to the user's prompt
                user_prompt = f"In reply to {original_sender}:\n'{original_text}'\n{original_attachment_info}\n\n{sender}'s message:\n{user_prompt}"
                logging.debug(f"Constructed prompt with reply context: {user_prompt[:200]}...")

            except Exception as e:
                logging.exception("Error fetching or processing replied-to message.")
                # Continue without reply context, maybe notify user?
                user_prompt = f"(Failed to load reply context)\n{sender}: {user_prompt}"

    # --- Guard against empty prompts ---
    if not user_prompt and not attachment_path:
        logging.warning("No actionable prompt or attachment found after processing.")
        await bot.chat.reply(conversation_id, msg_id,
                             "What can I do for you? Please provide a command or question after mentioning me.")
        await reaction_task  # Ensure reaction is awaited
        return

    # Add metadata as a JSON string at the end of the prompt for the AI
    # Only add if there's actually a prompt to add it to
    if user_prompt:
        metadata_json = json.dumps(message_metadata, indent=2)
        user_prompt += f"\n\n--- Message Context ---\n{metadata_json}"

    # --- Call the AI ---
    logging.info("Calling get_ai_response...")
    response = await get_ai_response(
        user_input=user_prompt,
        team_name=team_name,
        image_path=attachment_path,  # Pass the downloaded path if it exists
        bot=bot,
        event=event,
        # context=context # Pass context if available
    )

    # --- Handle the AI Response ---
    logging.info(f"AI response received: {response}")
    try:
        if isinstance(response, dict) and "type" in response:
            response_type = response["type"]
            response_content = response.get("content")  # Use .get for safety
            response_url = response.get("url")

            if response_type == "text":
                if isinstance(response_content, str):
                    await bot.chat.reply(conversation_id, msg_id, response_content)
                # Handle case where a tool returned a dict {msg: ..., file: ...}
                elif isinstance(response_content, dict) and "msg" in response_content:
                    await bot.chat.reply(conversation_id, msg_id, response_content["msg"])
                    if "file" in response_content and response_content["file"]:
                        logging.info(f"Attaching file: {response_content['file']}")
                        try:
                            await bot.chat.attach(channel=conversation_id,  # Use channel=conv_id
                                                  filename=response_content["file"],
                                                  title=response_content.get("title", response_content["msg"][
                                                                                      :50]))  # Add title kwarg
                        except Exception as attach_err:
                            logging.error(f"Failed to attach file {response_content['file']}: {attach_err}")
                            await bot.chat.reply(conversation_id, msg_id,
                                                 f"(Couldn't attach the generated file: {attach_err})")

                else:
                    logging.error(f"Invalid content format for text response: {response_content}")
                    await bot.chat.reply(conversation_id, msg_id, "⚠️ Received an invalid text response from AI.")

            elif response_type == "image":
                if response_url:
                    logging.info(f"Downloading and attaching image from URL: {response_url}")
                    try:
                        downloaded_image_path = download_image(response_url)  # Assumes this returns a local path
                        if downloaded_image_path:
                            await bot.chat.attach(channel=conversation_id,  # Use channel=conv_id
                                                  filename=downloaded_image_path,
                                                  title="Here is the image you requested:")  # Add title kwarg
                        else:
                            raise ValueError("Download function returned None")
                    except Exception as img_err:
                        logging.exception("Error downloading or attaching AI-generated image")
                        await bot.chat.reply(conversation_id, msg_id,
                                             f"⚠️ Sorry, I couldn't attach the image: {img_err}")
                else:
                    logging.error("Image response type received, but no URL provided.")
                    await bot.chat.reply(conversation_id, msg_id,
                                         "⚠️ AI indicated an image response, but the URL was missing.")


            elif response_type == "error":
                await bot.chat.reply(conversation_id, msg_id, response_content or "⚠️ An unknown error occurred.")
            else:
                logging.error(f"Unknown response type received: {response_type}")
                await bot.chat.reply(conversation_id, msg_id, "⚠️ Received an unknown response type from AI.")
        else:
            logging.error(f"Invalid response format from get_ai_response: {response}")
            await bot.chat.reply(conversation_id, msg_id,
                                 "⚠️ Error: Received an improperly formatted response from the AI handler.")

    except Exception as handler_err:
        logging.exception("Error handling AI response in handle_marvn_mention")
        await bot.chat.reply(conversation_id, msg_id,
                             f"💥 Apologies, a critical error occurred while handling my own response: {handler_err}")

    finally:
        # Clean up downloaded attachment if it exists
        if attachment_path and os.path.exists(attachment_path):
            try:
                os.remove(attachment_path)
                logging.info(f"Cleaned up attachment: {attachment_path}")
            except OSError as e:
                logging.error(f"Error removing attachment file {attachment_path}: {e}")
        # Ensure the initial reaction task is awaited
        await reaction_task
        # Disable unfurling for the bot's messages if needed
        await set_unfurl(bot, False)


if __name__ == "__main__":
    # Example local test (won't have bot/event objects)
    async def run_test():
        test_prompt = "Please list the current 'since' events for team 'test_team' and then reset the one named 'Last Coffee Break' if it exists."
        # test_prompt = "What is the weather?"
        # test_prompt = "Tell me a joke"
        # test_prompt = "award 5 points to bob for helping" # Will fail without bot/event
        response = await get_ai_response(user_input=test_prompt, team_name="test_team")  # No bot/event provided
        print(json.dumps(response, indent=2))


    # asyncio.run(run_test())
    print("Run the main bot script to test interactively.")
    pass

# --- END OF FILE open_ai_agent.py ---