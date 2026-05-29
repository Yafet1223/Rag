import os
import sys
import unittest
from datetime import datetime, timedelta

# Ensure project root is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Event.event import Event, parse_time
from Event.event_manager import EventManager


class TestEventAndManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configure a test database file
        cls.test_db_path = "test_store.sqlite"
        os.environ["SQLITE_DB_PATH"] = cls.test_db_path
        # Force SQLite fallback for predictable test environment
        cls.manager = EventManager()
        cls.manager.use_sqlite = True
        cls.manager.sqlite_db_path = cls.test_db_path
        cls.manager._init_sqlite_db()

    @classmethod
    def tearDownClass(cls):
        # Clean up database file after testing
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception as e:
                print(f"Error removing test database file: {e}")

    def setUp(self):
        # Clear database table before each test
        conn = self.manager._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM events;")
        finally:
            conn.close()

    def test_sleep_duration_calculations(self):
        # Test 1: Simple sleep duration across midnight
        ev1 = Event(
            user_id="test_user",
            event_type="sleep",
            sleep_time="11:00 PM",
            wake_time="6:30 AM"
        )
        self.assertEqual(ev1.calculate_sleep_duration(), 7.5)

        # Test 2: Standard 24h military times
        ev2 = Event(
            user_id="test_user",
            event_type="sleep",
            sleep_time="23:30",
            wake_time="07:30"
        )
        self.assertEqual(ev2.calculate_sleep_duration(), 8.0)

        # Test 3: Sleep same day (e.g. nap)
        ev3 = Event(
            user_id="test_user",
            event_type="sleep",
            sleep_time="1:00 PM",
            wake_time="3:15 PM"
        )
        self.assertEqual(ev3.calculate_sleep_duration(), 2.25)

        # Test 4: Parse edge cases (midnight, periods, no spaces)
        ev4 = Event(
            user_id="test_user",
            event_type="sleep",
            sleep_time="midnight",
            wake_time="6am"
        )
        self.assertEqual(ev4.calculate_sleep_duration(), 6.0)

    def test_event_crud_operations(self):
        # Create
        ev = Event(
            user_id="user_123",
            event_type="study",
            study_hours=3.5,
            mood="motivated",
            bible_read=True,
            prayer_done=True,
            notes="Studied Python and read Psalms.",
            tags="programming, religion",
            raw_message="I studied Python for 3.5 hours today and read the Bible. Feeling motivated!",
            metadata='{"energy_level": 4, "exercise_duration": 45}'
        )
        self.manager.add_event(ev)
        self.assertIsNotNone(ev.id)

        # Read
        all_events = self.manager.get_events("user_123")
        self.assertEqual(len(all_events), 1)
        self.assertEqual(all_events[0].study_hours, 3.5)
        self.assertEqual(all_events[0].mood, "motivated")
        self.assertEqual(all_events[0].bible_read, True)
        self.assertEqual(all_events[0].prayer_done, True)
        self.assertEqual(all_events[0].get_tags_list(), ["programming", "religion"])
        self.assertEqual(all_events[0].raw_message, "I studied Python for 3.5 hours today and read the Bible. Feeling motivated!")
        self.assertEqual(all_events[0].get_metadata_dict(), {"energy_level": 4, "exercise_duration": 45})

        # Update
        updated_ev = Event(
            user_id="user_123",
            event_type="study",
            study_hours=4.5,  # updated
            mood="exhausted",  # updated
            bible_read=True,
            prayer_done=True,
            notes="Finished hard advanced data engineering chapters.",
            tags="programming, extreme",
            raw_message="I studied Python for 4.5 hours today and read the Bible. Feeling exhausted!",
            metadata='{"energy_level": 2, "exercise_duration": 45}'
        )
        self.manager.update_event(ev.id, updated_ev)
        
        events_after_update = self.manager.get_events("user_123")
        self.assertEqual(len(events_after_update), 1)
        self.assertEqual(events_after_update[0].study_hours, 4.5)
        self.assertEqual(events_after_update[0].mood, "exhausted")
        self.assertEqual(events_after_update[0].raw_message, "I studied Python for 4.5 hours today and read the Bible. Feeling exhausted!")
        self.assertEqual(events_after_update[0].get_metadata_dict(), {"energy_level": 2, "exercise_duration": 45})

        # Delete
        self.manager.delete_event(ev.id)
        events_after_delete = self.manager.get_events("user_123")
        self.assertEqual(len(events_after_delete), 0)

    def test_filters_and_keyword_search(self):
        base_time = datetime.utcnow()
        ev1 = Event(
            user_id="filter_user",
            event_type="study",
            timestamp=base_time - timedelta(days=2),
            study_hours=2.0,
            notes="Calculus homework.",
            tags="math"
        )
        ev2 = Event(
            user_id="filter_user",
            event_type="sleep",
            timestamp=base_time - timedelta(days=1),
            sleep_time="10 PM",
            wake_time="6 AM",
            notes="Felt refreshed.",
            tags="health"
        )
        ev3 = Event(
            user_id="filter_user",
            event_type="spiritual",
            timestamp=base_time,
            bible_read=True,
            notes="Read Genesis chapter 1.",
            tags="spirituality"
        )
        self.manager.add_event(ev1)
        self.manager.add_event(ev2)
        self.manager.add_event(ev3)

        # Test date range filter
        in_range = self.manager.get_events_by_date_range(
            "filter_user", 
            base_time - timedelta(days=3), 
            base_time - timedelta(hours=12)
        )
        self.assertEqual(len(in_range), 2)
        self.assertEqual(in_range[0].event_type, "study")
        self.assertEqual(in_range[1].event_type, "sleep")

        # Test type filter
        study_events = self.manager.get_events_by_type("filter_user", "study")
        self.assertEqual(len(study_events), 1)
        self.assertEqual(study_events[0].notes, "Calculus homework.")

        # Test text keyword search
        search_res = self.manager.search_events_by_keyword("filter_user", "genesis")
        self.assertEqual(len(search_res), 1)
        self.assertEqual(search_res[0].event_type, "spiritual")

        search_refreshed = self.manager.search_events_by_keyword("filter_user", "refreshed")
        self.assertEqual(len(search_refreshed), 1)
        self.assertEqual(search_refreshed[0].event_type, "sleep")

        search_tag = self.manager.search_events_by_keyword("filter_user", "math")
        self.assertEqual(len(search_tag), 1)
        self.assertEqual(search_tag[0].event_type, "study")

    def test_behavioral_analytics_engine(self):
        base_time = datetime.utcnow()
        user_id = "analytics_user"

        # Log habits over past 5 days
        for i in range(5):
            day_time = base_time - timedelta(days=i)
            # Study on 3 of the days
            study_hours = 2.0 if i in [0, 2, 4] else None
            # Read bible on 4 of the days
            bible = True if i in [0, 1, 2, 3] else False
            mood = "focused" if i in [0, 2, 4] else "lazy"

            ev = Event(
                user_id=user_id,
                event_type="habit_log",
                timestamp=day_time,
                study_hours=study_hours,
                bible_read=bible,
                prayer_done=True,
                mood=mood,
                sleep_time="11:00 PM",
                wake_time="7:00 AM"
            )
            self.manager.add_event(ev)

        analytics = self.manager.get_behavioral_analytics(user_id, days=7)
        
        # Verify stats calculations
        self.assertEqual(analytics["total_logged_days"], 5)
        self.assertEqual(analytics["total_study_hours"], 6.0)
        self.assertEqual(analytics["avg_study_per_day"], 1.2) # 6 hours / 5 logged days
        self.assertEqual(analytics["study_consistency_percent"], 42.9) # 3 days out of 7 = 42.9%
        self.assertEqual(analytics["dominant_mood"], "focused")
        self.assertEqual(analytics["bible_reading_percent"], 80.0) # 4 / 5 days = 80.0%
        self.assertEqual(analytics["prayer_percent"], 100.0) # 5 / 5 days = 100.0%
        self.assertEqual(analytics["bible_streak_days"], 4) # 4 consecutive days from today/yesterday
        self.assertEqual(analytics["avg_sleep_duration_hours"], 8.0)
        
        # Ensure markdown summary exists and contains core values
        self.assertIn("Academic & Study Habits", analytics["summary_markdown"])
        self.assertIn("6.0 hours", analytics["summary_markdown"])
        self.assertIn("Dominant Mood", analytics["summary_markdown"])
        self.assertIn("Bible Reading Streak", analytics["summary_markdown"])


if __name__ == "__main__":
    unittest.main()
