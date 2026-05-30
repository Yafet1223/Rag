"""Builds long-term memory context from events, profile, and behaviour for chat / RAG prompts."""

from Behaviour.behaviour import BehaviourAnalyzer
from Event.event_manager import EventManager
from Profile.memory.profile_manager import ProfileManager


def build_memory_context(
    user_id: str,
    event_manager: EventManager,
    profile_manager: ProfileManager,
    *,
    analytics_days: int = 30,
    recent_event_limit: int = 5,
    include_behaviour: bool = True,
) -> str:
    events = event_manager.get_events(user_id)
    analytics = event_manager.get_behavioral_analytics(user_id, days=analytics_days)
    profile_summary = profile_manager.get_profile_summary(user_id)
    profile_facts = profile_manager.get_facts(user_id)

    memory_context = "=== USER STORED MEMORIES & ANALYTICS ===\n"
    memory_context += analytics.get("summary_markdown", "") + "\n\n"
    memory_context += profile_summary.get("summary_markdown", "") + "\n"

    if include_behaviour:
        behaviour = BehaviourAnalyzer(event_manager, profile_manager).analyze(
            user_id, days=analytics_days
        )
        memory_context += "\n" + behaviour.get("summary_markdown", "") + "\n"

    if not events and not profile_facts:
        memory_context += (
            "(No specific events or profile facts stored yet. "
            "Encourage the user to share habits and activities when relevant.)\n"
        )

    if events:
        memory_context += f"\n--- Recent Events (last {recent_event_limit}) ---\n"
        for i, ev in enumerate(events[-recent_event_limit:], 1):
            details = []
            if ev.study_hours is not None:
                details.append(f"Studied: {ev.study_hours} hrs")
            if ev.mood:
                details.append(f"Mood: {ev.mood}")
            if ev.bible_read is not None:
                details.append(f"Read Bible: {ev.bible_read}")
            if ev.prayer_done is not None:
                details.append(f"Prayed: {ev.prayer_done}")

            duration = ev.calculate_sleep_duration()
            if duration:
                details.append(f"Sleep: {ev.sleep_time} to {ev.wake_time} ({duration} hrs)")
            else:
                if ev.sleep_time:
                    details.append(f"Slept: {ev.sleep_time}")
                if ev.wake_time:
                    details.append(f"Woke: {ev.wake_time}")

            if ev.notes:
                details.append(f"Notes: {ev.notes}")
            if ev.tags:
                details.append(f"Tags: {ev.tags}")

            ts_str = (
                ev.timestamp.strftime("%Y-%m-%d %H:%M")
                if hasattr(ev.timestamp, "strftime")
                else str(ev.timestamp)
            )
            memory_context += f"Event #{i} [{ev.event_type}] ({ts_str}): {', '.join(details)}\n"

    if profile_facts:
        memory_context += "\n--- Profile Facts ---\n"
        for i, prof in enumerate(profile_facts, 1):
            memory_context += (
                f"Fact #{i} [{prof.topic}/{prof.trait_type}]: {prof.statement}\n"
            )

    return memory_context
