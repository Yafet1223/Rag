import os
import sys
import unittest
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Profile.models.user_profile import ExtractedProfileData, ProfileFact
from Profile.memory.profile_manager import ProfileManager


class TestProfileAndManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_db_path = "test_profile_store.sqlite"
        os.environ["SQLITE_DB_PATH"] = cls.test_db_path
        cls.manager = ProfileManager()
        cls.manager.use_sqlite = True
        cls.manager.sqlite_db_path = cls.test_db_path
        cls.manager._init_sqlite_db()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except OSError as e:
                print(f"Error removing test database file: {e}")

    def setUp(self):
        conn = self.manager._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM profile_facts;")
        finally:
            conn.close()

    def test_from_extraction_polarity_defaults(self):
        extracted = ExtractedProfileData(
            statement="Struggles to focus in noisy rooms",
            topic="productivity",
            trait_type="weakness",
            confidence=0.95,
        )
        fact = ProfileFact.from_extraction("user_1", extracted, raw_message="I struggle with focus")
        self.assertEqual(fact.polarity, "negative")
        self.assertEqual(fact.statement, "Struggles to focus in noisy rooms")

    def test_profile_crud_and_search(self):
        fact = ProfileFact(
            user_id="user_123",
            statement="Prefers studying late at night",
            topic="productivity",
            trait_type="preference",
            polarity="neutral",
            confidence=0.9,
            raw_message="I prefer studying late at night",
        )
        self.manager.add_fact(fact)
        self.assertIsNotNone(fact.id)

        all_facts = self.manager.get_facts("user_123")
        self.assertEqual(len(all_facts), 1)
        self.assertEqual(all_facts[0].statement, "Prefers studying late at night")

        by_topic = self.manager.get_facts_by_topic("user_123", "productivity")
        self.assertEqual(len(by_topic), 1)

        hits = self.manager.search_facts("user_123", "late")
        self.assertEqual(len(hits), 1)

        updated = ProfileFact(
            user_id="user_123",
            statement="Prefers studying after 10 PM",
            topic="productivity",
            trait_type="habit",
            polarity="neutral",
            confidence=1.0,
        )
        self.manager.update_fact(fact.id, updated)
        refreshed = self.manager.get_facts("user_123")[0]
        self.assertEqual(refreshed.trait_type, "habit")
        self.assertIn("10 PM", refreshed.statement)

        self.manager.deactivate_fact(fact.id)
        active_only = self.manager.get_facts("user_123", active_only=True)
        self.assertEqual(len(active_only), 0)
        all_including_inactive = self.manager.get_facts("user_123", active_only=False)
        self.assertEqual(len(all_including_inactive), 1)

        self.manager.delete_fact(fact.id)
        self.assertEqual(len(self.manager.get_facts("user_123", active_only=False)), 0)

    def test_profile_summary_markdown(self):
        samples = [
            ProfileFact(
                user_id="coach_user",
                statement="Good at breaking tasks into small steps",
                topic="productivity",
                trait_type="strength",
            ),
            ProfileFact(
                user_id="coach_user",
                statement="Struggles with morning routines",
                topic="lifestyle",
                trait_type="weakness",
            ),
            ProfileFact(
                user_id="coach_user",
                statement="Wants to read the Bible daily",
                topic="spirituality",
                trait_type="goal",
            ),
        ]
        for sample in samples:
            self.manager.add_fact(sample)

        summary = self.manager.get_profile_summary("coach_user")
        self.assertEqual(summary["total_facts"], 3)
        self.assertIn("Strengths", summary["summary_markdown"])
        self.assertIn("Growth areas", summary["summary_markdown"])
        self.assertIn("Stated goals", summary["summary_markdown"])
        self.assertEqual(len(summary["strengths"]), 1)
        self.assertEqual(len(summary["weaknesses"]), 1)
        self.assertEqual(len(summary["goals"]), 1)


if __name__ == "__main__":
    unittest.main()
