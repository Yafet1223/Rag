import json
from typing import Literal
from pydantic import BaseModel, Field
from google import genai


class RoutingResult(BaseModel):
    type: Literal["event", "profile", "chat", "ignore"]
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")
    reason: str = Field(description="Brief reason explaining the routing decision")


class AIRouter:

    def __init__(self, client: genai.Client, model: str = "gemini-2.5-flash"):
        self.client = client
        self.model = model

    def classify(self, message: str) -> dict:
        prompt = f"""You are a memory routing system for a personalized AI life assistant.
Your job is to analyze the user's message and classify it into one of these four categories:

1. 'event' - Things the user did, scheduled, or experienced (e.g., studying, sleeping, praying, working, mood).
2. 'profile' - Explicit preferences, habits, personality, standards, strengths, or weaknesses (e.g., "I prefer coffee", "I struggle with focusing").
3. 'chat' - Casual conversations, general questions, greetings, or off-topic messages.
4. 'ignore' - Short, low-value conversational responses that don't need memory storage (e.g., "haha", "ok", "cool").

User Message: "{message}"
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": RoutingResult,
                }
            )

            if response.text:
                return json.loads(response.text)

            raise ValueError("Empty response text from generative AI client")

        except Exception as e:
            return {
                "type": "chat",
                "confidence": 0.5,
                "reason": f"Fallback due to exception: {str(e)}"
            }