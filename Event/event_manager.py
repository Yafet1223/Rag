import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from .event import Event

load_dotenv()


class EventManager:

    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.dbname = os.getenv("DB_NAME", "rag_memory")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "password")
        self.use_sqlite = False
        self.sqlite_db_path = os.getenv("SQLITE_DB_PATH", "store_db.sqlite")
        
        # Connect to DB and initialize the schema
        self._init_db()

    def _get_connection(self):
        if self.use_sqlite:
            conn = sqlite3.connect(self.sqlite_db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row
            return conn
        else:
            return psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )

    def _prepare_query(self, query: str) -> str:
        """Adapts the SQL query parameter placeholders to SQLite format if fallback is active."""
        if self.use_sqlite:
            return query.replace("%s", "?")
        return query

    def _init_db(self):
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(100) NOT NULL,
                        event_type VARCHAR(100) NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        study_hours DOUBLE PRECISION,
                        mood VARCHAR(100),
                        bible_read BOOLEAN,
                        prayer_done BOOLEAN,
                        sleep_time VARCHAR(50),
                        wake_time VARCHAR(50),
                        notes TEXT,
                        tags TEXT,
                        raw_message TEXT,
                        metadata TEXT
                    );
                """)
                conn.commit()
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            print(f"[EventManager] PostgreSQL initialization warning/error: {e}")
            if not self.use_sqlite:
                print(f"[EventManager] Attempting to auto-create database '{self.dbname}'...")
                try:
                    self._create_database_if_not_exists()
                except Exception as ex:
                    print(f"[EventManager] Failed to configure PostgreSQL: {ex}. Falling back to SQLite...")
                    self.use_sqlite = True
                    self._init_sqlite_db()
            else:
                self._init_sqlite_db()
        finally:
            if conn:
                conn.close()

    def _create_database_if_not_exists(self):
        conn = None
        try:
            # Connect to default 'postgres' database first to execute CREATE DATABASE
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname="postgres",
                user=self.user,
                password=self.password
            )
            conn.autocommit = True
            with conn.cursor() as cur:
                # Check if the target database already exists
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (self.dbname,))
                exists = cur.fetchone()
                if not exists:
                    cur.execute(f'CREATE DATABASE "{self.dbname}";')
                    print(f"[EventManager] Database '{self.dbname}' created successfully!")
            
            # Now retry initializing the schema in the newly created database
            conn2 = self._get_connection()
            with conn2.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(100) NOT NULL,
                        event_type VARCHAR(100) NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        study_hours DOUBLE PRECISION,
                        mood VARCHAR(100),
                        bible_read BOOLEAN,
                        prayer_done BOOLEAN,
                        sleep_time VARCHAR(50),
                        wake_time VARCHAR(50),
                        notes TEXT,
                        tags TEXT,
                        raw_message TEXT,
                        metadata TEXT
                    );
                """)
                conn2.commit()
                conn2.close()
        except Exception as ex:
            print(f"[EventManager] Critical: Failed to auto-create database or tables: {ex}")
            if conn:
                conn.close()
            # If everything Postgres fails, fall back to SQLite
            print("[EventManager] PostgreSQL connection completely failed. Falling back to SQLite...")
            self.use_sqlite = True
            self._init_sqlite_db()

    def _init_sqlite_db(self):
        conn = sqlite3.connect(self.sqlite_db_path)
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        study_hours REAL,
                        mood TEXT,
                        bible_read BOOLEAN,
                        prayer_done BOOLEAN,
                        sleep_time TEXT,
                        wake_time TEXT,
                        notes TEXT,
                        tags TEXT,
                        raw_message TEXT,
                        metadata TEXT
                    );
                """)
            print(f"[EventManager] SQLite database initialized successfully at: {self.sqlite_db_path}")
        except Exception as e:
            print(f"[EventManager] Critical SQLite initialization error: {e}")
        finally:
            conn.close()

    def _row_to_event(self, row) -> Event:
        data = dict(row)
        if isinstance(data.get("timestamp"), str):
            try:
                ts_str = data["timestamp"]
                if ts_str.endswith("Z"):
                    ts_str = ts_str[:-1] + "+00:00"
                data["timestamp"] = datetime.fromisoformat(ts_str)
            except ValueError:
                data["timestamp"] = datetime.utcnow()
        
        # Convert boolean-like values for SQLite
        if isinstance(data.get("bible_read"), int):
            data["bible_read"] = bool(data["bible_read"])
        if isinstance(data.get("prayer_done"), int):
            data["prayer_done"] = bool(data["prayer_done"])
            
        return Event(**data)

    # -------------------------
    # Add event
    # -------------------------

    def add_event(self, event: Event):
        conn = self._get_connection()
        query = """
            INSERT INTO events (
                user_id, event_type, timestamp, study_hours, mood,
                bible_read, prayer_done, sleep_time, wake_time, notes, tags,
                raw_message, metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        query = self._prepare_query(query)
        ts = event.timestamp.isoformat() if self.use_sqlite else event.timestamp
        try:
            if self.use_sqlite:
                with conn:
                    cursor = conn.execute(query, (
                        event.user_id,
                        event.event_type,
                        ts,
                        event.study_hours,
                        event.mood,
                        event.bible_read,
                        event.prayer_done,
                        event.sleep_time,
                        event.wake_time,
                        event.notes,
                        event.tags,
                        event.raw_message,
                        event.metadata
                    ))
                    event.id = cursor.lastrowid
            else:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query + " RETURNING id;", (
                        event.user_id,
                        event.event_type,
                        ts,
                        event.study_hours,
                        event.mood,
                        event.bible_read,
                        event.prayer_done,
                        event.sleep_time,
                        event.wake_time,
                        event.notes,
                        event.tags,
                        event.raw_message,
                        event.metadata
                    ))
                    row = cur.fetchone()
                    if row:
                        event.id = row["id"]
                conn.commit()
        except Exception as e:
            if not self.use_sqlite:
                conn.rollback()
            print(f"[EventManager] Error adding event: {e}")
            raise e
        finally:
            conn.close()

    # -------------------------
    # Update event
    # -------------------------

    def update_event(self, event_id: int, updated_event: Event):
        conn = self._get_connection()
        query = """
            UPDATE events SET
                event_type = %s,
                timestamp = %s,
                study_hours = %s,
                mood = %s,
                bible_read = %s,
                prayer_done = %s,
                sleep_time = %s,
                wake_time = %s,
                notes = %s,
                tags = %s,
                raw_message = %s,
                metadata = %s
            WHERE id = %s;
        """
        query = self._prepare_query(query)
        ts = updated_event.timestamp.isoformat() if self.use_sqlite else updated_event.timestamp
        try:
            if self.use_sqlite:
                with conn:
                    conn.execute(query, (
                        updated_event.event_type,
                        ts,
                        updated_event.study_hours,
                        updated_event.mood,
                        updated_event.bible_read,
                        updated_event.prayer_done,
                        updated_event.sleep_time,
                        updated_event.wake_time,
                        updated_event.notes,
                        updated_event.tags,
                        updated_event.raw_message,
                        updated_event.metadata,
                        event_id
                    ))
            else:
                with conn.cursor() as cur:
                    cur.execute(query, (
                        updated_event.event_type,
                        ts,
                        updated_event.study_hours,
                        updated_event.mood,
                        updated_event.bible_read,
                        updated_event.prayer_done,
                        updated_event.sleep_time,
                        updated_event.wake_time,
                        updated_event.notes,
                        updated_event.tags,
                        updated_event.raw_message,
                        updated_event.metadata,
                        event_id
                    ))
                conn.commit()
        except Exception as e:
            if not self.use_sqlite:
                conn.rollback()
            print(f"[EventManager] Error updating event: {e}")
            raise e
        finally:
            conn.close()

    # -------------------------
    # Delete event
    # -------------------------

    def delete_event(self, event_id: int):
        conn = self._get_connection()
        query = "DELETE FROM events WHERE id = %s;"
        query = self._prepare_query(query)
        try:
            if self.use_sqlite:
                with conn:
                    conn.execute(query, (event_id,))
            else:
                with conn.cursor() as cur:
                    cur.execute(query, (event_id,))
                conn.commit()
        except Exception as e:
            if not self.use_sqlite:
                conn.rollback()
            print(f"[EventManager] Error deleting event: {e}")
            raise e
        finally:
            conn.close()

    # -------------------------
    # Get all events
    # -------------------------

    def get_events(self, user_id: str):
        conn = self._get_connection()
        query = """
            SELECT id, user_id, event_type, timestamp, study_hours, mood,
                   bible_read, prayer_done, sleep_time, wake_time, notes, tags,
                   raw_message, metadata
            FROM events
            WHERE user_id = %s
            ORDER BY timestamp ASC;
        """
        query = self._prepare_query(query)
        events = []
        try:
            if self.use_sqlite:
                cursor = conn.execute(query, (user_id,))
                rows = cursor.fetchall()
            else:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, (user_id,))
                    rows = cur.fetchall()
            for row in rows:
                events.append(self._row_to_event(row))
        except Exception as e:
            print(f"[EventManager] Error getting events: {e}")
        finally:
            conn.close()
        return events

    # -------------------------
    # Get recent events
    # -------------------------

    def get_recent_events(self, user_id: str, limit: int = 5):
        conn = self._get_connection()
        query = """
            SELECT id, user_id, event_type, timestamp, study_hours, mood,
                   bible_read, prayer_done, sleep_time, wake_time, notes, tags,
                   raw_message, metadata
            FROM events
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT %s;
        """
        query = self._prepare_query(query)
        events = []
        try:
            if self.use_sqlite:
                cursor = conn.execute(query, (user_id, limit))
                rows = cursor.fetchall()
            else:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, (user_id, limit))
                    rows = cur.fetchall()
            for row in rows:
                events.append(self._row_to_event(row))
        except Exception as e:
            print(f"[EventManager] Error getting recent events: {e}")
        finally:
            conn.close()
        return events

    # -------------------------
    # Get events by date range
    # -------------------------

    def get_events_by_date_range(self, user_id: str, start_date: datetime, end_date: datetime):
        conn = self._get_connection()
        query = """
            SELECT id, user_id, event_type, timestamp, study_hours, mood,
                   bible_read, prayer_done, sleep_time, wake_time, notes, tags,
                   raw_message, metadata
            FROM events
            WHERE user_id = %s AND timestamp >= %s AND timestamp <= %s
            ORDER BY timestamp ASC;
        """
        query = self._prepare_query(query)
        start_val = start_date.isoformat() if self.use_sqlite else start_date
        end_val = end_date.isoformat() if self.use_sqlite else end_date
        events = []
        try:
            if self.use_sqlite:
                cursor = conn.execute(query, (user_id, start_val, end_val))
                rows = cursor.fetchall()
            else:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, (user_id, start_val, end_val))
                    rows = cur.fetchall()
            for row in rows:
                events.append(self._row_to_event(row))
        except Exception as e:
            print(f"[EventManager] Error getting events by date range: {e}")
        finally:
            conn.close()
        return events

    # -------------------------
    # Get events by type
    # -------------------------

    def get_events_by_type(self, user_id: str, event_type: str, limit: int = 100):
        conn = self._get_connection()
        query = """
            SELECT id, user_id, event_type, timestamp, study_hours, mood,
                   bible_read, prayer_done, sleep_time, wake_time, notes, tags,
                   raw_message, metadata
            FROM events
            WHERE user_id = %s AND event_type = %s
            ORDER BY timestamp DESC
            LIMIT %s;
        """
        query = self._prepare_query(query)
        events = []
        try:
            if self.use_sqlite:
                cursor = conn.execute(query, (user_id, event_type, limit))
                rows = cursor.fetchall()
            else:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, (user_id, event_type, limit))
                    rows = cur.fetchall()
            for row in rows:
                events.append(self._row_to_event(row))
        except Exception as e:
            print(f"[EventManager] Error getting events by type: {e}")
        finally:
            conn.close()
        return events

    # -------------------------
    # Search events by keyword
    # -------------------------

    def search_events_by_keyword(self, user_id: str, query_text: str, limit: int = 10):
        conn = self._get_connection()
        query = """
            SELECT id, user_id, event_type, timestamp, study_hours, mood,
                   bible_read, prayer_done, sleep_time, wake_time, notes, tags,
                   raw_message, metadata
            FROM events
            WHERE user_id = %s AND (notes ILIKE %s OR event_type ILIKE %s OR tags ILIKE %s OR raw_message ILIKE %s)
            ORDER BY timestamp DESC
            LIMIT %s;
        """
        if self.use_sqlite:
            query = query.replace("ILIKE", "LIKE")
        query = self._prepare_query(query)
        like_pattern = f"%{query_text}%"
        events = []
        try:
            if self.use_sqlite:
                cursor = conn.execute(query, (user_id, like_pattern, like_pattern, like_pattern, like_pattern, limit))
                rows = cursor.fetchall()
            else:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, (user_id, like_pattern, like_pattern, like_pattern, like_pattern, limit))
                    rows = cur.fetchall()
            for row in rows:
                events.append(self._row_to_event(row))
        except Exception as e:
            print(f"[EventManager] Error searching events: {e}")
        finally:
            conn.close()
        return events

    # -------------------------
    # Behavioral Habit Analytics
    # -------------------------

    def get_behavioral_analytics(self, user_id: str, days: int = 30) -> dict:
        """Computes comprehensive behavioral analytics for the user over the past N days."""
        from datetime import timedelta, date
        from collections import Counter
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        events = self.get_events_by_date_range(user_id, start_date, end_date)
        if not events:
            return {
                "period_days": days,
                "total_events": 0,
                "summary_markdown": f"### 📊 Behavioral Insights & Habit Analysis (Past {days} Days)\nNo events logged in the past period to analyze. Tell me what you've been up to!"
            }
            
        # Group events by calendar date to avoid double counting per day
        events_by_date = {}
        for ev in events:
            ev_date = ev.timestamp.date()
            if ev_date not in events_by_date:
                events_by_date[ev_date] = []
            events_by_date[ev_date].append(ev)
            
        total_logged_days = len(events_by_date)
        
        # 1. Study analytics
        study_days = 0
        total_study_hours = 0.0
        study_hours_by_day = {}
        
        # 2. Mood analytics
        moods = []
        mood_study_map = {} # mood -> list of study hours
        
        # 3. Spiritual practices
        bible_reads = 0
        prayers_done = 0
        bible_days = set()
        
        # 4. Sleep analytics
        sleep_durations = []
        bed_times = []
        wake_times = []
        
        for d, day_events in events_by_date.items():
            day_study = 0.0
            day_moods = []
            day_bible = False
            day_prayer = False
            
            for ev in day_events:
                if ev.study_hours is not None:
                    day_study += ev.study_hours
                if ev.mood:
                    day_moods.append(ev.mood)
                if ev.bible_read:
                    day_bible = True
                    bible_days.add(d)
                if ev.prayer_done:
                    day_prayer = True
                
                duration = ev.calculate_sleep_duration()
                if duration is not None:
                    sleep_durations.append(duration)
                if ev.sleep_time:
                    bed_times.append(ev.sleep_time)
                if ev.wake_time:
                    wake_times.append(ev.wake_time)
                    
            if day_study > 0:
                study_days += 1
                total_study_hours += day_study
                study_hours_by_day[d] = day_study
                
            if day_moods:
                # Use the last mood reported in the day
                primary_mood = day_moods[-1]
                moods.append(primary_mood)
                if primary_mood not in mood_study_map:
                    mood_study_map[primary_mood] = []
                mood_study_map[primary_mood].append(day_study)
                
            if day_bible:
                bible_reads += 1
            if day_prayer:
                prayers_done += 1
                
        # Calculate streaks for Bible reading
        # Let's count consecutive days up to today
        bible_streak = 0
        today = datetime.utcnow().date()
        check_date = today
        # If not read today, check starting yesterday
        if check_date not in bible_days:
            check_date -= timedelta(days=1)
            
        while check_date in bible_days:
            bible_streak += 1
            check_date -= timedelta(days=1)
            
        # Summarize analytics
        avg_study_per_logged_day = round(total_study_hours / total_logged_days, 2) if total_logged_days > 0 else 0
        avg_study_per_study_day = round(total_study_hours / study_days, 2) if study_days > 0 else 0
        study_consistency = round((study_days / days) * 100, 1)
        
        mood_counter = Counter(moods)
        most_frequent_mood = mood_counter.most_common(1)[0][0] if moods else None
        
        avg_study_by_mood = {}
        for m, hours_list in mood_study_map.items():
            avg_study_by_mood[m] = round(sum(hours_list) / len(hours_list), 2)
            
        bible_consistency = round((bible_reads / total_logged_days) * 100, 1) if total_logged_days > 0 else 0
        prayer_consistency = round((prayers_done / total_logged_days) * 100, 1) if total_logged_days > 0 else 0
        
        avg_sleep_duration = round(sum(sleep_durations) / len(sleep_durations), 2) if sleep_durations else None
        
        # Format a beautifully readable Markdown summary that the LLM can use as system prompt context!
        summary_md = f"""### 📊 Behavioral Insights & Habit Analysis (Past {days} Days)
* **General Activity**: Logged {len(events)} events across {total_logged_days} distinct days.

#### 📚 Academic & Study Habits:
* **Total Study Time**: {total_study_hours} hours.
* **Averages**: {avg_study_per_logged_day} hours/day overall ({avg_study_per_study_day} hours on days you actually studied).
* **Consistency**: Studied on {study_days} out of {days} days ({study_consistency}% consistency).

#### 🎭 Mood & Emotional Trends:
* **Dominant Mood**: '{most_frequent_mood or "Unknown"}' (reported {mood_counter[most_frequent_mood]} times).
* **Mood Distribution**: {dict(mood_counter)}
* **Study & Mood Correlation**:
"""
        if avg_study_by_mood:
            for m, h in avg_study_by_mood.items():
                summary_md += f"  - When in a **{m}** mood, you studied an average of {h} hours.\n"
        else:
            summary_md += "  - (Not enough study and mood data to correlate yet).\n"
            
        summary_md += f"""
#### ⛪ Spiritual Practice:
* **Bible Reading Rate**: Read Bible on {bible_reads} out of {total_logged_days} logged days ({bible_consistency}%).
* **Prayer Rate**: Prayed on {prayers_done} out of {total_logged_days} logged days ({prayer_consistency}%).
* **Current Bible Reading Streak**: {bible_streak} consecutive days! 🔥

#### 😴 Sleep & Rest Patterns:
* **Average Sleep Duration**: {avg_sleep_duration or 'N/A'} hours per night.
"""
        if bed_times or wake_times:
            summary_md += f"* **Recorded Bedtimes**: {', '.join(bed_times[-5:])}\n"
            summary_md += f"* **Recorded Waketimes**: {', '.join(wake_times[-5:])}\n"
            
        return {
            "period_days": days,
            "total_events": len(events),
            "total_logged_days": total_logged_days,
            "total_study_hours": total_study_hours,
            "avg_study_per_day": avg_study_per_logged_day,
            "study_consistency_percent": study_consistency,
            "dominant_mood": most_frequent_mood,
            "mood_distribution": dict(mood_counter),
            "study_by_mood": avg_study_by_mood,
            "bible_reading_percent": bible_consistency,
            "prayer_percent": prayer_consistency,
            "bible_streak_days": bible_streak,
            "avg_sleep_duration_hours": avg_sleep_duration,
            "summary_markdown": summary_md
        }