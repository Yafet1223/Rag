from fastapi import APIRouter
from datetime import datetime

from memory import chat_buffer
from memory.schema import ChatMessage

from Services.llm_services import generate_response


router = APIRouter()


@router.post("/chat")
async def chat(
    user_id: str,
    message: str
):

    # -----------------------------
    # Store user message
    # -----------------------------

    user_message = ChatMessage(
        role="user",
        content=message,
        timestamp=datetime.utcnow()
    )

    chat_buffer.add_message(
        user_id,
        user_message
    )

    # -----------------------------
    # Build chat history
    # -----------------------------

    messages = chat_buffer.get_messages(
        user_id
    )

    # -----------------------------
    # Generate AI response
    # -----------------------------

    response = generate_response(
        messages
    )

    # -----------------------------
    # Store assistant response
    # -----------------------------

    assistant_message = ChatMessage(
        role="assistant",
        content=response,
        timestamp=datetime.utcnow()
    )

    chat_buffer.add_message(
        user_id,
        assistant_message
    )

    # -----------------------------
    # Return response
    # -----------------------------

    return {
        "response": response
    }