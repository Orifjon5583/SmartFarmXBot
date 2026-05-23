import math
from datetime import datetime, timedelta, timezone

from backend.config import Config
from backend.services.history import HistoryStore


class SensorService:
    def __init__(self, history_store=None):
        self.started_at = datetime.now()
        self.history = []
        self.history_store = history_store or HistoryStore()
        self.external_snapshot = None
        self.external_updated_at = None
        self.real_sensors_available = False
        self.dht = None
        self.spi = None
        self.gpio = None

        if Config.USE_REAL_SENSORS:
            self._setup_real_sensors()

    def _setup_real_sensors(self):
        try:
            import RPi.GPIO as GPIO
            import spidev
            import adafruit_dht
            import board

            sensor_name = Config.DHT_SENSOR.upper()
            pin_attr = f"D{Config.DHT_PIN}"
            pin = getattr(board, pin_attr, board.D4)
            self.dht = adafruit_dht.DHT22(pin) if sensor_name == "DHT22" else adafruit_dht.DHT11(pin)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(Config.LIGHT_DIGITAL_PIN, GPIO.IN)
            GPIO.setup(Config.MQ2_DIGITAL_PIN, GPIO.IN)
            self.gpio = GPIO
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)
            self.spi.max_speed_hz = 1350000
            self.real_sensors_available = True
        except Exception:
            self.real_sensors_available = False

    def current(self):
        if self.external_snapshot is not None:
            return dict(self.external_snapshot)

        if self.real_sensors_available:
            return self._read_real_sensors()

        return self._empty_current()

    def update_external_snapshot(self, payload):
        if not isinstance(payload, dict):
            return self.current()

        sensors = payload.get("sensors") if isinstance(payload.get("sensors"), dict) else payload
        devices = payload.get("devices") if isinstance(payload.get("devices"), dict) else None

        snapshot = {
            "temperature": self._pick(sensors, "temperature", "temp", "airTemperature"),
            "humidity": self._pick(sensors, "humidity", "airHumidity"),
            "soilMoisture": self._pick(sensors, "soilMoisture", "soil_moisture", "soil"),
            "light": self._pick(sensors, "light", "lightLevel", "ldr"),
            "gasLevel": self._pick(sensors, "gasLevel", "gas_level", "mq2", "mq2Level"),
            "gasDetected": bool(self._pick(sensors, "gasDetected", "gas_detected", default=False)),
            "weather": {
                "condition": "MQTT IoT telemetriya",
                "outsideTemp": self._pick(sensors, "outsideTemp", default=self._pick(sensors, "temperature", "temp")),
                "wind": self._pick(sensors, "wind", default=0),
                "uv": self._pick(sensors, "uv", default=0),
            },
            "source": payload.get("source", "mqtt"),
            "timestamp": payload.get("timestamp")
            or datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        }

        if devices is not None:
            snapshot["devices"] = devices

        self.external_snapshot = {key: value for key, value in snapshot.items() if value is not None}
        self.external_updated_at = datetime.now(timezone.utc).astimezone()
        return dict(self.external_snapshot)

    def record_current(self):
        latest = self.current()
        point = self.history_store.insert_sensor(latest)

        if point is None:
            point = HistoryStore.sensor_point(latest)

        self.history.append(point)
        self.history = self.history[-Config.HISTORY_QUERY_LIMIT :]
        return latest, point

    def _empty_current(self):
        return {
            "temperature": None,
            "humidity": None,
            "soilMoisture": None,
            "light": None,
            "gasLevel": None,
            "gasDetected": False,
            "weather": {
                "condition": "--",
                "outsideTemp": "--",
                "wind": "--",
                "uv": "--",
            },
        }

    def _read_real_sensors(self):
        try:
            humidity = self.dht.humidity
            temperature = self.dht.temperature
        except Exception:
            humidity = None
            temperature = None

        soil_raw = self._read_adc(Config.SOIL_ADC_CHANNEL)
        mq2_raw = self._read_adc(Config.MQ2_ADC_CHANNEL)
        light_digital = self.gpio.input(Config.LIGHT_DIGITAL_PIN) if self.gpio else Config.LIGHT_DARK_SIGNAL
        mq2_digital = self.gpio.input(Config.MQ2_DIGITAL_PIN) if self.gpio else 1 - Config.MQ2_DANGER_SIGNAL
        is_dark = int(light_digital) == Config.LIGHT_DARK_SIGNAL
        gas_detected = int(mq2_digital) == Config.MQ2_DANGER_SIGNAL

        return {
            "temperature": round(temperature, 1) if temperature is not None else None,
            "humidity": round(humidity) if humidity is not None else None,
            "soilMoisture": self._soil_percent(soil_raw),
            "light": 80 if is_dark else 850,
            "lightDigital": int(light_digital),
            "isDark": is_dark,
            "gasLevel": self._gas_percent(mq2_raw),
            "gasDetected": gas_detected,
            "mq2Raw": mq2_raw,
            "mq2Digital": int(mq2_digital),
            "weather": {
                "condition": "Real sensor rejimi",
                "outsideTemp": round(temperature, 1) if temperature is not None else None,
                "wind": 0,
                "uv": 0,
            },
        }

    def _read_adc(self, channel):
        if channel < 0 or channel > 7:
            raise ValueError("MCP3008 kanali 0 dan 7 gacha bo'lishi kerak")

        response = self.spi.xfer2([1, (8 + channel) << 4, 0])
        return ((response[1] & 3) << 8) + response[2]

    @staticmethod
    def _light_lux_estimate(raw_value):
        return round((raw_value / 1023) * 1000)

    @staticmethod
    def _soil_percent(raw_value):
        dry = Config.SOIL_DRY_VALUE
        wet = Config.SOIL_WET_VALUE
        if dry == wet:
            return 0

        percent = (dry - raw_value) * 100 / (dry - wet)
        return round(max(0, min(100, percent)))

    @staticmethod
    def _gas_percent(raw_value):
        return round(max(0, min(100, raw_value * 100 / 1023)))

    @staticmethod
    def _pick(source, *keys, default=None):
        for key in keys:
            if key in source and source[key] is not None:
                return source[key]
        return default

    def history_data(self, start=None, end=None, limit=None):
        database_history = self.history_store.sensor_history(start=start, end=end, limit=limit)
        if database_history:
            return database_history

        limit = min(max(int(limit or 24), 1), Config.HISTORY_QUERY_LIMIT)
        return self.history[-int(limit) :]

    def status(self, device_snapshot):
        uptime = datetime.now() - self.started_at
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes = remainder // 60
        return {
            "raspberryPi": "onlayn",
            "api": "ulangan",
            "database": self.history_store.status(),
            "uptime": f"{hours} soat {minutes} daqiqa",
            "sensorMode": "real" if self.real_sensors_available else "kutish",
            "telemetrySource": "mqtt" if self.external_snapshot is not None else "hech narsa",
            "telemetryUpdatedAt": self.external_updated_at.isoformat(timespec="seconds")
            if self.external_updated_at
            else None,
            **device_snapshot,
        }
