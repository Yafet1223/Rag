from datetime import datetime
from typing import Literal, Optional
import json

from pydantic import BaseModel, Field


ProfileTopic = Literal[
    "lifestyle", "productivity", "diet", "spirituality", "general", "health"
]
ProfileTraitType = Literal[
    "preference", "habit", "strength", "weakness", "standard", "goal"
]
ProfilePolarity = Literal["positive", "negative", "neutral"]


class ExtractedProfileData(BaseModel):
    """Structured output from Gemini when routing classifies a message as profile."""

    statement: str = Field(
        description=(
            "A clear, durable fact about the user "
            "(e.g. 'Prefers working late at night', 'Struggles to focus in noisy rooms')"
        )
    )
    topic: ProfileTopic = Field(description="Main topic category for this fact")
    trait_type: ProfileTraitType = Field(
        description="Whether this is a preference, habit, strength, weakness, standard, or goal"
    )
    polarity: Optional[ProfilePolarity] = Field(
        None,
        description="Sentiment of the trait when applicable (e.g. weakness -> negative)",
    )
    confidence: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Extraction confidence from 0.0 to 1.0",
    )


class ProfileFact(BaseModel):
    id: Optional[int] = None
    user_id: str
    statement: str
    topic: ProfileTopic = "general"
    trait_type: ProfileTraitType = "preference"
    polarity: Optional[ProfilePolarity] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    raw_message: Optional[str] = None
    source: str = "user_stated"
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    metadata: Optional[str] = None

    def get_metadata_dict(self) -> dict:
        if not self.metadata:
            return {}
        try:
            return json.loads(self.metadata)
        except Exception:
            return {}

    def set_metadata_dict(self, data: dict) -> None:
        self.metadata = json.dumps(data)

    @classmethod
    def from_extraction(
        cls,
        user_id: str,
        extracted: ExtractedProfileData,
        raw_message: Optional[str] = None,
    ) -> "ProfileFact":
        polarity = extracted.polarity
        if polarity is None:
            if extracted.trait_type == "weakness":
                polarity = "negative"
            elif extracted.trait_type in ("strength", "goal"):
                polarity = "positive"
            else:
                polarity = "neutral"

        return cls(
            user_id=user_id,
            statement=extracted.statement.strip(),
            topic=extracted.topic,
            trait_type=extracted.trait_type,
            polarity=polarity,
            confidence=extracted.confidence,
            raw_message=raw_message,
            source="user_stated",
        )
