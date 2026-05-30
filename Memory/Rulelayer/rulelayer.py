import re

class Rulelayer:
    def __init__(self):
        self.rules = [
            "i studied",
            "i slept",
            "i worked",
            "today i",
            "yesterday i"
        ]
        self.profile = [
            "i prefer",
            "i usually",
            "i always",
            "i struggle with",
            "i am good at",
            "if i",
            "when i",
            "makes me",
            "causes me",
            "starts tomorrow",
        ]
        self.chat = [
            "about to",
            "should i",
            "what if",
            "help me",
            "can you",
            "going to sleep",
        ]
        self.ignore = [
            "ok",
            "lol",
            "haha",
            "nice",
            "cool"
        ]

    def normalize(self, message: str) -> str:
        return message.lower().strip()

    def _matches_pattern(self, signal: str, message: str) -> bool:
        # Check for whole-word or phrase boundary to prevent substring greediness
        pattern = r'\b' + re.escape(signal) + r'\b'
        return bool(re.search(pattern, message, re.IGNORECASE))

    def _is_hypothetical(self, message: str) -> bool:
        hypothetical = [r"\bif i\b", r"\bwhen i\b", r"\babout to\b", r"\bwhat if\b"]
        return any(re.search(p, message, re.IGNORECASE) for p in hypothetical)

    def is_chat(self, message: str) -> bool:
        for signal in self.chat:
            if self._matches_pattern(signal, message):
                return True
        return False

    def is_event(self, message: str) -> bool:
        if self._is_hypothetical(message):
            return False
        for signal in self.rules:
            if self._matches_pattern(signal, message):
                return True
        return False

    def is_profile(self, message: str) -> bool:
        for signal in self.profile:
            if self._matches_pattern(signal, message):
                return True
        return False

    def is_ignore(self, message: str) -> bool:
        for signal in self.ignore:
            if self._matches_pattern(signal, message):
                return True
        return False

    def classify(self, message: str) -> str:
        norm_message = self.normalize(message)
        if self.is_ignore(norm_message):
            return "ignore"
        if self.is_profile(norm_message):
            return "profile"
        if self.is_chat(norm_message):
            return "chat"
        if self.is_event(norm_message):
            return "event"
        return "unknown"