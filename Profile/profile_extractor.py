import json

from google import genai

from Profile.models.user_profile import ExtractedProfileData


def extract_profile_with_ai(
    client: genai.Client,
    message: str,
    model: str = "gemini-2.5-flash",
) -> ExtractedProfileData:
    """Uses Gemini to extract structured profile facts from a user statement."""
    prompt = f"""Extract a durable personal profile fact from this user statement.
Focus on preferences, habits, personality traits, standards, strengths, weaknesses, or goals.
Normalize the statement into a clear fact the assistant can reuse later.

User statement: "{message}"
"""
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ExtractedProfileData,
        },
    )
    return ExtractedProfileData(**json.loads(response.text))
