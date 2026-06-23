import os
import sqlite3
import json
import logging
import queue
import threading
from config.settings import DB_PATH, JSON_LOG_PATH, DB_TYPE, POSTGRES_CONN_STRING

# Set up logging for database operations
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DatabaseManager")

# Soft import psycopg2 to handle environment issues gracefully
try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    logger.warning("psycopg2 package not found. PostgreSQL support will be disabled.")


class DatabaseManager:
    """
    Manages structured storage for traffic memory.
    Supports PostgreSQL and SQLite database backends, along with local JSON logging.
    Maintains a local memory cache of event stats to prevent performance bottlenecks.
    """

    def __init__(self):
        self.db_type = DB_TYPE.lower()
        self.postgres_conn_string = POSTGRES_CONN_STRING
        self.db_path = DB_PATH
        self.json_path = JSON_LOG_PATH
        
        # Memory Cache for frame-rate performance optimization
        self.cached_event_count = 0
        self.cached_recent_events = []

        # Initialize JSON file
        self._init_json()

        # Initialize SQL Database
        if self.db_type == "postgres":
            if not POSTGRES_AVAILABLE:
                logger.warning("PostgreSQL requested but psycopg2 is not installed. Falling back to SQLite.")
                self.db_type = "sqlite"
                self._init_sqlite()
            else:
                try:
                    self._init_postgres()
                except Exception as e:
                    logger.error("Failed to connect to PostgreSQL: %s", e)
                    logger.warning("Falling back to SQLite database.")
                    self.db_type = "sqlite"
                    self._init_sqlite()
        else:
            self._init_sqlite()

        # Clean up local SQLite db if postgres is successfully connected and no sqlite fallback was triggered
        if self.db_type == "postgres" and os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
                logger.info("Removed unused local SQLite file: %s", self.db_path)
            except OSError as e:
                logger.warning("Failed to remove unused SQLite file: %s", e)

        # Pre-populate the cache from the active SQL database
        self._populate_cache()

        # Asynchronous logging worker setup
        self.log_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def _worker(self):
        """Background thread worker to process and log queued events sequentially."""
        while True:
            try:
                item = self.log_queue.get()
                if item is None:
                    # Shutdown sentinel
                    self.log_queue.task_done()
                    break
                
                event_type, timestamp, vehicle_count = item
                
                sql_success = False
                if self.db_type == "postgres":
                    sql_success = self._log_to_postgres(event_type, timestamp, vehicle_count)
                    if not sql_success:
                        logger.warning("PostgreSQL insert failed. Attempting SQLite write fallback.")
                        sql_success = self._log_to_sqlite(event_type, timestamp, vehicle_count)
                else:
                    sql_success = self._log_to_sqlite(event_type, timestamp, vehicle_count)

                json_success = self._log_to_json(event_type, timestamp, vehicle_count)
                
                if sql_success and json_success:
                    logger.info("Event successfully logged in background: Type=%s, Count=%d", event_type, vehicle_count)
                else:
                    logger.error("Background logging partial failure: SQL=%s, JSON=%s", sql_success, json_success)
                
                self.log_queue.task_done()
            except Exception as e:
                logger.error("Error in background database worker thread: %s", e)
                # Ensure task_done is called even on error to prevent shutdown deadlock
                try:
                    self.log_queue.task_done()
                except Exception:
                    pass

    def _init_postgres(self):
        """Initializes PostgreSQL database and creates the events table if it does not exist."""
        conn = psycopg2.connect(self.postgres_conn_string)
        try:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS events (
                            id SERIAL PRIMARY KEY,
                            event_type VARCHAR(50) NOT NULL,
                            timestamp VARCHAR(50) NOT NULL,
                            vehicle_count INTEGER NOT NULL
                        );
                    """)
            logger.info("PostgreSQL database initialized successfully.")
        finally:
            conn.close()

    def _init_sqlite(self):
        """Initializes SQLite database and creates the events table if it does not exist."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        vehicle_count INTEGER NOT NULL
                    )
                """)
                conn.commit()
            logger.info("SQLite database initialized successfully at %s", self.db_path)
        except sqlite3.Error as e:
            logger.error("Failed to initialize SQLite database: %s", e)
            raise

    def _init_json(self):
        """Ensures that the JSON log file exists and is initialized as a valid JSON list."""
        try:
            os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
            if not os.path.exists(self.json_path) or os.path.getsize(self.json_path) == 0:
                with open(self.json_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)
                logger.info("Initialized new JSON events file at %s", self.json_path)
            else:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.warning("JSON file was invalid or unreadable. Reinitializing. Error: %s", e)
            try:
                with open(self.json_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)
            except IOError as write_err:
                logger.error("Failed to reinitialize JSON file: %s", write_err)

    def _populate_cache(self):
        """Fetches initial event statistics from the active database to populate memory cache."""
        logger.info("Populating memory cache from %s database...", self.db_type)
        if self.db_type == "postgres":
            try:
                conn = psycopg2.connect(self.postgres_conn_string)
                try:
                    with conn:
                        with conn.cursor() as cursor:
                            # Fetch count
                            cursor.execute("SELECT COUNT(*) FROM events")
                            self.cached_event_count = cursor.fetchone()[0]

                            # Fetch recent 3 events
                            cursor.execute("SELECT timestamp, vehicle_count FROM events ORDER BY id DESC LIMIT 3")
                            self.cached_recent_events = [
                                {"timestamp": row[0], "vehicle_count": row[1]} for row in cursor.fetchall()
                            ]
                finally:
                    conn.close()
                logger.info(
                    "Cache loaded: Count=%d, History=%d items",
                    self.cached_event_count,
                    len(self.cached_recent_events)
                )
            except Exception as e:
                logger.error("Failed to query PostgreSQL during cache setup: %s", e)
                # Fallback to SQLite query if PostgreSQL setup queries fail
                self._populate_cache_sqlite()
        else:
            self._populate_cache_sqlite()

    def _populate_cache_sqlite(self):
        """Helper to populate cache from SQLite database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM events")
                self.cached_event_count = cursor.fetchone()[0]

                cursor.execute("SELECT timestamp, vehicle_count FROM events ORDER BY id DESC LIMIT 3")
                self.cached_recent_events = [
                    {"timestamp": row[0], "vehicle_count": row[1]} for row in cursor.fetchall()
                ]
            logger.info(
                "Cache loaded (SQLite): Count=%d, History=%d items",
                self.cached_event_count,
                len(self.cached_recent_events)
            )
        except sqlite3.Error as e:
            logger.error("Failed to populate cache from SQLite: %s", e)

    def log_event(self, event_type: str, timestamp: str, vehicle_count: int) -> bool:
        """
        Enqueues the logging of a congestion event to the background thread
        and immediately updates the local memory cache for HUD visualization.

        :param event_type: Type of event (e.g. 'Congestion')
        :param timestamp: Formatted timestamp string of the event
        :param vehicle_count: The number of vehicles in the zone when event triggered
        :return: True if successfully enqueued
        """
        # Update memory cache immediately so the UI reflects the event without latency
        self.cached_event_count += 1
        self.cached_recent_events.insert(0, {"timestamp": timestamp, "vehicle_count": vehicle_count})
        self.cached_recent_events = self.cached_recent_events[:3]

        # Enqueue the event for background logging
        self.log_queue.put((event_type, timestamp, vehicle_count))
        return True

    def _log_to_sqlite(self, event_type: str, timestamp: str, vehicle_count: int) -> bool:
        """Helper to insert event record into SQLite database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO events (event_type, timestamp, vehicle_count) VALUES (?, ?, ?)",
                    (event_type, timestamp, vehicle_count)
                )
                conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error("SQLite insert error: %s", e)
            return False

    def _log_to_postgres(self, event_type: str, timestamp: str, vehicle_count: int) -> bool:
        """Helper to insert event record into PostgreSQL database."""
        try:
            conn = psycopg2.connect(self.postgres_conn_string)
            try:
                with conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO events (event_type, timestamp, vehicle_count) VALUES (%s, %s, %s)",
                            (event_type, timestamp, vehicle_count)
                        )
                return True
            finally:
                conn.close()
        except Exception as e:
            logger.error("PostgreSQL insert error: %s", e)
            return False

    def _log_to_json(self, event_type: str, timestamp: str, vehicle_count: int) -> bool:
        """Helper to append event record to the JSON file list."""
        try:
            events = []
            if os.path.exists(self.json_path):
                with open(self.json_path, "r", encoding="utf-8") as f:
                    try:
                        events = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning("Corrupt JSON file contents, overwriting with empty list")
                        events = []
            
            new_event = {
                "event_type": event_type,
                "timestamp": timestamp,
                "vehicle_count": vehicle_count
            }
            events.append(new_event)
            
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(events, f, indent=4)
            return True
        except IOError as e:
            logger.error("JSON write error: %s", e)
            return False

    def get_event_count(self) -> int:
        """
        Returns the total number of logged events.
        Serves from cache to avoid database latency.
        """
        return self.cached_event_count

    def get_recent_events(self, limit: int = 3) -> list:
        """
        Retrieves the most recent logged events.
        Serves from cache to avoid database latency.
        """
        return self.cached_recent_events[:limit]

    def shutdown(self):
        """Blocks until all queued events are processed, then shuts down the worker thread."""
        logger.info("Waiting for background database logging tasks to complete...")
        self.log_queue.join()
        # Send sentinel to terminate worker thread
        self.log_queue.put(None)
        self.worker_thread.join(timeout=3.0)
        logger.info("Database background worker shutdown complete.")
