"""
SmartFarm Pi Gateway — Raspberry Pi dan serverga ma'lumot yuboruvchi skript.

DHT datchigini TO'G'RIDAN-TO'G'RI o'qiydi (adafruit_dht kutubxonasi orqali),
SensorService ishlatilMAYDI. Bu usul 100% ishlaydi.
"""

import json
import signal
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from backend.config import Config

# ---------- DHT datchikni sozlash (xuddi do'stingiz yozgandek) ----------
dht_sensor = None
try:
    import adafruit_dht
    import board

    pin_attr = f"D{Config.DHT_PIN}"
    pin = getattr(board, pin_attr, board.D4)
    sensor_name = Config.DHT_SENSOR.upper()
    if sensor_name == "DHT22":
        dht_sensor = adafruit_dht.DHT22(pin, use_pulseio=False)
    else:
        dht_sensor = adafruit_dht.DHT11(pin, use_pulseio=False)
    print(f"✅ DHT datchik sozlandi: {sensor_name}, pin: GPIO{Config.DHT_PIN}")
except Exception as e:
    print(f"⚠️ DHT datchikni sozlab bo'lmadi: {e}")

# ---------- GPIO (rele) ni sozlash ----------
device_controller = None
try:
    from backend.services.devices import DeviceController
    device_controller = DeviceController()
except Exception:
    pass

running = True


def get_devices():
    if device_controller:
        return device_controller.snapshot()["devices"]
    return {
        "drip_pump": False, "rain_pump": False,
        "photo_led": False, "insect_led": False,
        "cooler_1": False, "cooler_2": False,
    }


def base_topic():
    return f"{Config.MQTT_TOPIC_PREFIX}/{Config.MQTT_GREENHOUSE_ID}"


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_dht():
    """DHT datchikdan harorat va namlikni o'qiydi. Xato bo'lsa None qaytaradi."""
    if dht_sensor is None:
        return None, None
    try:
        temperature = dht_sensor.temperature
        humidity = dht_sensor.humidity
        return temperature, humidity
    except Exception:
        return None, None


# ---------- MQTT callbacks ----------
def on_connect(client, _userdata, _flags, reason_code, _properties=None):
    connected = str(reason_code) == "Success" or str(reason_code) == "0"
    if not connected:
        print(f"❌ MQTT connect xato: {reason_code}")
        return

    print(f"✅ MQTT serverga ulandi: {Config.MQTT_HOST}:{Config.MQTT_PORT}")
    client.subscribe(f"{base_topic()}/command", qos=1)
    client.publish(f"{base_topic()}/availability", "online", qos=1, retain=True)


def on_message(client, _userdata, message):
    if device_controller is None:
        return
    try:
        payload = json.loads(message.payload.decode("utf-8"))
    except json.JSONDecodeError:
        return

    try:
        device = payload.get("device")
        enabled = bool(payload.get("enabled", False))
        snapshot = device_controller.set_device(device, enabled, payload.get("source", "mqtt"))
        print(f"📩 Buyruq qabul qilindi: {device} -> {'ON' if enabled else 'OFF'}")

        state_payload = {
            "devices": snapshot["devices"],
            "source": "command",
            "command": snapshot.get("command"),
            "timestamp": now_iso(),
        }
        client.publish(f"{base_topic()}/state", json.dumps(state_payload), qos=0)
    except ValueError as error:
        print(f"❌ Buyruq xato: {error}")


# ---------- Telemetry ----------
def publish_telemetry(client):
    temperature, humidity = read_dht()
    devices = get_devices()

    if temperature is not None and humidity is not None:
        print(f"[{now_iso()}] ✅ YUBORILDI -> Harorat: {temperature}°C, Namlik: {humidity}%")
    else:
        print(f"[{now_iso()}] ⚠️ DIQQAT: Datchikdan signal yo'q!")

    payload = {
        "temperature": round(temperature, 1) if temperature is not None else None,
        "humidity": round(humidity) if humidity is not None else None,
        "soilMoisture": None,
        "light": None,
        "gasLevel": None,
        "gasDetected": False,
        "weather": {
            "condition": "MQTT IoT telemetriya",
            "outsideTemp": round(temperature, 1) if temperature is not None else None,
            "wind": 0,
            "uv": 0,
        },
        "devices": devices,
        "source": "raspberry-pi",
        "timestamp": now_iso(),
    }
    client.publish(f"{base_topic()}/telemetry", json.dumps(payload), qos=0)


# ---------- Automation ----------
def run_automation(client, temperature):
    if not Config.PI_AUTOMATION_ENABLED or device_controller is None:
        return
    if temperature is None:
        return

    changes = {}
    if temperature > Config.PI_TEMPERATURE_LIMIT:
        changes["cooler_1"] = True
    else:
        changes["cooler_1"] = False

    if temperature > Config.PI_TEMPERATURE_LIMIT + 1:
        changes["cooler_2"] = True
    else:
        changes["cooler_2"] = False

    for device, enabled in changes.items():
        current = get_devices().get(device)
        if current == enabled:
            continue
        snapshot = device_controller.set_device(device, enabled, "auto")
        command = snapshot.get("command") or {}
        if not command.get("ignored"):
            state_payload = {
                "devices": snapshot["devices"],
                "source": "auto",
                "command": command,
                "timestamp": now_iso(),
            }
            client.publish(f"{base_topic()}/state", json.dumps(state_payload), qos=0)
            print(f"🤖 Avtomatika: {device} -> {'ON' if enabled else 'OFF'}")


# ---------- Main ----------
def stop(_signum, _frame):
    global running
    running = False


def create_client():
    try:
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=Config.MQTT_PI_CLIENT_ID,
        )
    except AttributeError:
        client = mqtt.Client(client_id=Config.MQTT_PI_CLIENT_ID)

    if Config.MQTT_USERNAME:
        client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD or None)
    if Config.MQTT_TLS:
        client.tls_set()

    client.on_connect = on_connect
    client.on_message = on_message
    return client


def main():
    if not Config.MQTT_ENABLED:
        print("❌ MQTT_ENABLED=true qilib ishga tushiring.")
        return 1

    print("🚀 SmartFarm Pi Gateway ishga tushmoqda...")
    print(f"   MQTT Server: {Config.MQTT_HOST}:{Config.MQTT_PORT}")
    print(f"   DHT Sensor:  {Config.DHT_SENSOR}")
    print(f"   DHT Pin:     GPIO{Config.DHT_PIN}")
    print(f"   Greenhouse:  {Config.MQTT_GREENHOUSE_ID}")
    print()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    client = create_client()
    client.will_set(f"{base_topic()}/availability", "offline", qos=1, retain=True)
    client.connect(Config.MQTT_HOST, Config.MQTT_PORT, keepalive=60)
    client.loop_start()

    try:
        while running:
            temperature, humidity = read_dht()
            publish_telemetry(client)
            run_automation(client, temperature)
            time.sleep(Config.SENSOR_BROADCAST_SECONDS)
    finally:
        client.publish(f"{base_topic()}/availability", "offline", qos=1, retain=True)
        client.loop_stop()
        client.disconnect()
        if dht_sensor:
            dht_sensor.exit()
        print("👋 Pi Gateway to'xtatildi.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
