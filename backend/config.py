import os


class Config:
    HOST = os.getenv("GREENHOUSE_HOST", "127.0.0.1")
    PORT = int(os.getenv("GREENHOUSE_PORT", "5000"))
    DEBUG = os.getenv("GREENHOUSE_DEBUG", "true").lower() == "true"
    USE_GPIO = os.getenv("USE_GPIO", "false").lower() == "true"
    USE_REAL_SENSORS = os.getenv("USE_REAL_SENSORS", "false").lower() == "true"
    TELEGRAM_TIMEOUT = float(os.getenv("TELEGRAM_TIMEOUT", "8"))

    GPIO_PINS = {
        "fan": int(os.getenv("GPIO_FAN_PIN", "4")),
        "pump": int(os.getenv("GPIO_PUMP_PIN", "17")),
        "light": int(os.getenv("GPIO_LIGHT_PIN", "22")),
        "camera": int(os.getenv("GPIO_CAMERA_PIN", "27")),
    }

    DHT_PIN = int(os.getenv("DHT_PIN", "5"))
    DHT_SENSOR = os.getenv("DHT_SENSOR", "DHT22")
    SOIL_ADC_CHANNEL = int(os.getenv("SOIL_ADC_CHANNEL", "0"))
    LIGHT_ADC_CHANNEL = int(os.getenv("LIGHT_ADC_CHANNEL", "1"))
    SOIL_DRY_VALUE = int(os.getenv("SOIL_DRY_VALUE", "850"))
    SOIL_WET_VALUE = int(os.getenv("SOIL_WET_VALUE", "350"))
