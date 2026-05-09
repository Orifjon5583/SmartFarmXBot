from datetime import datetime, timezone

from backend.config import Config


class DeviceController:
    def __init__(self):
        self.states = {
            "fan": False,
            "pump": False,
            "light": False,
            "camera": True,
        }
        self.logs = []
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
                GPIO.output(pin, GPIO.LOW)
            self.gpio = GPIO
            self.gpio_available = True
        except Exception as error:
            self.gpio_available = False
            self.logs.append(self._log("system", "GPIO ishga tushmadi", str(error)))

    def set_device(self, device, enabled):
        if device not in self.states:
            raise ValueError(f"Noma'lum qurilma: {device}")

        enabled = bool(enabled)
        self.states[device] = enabled

        if self.gpio_available:
            pin = Config.GPIO_PINS[device]
            self.gpio.output(pin, self.gpio.HIGH if enabled else self.gpio.LOW)

        event = "yoqildi" if enabled else "o'chirildi"
        self.logs.insert(0, self._log(device, event, "GPIO" if self.gpio_available else "mock"))
        self.logs = self.logs[:50]
        return self.snapshot()

    def snapshot(self):
        return {
            "devices": self.states,
            "gpio": self.gpio_status(),
            "gpioAvailable": self.gpio_available,
            "logs": self.logs[:10],
        }

    def gpio_status(self):
        labels = {
            "fan": "Ventilyator relesi",
            "pump": "Nasos relesi",
            "light": "Ostirish chirogi",
            "camera": "Kamera",
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
