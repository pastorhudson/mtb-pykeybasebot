import openai
from datetime import datetime
from typing import List, Dict, Optional


class ChatContextManager:
    def __init__(self, max_recent_messages=5, max_summary_length=300, summary_interval=10):
        self.recent_messages = []  # Store recent messages
        self.conversation_summary = "No conversation yet."  # Running summary
        self.message_count = 0  # Total messages seen
        self.max_recent_messages = max_recent_messages
        self.max_summary_length = max_summary_length
        self.summary_interval = summary_interval
        self.client = openai.OpenAI()  # Initialize OpenAI client

    def add_message(self, message: Dict) -> None:
        """Add a new message to the context."""
        # Remove sensitive information (simple example)
        clean_message = self._sanitize_message(message)

        # Add to recent messages, maintaining size limit
        self.recent_messages.append(clean_message)
        if len(self.recent_messages) > self.max_recent_messages:
            self.recent_messages.pop(0)

        self.message_count += 1

        # Update summary periodically
        if self.message_count % self.summary_interval == 0:
            self._update_summary()

    def _sanitize_message(self, message: Dict) -> Dict:
        """Remove sensitive information from messages."""
        # Basic example - you'd want more sophisticated filtering in practice
        sensitive_terms = ["password", "ssn", "credit card", "address"]
        content = message["content"]

        for term in sensitive_terms:
            content = content.replace(term, "[REDACTED]")

        return {
            "role": message["role"],
            "content": content,
            "timestamp": message.get("timestamp", datetime.now().isoformat())
        }

    def _update_summary(self) -> None:
        """Update the conversation summary using OpenAI."""
        messages = [
            {"role": "system",
             "content": f"Summarize this conversation in under {self.max_summary_length} characters. Focus only on key topics and important information."},
            {"role": "user",
             "content": f"Current summary: {self.conversation_summary}\n\nRecent messages: {str(self.recent_messages)}"}
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use a smaller model for summaries to save cost
                messages=messages,
                max_tokens=150
            )
            self.conversation_summary = response.choices[0].message.content
        except Exception as e:
            print(f"Error updating summary: {e}")

    def get_context_for_bot(self) -> List[Dict]:
        """Return the context to be sent to the chatbot."""
        context = [
            {"role": "system", "content": f"Conversation summary: {self.conversation_summary}"}
        ]
        # Add recent messages
        for msg in self.recent_messages:
            context.append({"role": msg["role"], "content": msg["content"]})

        return context

    def reset_context(self) -> None:
        """Reset the context (for example, when conversation topic changes drastically)."""
        self.recent_messages = []
        self.conversation_summary = "No conversation yet."


# Example usage in a chat bot
class ChatBot:
    def __init__(self):
        self.context_manager = ChatContextManager()
        self.client = openai.OpenAI()

    def process_message(self, user_message: str, user_id: str) -> str:
        """Process an incoming message and generate a response."""
        # Add user message to context
        self.context_manager.add_message({
            "role": "user",
            "content": user_message,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })

        # Get context for the bot
        context = self.context_manager.get_context_for_bot()

        # Add the current query
        context.append({"role": "user", "content": user_message})

        # Get response from OpenAI
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",  # Or your preferred model
                messages=context
            )
            bot_response = response.choices[0].message.content

            # Add bot response to context
            self.context_manager.add_message({
                "role": "assistant",
                "content": bot_response,
                "timestamp": datetime.now().isoformat()
            })

            return bot_response
        except Exception as e:
            print(f"Error getting response: {e}")
            return "Sorry, I couldn't process that message."

    def handle_command(self, command: str) -> str:
        """Handle special commands from users."""
        if command == "/forget":
            self.context_manager.reset_context()
            return "I've cleared my memory of our conversation."
        elif command == "/summary":
            return f"Current conversation summary: {self.context_manager.conversation_summary}"
        # Add more commands as needed
        return "Unknown command."