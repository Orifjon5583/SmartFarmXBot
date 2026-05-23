import json
from datetime import datetime, timezone

from backend.config import Config

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None


class MQTTBridge:
    def __init__(self, on_telemetry=None, on_state=None, on_event=None):
        self.on_telemetry = on_telemetry
        self.on_state = on_state
        self.on_event = on_event
        self.client = None
        self.connected = False
        self.error = None
        self.last_message_at = None

    @property
    def base_topic(self):
        return f"{Config.MQTT_TOPIC_PREFIX}/{Config.MQTT_GREENHOUSE_ID}"

    def start(self):
        if self.client is not None:
            return True

        if not Config.MQTT_ENABLED:
            self.error = "MQTT o'chirilgan"
            return False

        if mqtt is None:
            self.error = "paho-mqtt o'rnatilmagan"
            return False

        try:
            try:
                self.client = mqtt.Client(
                    mqtt.CallbackAPIVersion.VERSION2,
                    client_id=Config.MQTT_CLIENT_ID,
                )
            except AttributeError:
                self.client = mqtt.Client(client_id=Config.MQTT_CLIENT_ID)

            if Config.MQTT_USERNAME:
                self.client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD or None)
            if Config.MQTT_TLS:
                self.client.tls_set()

            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            self.client.connect_async(Config.MQTT_HOST, Config.MQTT_PORT, keepalive=60)
            self.client.loop_start()
            return True
        except Exception as error:
            self.connected = False
            self.error = str(error)
            return False

    def publish_command(self, command):
        return self.publish("command", command, qos=1)

    def publish(self, topic_suffix, payload, qos=0, retain=False):
        if not self.client or not Config.MQTT_ENABLED:
            return False

        topic = f"{self.base_topic}/{topic_suffix}"
        try:
            self.client.publish(topic, json.dumps(payload), qos=qos, retain=retain)
            return True
        except Exception as error:
            self.error = str(error)
            return False

    def status(self):
        if not Config.MQTT_ENABLED:
            return "mqtt o'chirilgan"
        if self.connected:
            return "mqtt ulangan"
        return f"mqtt xato: {self.error}" if self.error else "mqtt ulanmoqda"

    def _on_connect(self, client, _userdata, _flags, reason_code, _properties=None):
        self.connected = str(reason_code) == "Success" or str(reason_code) == "0"
        self.error = None if self.connected else f"connect code {reason_code}"

        if self.connected:
            client.subscribe(f"{self.base_topic}/telemetry", qos=0)
            client.subscribe(f"{self.base_topic}/state", qos=0)
            client.subscribe(f"{self.base_topic}/event", qos=0)
            client.publish(f"{self.base_topic}/backend/availability", "online", qos=1, retain=True)

    def _on_disconnect(self, _client, _userdata, reason_code, _properties=None):
        self.connected = False
        self.error = f"disconnect code {reason_code}"

    def _on_message(self, _client, _userdata, message):
        payload = self._decode_payload(message.payload)
        self.last_message_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

        if message.topic.endswith("/telemetry") and self.on_telemetry:
            self.on_telemetry(payload)
        elif message.topic.endswith("/state") and self.on_state:
            self.on_state(payload)
        elif message.topic.endswith("/event") and self.on_event:
            self.on_event(payload)

    @staticmethod
    def _decode_payload(raw_payload):
        text = raw_payload.decode("utf-8", errors="replace")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"message": text}
