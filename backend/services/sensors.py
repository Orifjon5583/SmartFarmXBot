import math
import random
from datetime import datetime, timedelta


class SensorService:
    def __init__(self):
        self.started_at = datetime.now()
        self.history = self._seed_history()

    def current(self):
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
