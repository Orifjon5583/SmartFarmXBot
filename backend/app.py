from flask import Flask, jsonify, request

from backend.config import Config
from backend.services.devices import DeviceController
from backend.services.sensors import SensorService


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
            enabled = payload.get("enabled", False)
            source = payload.get("source", "site")
            snapshot = device_controller.set_device(device, enabled, source)
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


app = create_app()


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
