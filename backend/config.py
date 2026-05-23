import os
from pathlib import Path


def _load_env_file():
    env_file = Path(__file__).resolve().parents[1] / ".env"
    if not env_file.exists():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()


class Config:
    HOST = os.getenv("GREENHOUSE_HOST", "127.0.0.1")
    PORT = int(os.getenv("GREENHOUSE_PORT", "5000"))
    DEBUG = os.getenv("GREENHOUSE_DEBUG", "true").lower() == "true"
    USE_GPIO = os.getenv("USE_GPIO", "false").lower() == "true"
    USE_REAL_SENSORS = os.getenv("USE_REAL_SENSORS", "false").lower() == "true"
    TELEGRAM_TIMEOUT = float(os.getenv("TELEGRAM_TIMEOUT", "8"))
    GPIO_ACTIVE_LOW = os.getenv("GPIO_ACTIVE_LOW", "true").lower() == "true"
    MANUAL_OVERRIDE_SECONDS = int(os.getenv("MANUAL_OVERRIDE_SECONDS", "120"))

    GPIO_PINS = {
        "drip": int(os.getenv("GPIO_DRIP_PIN", "17")),
        "rain": int(os.getenv("GPIO_RAIN_PIN", "27")),
        "cooler": int(os.getenv("GPIO_COOLER_PIN", "22")),
        "led": int(os.getenv("GPIO_LED_PIN", "5")),
    }
    GPIO_ALIASES = {
        "pump": "drip",
        "fan": "cooler",
        "cooler1": "cooler",
        "cooler2": "cooler",
        "cooler3": "cooler",
        "light": "led",
    }

    DHT_PIN = int(os.getenv("DHT_PIN", "4"))
    DHT_SENSOR = os.getenv("DHT_SENSOR", "DHT22")
    IR_PIN = int(os.getenv("IR_PIN", "18"))
    LIGHT_DIGITAL_PIN = int(os.getenv("LIGHT_DIGITAL_PIN", "23"))
    LIGHT_DARK_SIGNAL = int(os.getenv("LIGHT_DARK_SIGNAL", "1"))
    SOIL_ADC_CHANNEL = int(os.getenv("SOIL_ADC_CHANNEL", "0"))
    LIGHT_ADC_CHANNEL = int(os.getenv("LIGHT_ADC_CHANNEL", "1"))
    SOIL_DRY_VALUE = int(os.getenv("SOIL_DRY_VALUE", "850"))
    SOIL_WET_VALUE = int(os.getenv("SOIL_WET_VALUE", "350"))
