import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Core.memory_context import build_memory_context
from Event.event import Event
from Event.event_manager import EventManager
from Profile.memory.profile_manager import ProfileManager
from Profile.models.user_profile import ExtractedProfileData, ProfileFact
from datetime import datetime


class TestMemoryContext(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_db = "test_orchestrator.sqlite"
        os.environ["SQLITE_DB_PATH"] = cls.test_db
        cls.events = EventManager()
        cls.events.use_sqlite = True
        cls.events.sqlite_db_path = cls.test_db
        cls.events._init_sqlite_db()
        cls.profiles = ProfileManager()
        cls.profiles.use_sqlite = True
        cls.profiles.sqlite_db_path = cls.test_db
        cls.profiles._init_sqlite_db()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

    def setUp(self):
        conn = self.events._get_connection()
        with conn:
            conn.execute("DELETE FROM events;")
            conn.execute("DELETE FROM profile_facts;")
        conn.close()

    def test_build_memory_context_includes_profile_and_events(self):
        self.events.add_event(
            Event(
                user_id="u1",
                event_type="study",
                timestamp=datetime.utcnow(),
                study_hours=2.0,
                mood="focused",
            )
        )
        ext = ExtractedProfileData(
            statement="Prefers night study",
            topic="productivity",
            trait_type="preference",
        )
        self.profiles.add_fact(ProfileFact.from_extraction("u1", ext))

        ctx = build_memory_context("u1", self.events, self.profiles)
        self.assertIn("Behavioral Insights", ctx)
        self.assertIn("User Profile", ctx)
        self.assertIn("Prefers night study", ctx)
        self.assertIn("study", ctx.lower())


if __name__ == "__main__":
    unittest.main()
