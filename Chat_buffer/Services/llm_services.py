import os
from google import genai

from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY", "AIzaSyDrNgEGwWUUv5NoONCols-gCV2_x2i27hM")
)

def generate_response(messages):

    formatted_context = ""

    for msg in messages:

        formatted_context += (
            f"{msg.role}: {msg.content}\n"
        )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=formatted_context
    )

    return response.text