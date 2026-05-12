import math
import random
from datetime import datetime, timedelta

from backend.config import Config


class SensorService:
    def __init__(self):
        self.started_at = datetime.now()
        self.history = self._seed_history()
        self.real_sensors_available = False
        self.dht = None
        self.spi = None

        if Config.USE_REAL_SENSORS:
            self._setup_real_sensors()

    def _setup_real_sensors(self):
        try:
            import Adafruit_DHT
            import spidev

            sensor_name = Config.DHT_SENSOR.upper()
            self.dht = Adafruit_DHT.DHT22 if sensor_name == "DHT22" else Adafruit_DHT.DHT11
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)
            self.spi.max_speed_hz = 1350000
            self.real_sensors_available = True
        except Exception:
            self.real_sensors_available = False

    def current(self):
        if self.real_sensors_available:
            return self._read_real_sensors()

        return self._mock_current()

    def _mock_current(self):
        minute = datetime.now().minute
        temperature = round(26.2 + math.sin(minute / 8) * 2.4 + random.uniform(-0.25, 0.25), 1)
        humidity = round(66 + math.cos(minute / 10) * 7 + random.uniform(-1.2, 1.2))
        soil = round(48 + math.sin(minute / 12) * 6 + random.uniform(-1.4, 1.4))
        light = round(650 + math.sin(minute / 9) * 180 + random.uniform(-24, 24))

        return {
            "temperature": temperature,
            "humidity": humidity,
            "soilMoisture": soil,
            "light": max(80, light),
            "weather": {
                "condition": "Ochiq va barqaror ob-havo",
                "outsideTemp": 22,
                "wind": 8,
                "uv": 5,
            },
        }

    def _read_real_sensors(self):
        import Adafruit_DHT

        humidity, temperature = Adafruit_DHT.read_retry(self.dht, Config.DHT_PIN)
        soil_raw = self._read_adc(Config.SOIL_ADC_CHANNEL)
        light_raw = self._read_adc(Config.LIGHT_ADC_CHANNEL)

        return {
            "temperature": round(temperature, 1) if temperature is not None else None,
            "humidity": round(humidity) if humidity is not None else None,
            "soilMoisture": self._soil_percent(soil_raw),
            "light": self._light_lux_estimate(light_raw),
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

    def history_data(self):
        latest = self.current()
        now_label = datetime.now().strftime("%H:%M")
        self.history.append(
            {
                "time": now_label,
                "temperature": latest["temperature"],
                "humidity": latest["humidity"],
                "soil": latest["soilMoisture"],
                "light": latest["light"],
                "energy": round(2.1 + random.random() * 0.8, 2),
            }
        )
        self.history = self.history[-24:]
        return self.history

    def status(self, device_snapshot):
        uptime = datetime.now() - self.started_at
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes = remainder // 60
        return {
            "raspberryPi": "onlayn",
            "api": "ulangan",
            "database": "mock xotira",
            "uptime": f"{hours} soat {minutes} daqiqa",
            "sensorMode": "real" if self.real_sensors_available else "mock",
            **device_snapshot,
        }

    @staticmethod
    def _seed_history():
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        points = []
        for index in range(24):
            stamp = now - timedelta(hours=23 - index)
            points.append(
                {
                    "time": stamp.strftime("%H:%M"),
                    "temperature": round(23 + math.sin(index / 3) * 3 + index * 0.11, 1),
                    "humidity": round(62 + math.cos(index / 4) * 8),
                    "soil": round(52 - index * 0.42 + math.sin(index / 2) * 4),
                    "light": max(110, round(420 + math.sin((index - 6) / 5) * 360)),
                    "energy": round(1.8 + math.sin(index / 4) * 0.5 + index * 0.045, 2),
                }
            )
        return points
