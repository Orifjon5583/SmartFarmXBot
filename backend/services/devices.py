from datetime import datetime, timedelta, timezone
from threading import Lock

from backend.config import Config


class DeviceController:
    def __init__(self):
        self.states = {
            "drip_pump": False,
            "rain_pump": False,
            "photo_led": False,
            "insect_led": False,
            "cooler_1": False,
            "cooler_2": False,
        }
        self.logs = []
        self.last_commands = {}
        self.manual_override_until = {}
        self.lock = Lock()
        self.gpio = None
        self.gpio_available = False

        if Config.USE_GPIO:
            self._setup_gpio()

    def _setup_gpio(self):
        try:
            import RPi.GPIO as GPIO

            GPIO.setmode(GPIO.BCM)
            for pin in Config.GPIO_PINS.values():
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, self._gpio_value(False))
            self.gpio = GPIO
            self.gpio_available = True
        except Exception as error:
            self.gpio_available = False
            self.logs.append(self._log("system", "GPIO ishga tushmadi", str(error)))

    def set_device(self, device, enabled, source="site"):
        requested_device = device
        device = Config.GPIO_ALIASES.get(device, device)

        if device not in self.states:
            raise ValueError(f"Noma'lum qurilma: {device}")

        enabled = bool(enabled)
        source = (source or "site").strip().lower()
        now = datetime.now(timezone.utc).astimezone()

        with self.lock:
            current = self.states[device]
            manual_until = self.manual_override_until.get(device)
            auto_blocked = (
                source == "auto"
                and manual_until is not None
                and now < manual_until
                and current != enabled
            )

            command = {
                "device": device,
                "requestedDevice": requested_device,
                "enabled": enabled,
                "source": source,
                "changed": False,
                "ignored": auto_blocked,
                "message": "",
            }

            if auto_blocked:
                command["message"] = "Qo'l boshqaruv ustuvorligi tugamaguncha auto buyruq o'tkazib yuborildi."
                self._remember_command(device, command)
                self._insert_log(device, "auto o'tkazildi", source)
                return self.snapshot(command)

            if source != "auto":
                self.manual_override_until[device] = now + timedelta(seconds=Config.MANUAL_OVERRIDE_SECONDS)

            if current == enabled:
                command["message"] = "Holat allaqachon shu qiymatda, GPIO qayta yozilmadi."
                self._remember_command(device, command)
                self._insert_log(device, "takroriy buyruq", source)
                return self.snapshot(command)

            self.states[device] = enabled

            if self.gpio_available:
                pin = Config.GPIO_PINS[device]
                self.gpio.output(pin, self._gpio_value(enabled))

            command["changed"] = True
            command["message"] = "GPIO holati yangilandi." if self.gpio_available else "Mock holat yangilandi."
            self._remember_command(device, command)
            event = "yoqildi" if enabled else "o'chirildi"
            self._insert_log(device, event, source)
            return self.snapshot(command)

    def apply_external_state(self, states, source="mqtt"):
        if not isinstance(states, dict):
            return self.snapshot()

        source = (source or "mqtt").strip().lower()
        changed_devices = []

        with self.lock:
            for requested_device, enabled in states.items():
                device = Config.GPIO_ALIASES.get(requested_device, requested_device)
                if device not in self.states:
                    continue

                enabled = bool(enabled)
                if self.states[device] == enabled:
                    continue

                self.states[device] = enabled
                changed_devices.append(device)
                self._insert_log(device, "tashqi holat", source)

            if changed_devices:
                command = {
                    "device": ",".join(changed_devices),
                    "requestedDevice": "external",
                    "enabled": None,
                    "source": source,
                    "changed": True,
                    "ignored": False,
                    "message": "MQTT/manual/IR holati sinxronlandi.",
                }
                self._remember_command("external", command)
                return self.snapshot(command)

        return self.snapshot()

    def snapshot(self, command=None):
        return {
            "devices": dict(self.states),
            "gpio": self.gpio_status(),
            "gpioAvailable": self.gpio_available,
            "lastCommands": dict(self.last_commands),
            "logs": self.logs[:10],
            "command": command,
        }

    def gpio_status(self):
        labels = {
            "drip_pump": "Tomchilatib sug'orish nasosi",
            "rain_pump": "Yomg'irlatib sug'orish nasosi",
            "photo_led": "Fotosintez LED chiroq",
            "insect_led": "Hashoratga qarshi LED",
            "cooler_1": "Kuler 1",
            "cooler_2": "Kuler 2",
        }
        return [
            {
                "pin": Config.GPIO_PINS[device],
                "label": labels[device],
                "active": state,
            }
            for device, state in self.states.items()
        ]

    @staticmethod
    def _log(device, event, value):
        return {
            "time": datetime.now(timezone.utc).astimezone().strftime("%H:%M"),
            "device": device,
            "event": event,
            "value": value,
        }

    def _insert_log(self, device, event, source):
        self.logs.insert(0, self._log(device, event, f"{source} / {'GPIO' if self.gpio_available else 'mock'}"))
        self.logs = self.logs[:50]

    def _remember_command(self, device, command):
        self.last_commands[device] = {
            **command,
            "time": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        }

    def _gpio_value(self, enabled):
        if Config.GPIO_ACTIVE_LOW:
            return 0 if enabled else 1
        return 1 if enabled else 0
