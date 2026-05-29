from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import re


def parse_time(time_str: str) -> Optional[datetime]:
    if not time_str:
        return None
    
    # Standard clean up
    cleaned = time_str.strip().upper()
    if cleaned == "MIDNIGHT":
        cleaned = "12:00 AM"
    elif cleaned == "NOON":
        cleaned = "12:00 PM"
        
    # Remove periods (e.g. P.M. -> PM)
    cleaned = cleaned.replace(".", "")
    
    formats = [
        "%I:%M %p", "%I %p", "%H:%M", "%H",
        "%I:%M%p", "%I%p"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
            
    # Try custom regex matching for things like "11pm" or "6:30am" without space
    match = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(AM|PM)$", cleaned)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        ampm = match.group(3)
        if ampm == "PM" and hour < 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0
        try:
            return datetime(1900, 1, 1, hour, minute)
        except ValueError:
            pass
            
    return None


class Event(BaseModel):
    id: Optional[int] = None
    user_id: str
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

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
    tags: Optional[str] = None  # Comma-separated tags, e.g., "exam_prep, heavy"
    raw_message: Optional[str] = None  # Raw statement that triggered this event
    metadata: Optional[str] = None  # Extensible JSON data (e.g. {"energy_level": 4, "exercise_duration": 45})

    def get_metadata_dict(self) -> dict:
        """Helper to parse custom JSON metadata dictionary."""
        import json
        if not self.metadata:
            return {}
        try:
            return json.loads(self.metadata)
        except Exception:
            return {}

    def set_metadata_dict(self, data: dict):
        """Helper to set metadata from a Python dictionary."""
        import json
        self.metadata = json.dumps(data)

    def calculate_sleep_duration(self) -> Optional[float]:
        """Calculates sleep duration in hours from sleep_time and wake_time."""
        if not self.sleep_time or not self.wake_time:
            return None
        
        t_sleep = parse_time(self.sleep_time)
        t_wake = parse_time(self.wake_time)
        
        if not t_sleep or not t_wake:
            return None
            
        diff = t_wake - t_sleep
        hours = diff.total_seconds() / 3600.0
        
        if hours < 0:
            # Went to bed before midnight, woke up the next day
            hours += 24.0
            
        return round(hours, 2)

    def get_tags_list(self) -> List[str]:
        """Returns the tags as a clean list of strings."""
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(",") if t.strip()]