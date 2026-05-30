"""
Deterministic routing overrides before/after the hybrid router.

Fixes cases like:
- "if I sleep after midnight I get a headache" → profile (not event)
- "I'm about to sleep after midnight" → chat (coaching, not logging)
"""

import re

# Conditional / rule statements → durable profile memory
PROFILE_PATTERNS = [
    r"\bif i\b",
    r"\bwhen i\b",
    r"\bwhenever i\b",
    r"\bmakes me\b",
    r"\bcauses me\b",
    r"\bi tend to\b",
    r"\bi usually get\b",
    r"\bstarts tomorrow\b",
    r"\bnext morning\b",
    r"\bthe next day\b",
]

# Imminent action or advice-seeking → conversational coaching
CHAT_PATTERNS = [
    r"\babout to\b",
    r"\bgoing to sleep\b",
    r"\bgonna sleep\b",
    r"\bi am going to\b",
    r"\bi'm going to\b",
    r"\bshould i\b",
    r"\bwhat if i\b",
    r"\bwhat should i\b",
    r"\bcan you\b",
    r"\bhelp me\b",
    r"\badvice\b",
    r"\bremind me\b",
]


def is_conditional_or_rule(message: str) -> bool:
    norm = message.lower().strip()
    return any(re.search(p, norm) for p in PROFILE_PATTERNS)


def is_coaching_intent(message: str) -> bool:
    norm = message.lower().strip()
    return any(re.search(p, norm) for p in CHAT_PATTERNS)


def refine_route(message: str, category: str) -> tuple[str, str]:
    """
    Returns (refined_category, reason_suffix).
    Profile and coaching intents take priority over event logging.
    """
    if category == "ignore":
        return category, ""

    if is_conditional_or_rule(message):
        if category != "profile":
            return "profile", " (routing override: conditional rule → profile memory)"
        return category, ""

    if is_coaching_intent(message):
        if category in ("event", "profile"):
            return "chat", " (routing override: advice/imminent action → chat)"
        return category, ""

    return category, ""
