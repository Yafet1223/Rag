from collections import defaultdict

from .event import Event


class EventManager:

    def __init__(self):

        self.events = defaultdict(list)

    # -------------------------
    # Add event
    # -------------------------

    def add_event(
        self,
        event: Event
    ):

        self.events[
            event.user_id
        ].append(event)

    # -------------------------
    # Get all events
    # -------------------------

    def get_events(
        self,
        user_id: str
    ):

        return self.events[user_id]

    # -------------------------
    # Get recent events
    # -------------------------

    def get_recent_events(
        self,
        user_id: str,
        limit: int = 5
    ):

        return self.events[user_id][-limit:]