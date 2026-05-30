"""
Matches the current message against stored profile facts and events
to produce proactive coaching without a separate LLM call.
"""

from __future__ import annotations

import re
from typing import List, Optional

from Event.event_manager import EventManager
from Profile.memory.profile_manager import ProfileManager

SLEEP_LATE_SIGNALS = (
    "midnight",
    "after midnight",
    "12 am",
    "12am",
    "late night",
    "stay up late",
    "about to sleep",
    "going to sleep",
    "gonna sleep",
)

HEADACHE_SIGNALS = ("headache", "migraine", "head pain")


def _norm(text: str) -> str:
    return text.lower().strip()


def _mentions_sleeping_late(message: str) -> bool:
    n = _norm(message)
    return any(s in n for s in SLEEP_LATE_SIGNALS)


def _text_mentions_headache_and_late_sleep(text: str) -> bool:
    n = _norm(text)
    has_headache = any(h in n for h in HEADACHE_SIGNALS)
    has_late = "midnight" in n or "late" in n or "after 12" in n
    return has_headache and (has_late or "sleep" in n)


def _collect_relevant_memories(
    user_id: str,
    profile_manager: ProfileManager,
    event_manager: EventManager,
) -> List[str]:
    snippets: List[str] = []

    for fact in profile_manager.get_facts(user_id):
        blob = f"{fact.statement} {fact.raw_message or ''}"
        if _text_mentions_headache_and_late_sleep(blob):
            snippets.append(fact.statement)

    for event in event_manager.get_recent_events(user_id, limit=15):
        blob = f"{event.raw_message or ''} {event.notes or ''} {event.mood or ''}"
        if _text_mentions_headache_and_late_sleep(blob):
            snippets.append(event.raw_message or event.notes or "late sleep → headache pattern")

    return snippets


def get_contextual_coaching(
    user_id: str,
    message: str,
    profile_manager: ProfileManager,
    event_manager: EventManager,
) -> Optional[str]:
    """
  Returns a short coaching line when the user message triggers a known
  pattern from memory (e.g. late sleep → headache).
    """
    if not _mentions_sleeping_late(message):
        return None

    memories = _collect_relevant_memories(user_id, profile_manager, event_manager)
    if not memories:
        return None

    if is_imminent_sleep(message):
        return (
            "You’ve told me that sleeping after midnight often leads to headaches the next morning. "
            "I’d suggest turning in earlier tonight if you can— even 30–45 minutes can help. "
            "Want a quick wind-down routine?"
        )

    return (
        "I’ll remember that pattern. When you’re thinking about sleeping late, "
        "I can remind you about the headache link you mentioned."
    )


def is_imminent_sleep(message: str) -> bool:
    n = _norm(message)
    return any(
        p in n
        for p in (
            "about to sleep",
            "going to sleep",
            "gonna sleep",
            "heading to bed",
            "off to bed",
        )
    ) or ("sleep" in n and "midnight" in n and "if " not in n[:20])
