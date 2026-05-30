import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Core.coaching_advisor import get_contextual_coaching, is_imminent_sleep
from Core.routing_hints import refine_route
from Event.event import Event
from Event.event_manager import EventManager
from Memory.Rulelayer.rulelayer import Rulelayer
from Profile.memory.profile_manager import ProfileManager
from Profile.models.user_profile import ExtractedProfileData, ProfileFact
from datetime import datetime


class TestCoachingAndRouting(unittest.TestCase):
    def test_rule_layer_conditional_is_profile(self):
        r = Rulelayer()
        msg = "if i sleep after midnight my headache starts tomorrow"
        self.assertEqual(r.classify(msg), "profile")

    def test_rule_layer_about_to_is_chat(self):
        r = Rulelayer()
        self.assertEqual(r.classify("hey i am about to sleep after midnight"), "chat")

    def test_refine_event_to_profile_for_conditional(self):
        cat, _ = refine_route("if i sleep late i feel bad", "event")
        self.assertEqual(cat, "profile")

    def test_refine_event_to_chat_for_imminent(self):
        cat, _ = refine_route("i am about to sleep after midnight", "event")
        self.assertEqual(cat, "chat")

    def test_coaching_from_stored_profile(self):
        db = "test_coaching.sqlite"
        os.environ["SQLITE_DB_PATH"] = db
        events = EventManager()
        events.use_sqlite = True
        events.sqlite_db_path = db
        events._init_sqlite_db()
        profiles = ProfileManager()
        profiles.use_sqlite = True
        profiles.sqlite_db_path = db
        profiles._init_sqlite_db()

        ext = ExtractedProfileData(
            statement="Sleeping after midnight causes headaches the next morning",
            topic="health",
            trait_type="weakness",
        )
        profiles.add_fact(
            ProfileFact.from_extraction(
                "u1",
                ext,
                raw_message="if i sleep after midnight my headache starts tomorrow",
            )
        )

        advice = get_contextual_coaching(
            "u1",
            "hey i am about to sleep after midnight",
            profiles,
            events,
        )
        self.assertIsNotNone(advice)
        self.assertIn("headache", advice.lower())

        if os.path.exists(db):
            os.remove(db)

    def test_imminent_sleep_detection(self):
        self.assertTrue(is_imminent_sleep("hey i am about to sleep after midnight"))


if __name__ == "__main__":
    unittest.main()
