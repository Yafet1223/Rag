import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from google import genai

from Core.chat_handler import ChatHandler
from Core.coaching_advisor import get_contextual_coaching, is_imminent_sleep
from Core.routing_hints import refine_route
from Event.event import Event
from Event.event_extractor import extract_event_with_ai
from Event.event_manager import EventManager
from Memory.Rulelayer.airouter import AIRouter
from Memory.Rulelayer.hybridrouter import HybridRouter
from Memory.Rulelayer.rulelayer import Rulelayer
from Profile.memory.profile_manager import ProfileManager
from Profile.models.user_profile import ProfileFact
from Profile.profile_extractor import extract_profile_with_ai


@dataclass
class OrchestratorResult:
    route_type: str
    source: str
    reason: str
    confidence: float
    action: str
    message: str = ""
    data: dict = field(default_factory=dict)


class MemoryOrchestrator:
    """
    Single entry point: classify message → event / profile / chat / ignore.
    """

    def __init__(
        self,
        *,
        client: Optional[genai.Client] = None,
        event_manager: Optional[EventManager] = None,
        profile_manager: Optional[ProfileManager] = None,
        model: str = "gemini-2.5-flash",
    ):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment or .env")

        self.client = client or genai.Client(api_key=api_key)
        self.model = model
        self.event_manager = event_manager or EventManager()
        self.profile_manager = profile_manager or ProfileManager()

        rule_layer = Rulelayer()
        ai_router = AIRouter(client=self.client, model=model)
        self.hybrid_router = HybridRouter(rule_layer=rule_layer, ai_router=ai_router)
        self.chat_handler = ChatHandler(
            self.client,
            self.event_manager,
            self.profile_manager,
            model=model,
        )

    def process_message(self, user_id: str, message: str) -> OrchestratorResult:
        route = self.hybrid_router.classify(message)
        category = route["type"]
        category, refine_suffix = refine_route(message, category)
        if refine_suffix:
            route["reason"] = (route.get("reason") or "") + refine_suffix
            route["type"] = category

        base = {
            "route_type": category,
            "source": route.get("source", "unknown"),
            "reason": route.get("reason", ""),
            "confidence": route.get("confidence", 0.0),
        }

        coaching = get_contextual_coaching(
            user_id, message, self.profile_manager, self.event_manager
        )
        if coaching and is_imminent_sleep(message):
            reply = self.chat_handler.reply(user_id, message)
            return OrchestratorResult(
                **base,
                route_type="chat",
                action="chat_reply",
                message=reply,
                data={"response": reply, "coaching_hint": coaching},
            )

        if category == "event":
            event_data = self._save_event(user_id, message)
            msg = self._build_save_message(user_id, message, coaching, "event")
            return OrchestratorResult(
                **base,
                action="event_saved",
                message=msg,
                data={"event": event_data},
            )

        if category == "profile":
            profile_data = self._save_profile(user_id, message)
            msg = self._build_save_message(user_id, message, coaching, "profile")
            return OrchestratorResult(
                **base,
                action="profile_saved",
                message=msg,
                data={"profile": profile_data},
            )

        if category == "ignore":
            return OrchestratorResult(
                **base,
                action="ignored",
                message="Message ignored (low memory value).",
            )

        # chat (default conversational path)
        reply = self.chat_handler.reply(user_id, message)
        return OrchestratorResult(
            **base,
            action="chat_reply",
            message=reply,
            data={"response": reply},
        )

    def query_memory(self, user_id: str, question: str) -> str:
        return self.chat_handler.query_memory(user_id, question)

    def _save_event(self, user_id: str, message: str) -> dict:
        extracted = extract_event_with_ai(self.client, message, model=self.model)
        db_event = Event(
            user_id=user_id,
            event_type=extracted.event_type,
            timestamp=datetime.utcnow(),
            study_hours=extracted.study_hours,
            mood=extracted.mood,
            bible_read=extracted.bible_read,
            prayer_done=extracted.prayer_done,
            sleep_time=extracted.sleep_time,
            wake_time=extracted.wake_time,
            notes=extracted.notes,
            raw_message=message,
            metadata=extracted.model_dump_json(),
        )
        self.event_manager.add_event(db_event)
        return db_event.model_dump(mode="json", exclude_none=True)

    def _build_save_message(
        self,
        user_id: str,
        message: str,
        coaching: Optional[str],
        kind: str,
    ) -> str:
        if coaching:
            return coaching
        if kind == "profile":
            return (
                "Got it — I saved that as a personal rule in your profile. "
                "I’ll use it when you ask for advice."
            )
        return "Event logged to memory."

    def _save_profile(self, user_id: str, message: str) -> dict:
        extracted = extract_profile_with_ai(self.client, message, model=self.model)
        db_fact = ProfileFact.from_extraction(
            user_id=user_id,
            extracted=extracted,
            raw_message=message,
        )
        self.profile_manager.add_fact(db_fact)
        return db_fact.model_dump(mode="json", exclude_none=True)

    def to_dict(self, result: OrchestratorResult) -> dict[str, Any]:
        return {
            "route": {
                "type": result.route_type,
                "source": result.source,
                "reason": result.reason,
                "confidence": result.confidence,
            },
            "action": result.action,
            "message": result.message,
            "data": result.data,
        }
