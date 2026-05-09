from flask import Flask, jsonify, request

from backend.config import Config
from backend.services.devices import DeviceController
from backend.services.sensors import SensorService
from backend.services.telegram import (
    notify_device_change,
    public_telegram_settings,
    save_telegram_settings,
    send_telegram_message,
    verify_telegram,
)


sensor_service = SensorService()
device_controller = DeviceController()


def create_app():
    app = Flask(__name__)

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
        return jsonify(sensor_service.current())

    @app.route("/api/history", methods=["GET"])
    def history():
        return jsonify(sensor_service.history_data())

    @app.route("/api/status", methods=["GET"])
    def status():
        return jsonify(sensor_service.status(device_controller.snapshot()))

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
            snapshot = device_controller.set_device(device, payload.get("enabled", False))
            notify_ok, notify_message = notify_device_change(device, payload.get("enabled", False))
            return jsonify({"ok": True, "notification": {"ok": notify_ok, "message": notify_message}, **snapshot})
        except ValueError as error:
            return jsonify({"ok": False, "message": str(error)}), 404

    @app.route("/api/telegram/settings", methods=["GET", "POST", "OPTIONS"])
    def telegram_settings():
        if request.method == "OPTIONS":
            return ("", 204)

        if request.method == "GET":
            return jsonify({"ok": True, "telegram": public_telegram_settings()})

        payload = request.get_json(silent=True) or {}
        settings = save_telegram_settings(
            payload.get("token"),
            payload.get("chatId"),
            payload.get("enabled", True),
        )
        return jsonify({"ok": True, "message": "Telegram sozlamalari backendga saqlandi.", "telegram": settings})

    @app.route("/api/telegram/test", methods=["POST", "OPTIONS"])
    def telegram_test():
        if request.method == "OPTIONS":
            return ("", 204)

        payload = request.get_json(silent=True) or {}
        token = payload.get("token")
        chat_id = payload.get("chatId")
        ok, message = verify_telegram(token, chat_id)
        if ok:
            save_telegram_settings(token, chat_id, payload.get("enabled", True))
        return jsonify({"ok": ok, "message": message}), 200 if ok else 400

    @app.route("/api/telegram/notify", methods=["POST", "OPTIONS"])
    def telegram_notify():
        if request.method == "OPTIONS":
            return ("", 204)

        payload = request.get_json(silent=True) or {}
        text = (payload.get("text") or "").strip()
        if not text:
            return jsonify({"ok": False, "message": "Xabar matni kiritilmadi."}), 400

        ok, message = send_telegram_message(text)
        return jsonify({"ok": ok, "message": message}), 200 if ok else 400

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"ok": False, "message": "Endpoint topilmadi."}), 404

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"ok": False, "message": "Server ichki xatosi."}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
