import json
import signal
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from backend.config import Config
from backend.services.devices import DeviceController
from backend.services.pi_hardware import IrEventReader, Lcd16x2, ManualSwitchReader
from backend.services.sensors import SensorService


# IMPORTANT: SensorService must init BEFORE DeviceController
# because adafruit_dht and RPi.GPIO conflict on GPIO chip access
sensor_service = SensorService()
device_controller = DeviceController()
manual_switches = ManualSwitchReader()
ir_reader = IrEventReader()
lcd = Lcd16x2()
running = True

# LED strip direct control
led_strip_gpio = None
led_strip_state = False
if Config.LED_STRIP_ENABLED:
    try:
        import RPi.GPIO as _GPIO
        _GPIO.setmode(_GPIO.BCM)
        _GPIO.setup(Config.LED_STRIP_PIN, _GPIO.OUT)
        _GPIO.output(Config.LED_STRIP_PIN, _GPIO.LOW)
        led_strip_gpio = _GPIO
        print(f"✅ LED strip sozlandi: GPIO{Config.LED_STRIP_PIN}")
    except Exception as e:
        print(f"⚠️ LED strip xato: {e}")


def base_topic():
    return f"{Config.MQTT_TOPIC_PREFIX}/{Config.MQTT_GREENHOUSE_ID}"


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def on_connect(client, _userdata, _flags, reason_code, _properties=None):
    connected = str(reason_code) == "Success" or str(reason_code) == "0"
    if not connected:
        print(f"MQTT connect xato: {reason_code}")
        return

    client.subscribe(f"{base_topic()}/command", qos=1)
    client.publish(f"{base_topic()}/availability", "online", qos=1, retain=True)
    publish_state(client, "boot")


def on_message(client, _userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
    except json.JSONDecodeError:
        publish_event(client, "command_error", {"message": "JSON xato"})
        return

    try:
        device = payload.get("device")
        enabled = bool(payload.get("enabled", False))
        if manual_switches.is_forcing_on(device) and not enabled:
            publish_event(
                client,
                "manual_override",
                {"device": device, "message": "Manual switch yoqilgan, sayt buyrug'i o'tkazilmadi."},
            )
            publish_state(client, "manual_override")
            return

        snapshot = device_controller.set_device(
            device,
            enabled,
            payload.get("source", "mqtt"),
        )
        publish_state(client, "command", snapshot.get("command"))
    except ValueError as error:
        publish_event(client, "command_error", {"message": str(error), "payload": payload})


def publish_telemetry(client):
    sensors = sensor_service.current()
    devices = device_controller.snapshot()["devices"]
    lcd.update(sensors, devices)
    
    temp = sensors.get("temperature")
    hum = sensors.get("humidity")
    if temp is None or hum is None:
        print(f"[{now_iso()}] ⚠️ DIQQAT: Datchikdan signal yo'q! (Simlarni yoki DHT turini tekshiring)")
    else:
        light_val = sensors.get("light", "?")
        gas_val = sensors.get("gasLevel", "?")
        gas_det = "⚠️GAZ" if sensors.get("gasDetected") else "ok"
        soil_val = sensors.get("soilMoisture", "?")
        print(f"[{now_iso()}] ✅ YUBORILDI -> Harorat: {temp}°C, Namlik: {hum}%, Yorug'lik: {light_val}, Gaz: {gas_val}%({gas_det}), Tuproq: {soil_val}%")
        
    payload = {
        **sensors,
        "devices": devices,
        "manualSwitchesAvailable": manual_switches.available,
        "irAvailable": ir_reader.available,
        "lcdAvailable": lcd.available,
        "source": "raspberry-pi",
        "timestamp": now_iso(),
    }
    client.publish(f"{base_topic()}/telemetry", json.dumps(payload), qos=0)


def publish_state(client, source, command=None):
    payload = {
        "devices": device_controller.snapshot()["devices"],
        "source": source,
        "command": command,
        "timestamp": now_iso(),
    }
    client.publish(f"{base_topic()}/state", json.dumps(payload), qos=0)


def publish_event(client, event, data=None):
    payload = {
        "event": event,
        "data": data or {},
        "timestamp": now_iso(),
    }
    client.publish(f"{base_topic()}/event", json.dumps(payload), qos=0)


def automation_state(sensors):
    if not Config.PI_AUTOMATION_ENABLED:
        return {}

    temperature = _number(sensors.get("temperature"))
    soil = _number(sensors.get("soilMoisture"))
    light = _number(sensors.get("light"))
    gas_level = _number(sensors.get("gasLevel"))
    gas_detected = bool(sensors.get("gasDetected"))

    next_state = {}
    if temperature is not None:
        next_state["cooler_1"] = temperature > Config.PI_TEMPERATURE_LIMIT
        next_state["cooler_2"] = temperature > Config.PI_TEMPERATURE_LIMIT + 1
    if soil is not None:
        next_state["drip_pump"] = soil < Config.PI_MOISTURE_LIMIT
        next_state["rain_pump"] = soil < Config.PI_MOISTURE_LIMIT - 12
    if light is not None:
        next_state["photo_led"] = light < Config.PI_LIGHT_LIMIT
        next_state["insect_led"] = light < Config.PI_LIGHT_LIMIT
    if gas_detected or (gas_level is not None and gas_level >= Config.PI_GAS_DANGER_LIMIT):
        next_state["cooler_1"] = True
        next_state["cooler_2"] = True
        next_state["photo_led"] = False
        next_state["insect_led"] = False

    return next_state


def run_local_automation(client, sensors):
    for device, enabled in automation_state(sensors).items():
        before = device_controller.snapshot()["devices"].get(device)
        if before == enabled:
            continue

        snapshot = device_controller.set_device(device, enabled, "auto")
        command = snapshot.get("command") or {}
        if before != snapshot["devices"].get(device) and not command.get("ignored"):
            publish_state(client, "auto", command)


def handle_manual_switches(client):
    changes = manual_switches.read_changes()
    for device, enabled in changes.items():
        snapshot = device_controller.set_device(device, enabled, "manual")
        publish_state(client, "manual", snapshot.get("command"))
        publish_event(client, "manual_switch", {"device": device, "enabled": enabled})


def handle_ir(client):
    event = ir_reader.read_event()
    if event:
        publish_event(client, "ir_signal", event)


def update_led_strip(sensors):
    """Turn LED strip ON when dark, OFF when light."""
    global led_strip_state

    if not led_strip_gpio or not Config.LED_STRIP_ENABLED:
        return

    is_dark = sensors.get("isDark", False)

    if is_dark and not led_strip_state:
        led_strip_gpio.output(Config.LED_STRIP_PIN, led_strip_gpio.HIGH)
        led_strip_state = True
        print(f"[{now_iso()}] 💡 LED yoqildi (qorong'i)")
    elif not is_dark and led_strip_state:
        led_strip_gpio.output(Config.LED_STRIP_PIN, led_strip_gpio.LOW)
        led_strip_state = False
        print(f"[{now_iso()}] 🌙 LED o'chirildi (yorug')")


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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
        print("MQTT_ENABLED=true qilib ishga tushiring.")
        return 1

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    client = create_client()
    client.will_set(f"{base_topic()}/availability", "offline", qos=1, retain=True)
    client.connect(Config.MQTT_HOST, Config.MQTT_PORT, keepalive=60)
    client.loop_start()

    try:
        while running:
            handle_manual_switches(client)
            handle_ir(client)
            sensors = sensor_service.current()
            run_local_automation(client, sensors)
            update_led_strip(sensors)
            lcd.update(sensors, device_controller.snapshot()["devices"])
            publish_telemetry(client)
            time.sleep(Config.SENSOR_BROADCAST_SECONDS)
    finally:
        if led_strip_gpio:
            led_strip_gpio.output(Config.LED_STRIP_PIN, led_strip_gpio.LOW)
        client.publish(f"{base_topic()}/availability", "offline", qos=1, retain=True)
        client.loop_stop()
        client.disconnect()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
