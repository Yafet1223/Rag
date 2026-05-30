import sys
from datetime import datetime
from pathlib import Path

from google import genai

from Core.memory_context import build_memory_context
from Event.event_manager import EventManager
from Profile.memory.profile_manager import ProfileManager

_CHAT_BUFFER_ROOT = Path(__file__).resolve().parent.parent / "Chat_buffer"
if str(_CHAT_BUFFER_ROOT) not in sys.path:
    sys.path.insert(0, str(_CHAT_BUFFER_ROOT))

from memory.Chatbuffer import ChatBuffer  # noqa: E402
from memory.schema import ChatMessage  # noqa: E402


class ChatHandler:
    """Multi-turn chat with short-term buffer + long-term event/profile memory."""

    def __init__(
        self,
        client: genai.Client,
        event_manager: EventManager,
        profile_manager: ProfileManager,
        *,
        model: str = "gemini-2.5-flash",
        max_messages: int = 10,
    ):
        self.client = client
        self.event_manager = event_manager
        self.profile_manager = profile_manager
        self.model = model
        self.buffer = ChatBuffer(max_messages=max_messages)

    def reply(self, user_id: str, message: str) -> str:
        user_message = ChatMessage(
            role="user",
            content=message,
            timestamp=datetime.utcnow(),
        )
        self.buffer.add_message(user_id, user_message)

        memory_context = build_memory_context(
            user_id, self.event_manager, self.profile_manager
        )
        history = self.buffer.get_messages(user_id)

        conversation = ""
        for msg in history[:-1]:
            conversation += f"{msg.role}: {msg.content}\n"

        prompt = f"""You are a Personal AI Life Assistant and behavior coach.
You know the user from stored events, habits, and profile facts below.
Be warm, concise, and actionable. Use their memory when it helps; do not dump raw statistics unless they ask.

{memory_context}

--- Recent conversation ---
{conversation or "(no prior messages in this session)"}

--- Latest user message ---
user: {message}

Reply as the assistant:"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        assistant_text = response.text or ""

        self.buffer.add_message(
            user_id,
            ChatMessage(
                role="assistant",
                content=assistant_text,
                timestamp=datetime.utcnow(),
            ),
        )
        return assistant_text

    def query_memory(self, user_id: str, question: str) -> str:
        """One-shot coaching answer grounded in stored memory (no chat buffer)."""
        memory_context = build_memory_context(
            user_id, self.event_manager, self.profile_manager
        )
        prompt = f"""You are a Personal AI Life Assistant & Behavior Coach.
Answer using ONLY the memory context below. Give personalized coaching when relevant.

{memory_context}

User question: "{question}"
Assistant response:"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text or ""

    def clear_session(self, user_id: str) -> None:
        self.buffer.clear_session(user_id)
