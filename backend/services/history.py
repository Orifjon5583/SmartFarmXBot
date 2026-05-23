from datetime import datetime, timedelta, timezone
from decimal import Decimal

from backend.config import Config

try:
    import psycopg
    from psycopg.rows import dict_row
    from psycopg.types.json import Jsonb
except ImportError:
    psycopg = None
    dict_row = None
    Jsonb = None


class HistoryStore:
    def __init__(self):
        self.database_url = Config.DATABASE_URL
        self.available = False
        self.error = None
        self.last_cleanup = None

    def initialize(self):
        if not self.database_url:
            self.error = "DATABASE_URL sozlanmagan"
            return False

        if psycopg is None:
            self.error = "psycopg o'rnatilmagan"
            return False

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS sensor_history (
                            id BIGSERIAL PRIMARY KEY,
                            recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                            temperature NUMERIC,
                            humidity NUMERIC,
                            soil_moisture NUMERIC,
                            light NUMERIC,
                            gas_level NUMERIC,
                            gas_detected BOOLEAN,
                            energy NUMERIC,
                            payload JSONB NOT NULL DEFAULT '{}'::jsonb
                        )
                        """
                    )
                    cursor.execute(
                        """
                        CREATE INDEX IF NOT EXISTS idx_sensor_history_recorded_at
                        ON sensor_history (recorded_at DESC)
                        """
                    )
                    cursor.execute(
                        """
                        ALTER TABLE sensor_history
                        ADD COLUMN IF NOT EXISTS gas_level NUMERIC
                        """
                    )
                    cursor.execute(
                        """
                        ALTER TABLE sensor_history
                        ADD COLUMN IF NOT EXISTS gas_detected BOOLEAN
                        """
                    )
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS device_history (
                            id BIGSERIAL PRIMARY KEY,
                            recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                            device TEXT NOT NULL,
                            enabled BOOLEAN NOT NULL,
                            source TEXT NOT NULL,
                            changed BOOLEAN NOT NULL DEFAULT false,
                            ignored BOOLEAN NOT NULL DEFAULT false,
                            message TEXT NOT NULL DEFAULT '',
                            command JSONB NOT NULL DEFAULT '{}'::jsonb
                        )
                        """
                    )
                    cursor.execute(
                        """
                        CREATE INDEX IF NOT EXISTS idx_device_history_recorded_at
                        ON device_history (recorded_at DESC)
                        """
                    )
                connection.commit()
            self.available = True
            self.error = None
            self.cleanup(force=True)
            return True
        except Exception as error:
            self.available = False
            self.error = str(error)
            return False

    def insert_sensor(self, snapshot):
        if not self.available:
            return None

        point = self.sensor_point(snapshot)
        try:
            with self._connect() as connection:
                with connection.cursor(row_factory=dict_row) as cursor:
                    cursor.execute(
                        """
                        INSERT INTO sensor_history
                            (temperature, humidity, soil_moisture, light, gas_level, gas_detected, energy, payload)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING recorded_at
                        """,
                        (
                            point["temperature"],
                            point["humidity"],
                            point["soil"],
                            point["light"],
                            point["gasLevel"],
                            point["gasDetected"],
                            point["energy"],
                            Jsonb(snapshot),
                        ),
                    )
                    row = cursor.fetchone()
                connection.commit()
            point["timestamp"] = row["recorded_at"].astimezone().isoformat(timespec="seconds")
            point["time"] = row["recorded_at"].astimezone().strftime("%H:%M")
            return point
        except Exception as error:
            self.available = False
            self.error = str(error)
            return None

    def insert_device_event(self, command):
        if not self.available or not command:
            return

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO device_history
                            (device, enabled, source, changed, ignored, message, command)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            command.get("device", "unknown"),
                            bool(command.get("enabled")),
                            command.get("source", "site"),
                            bool(command.get("changed")),
                            bool(command.get("ignored")),
                            command.get("message", ""),
                            Jsonb(command),
                        ),
                    )
                connection.commit()
        except Exception as error:
            self.available = False
            self.error = str(error)

    def sensor_history(self, start=None, end=None, limit=None):
        if not self.available:
            return []

        limit = min(max(int(limit or Config.HISTORY_QUERY_LIMIT), 1), 5000)
        conditions = []
        params = []

        if start is not None:
            conditions.append("recorded_at >= %s")
            params.append(start)
        if end is not None:
            conditions.append("recorded_at <= %s")
            params.append(end)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)

        try:
            with self._connect() as connection:
                with connection.cursor(row_factory=dict_row) as cursor:
                    cursor.execute(
                        f"""
                        SELECT recorded_at, temperature, humidity, soil_moisture, light, gas_level, gas_detected, energy
                        FROM sensor_history
                        {where_clause}
                        ORDER BY recorded_at DESC
                        LIMIT %s
                        """,
                        params,
                    )
                    rows = cursor.fetchall()
            return [self._row_to_point(row) for row in reversed(rows)]
        except Exception as error:
            self.available = False
            self.error = str(error)
            return []

    def cleanup(self, force=False):
        if not self.available:
            return 0

        now = datetime.now(timezone.utc)
        if not force and self.last_cleanup and now - self.last_cleanup < timedelta(hours=1):
            return 0

        cutoff = now - timedelta(days=Config.HISTORY_RETENTION_DAYS)
        deleted = 0
        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM sensor_history WHERE recorded_at < %s", (cutoff,))
                    deleted += cursor.rowcount
                    cursor.execute("DELETE FROM device_history WHERE recorded_at < %s", (cutoff,))
                    deleted += cursor.rowcount
                connection.commit()
            self.last_cleanup = now
        except Exception as error:
            self.available = False
            self.error = str(error)
        return deleted

    def status(self):
        if self.available:
            return "postgres ulangan"
        if self.database_url:
            return f"postgres xato: {self.error}"
        return "mock xotira"

    def _connect(self):
        return psycopg.connect(self.database_url)

    @staticmethod
    def sensor_point(snapshot):
        return {
            "time": datetime.now().strftime("%H:%M"),
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "temperature": snapshot.get("temperature"),
            "humidity": snapshot.get("humidity"),
            "soil": snapshot.get("soilMoisture"),
            "light": snapshot.get("light"),
            "gasLevel": snapshot.get("gasLevel"),
            "gasDetected": bool(snapshot.get("gasDetected", False)),
            "energy": round(2.1 + ((datetime.now().second % 10) / 10) * 0.8, 2),
        }

    @classmethod
    def _row_to_point(cls, row):
        recorded_at = row["recorded_at"].astimezone()
        return {
            "time": recorded_at.strftime("%H:%M"),
            "timestamp": recorded_at.isoformat(timespec="seconds"),
            "temperature": cls._number(row["temperature"]),
            "humidity": cls._number(row["humidity"]),
            "soil": cls._number(row["soil_moisture"]),
            "light": cls._number(row["light"]),
            "gasLevel": cls._number(row["gas_level"]),
            "gasDetected": bool(row["gas_detected"]),
            "energy": cls._number(row["energy"]),
        }

    @staticmethod
    def _number(value):
        if isinstance(value, Decimal):
            value = float(value)
            return int(value) if value.is_integer() else value
        return value
