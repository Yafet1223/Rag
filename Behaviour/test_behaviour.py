import os
import sys
import unittest
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Behaviour.behaviour import BehaviourAnalyzer
from Event.event import Event
from Event.event_manager import EventManager
from Profile.memory.profile_manager import ProfileManager
from Profile.models.user_profile import ExtractedProfileData, ProfileFact


class TestBehaviourAnalyzer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_db = "test_behaviour.sqlite"
        os.environ["SQLITE_DB_PATH"] = cls.test_db
        cls.events = EventManager()
        cls.events.use_sqlite = True
        cls.events.sqlite_db_path = cls.test_db
        cls.events._init_sqlite_db()
        cls.profiles = ProfileManager()
        cls.profiles.use_sqlite = True
        cls.profiles.sqlite_db_path = cls.test_db
        cls.profiles._init_sqlite_db()
        cls.analyzer = BehaviourAnalyzer(cls.events, cls.profiles)

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

    def test_empty_state_recommends_logging(self):
        result = self.analyzer.analyze("u1", days=30)
        self.assertGreater(len(result["recommendations"]), 0)
        self.assertIn("Behaviour", result["summary_markdown"])

    def test_profile_without_events_surfaces_gap(self):
        ext = ExtractedProfileData(
            statement="Prefers studying at night",
            topic="productivity",
            trait_type="preference",
        )
        self.profiles.add_fact(ProfileFact.from_extraction("u1", ext))
        result = self.analyzer.analyze("u1", days=30)
        self.assertTrue(any("profile" in g.lower() or "event" in g.lower() for g in result["gaps"]))

    def test_study_events_with_profile_alignment(self):
        self.profiles.add_fact(
            ProfileFact.from_extraction(
                "u1",
                ExtractedProfileData(
                    statement="Likes to study daily",
                    topic="productivity",
                    trait_type="habit",
                ),
            )
        )
        for _ in range(5):
            self.events.add_event(
                Event(
                    user_id="u1",
                    event_type="study",
                    timestamp=datetime.utcnow(),
                    study_hours=2.0,
                )
            )
        result = self.analyzer.analyze("u1", days=30)
        self.assertGreater(result["total_events"], 0)


if __name__ == "__main__":
    unittest.main()
