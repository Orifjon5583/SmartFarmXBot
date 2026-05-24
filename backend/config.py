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


def _parse_device_pin_map(value):
    pins = {}
    for item in (value or "").split(","):
        if ":" not in item:
            continue

        device, pin = item.split(":", 1)
        device = device.strip()
        pin = pin.strip()
        if not device or not pin:
            continue

        pins[device] = int(pin)
    return pins


class Config:
    HOST = os.getenv("GREENHOUSE_HOST", "127.0.0.1")
    PORT = int(os.getenv("GREENHOUSE_PORT", "5000"))
    DEBUG = os.getenv("GREENHOUSE_DEBUG", "true").lower() == "true"
    USE_GPIO = os.getenv("USE_GPIO", "false").lower() == "true"
    USE_REAL_SENSORS = os.getenv("USE_REAL_SENSORS", "false").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    HISTORY_RETENTION_DAYS = int(os.getenv("HISTORY_RETENTION_DAYS", "30"))
    HISTORY_DEFAULT_HOURS = int(os.getenv("HISTORY_DEFAULT_HOURS", "24"))
    HISTORY_QUERY_LIMIT = int(os.getenv("HISTORY_QUERY_LIMIT", "500"))
    SENSOR_BROADCAST_SECONDS = float(os.getenv("SENSOR_BROADCAST_SECONDS", "5"))
    MQTT_ENABLED = os.getenv("MQTT_ENABLED", "false").lower() == "true"
    MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
    MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
    MQTT_TLS = os.getenv("MQTT_TLS", "false").lower() == "true"
    MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "smartfarm-backend")
    MQTT_PI_CLIENT_ID = os.getenv("MQTT_PI_CLIENT_ID", "smartfarm-pi")
    MQTT_GREENHOUSE_ID = os.getenv("MQTT_GREENHOUSE_ID", "greenhouse-1")
    MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "smartfarm")
    SOCKET_AUTH_REQUIRED = os.getenv("SOCKET_AUTH_REQUIRED", "true").lower() == "true"
    SOCKET_TOKENS = {
        token.strip()
        for token in os.getenv("SOCKET_TOKENS", os.getenv("GREENHOUSE_API_TOKEN", "")).split(",")
        if token.strip()
    }
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "*").split(",")
        if origin.strip()
    ]
    TELEGRAM_TIMEOUT = float(os.getenv("TELEGRAM_TIMEOUT", "8"))
    GPIO_ACTIVE_LOW = os.getenv("GPIO_ACTIVE_LOW", "true").lower() == "true"
    MANUAL_OVERRIDE_SECONDS = int(os.getenv("MANUAL_OVERRIDE_SECONDS", "120"))
    PI_AUTOMATION_ENABLED = os.getenv("PI_AUTOMATION_ENABLED", "true").lower() == "true"
    PI_TEMPERATURE_LIMIT = float(os.getenv("PI_TEMPERATURE_LIMIT", "30"))
    PI_MOISTURE_LIMIT = float(os.getenv("PI_MOISTURE_LIMIT", "40"))
    PI_LIGHT_LIMIT = float(os.getenv("PI_LIGHT_LIMIT", "420"))
    PI_GAS_DANGER_LIMIT = float(os.getenv("PI_GAS_DANGER_LIMIT", "70"))
    MANUAL_SWITCH_ACTIVE_LOW = os.getenv("MANUAL_SWITCH_ACTIVE_LOW", "true").lower() == "true"
    MANUAL_SWITCH_DEBOUNCE_SECONDS = float(os.getenv("MANUAL_SWITCH_DEBOUNCE_SECONDS", "0.08"))
    MANUAL_SWITCH_PINS = _parse_device_pin_map(
        os.getenv(
            "MANUAL_SWITCH_PINS",
            "drip_pump:12,rain_pump:16,photo_led:20,insect_led:21,cooler_1:19,cooler_2:13",
        )
    )
    LCD_ENABLED = os.getenv("LCD_ENABLED", "false").lower() == "true"
    LCD_I2C_ADDRESS = int(os.getenv("LCD_I2C_ADDRESS", "0x27"), 0)
    LCD_I2C_BUS = int(os.getenv("LCD_I2C_BUS", "1"))
    IR_ENABLED = os.getenv("IR_ENABLED", "false").lower() == "true"
    IR_ACTIVE_LOW = os.getenv("IR_ACTIVE_LOW", "true").lower() == "true"
    IR_EVENT_COOLDOWN_SECONDS = float(os.getenv("IR_EVENT_COOLDOWN_SECONDS", "0.45"))

    GPIO_PINS = {
        "drip_pump": int(os.getenv("GPIO_DRIP_PUMP_PIN", os.getenv("GPIO_DRIP_PIN", "17"))),
        "rain_pump": int(os.getenv("GPIO_RAIN_PUMP_PIN", os.getenv("GPIO_RAIN_PIN", "27"))),
        "photo_led": int(os.getenv("GPIO_PHOTO_LED_PIN", os.getenv("GPIO_LED_PIN", "5"))),
        "insect_led": int(os.getenv("GPIO_INSECT_LED_PIN", "6")),
        "cooler_1": int(os.getenv("GPIO_COOLER_1_PIN", os.getenv("GPIO_COOLER_PIN", "22"))),
        "cooler_2": int(os.getenv("GPIO_COOLER_2_PIN", "26")),
    }
    GPIO_ALIASES = {
        "drip": "drip_pump",
        "pump": "drip_pump",
        "rain": "rain_pump",
        "photo": "photo_led",
        "led": "photo_led",
        "light": "photo_led",
        "insect": "insect_led",
        "insect_light": "insect_led",
        "fan": "cooler_1",
        "cooler": "cooler_1",
        "cooler1": "cooler_1",
        "cooler2": "cooler_2",
    }

    DHT_PIN = int(os.getenv("DHT_PIN", "4"))
    DHT_SENSOR = os.getenv("DHT_SENSOR", "DHT22")
    IR_PIN = int(os.getenv("IR_PIN", "18"))
    LIGHT_DIGITAL_PIN = int(os.getenv("LIGHT_DIGITAL_PIN", "23"))
    LIGHT_DARK_SIGNAL = int(os.getenv("LIGHT_DARK_SIGNAL", "1"))
    MQ2_DIGITAL_PIN = int(os.getenv("MQ2_DIGITAL_PIN", "24"))
    SOIL_DIGITAL_PIN = int(os.getenv("SOIL_DIGITAL_PIN", "21"))
    MQ2_DANGER_SIGNAL = int(os.getenv("MQ2_DANGER_SIGNAL", "0"))
    SOIL_ADC_CHANNEL = int(os.getenv("SOIL_ADC_CHANNEL", "0"))
    LIGHT_ADC_CHANNEL = int(os.getenv("LIGHT_ADC_CHANNEL", "1"))
    MQ2_ADC_CHANNEL = int(os.getenv("MQ2_ADC_CHANNEL", "2"))
    SOIL_DRY_VALUE = int(os.getenv("SOIL_DRY_VALUE", "850"))
    SOIL_WET_VALUE = int(os.getenv("SOIL_WET_VALUE", "350"))

    # Direct LED strip control (not via relay)
    LED_STRIP_PIN = int(os.getenv("LED_STRIP_PIN", "18"))
    LED_STRIP_ENABLED = os.getenv("LED_STRIP_ENABLED", "true").lower() == "true"
