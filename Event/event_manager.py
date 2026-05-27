import os
import psycopg2
from psycopg2.extras import RealDictCursor
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
        
        # Connect to DB and initialize the schema
        self._init_db()

    def _get_connection(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password
        )

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
                        notes TEXT
                    );
                """)
                conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[EventManager] Database initialization warning/error: {e}")
            print(f"[EventManager] Attempting to auto-create database '{self.dbname}'...")
            self._create_database_if_not_exists()
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
                        notes TEXT
                    );
                """)
                conn2.commit()
                conn2.close()
        except Exception as ex:
            print(f"[EventManager] Critical: Failed to auto-create database or tables: {ex}")
            if conn:
                conn.close()

    # -------------------------
    # Add event
    # -------------------------

    def add_event(self, event: Event):
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO events (
                        user_id, event_type, timestamp, study_hours, mood,
                        bible_read, prayer_done, sleep_time, wake_time, notes
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    event.user_id,
                    event.event_type,
                    event.timestamp,
                    event.study_hours,
                    event.mood,
                    event.bible_read,
                    event.prayer_done,
                    event.sleep_time,
                    event.wake_time,
                    event.notes
                ))
                conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"[EventManager] Error adding event: {e}")
            raise e
        finally:
            conn.close()

    # -------------------------
    # Get all events
    # -------------------------

    def get_events(self, user_id: str):
        conn = self._get_connection()
        events = []
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT user_id, event_type, timestamp, study_hours, mood,
                           bible_read, prayer_done, sleep_time, wake_time, notes
                    FROM events
                    WHERE user_id = %s
                    ORDER BY timestamp ASC;
                """, (user_id,))
                rows = cur.fetchall()
                for row in rows:
                    events.append(Event(**row))
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
        events = []
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT user_id, event_type, timestamp, study_hours, mood,
                           bible_read, prayer_done, sleep_time, wake_time, notes
                    FROM events
                    WHERE user_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s;
                """, (user_id, limit))
                rows = cur.fetchall()
                for row in rows:
                    events.append(Event(**row))
        except Exception as e:
            print(f"[EventManager] Error getting recent events: {e}")
        finally:
            conn.close()
        return events