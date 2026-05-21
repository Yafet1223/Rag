from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Event(BaseModel):

    user_id: str

    event_type: str

    timestamp: datetime = datetime.utcnow()

    # -------------------------
    # Optional event data
    # -------------------------

    study_hours: Optional[float] = None

    mood: Optional[str] = None

    bible_read: Optional[bool] = None

    prayer_done: Optional[bool] = None

    sleep_time: Optional[str] = None

    wake_time: Optional[str] = None

    notes: Optional[str] = None