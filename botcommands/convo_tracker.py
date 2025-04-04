import os
import json
import logging
from datetime import datetime
from pathlib import Path
from collections import deque
import asyncio
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('conversation_tracker')


class ConversationTracker:
    """
    Tracks conversations by team/channel and stores them in a rolling buffer.
    Each team/channel gets its own file for conversation history.
    """

    def __init__(self, storage_dir: str = "./conversation_history", max_messages: int = 50):
        """
        Initialize the conversation tracker.

        Args:
            storage_dir: Directory to store conversation history files
            max_messages: Maximum number of messages to keep in the rolling buffer per team/channel
        """
        self.storage_dir = Path(storage_dir)
        self.max_messages = max_messages
        self.conversations: Dict[str, deque] = {}
        self.lock = asyncio.Lock()  # For thread safety when updating files

        # Create storage directory if it doesn't exist
        self.storage_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"Initialized ConversationTracker with storage at {self.storage_dir}")

        # Load existing conversations
        self._load_all_conversations()

    def _get_file_path(self, team_name: str) -> Path:
        """Get the file path for a team's conversation history."""
        # Sanitize team name for file system use
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in team_name)
        return self.storage_dir / f"{safe_name}_history.json"

    def _load_all_conversations(self) -> None:
        """Load all existing conversation histories from disk."""
        if not self.storage_dir.exists():
            return

        for file_path in self.storage_dir.glob("*_history.json"):
            try:
                team_name = file_path.stem.rsplit("_history", 1)[0]
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Initialize a deque with the loaded messages
                    self.conversations[team_name] = deque(data["messages"], maxlen=self.max_messages)
                    logger.info(f"Loaded {len(self.conversations[team_name])} messages for {team_name}")
            except Exception as e:
                logger.error(f"Error loading conversation history from {file_path}: {e}")

    def _load_conversation(self, team_name: str) -> None:
        """Load conversation history for a specific team."""
        if team_name in self.conversations:
            return  # Already loaded

        file_path = self._get_file_path(team_name)
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversations[team_name] = deque(data["messages"], maxlen=self.max_messages)
                    logger.info(f"Loaded {len(self.conversations[team_name])} messages for {team_name}")
            except Exception as e:
                logger.error(f"Error loading conversation for {team_name}: {e}")
                # Initialize empty conversation if loading fails
                self.conversations[team_name] = deque(maxlen=self.max_messages)
        else:
            # Initialize new conversation
            self.conversations[team_name] = deque(maxlen=self.max_messages)

    async def _save_conversation(self, team_name: str) -> None:
        """Save conversation history for a specific team."""
        file_path = self._get_file_path(team_name)

        async with self.lock:  # Use lock to prevent concurrent writes
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "team_name": team_name,
                        "last_updated": datetime.now().isoformat(),
                        "messages": list(self.conversations[team_name])
                    }, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved {len(self.conversations[team_name])} messages for {team_name}")
            except Exception as e:
                logger.error(f"Error saving conversation for {team_name}: {e}")

    async def add_message(self, team_name: str, message: dict) -> None:
        """
        Add a message to the conversation history.

        Args:
            team_name: Team or channel name
            message: Message data to add (must be JSON-serializable)
        """
        # Ensure conversation is loaded
        if team_name not in self.conversations:
            self._load_conversation(team_name)

        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()

        # Add message to the deque
        self.conversations[team_name].append(message)

        # Save to disk
        await self._save_conversation(team_name)

    def get_conversation(self, team_name: str, limit: Optional[int] = None) -> List[dict]:
        """
        Get conversation history for a team.

        Args:
            team_name: Team or channel name
            limit: Maximum number of recent messages to return (None for all)

        Returns:
            List of message dictionaries
        """
        # Ensure conversation is loaded
        if team_name not in self.conversations:
            self._load_conversation(team_name)

        # Return the requested number of messages (or all if limit is None)
        messages = list(self.conversations[team_name])
        if limit is not None:
            messages = messages[-limit:] if limit > 0 else []

        return messages

    async def clear_conversation(self, team_name: str) -> None:
        """
        Clear conversation history for a team.

        Args:
            team_name: Team or channel name
        """
        # Clear conversation
        self.conversations[team_name] = deque(maxlen=self.max_messages)

        # Save empty conversation
        await self._save_conversation(team_name)
        logger.info(f"Cleared conversation history for {team_name}")


# Integration with the existing bot system

# async def track_message(conversation_tracker, bot, event, is_bot_message=False):
#     """
#     Track a message in the conversation history.
#
#     Args:
#         conversation_tracker: ConversationTracker instance
#         bot: Bot instance
#         event: Message event
#         is_bot_message: True if the message is from the bot, False otherwise
#     """
#     # Determine team/channel name
#     team_name = event.msg.channel.name if hasattr(event.msg,
#                                                   'channel') and event.msg.channel else f"DM_{event.msg.conv_id[:8]}"
#     conversation_id = event.msg.conv_id
#
#     # Create message object
#     message = {
#         "sender": "marvn" if is_bot_message else event.msg.sender.username,
#         "content": event.msg.content.text.body if hasattr(event.msg.content, 'text') else "[NON-TEXT CONTENT]",
#         "msg_id": event.msg.id,
#         "timestamp": datetime.now().isoformat(),
#         "is_bot": is_bot_message
#     }
#
#     # Add attachment info if present
#     if hasattr(event.msg.content, 'attachment') and event.msg.content.attachment:
#         message["has_attachment"] = True
#         message["attachment_filename"] = event.msg.content.attachment.object.filename
#         message["attachment_title"] = event.msg.content.attachment.object.title
#
#     # Add reply info if present
#     if hasattr(event.msg.content, 'text') and event.msg.content.text.reply_to:
#         reply_to_id = event.msg.content.text.reply_to
#         message["reply_to"] = reply_to_id
#
#         # Fetch and store the original message content
#         try:
#             original_msg_info = await bot.chat.get(conversation_id, reply_to_id)
#             if original_msg_info and original_msg_info.message and len(original_msg_info.message) > 0:
#                 original_msg = original_msg_info.message[0]['msg']
#                 original_sender = original_msg.get('sender', {}).get('username', 'unknown')
#                 original_content_type = original_msg.get('content', {}).get('type', 'unknown')
#
#                 original_data = {
#                     "sender": original_sender,
#                     "msg_id": reply_to_id,
#                 }
#
#                 if original_content_type == "text":
#                     original_data["content"] = original_msg.get('content', {}).get('text', {}).get('body', '')
#                 elif original_content_type == "attachment":
#                     obj = original_msg.get('content', {}).get('attachment', {}).get('object', {})
#                     original_data["content"] = obj.get('title', '[Attachment]')
#                     original_data["has_attachment"] = True
#                     original_data["attachment_filename"] = obj.get('filename', 'unknown')
#                     original_data["attachment_title"] = obj.get('title', '')
#
#                 # Store the original message content in this message's metadata
#                 message["replied_to_message"] = original_data
#
#                 # Log the successful retrieval of the original message
#                 logging.info(f"Retrieved original message from {original_sender} for reply chain context")
#         except Exception as e:
#             logging.error(f"Error retrieving original message for reply chain: {e}")
#             message["replied_to_message"] = {"error": f"Failed to retrieve: {str(e)}"}
#
#     # Track the message
#     await conversation_tracker.add_message(team_name, message)
#     return message

async def track_message(conversation_tracker, bot, event, is_bot_message=False):
    """
    Track a message in the conversation history.

    Args:
        conversation_tracker: ConversationTracker instance
        bot: Bot instance
        event: Message event
        is_bot_message: True if the message is from the bot, False otherwise
    """
    # Determine team/channel name
    team_name = event.msg.channel.name if hasattr(event.msg,
                                                  'channel') and event.msg.channel else f"DM_{event.msg.conv_id[:8]}"
    conversation_id = event.msg.conv_id

    # Get message content safely
    message_content = "[NON-TEXT CONTENT]"
    if hasattr(event.msg.content, 'text') and event.msg.content.text is not None:
        message_content = event.msg.content.text.body
    elif hasattr(event.msg.content, 'attachment') and event.msg.content.attachment is not None:
        # For attachments, use the title as content if available
        if hasattr(event.msg.content.attachment.object, 'title') and event.msg.content.attachment.object.title:
            message_content = f"[ATTACHMENT: {event.msg.content.attachment.object.title}]"
        else:
            message_content = "[ATTACHMENT]"

    # Create message object
    message = {
        "sender": "marvn" if is_bot_message else event.msg.sender.username,
        "content": message_content,
        "msg_id": event.msg.id,
        "timestamp": datetime.now().isoformat(),
        "is_bot": is_bot_message
    }

    # Add attachment info if present
    if hasattr(event.msg.content, 'attachment') and event.msg.content.attachment:
        message["has_attachment"] = True
        message["attachment_filename"] = event.msg.content.attachment.object.filename
        message["attachment_title"] = event.msg.content.attachment.object.title or ""

    # Add reply info if present
    if hasattr(event.msg.content, 'text') and event.msg.content.text is not None and event.msg.content.text.reply_to:
        reply_to_id = event.msg.content.text.reply_to
        message["reply_to"] = reply_to_id

        # Fetch and store the original message content
        try:
            original_msg_info = await bot.chat.get(conversation_id, reply_to_id)
            if original_msg_info and original_msg_info.message and len(original_msg_info.message) > 0:
                original_msg = original_msg_info.message[0]['msg']
                original_sender = original_msg.get('sender', {}).get('username', 'unknown')
                original_content_type = original_msg.get('content', {}).get('type', 'unknown')

                original_data = {
                    "sender": original_sender,
                    "msg_id": reply_to_id,
                }

                if original_content_type == "text":
                    original_text = original_msg.get('content', {}).get('text', {})
                    original_data["content"] = original_text.get('body', '') if original_text else ''
                elif original_content_type == "attachment":
                    obj = original_msg.get('content', {}).get('attachment', {}).get('object', {})
                    original_data["content"] = obj.get('title', '[Attachment]')
                    original_data["has_attachment"] = True
                    original_data["attachment_filename"] = obj.get('filename', 'unknown')
                    original_data["attachment_title"] = obj.get('title', '')

                # Store the original message content in this message's metadata
                message["replied_to_message"] = original_data

                # Log the successful retrieval of the original message
                logging.info(f"Retrieved original message from {original_sender} for reply chain context")
        except Exception as e:
            logging.error(f"Error retrieving original message for reply chain: {e}")
            message["replied_to_message"] = {"error": f"Failed to retrieve: {str(e)}"}

    # Track the message
    await conversation_tracker.add_message(team_name, message)
    return message

# Function to get conversation context for AI
def get_conversation_context(conversation_tracker, team_name, limit=15):
    """
    Get recent conversation history formatted for AI context.

    Args:
        conversation_tracker: ConversationTracker instance
        team_name: Team/channel name
        limit: Number of recent messages to include

    Returns:
        Formatted conversation history string
    """
    messages = conversation_tracker.get_conversation(team_name, limit=limit)
    if not messages:
        return "No recent conversation."

    formatted_messages = []
    for msg in messages:
        sender = msg["sender"]
        content = msg.get("content", "[CONTENT UNAVAILABLE]")
        timestamp = msg.get("timestamp", "")

        # Format timestamp if present
        time_str = ""
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%H:%M:%S")
            except:
                time_str = timestamp

        # Format attachments if present
        attachment_info = ""
        if msg.get("has_attachment", False):
            filename = msg.get("attachment_filename", msg.get("file_path", "unknown"))
            attachment_info = f" [Attachment: {filename}]"

        # Format reply context if present
        reply_context = ""
        if "replied_to_message" in msg and isinstance(msg["replied_to_message"], dict):
            original = msg["replied_to_message"]
            original_sender = original.get("sender", "unknown")
            original_content = original.get("content", "[CONTENT UNAVAILABLE]")

            # Truncate long original messages
            if len(original_content) > 100:
                original_content = original_content[:97] + "..."

            reply_context = f" [Replying to {original_sender}: \"{original_content}\"]"

        # Format message
        formatted_msg = f"[{time_str}] {sender}: {content}{attachment_info}{reply_context}"
        formatted_messages.append(formatted_msg)

    return "\n".join(formatted_messages)


# Integration with the existing bot code in handle_marvn_mention
async def enhance_marvn_with_conversation_context(bot, event, conversation_tracker):
    """
    Enhance @marvn mentions with conversation context.
    This function would be integrated with your existing handle_marvn_mention function.
    """
    msg_id = event.msg.id
    team_name = event.msg.channel.name or f"DM_{event.msg.conv_id[:8]}"

    # Track the incoming message
    await track_message(conversation_tracker, bot, event)

    # Get the recent conversation context
    recent_conversation = get_conversation_context(conversation_tracker, team_name, limit=10)

    # Add conversation context to the user's prompt
    # This would be integrated with your existing code to prepare the user_prompt_text
    conversation_context = f"\n\n--- Recent Conversation Context ---\n{recent_conversation}\n---\n\n"

    # After the AI response is received and sent, track the bot's response
    # This would be called after sending the response to the user
    bot_response_event = event  # You'd need to create an event-like object with the response
    # Note: You'll need to adapt this to your actual response handling logic
    await track_message(conversation_tracker, bot, bot_response_event, is_bot_message=True)

    return conversation_context


# Example usage in your main bot code
"""
# Initialization
conversation_tracker = ConversationTracker(storage_dir="./conversation_history", max_messages=50)

# In your message handling function where handle_marvn_mention is called
async def on_message(bot, event):
    # Check if the message mentions @marvn
    if "@marvn" in event.msg.content.text.body.lower():
        # Track the incoming message
        await track_message(conversation_tracker, bot, event)
        
        # Get conversation context
        team_name = event.msg.channel.name or f"DM_{event.msg.conv_id[:8]}"
        conversation_context = get_conversation_context(conversation_tracker, team_name, limit=10)
        
        # Add conversation context to user_prompt_text
        user_prompt_text = f"{event.msg.content.text.body}\n\n--- Recent Conversation Context ---\n{conversation_context}\n---"
        
        # Call your existing handle_marvn_mention, but with enhanced prompt
        response = await handle_marvn_mention(bot, event, user_prompt_text)
        
        # Track the bot's response
        # Create a simulated event for the bot's response
        bot_response_event = create_bot_response_event(event, response)  # You'd need to implement this
        await track_message(conversation_tracker, bot, bot_response_event, is_bot_message=True)
"""