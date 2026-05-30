import json
from typing import Optional

from google import genai
from pydantic import BaseModel, Field


class ExtractedEventData(BaseModel):
    event_type: str = Field(
        description="Generic category of the event, e.g. study, sleep, work, health, spirituality"
    )
    study_hours: Optional[float] = Field(None, description="Hours spent studying, if mentioned")
    mood: Optional[str] = Field(None, description="User mood or physical feeling, if mentioned")
    bible_read: Optional[bool] = Field(None, description="Whether the user read the bible")
    prayer_done: Optional[bool] = Field(None, description="Whether the user prayed")
    sleep_time: Optional[str] = Field(None, description="Bedtime e.g. '11:00 PM'")
    wake_time: Optional[str] = Field(None, description="Wake time e.g. '6:30 AM'")
    notes: Optional[str] = Field(None, description="Extra context or summary")


def extract_event_with_ai(
    client: genai.Client,
    message: str,
    model: str = "gemini-2.5-flash",
) -> ExtractedEventData:
    prompt = f'Analyze this user event message and extract all mentioned variables: "{message}"'
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ExtractedEventData,
        },
    )
    return ExtractedEventData(**json.loads(response.text))
