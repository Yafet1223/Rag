import os
import sqlite3
from collections import Counter
from datetime import datetime
from typing import List, Optional

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

from Profile.models.user_profile import ProfileFact, ProfileTopic, ProfileTraitType

load_dotenv()


class ProfileManager:
    """Persists long-term user profile facts (preferences, habits, traits)."""

    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.dbname = os.getenv("DB_NAME", "rag_memory")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "password")
        self.use_sqlite = False
        self.sqlite_db_path = os.getenv("SQLITE_DB_PATH", "store_db.sqlite")
        self._init_db()

    def _get_connection(self):
        if self.use_sqlite:
            conn = sqlite3.connect(self.sqlite_db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row
            return conn
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )

    def _prepare_query(self, query: str) -> str:
        if self.use_sqlite:
            return query.replace("%s", "?")
        return query

    def _profiles_table_sql(self) -> str:
        if self.use_sqlite:
            return """
                CREATE TABLE IF NOT EXISTS profile_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    statement TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    trait_type TEXT NOT NULL,
                    polarity TEXT,
                    confidence REAL NOT NULL DEFAULT 1.0,
                    raw_message TEXT,
                    source TEXT NOT NULL DEFAULT 'user_stated',
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    metadata TEXT
                );
            """
        return """
            CREATE TABLE IF NOT EXISTS profile_facts (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                statement TEXT NOT NULL,
                topic VARCHAR(50) NOT NULL,
                trait_type VARCHAR(50) NOT NULL,
                polarity VARCHAR(20),
                confidence DOUBLE PRECISION NOT NULL DEFAULT 1.0,
                raw_message TEXT,
                source VARCHAR(50) NOT NULL DEFAULT 'user_stated',
                active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE,
                metadata TEXT
            );
        """

    def _init_db(self):
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute(self._profiles_table_sql())
            conn.commit()
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            print(f"[ProfileManager] PostgreSQL initialization warning/error: {e}")
            if not self.use_sqlite:
                print("[ProfileManager] Falling back to SQLite...")
                self.use_sqlite = True
                self._init_sqlite_db()
            else:
                self._init_sqlite_db()
        finally:
            if conn:
                conn.close()

    def _init_sqlite_db(self):
        conn = sqlite3.connect(self.sqlite_db_path)
        try:
            with conn:
                conn.execute(self._profiles_table_sql())
            print(
                f"[ProfileManager] SQLite database initialized successfully at: {self.sqlite_db_path}"
            )
        except Exception as e:
            print(f"[ProfileManager] Critical SQLite initialization error: {e}")
        finally:
            conn.close()

    def _row_to_profile(self, row) -> ProfileFact:
        data = dict(row)
        for field in ("created_at", "updated_at"):
            if isinstance(data.get(field), str):
                try:
                    ts_str = data[field]
                    if ts_str and ts_str.endswith("Z"):
                        ts_str = ts_str[:-1] + "+00:00"
                    data[field] = datetime.fromisoformat(ts_str) if ts_str else None
                except ValueError:
                    if field == "created_at":
                        data[field] = datetime.utcnow()
        if isinstance(data.get("active"), int):
            data["active"] = bool(data["active"])
        return ProfileFact(**data)

    def add_fact(self, fact: ProfileFact) -> ProfileFact:
        conn = self._get_connection()
        query = """
            INSERT INTO profile_facts (
                user_id, statement, topic, trait_type, polarity, confidence,
                raw_message, source, active, created_at, updated_at, metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        query = self._prepare_query(query)
        created = fact.created_at.isoformat() if self.use_sqlite else fact.created_at
        updated = (
            fact.updated_at.isoformat()
            if self.use_sqlite and fact.updated_at
            else fact.updated_at
        )
        try:
            if self.use_sqlite:
                with conn:
                    cursor = conn.execute(
                        query,
                        (
                            fact.user_id,
                            fact.statement,
                            fact.topic,
                            fact.trait_type,
                            fact.polarity,
                            fact.confidence,
                            fact.raw_message,
                            fact.source,
                            int(fact.active),
                            created,
                            updated,
                            fact.metadata,
                        ),
                    )
                    fact.id = cursor.lastrowid
            else:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        query + " RETURNING id;",
                        (
                            fact.user_id,
                            fact.statement,
                            fact.topic,
                            fact.trait_type,
                            fact.polarity,
                            fact.confidence,
                            fact.raw_message,
                            fact.source,
                            fact.active,
                            created,
                            updated,
                            fact.metadata,
                        ),
                    )
                    row = cur.fetchone()
                    if row:
                        fact.id = row["id"]
                conn.commit()
        except Exception as e:
            if not self.use_sqlite:
                conn.rollback()
            print(f"[ProfileManager] Error adding profile fact: {e}")
            raise
        finally:
            conn.close()
        return fact

    def update_fact(self, fact_id: int, updated: ProfileFact) -> None:
        conn = self._get_connection()
        query = """
            UPDATE profile_facts SET
                statement = %s,
                topic = %s,
                trait_type = %s,
                polarity = %s,
                confidence = %s,
                raw_message = %s,
                source = %s,
                active = %s,
                updated_at = %s,
                metadata = %s
            WHERE id = %s;
        """
        query = self._prepare_query(query)
        updated.updated_at = updated.updated_at or datetime.utcnow()
        updated_ts = (
            updated.updated_at.isoformat() if self.use_sqlite else updated.updated_at
        )
        try:
            params = (
                updated.statement,
                updated.topic,
                updated.trait_type,
                updated.polarity,
                updated.confidence,
                updated.raw_message,
                updated.source,
                int(updated.active) if self.use_sqlite else updated.active,
                updated_ts,
                updated.metadata,
                fact_id,
            )
            if self.use_sqlite:
                with conn:
                    conn.execute(query, params)
            else:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                conn.commit()
        except Exception as e:
            if not self.use_sqlite:
                conn.rollback()
            print(f"[ProfileManager] Error updating profile fact: {e}")
            raise
        finally:
            conn.close()

    def deactivate_fact(self, fact_id: int) -> None:
        conn = self._get_connection()
        query = """
            UPDATE profile_facts
            SET active = %s, updated_at = %s
            WHERE id = %s;
        """
        query = self._prepare_query(query)
        now = datetime.utcnow()
        now_val = now.isoformat() if self.use_sqlite else now
        active_val = 0 if self.use_sqlite else False
        try:
            if self.use_sqlite:
                with conn:
                    conn.execute(query, (active_val, now_val, fact_id))
            else:
                with conn.cursor() as cur:
                    cur.execute(query, (active_val, now, fact_id))
                conn.commit()
        except Exception as e:
            if not self.use_sqlite:
                conn.rollback()
            print(f"[ProfileManager] Error deactivating profile fact: {e}")
            raise
        finally:
            conn.close()

    def delete_fact(self, fact_id: int) -> None:
        conn = self._get_connection()
        query = "DELETE FROM profile_facts WHERE id = %s;"
        query = self._prepare_query(query)
        try:
            if self.use_sqlite:
                with conn:
                    conn.execute(query, (fact_id,))
            else:
                with conn.cursor() as cur:
                    cur.execute(query, (fact_id,))
                conn.commit()
        except Exception as e:
            if not self.use_sqlite:
                conn.rollback()
            print(f"[ProfileManager] Error deleting profile fact: {e}")
            raise
        finally:
            conn.close()

    def get_facts(
        self,
        user_id: str,
        *,
        active_only: bool = True,
    ) -> List[ProfileFact]:
        conn = self._get_connection()
        query = """
            SELECT id, user_id, statement, topic, trait_type, polarity, confidence,
                   raw_message, source, active, created_at, updated_at, metadata
            FROM profile_facts
            WHERE user_id = %s
        """
        if active_only:
            query += " AND active = %s" if not self.use_sqlite else " AND active = 1"
        query += " ORDER BY created_at ASC;"
        query = self._prepare_query(query)
        facts: List[ProfileFact] = []
        try:
            params = (user_id, True) if active_only and not self.use_sqlite else (user_id,)
            if self.use_sqlite:
                rows = conn.execute(query, params).fetchall()
            else:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    rows = cur.fetchall()
            for row in rows:
                facts.append(self._row_to_profile(row))
        except Exception as e:
            print(f"[ProfileManager] Error getting profile facts: {e}")
        finally:
            conn.close()
        return facts

    def get_facts_by_topic(
        self,
        user_id: str,
        topic: ProfileTopic,
        *,
        active_only: bool = True,
    ) -> List[ProfileFact]:
        all_facts = self.get_facts(user_id, active_only=active_only)
        return [f for f in all_facts if f.topic == topic]

    def get_facts_by_trait_type(
        self,
        user_id: str,
        trait_type: ProfileTraitType,
        *,
        active_only: bool = True,
    ) -> List[ProfileFact]:
        all_facts = self.get_facts(user_id, active_only=active_only)
        return [f for f in all_facts if f.trait_type == trait_type]

    def search_facts(
        self,
        user_id: str,
        query_text: str,
        limit: int = 10,
        *,
        active_only: bool = True,
    ) -> List[ProfileFact]:
        conn = self._get_connection()
        query = """
            SELECT id, user_id, statement, topic, trait_type, polarity, confidence,
                   raw_message, source, active, created_at, updated_at, metadata
            FROM profile_facts
            WHERE user_id = %s
              AND (statement ILIKE %s OR raw_message ILIKE %s OR topic ILIKE %s)
        """
        if active_only:
            query += " AND active = TRUE" if not self.use_sqlite else " AND active = 1"
        query += " ORDER BY created_at DESC LIMIT %s;"
        if self.use_sqlite:
            query = query.replace("ILIKE", "LIKE")
        query = self._prepare_query(query)
        like_pattern = f"%{query_text}%"
        facts: List[ProfileFact] = []
        try:
            if self.use_sqlite:
                rows = conn.execute(
                    query, (user_id, like_pattern, like_pattern, like_pattern, limit)
                ).fetchall()
            else:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        query,
                        (user_id, like_pattern, like_pattern, like_pattern, limit),
                    )
                    rows = cur.fetchall()
            for row in rows:
                facts.append(self._row_to_profile(row))
        except Exception as e:
            print(f"[ProfileManager] Error searching profile facts: {e}")
        finally:
            conn.close()
        return facts

    def get_profile_summary(self, user_id: str) -> dict:
        """Builds structured stats and markdown for RAG / coaching prompts."""
        facts = self.get_facts(user_id, active_only=True)
        if not facts:
            return {
                "total_facts": 0,
                "summary_markdown": (
                    "### 👤 User Profile & Preferences\n"
                    "No profile facts stored yet. Share your preferences, habits, or struggles "
                    "so I can personalize coaching."
                ),
            }

        topic_counter = Counter(f.topic for f in facts)
        trait_counter = Counter(f.trait_type for f in facts)
        polarity_counter = Counter(f.polarity or "neutral" for f in facts)

        by_topic: dict = {}
        for fact in facts:
            by_topic.setdefault(fact.topic, []).append(fact)

        summary_md = "### 👤 User Profile & Preferences\n"
        summary_md += (
            f"* **Total stored facts**: {len(facts)} "
            f"across {len(by_topic)} topics.\n"
        )
        summary_md += f"* **Topics**: {dict(topic_counter)}\n"
        summary_md += f"* **Trait types**: {dict(trait_counter)}\n"
        summary_md += f"* **Polarity mix**: {dict(polarity_counter)}\n\n"

        for topic, topic_facts in sorted(by_topic.items()):
            summary_md += f"#### {topic.replace('_', ' ').title()}\n"
            for fact in topic_facts:
                tag = fact.trait_type.replace("_", " ")
                summary_md += f"* **[{tag}]** {fact.statement}\n"
            summary_md += "\n"

        strengths = [f.statement for f in facts if f.trait_type == "strength"]
        weaknesses = [f.statement for f in facts if f.trait_type == "weakness"]
        goals = [f.statement for f in facts if f.trait_type == "goal"]

        if strengths:
            summary_md += "#### 💪 Strengths\n" + "\n".join(f"* {s}" for s in strengths) + "\n\n"
        if weaknesses:
            summary_md += "#### 🎯 Growth areas\n" + "\n".join(f"* {w}" for w in weaknesses) + "\n\n"
        if goals:
            summary_md += "#### 🏁 Stated goals\n" + "\n".join(f"* {g}" for g in goals) + "\n"

        return {
            "total_facts": len(facts),
            "topics": dict(topic_counter),
            "trait_types": dict(trait_counter),
            "polarities": dict(polarity_counter),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "goals": goals,
            "summary_markdown": summary_md.strip(),
        }
