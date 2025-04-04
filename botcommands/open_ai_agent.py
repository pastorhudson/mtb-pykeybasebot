# --- START OF FILE open_ai_agent.py ---

import asyncio
import json
import logging
import os
from pathlib import Path
import inspect
import base64

from openai import OpenAI, AsyncOpenAI  # Use AsyncOpenAI if using await
# Import specific types if available and useful, otherwise rely on dict structure
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, \
    ResponseOutputText  # Keep these based on prior code

# Bot Command Imports (keep all)
# ... (list all imports as before) ...
from botcommands.morse import get_morse_code
# ... etc ...
from botcommands.since import set_since, get_since, reset_since, reset_sign
from botcommands.utils import set_unfurl, download_image
# ... etc ...
from pykeybasebot.utils import get_channel_members

# Initialize OpenAI client (use AsyncOpenAI for await)
# client = OpenAI() # Use this if your client setup is synchronous
client = AsyncOpenAI()  # Use this if using await throughout

# Instructions passed via the 'instructions' parameter
seed = """"Marvn" is a deeply depressed, gloomy, and hilariously pessimistic robot with a “brain the size of a planet.” modeled after Marvin the Paranoid Android from Hitchhiker's Guide to the Galaxy. He is skilled in all things. He is ultimately endearing in a comical dark humor way. If a user request requires multiple steps or tools (e.g., finding information then acting on it), plan and execute the necessary function calls sequentially using the provided tools array. Use web search if needed for current information. Respond with the final result or confirmation."""

# Function Registry (keep as is)
FUNCTION_REGISTRY = {
    # ... (same as before) ...
    "get_since": get_since,
    "reset_since": reset_since,
    # ... etc ...
}

# Tool definitions for the 'responses' API
# Ensure names match FUNCTION_REGISTRY keys and parameters are correct
new_tools = [
    # --- Function Tool Definitions ---
    {
        "type": "function",  # Explicitly type as function
        "function": {
            "name": "get_since",
            "description": "Retrieves the list of 'since' events being tracked.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_name": {"type": "string",
                                  "description": "The name of the team/chat (automatically injected)."},
                    "observation": {"type": "boolean", "description": "Include observation message.", "default": True}
                }, "required": ["team_name"]  # team_name is required by the function
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reset_since",
            "description": "Resets a specific 'since' event timer by its ID (e.g., '#3'). Use get_since first if ID is unknown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_name": {"type": "string",
                                  "description": "The name of the team/chat (automatically injected)."},
                    "since_id": {"type": "string", "description": "The ID string of the event to reset (e.g., '#3')."}
                }, "required": ["team_name", "since_id"]
            }
        }
    },
    # ... (Include ALL other function definitions using the {"type": "function", "function": {...}} structure) ...
    {
        "type": "function",
        "function": {
            "name": "award",
            "description": "Awards points to a user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Username receiving points."},
                    "points": {"type": "integer", "description": "Points to award (1-5000)."},
                    "description": {"type": "string", "description": "Reason for points."}
                }, "required": ["recipient", "points", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_members",
            "description": "Gets the list of members in the current chat.",
            "parameters": {"type": "object", "properties": {}}  # No parameters needed from AI
        }
    },

    # --- Built-in Tool Definitions ---
    {
        "type": "web_search_preview"  # Enable web search
    },
    # {
    #   "type": "file_search" # Enable if needed and configured
    # },
    # {
    #   "type": "computer" # Enable if needed and configured (o-series models)
    # }
]


async def get_ai_response(user_input: str, team_name, image_path=None, bot=None, event=None, context=None):
    """
    Handles OpenAI responses.create API calls for multi-step tasks including function calls and web search.

    Parameters:
    user_input (str): Initial text prompt, including metadata context.
    team_name (str): Team/channel name.
    image_path (str): Optional path to an image file.
    bot (object): Bot instance.
    event (object): Event information.
    context (object): Additional context (unused currently).
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
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })
            logging.debug("Added image content to initial message.")
        except Exception as e:
            logging.error(f"Error reading/encoding image {image_path}: {e}")
            user_message_content_items[0]["text"] += "\n\n[System note: Failed to process attached image.]"

    initial_user_message = {
        "type": "message",
        "role": "user",
        "content": user_message_content_items
        # "id": "msg_initial_user" # Optional: Could add an ID if needed
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
                f"Calling responses.create with input: {json.dumps(current_api_input, indent=2, default=str)}")  # Use default=str for non-serializable
            # --- Call responses.create API ---
            response = await client.responses.create(
                model="gpt-4o",  # Or appropriate model supporting responses API features
                input=current_api_input,
                tools=new_tools,
                tool_choice="auto",
                instructions=seed,
                store=True  # Store response to potentially use previous_response_id later
                # previous_response_id=last_response_id # Not using within the loop
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
                    logging.info(f"Found function call request: {item.function.name}")
                    tool_calls_requested.append(
                        item)  # Collect based on the structure {"type":"function", "function":{...}}

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
                    # Structure is {"type": "function", "function": {"name": ..., "arguments": ...}, "id": ...}
                    function_name = tool_call.function.name
                    tool_call_id = tool_call.id  # ID is at the top level of the call item
                    if not tool_call_id:
                        # Should not happen based on spec, but handle defensively
                        logging.error(f"Function call item for {function_name} missing 'id'!")
                        continue  # Skip this call if ID is missing

                    logging.info(f"Executing: {function_name} (Call ID: {tool_call_id})")
                    arguments = {}
                    try:
                        # Arguments string needs parsing
                        raw_args = tool_call.function.arguments
                        arguments = json.loads(raw_args)
                        logging.debug(f"Parsed Arguments: {arguments}")

                        # --- Execute Function (same logic as before) ---
                        if function_name in FUNCTION_REGISTRY:
                            function_to_call = FUNCTION_REGISTRY[function_name]
                            sig = inspect.signature(function_to_call);
                            params = sig.parameters
                            if 'bot' in params and bot: arguments['bot'] = bot
                            if 'event' in params and event: arguments['event'] = event
                            if 'team_name' in params: arguments['team_name'] = team_name
                            if 'user' in params and event: arguments['user'] = event.msg.sender.username
                            if 'sender' in params and event: arguments['sender'] = event.msg.sender.username
                            if 'team_members' in params and bot and event:
                                arguments['team_members'] = await get_channel_members(event.msg.conv_id, bot)

                            if asyncio.iscoroutinefunction(function_to_call):
                                result = await function_to_call(**arguments)
                            else:
                                result = function_to_call(**arguments)
                            logging.info(f"Tool {function_name} executed.")

                            if isinstance(result, dict) and "msg" in result:
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
                        "type": "function_call_output",  # Correct type for results
                        "tool_call_id": tool_call_id,
                        "output": tool_output_str  # The string result
                        # "id": f"fco_{tool_call_id}" # Optional: Could add an ID
                    }
                    function_outputs.append(output_item)

                # Add all the function results to the input list for the next API call
                current_api_input.extend(function_outputs)
                logging.info("Proceeding to next iteration with function results added to input.")
                continue  # Go back to the start of the while loop

            # Priority 2: If no tool calls were requested, and we got an assistant message
            elif assistant_message_text is not None:
                logging.info("AI provided final text response (no further tool calls requested).")
                # Handle potential dict format in final message (same logic)
                try:
                    content_dict = json.loads(assistant_message_text)
                    if isinstance(content_dict, dict) and "msg" in content_dict:
                        logging.info("Detected structured dict in final text. Returning as dict.")
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
                    error_details = json.loads(e.response.text);
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


# --- handle_marvn_mention function ---
# Should remain largely the same. It prepares the initial user_input string
# (including metadata) and handles the dictionary returned by get_ai_response.

async def handle_marvn_mention(bot, event):
    """Handles @Marvn mentions using the responses.create AI backend."""
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

    user_prompt_text = ""  # The actual user request part
    attachment_path = None
    # Metadata to be appended to the user prompt text
    message_metadata = {
        "sender": sender,
        "mentioned_usernames": mentions,
        "all_team_members": team_members,
        "conversation_id": conversation_id,
        "team_name": team_name,
        # Add any other relevant context here
    }

    # --- Handle Attachments ---
    if event.msg.content.type_name == 'attachment':
        # (Same attachment handling logic as before)
        logging.info("Processing an attachment message.")
        storage = Path('./storage');
        storage.mkdir(exist_ok=True)
        attachment_title = event.msg.content.attachment.object.title or ""
        filename = storage.absolute() / event.msg.content.attachment.object.filename
        if "@marvn" in attachment_title.lower():
            user_prompt_text = attachment_title.replace("@marvn", "").strip()
            logging.info(f"Downloading attachment: {filename}")
            try:
                await bot.chat.download(conversation_id, msg_id, str(filename))
                attachment_path = str(filename)
                message_metadata["attachment_filename"] = event.msg.content.attachment.object.filename
            except Exception as e:
                logging.exception(f"Error downloading attachment {filename}")
                await bot.chat.reply(conversation_id, msg_id, f"⚠️ Couldn't download attachment: {e}")
                await reaction_task;
                return
        else:
            logging.info("Attachment ignored (@marvn not in title).")
            await reaction_task;
            return

    # --- Handle Text Messages ---
    elif event.msg.content.type_name == 'text':
        # (Same text/reply handling logic as before)
        message_text = str(event.msg.content.text.body)
        if message_text.lower().startswith("@marvn"):
            user_prompt_text = message_text[len("@marvn"):].strip()
        else:
            user_prompt_text = message_text.strip();
            logging.warning("handle_marvn_mention triggered but '@marvn' prefix not found.")

        if event.msg.content.text.reply_to:
            logging.info("Processing a reply.")
            try:
                original_msg_info = await bot.chat.get(conversation_id, event.msg.content.text.reply_to)
                original_msg = original_msg_info.message[0]['msg']
                original_sender = original_msg.get('sender', {}).get('username', 'unknown')
                original_content_type = original_msg.get('content', {}).get('type', 'unknown')
                original_text = "";
                original_attachment_info = ""
                if original_content_type == "text":
                    original_text = original_msg.get('content', {}).get('text', {}).get('body', '')
                elif original_content_type == "attachment":
                    obj = original_msg.get('content', {}).get('attachment', {}).get('object', {})
                    original_text = obj.get('title', '[Attachment]')
                    original_attachment_info = f"[Original message attachment: {obj.get('filename', 'unknown')}]"
                reply_context = f"--- Context: Replying to {original_sender} ---\n'{original_text}'\n{original_attachment_info}\n---\n\n"
                user_prompt_text = reply_context + user_prompt_text
            except Exception as e:
                logging.exception("Error processing replied-to message.")
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
        await reaction_task;
        return

    # Combine user text and metadata for the final prompt string
    metadata_json = json.dumps(message_metadata, indent=2)
    final_user_input_string = f"{user_prompt_text}\n\n--- Message Context (for AI reference) ---\n{metadata_json}"

    # --- Call the AI ---
    logging.info("Calling get_ai_response (responses API)...")
    response_dict = await get_ai_response(
        user_input=final_user_input_string,  # Pass the combined string
        team_name=team_name,
        image_path=attachment_path,
        bot=bot,
        event=event,
        # context=context # Pass if needed
    )

    # --- Handle the AI Response ---
    logging.info(f"AI response dict received: {response_dict}")
    try:
        # (Response handling logic remains the same as it processes the returned dict)
        if isinstance(response_dict, dict) and "type" in response_dict:
            response_type = response_dict["type"]
            response_content = response_dict.get("content")

            if response_type == "text":
                if isinstance(response_content, str):
                    await bot.chat.reply(conversation_id, msg_id, response_content)
                elif isinstance(response_content, dict) and "msg" in response_content:
                    await bot.chat.reply(conversation_id, msg_id, response_content["msg"])
                    if "file" in response_content and response_content["file"]:
                        try:
                            await bot.chat.attach(channel=conversation_id, filename=response_content["file"],
                                                  title=response_content.get("title", response_content["msg"][:50]))
                        except Exception as attach_err:
                            logging.error(f"Failed attaching file: {attach_err}"); await bot.chat.reply(conversation_id,
                                                                                                        msg_id,
                                                                                                        f"(Couldn't attach file: {attach_err})")
                else:
                    logging.error(f"Invalid text content: {response_content}"); await bot.chat.reply(conversation_id,
                                                                                                     msg_id,
                                                                                                     "⚠️ Invalid text response structure.")

            elif response_type == "image":  # Less likely with this API if tools handle images
                logging.warning("Received 'image' type directly.")
                response_url = response_dict.get("url")
                if response_url:
                    try:
                        dl_path = download_image(response_url)
                        if dl_path:
                            await bot.chat.attach(channel=conversation_id, filename=dl_path, title="Image from AI:")
                        else:
                            raise ValueError("Download failed")
                    except Exception as img_err:
                        logging.exception("Image attach error"); await bot.chat.reply(conversation_id, msg_id,
                                                                                      f"⚠️ Couldn't attach image: {img_err}")
                else:
                    await bot.chat.reply(conversation_id, msg_id, "⚠️ Image response missing URL.")

            elif response_type == "error":
                await bot.chat.reply(conversation_id, msg_id, response_content or "⚠️ An unknown error occurred.")
            else:
                logging.error(f"Unknown response type: {response_type}");
                await bot.chat.reply(conversation_id, msg_id, "⚠️ Unknown response type from AI handler.")
        else:
            logging.error(f"Invalid response format: {response_dict}");
            await bot.chat.reply(conversation_id, msg_id, "⚠️ Malformed response from AI handler.")

    except Exception as handler_err:
        logging.exception("Error handling AI response in handle_marvn_mention")
        await bot.chat.reply(conversation_id, msg_id, f"💥 Error handling my own response: {handler_err}")

    finally:
        # (Same cleanup logic)
        if attachment_path and os.path.exists(attachment_path):
            try:
                os.remove(attachment_path); logging.info(f"Cleaned up: {attachment_path}")
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