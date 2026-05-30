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
Classify the user message into exactly one category:

1. 'event' - A COMPLETED past activity they are reporting (e.g. "I studied 2 hours today", "I slept at 2am last night").
   NOT for hypotheticals ("if I sleep...") or plans ("I'm about to sleep").

2. 'profile' - Durable facts, rules, preferences, causes and effects (e.g. "I prefer coffee",
   "If I sleep after midnight I get a headache tomorrow", "I struggle with focus in noise").

3. 'chat' - Questions, greetings, advice requests, or imminent decisions needing a conversational reply
   (e.g. "I'm about to sleep after midnight", "Should I stay up?", "How can I focus?").

4. 'ignore' - Very short low-value replies ("ok", "lol", "haha").

Examples:
- "if i sleep after midnight my headache starts tomorrow" → profile
- "hey i am about to sleep after midnight" → chat
- "i studied 3 hours and feel tired" → event

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