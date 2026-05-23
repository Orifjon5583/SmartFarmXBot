from datetime import datetime, timedelta, timezone
from threading import Lock

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit

from backend.config import Config
from backend.services.devices import DeviceController
from backend.services.history import HistoryStore
from backend.services.mqtt_bus import MQTTBridge
from backend.services.sensors import SensorService


history_store = HistoryStore()
sensor_service = SensorService(history_store)
device_controller = DeviceController()
socketio = SocketIO(async_mode="threading", cors_allowed_origins=Config.CORS_ORIGINS)
background_lock = Lock()
background_started = False
mqtt_bridge = MQTTBridge()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SOCKET_TOKENS and next(iter(Config.SOCKET_TOKENS)) or "greenhouse-dev"
    socketio.init_app(app)
    history_store.initialize()
    _setup_mqtt_bridge()

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"ok": True, "service": "greenhouse-api"})

    @app.route("/api/sensors", methods=["GET"])
    def sensors():
        latest, _point = sensor_service.record_current()
        history_store.cleanup()
        return jsonify(latest)

    @app.route("/api/history", methods=["GET"])
    def history():
        start, end, limit = _history_query()
        return jsonify(sensor_service.history_data(start=start, end=end, limit=limit))

    @app.route("/api/status", methods=["GET"])
    def status():
        return jsonify(_status_payload(device_controller.snapshot()))

    @app.route("/api/camera", methods=["GET"])
    def camera():
        return jsonify(
            {
                "streamUrl": "/api/camera/stream",
                "aiStatus": "O'simliklar sog'lom",
                "confidence": 94,
                "timelapseFrames": 96,
            }
        )

    @app.route("/api/device/<device>", methods=["POST", "OPTIONS"])
    def device(device):
        if request.method == "OPTIONS":
            return ("", 204)

        payload = request.get_json(silent=True) or {}
        try:
            enabled = payload.get("enabled", False)
            source = payload.get("source", "site")
            snapshot = device_controller.set_device(device, enabled, source)
            history_store.insert_device_event(snapshot.get("command"))
            _publish_device_command(snapshot.get("command"))
            socketio.emit("device:update", snapshot)
            socketio.emit("status:update", _status_payload(snapshot))
            command = snapshot.get("command") or {}
            return jsonify({"ok": True, "message": command.get("message", "Holat yangilandi."), **snapshot})
        except ValueError as error:
            return jsonify({"ok": False, "message": str(error)}), 404

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"ok": False, "message": "Endpoint topilmadi."}), 404

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"ok": False, "message": "Server ichki xatosi."}), 500

    return app


def _setup_mqtt_bridge():
    mqtt_bridge.on_telemetry = _handle_mqtt_telemetry
    mqtt_bridge.on_state = _handle_mqtt_state
    mqtt_bridge.on_event = _handle_mqtt_event
    mqtt_bridge.start()


def _handle_mqtt_telemetry(payload):
    latest = sensor_service.update_external_snapshot(payload)
    point = history_store.insert_sensor(latest) or HistoryStore.sensor_point(latest)

    devices = payload.get("devices") if isinstance(payload, dict) else None
    if isinstance(devices, dict):
        device_snapshot = device_controller.apply_external_state(devices, source=payload.get("source", "mqtt"))
    else:
        device_snapshot = device_controller.snapshot()

    socketio.emit("sensor:update", latest)
    socketio.emit("history:append", point)
    socketio.emit("device:update", device_snapshot)
    socketio.emit("status:update", _status_payload(device_snapshot))


def _handle_mqtt_state(payload):
    devices = payload.get("devices") if isinstance(payload, dict) else payload
    if devices is None and isinstance(payload, dict):
        devices = payload
    device_snapshot = device_controller.apply_external_state(devices, source=payload.get("source", "mqtt") if isinstance(payload, dict) else "mqtt")
    socketio.emit("device:update", device_snapshot)
    socketio.emit("status:update", _status_payload(device_snapshot))


def _handle_mqtt_event(payload):
    socketio.emit("iot:event", payload)
    socketio.emit("status:update", _status_payload(device_controller.snapshot()))


def _publish_device_command(command):
    if not command or command.get("ignored"):
        return False

    return mqtt_bridge.publish_command(
        {
            "device": command.get("device"),
            "enabled": command.get("enabled"),
            "source": command.get("source", "site"),
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        }
    )


def _status_payload(device_snapshot):
    return {
        **sensor_service.status(device_snapshot),
        "mqtt": mqtt_bridge.status(),
        "mqttLastMessageAt": mqtt_bridge.last_message_at,
    }


def _history_query():
    end = _parse_datetime(request.args.get("to")) or datetime.now(timezone.utc)
    hours = request.args.get("hours", type=float)
    start = _parse_datetime(request.args.get("from"))

    if start is None and hours is None:
        hours = Config.HISTORY_DEFAULT_HOURS
    if start is None and hours is not None:
        start = end - timedelta(hours=hours)

    limit = request.args.get("limit", default=Config.HISTORY_QUERY_LIMIT, type=int)
    return start, end, limit


def _parse_datetime(value):
    if not value:
        return None

    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return None


def _socket_token(auth):
    if isinstance(auth, dict) and auth.get("token"):
        return str(auth["token"])

    header = request.headers.get("Authorization", "")
    if header.lower().startswith("bearer "):
        return header.split(" ", 1)[1].strip()

    return request.args.get("token", "")


def _socket_authorized(auth):
    if not Config.SOCKET_AUTH_REQUIRED:
        return True

    token = _socket_token(auth)
    if not token:
        return False

    if Config.SOCKET_TOKENS:
        return token in Config.SOCKET_TOKENS

    return token == "demo-token" or token.startswith("demo-token-")


def _ensure_background_task():
    global background_started

    with background_lock:
        if background_started:
            return

        socketio.start_background_task(_sensor_broadcast_loop)
        background_started = True


def _sensor_broadcast_loop():
    while True:
        latest, point = sensor_service.record_current()
        history_store.cleanup()
        device_snapshot = device_controller.snapshot()
        socketio.emit("sensor:update", latest)
        socketio.emit("history:append", point)
        socketio.emit("device:update", device_snapshot)
        socketio.emit("status:update", _status_payload(device_snapshot))
        socketio.sleep(Config.SENSOR_BROADCAST_SECONDS)


@socketio.on("connect")
def socket_connect(auth):
    if not _socket_authorized(auth):
        return False

    _ensure_background_task()
    device_snapshot = device_controller.snapshot()
    emit("sensor:update", sensor_service.current())
    emit("device:update", device_snapshot)
    emit("status:update", _status_payload(device_snapshot))
    emit("history:init", sensor_service.history_data(limit=Config.HISTORY_DEFAULT_HOURS))


@socketio.on("device:set")
def socket_set_device(payload):
    payload = payload or {}
    try:
        snapshot = device_controller.set_device(
            payload.get("device"),
            payload.get("enabled", False),
            payload.get("source", "site"),
        )
        history_store.insert_device_event(snapshot.get("command"))
        _publish_device_command(snapshot.get("command"))
        socketio.emit("device:update", snapshot)
        socketio.emit("status:update", _status_payload(snapshot))
        return {"ok": True, **snapshot}
    except ValueError as error:
        return {"ok": False, "message": str(error)}


app = create_app()


if __name__ == "__main__":
    socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        allow_unsafe_werkzeug=True,
    )
