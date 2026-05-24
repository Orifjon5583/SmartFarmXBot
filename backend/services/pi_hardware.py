import time

from backend.config import Config


class ManualSwitchReader:
    def __init__(self):
        self.gpio = None
        self.available = False
        self.last_states = {}

        if not Config.USE_GPIO:
            return

        try:
            import RPi.GPIO as GPIO

            GPIO.setmode(GPIO.BCM)
            pull = GPIO.PUD_UP if Config.MANUAL_SWITCH_ACTIVE_LOW else GPIO.PUD_DOWN
            for pin in Config.MANUAL_SWITCH_PINS.values():
                GPIO.setup(pin, GPIO.IN, pull_up_down=pull)
            self.gpio = GPIO
            self.available = True
        except Exception:
            self.available = False

    def read_changes(self):
        if not self.available:
            return {}

        changes = {}
        for device, pin in Config.MANUAL_SWITCH_PINS.items():
            raw_value = self.gpio.input(pin)
            enabled = raw_value == 0 if Config.MANUAL_SWITCH_ACTIVE_LOW else raw_value == 1
            previous = self.last_states.get(device)

            if previous is None:
                self.last_states[device] = enabled
                continue

            if previous != enabled:
                time.sleep(Config.MANUAL_SWITCH_DEBOUNCE_SECONDS)
                raw_value = self.gpio.input(pin)
                enabled = raw_value == 0 if Config.MANUAL_SWITCH_ACTIVE_LOW else raw_value == 1
                if self.last_states.get(device) != enabled:
                    self.last_states[device] = enabled
                    changes[device] = enabled

        return changes

    def is_forcing_on(self, device):
        return bool(self.last_states.get(device))


class IrEventReader:
    def __init__(self):
        self.gpio = None
        self.available = False
        self.last_event_at = 0

        if not Config.USE_GPIO or not Config.IR_ENABLED:
            return

        try:
            import RPi.GPIO as GPIO

            GPIO.setmode(GPIO.BCM)
            pull = GPIO.PUD_UP if Config.IR_ACTIVE_LOW else GPIO.PUD_DOWN
            GPIO.setup(Config.IR_PIN, GPIO.IN, pull_up_down=pull)
            self.gpio = GPIO
            self.available = True
        except Exception:
            self.available = False

    def read_event(self):
        if not self.available:
            return None

        raw_value = self.gpio.input(Config.IR_PIN)
        active = raw_value == 0 if Config.IR_ACTIVE_LOW else raw_value == 1
        now = time.monotonic()

        if not active or now - self.last_event_at < Config.IR_EVENT_COOLDOWN_SECONDS:
            return None

        self.last_event_at = now
        return {"pin": Config.IR_PIN, "message": "IR signal qabul qilindi"}


class Lcd16x2:
    ENABLE = 0b00000100
    BACKLIGHT = 0b00001000
    COMMAND = 0
    DATA = 1

    def __init__(self):
        self.bus = None
        self.available = False
        self.last_text = None

        if not Config.LCD_ENABLED:
            return

        try:
            from smbus2 import SMBus

            self.bus = SMBus(Config.LCD_I2C_BUS)
            self._init_display()
            self.available = True
        except Exception:
            self.available = False

    def update(self, sensors, devices):
        if not self.available:
            return

        # Carousel: rotate between pages every 3 cycles (15 sec with 5s interval)
        if not hasattr(self, '_page'):
            self._page = 0
            self._cycle = 0

        self._cycle += 1
        if self._cycle >= 3:
            self._cycle = 0
            self._page = (self._page + 1) % 4

        temp = sensors.get('temperature', '--')
        hum = sensors.get('humidity', '--')
        soil = sensors.get('soilMoisture', '--')
        light = sensors.get('light', '--')
        gas = sensors.get('gasLevel', 0)
        gas_det = sensors.get('gasDetected', False)
        active_count = sum(1 for enabled in devices.values() if enabled)

        if self._page == 0:
            line_1 = f"Harorat: {temp}C"
            line_2 = f"Namlik:  {hum}%"
        elif self._page == 1:
            line_1 = f"Tuproq: {soil}%"
            line_2 = f"Yorug: {light} lux"
        elif self._page == 2:
            line_1 = f"Gaz: {gas}%"
            line_2 = "XAVF!" if gas_det else "Normal holat"
        else:
            line_1 = f"Relay: {active_count} ta ON"
            line_2 = "SmartFarm v1.0"

        text = (line_1[:16], line_2[:16])

        if text == self.last_text:
            return

        self.clear()
        self.write_line(0, text[0])
        self.write_line(1, text[1])
        self.last_text = text

    def clear(self):
        self._write_byte(0x01, self.COMMAND)
        time.sleep(0.002)

    def write_line(self, row, text):
        self._write_byte(0x80 + (0x40 if row else 0), self.COMMAND)
        for char in text.ljust(16)[:16]:
            self._write_byte(ord(char), self.DATA)

    def _init_display(self):
        time.sleep(0.05)
        for command in (0x33, 0x32, 0x28, 0x0C, 0x06, 0x01):
            self._write_byte(command, self.COMMAND)
            time.sleep(0.005)

    def _write_byte(self, bits, mode):
        high = mode | (bits & 0xF0) | self.BACKLIGHT
        low = mode | ((bits << 4) & 0xF0) | self.BACKLIGHT
        self._toggle(high)
        self._toggle(low)

    def _toggle(self, bits):
        self.bus.write_byte(Config.LCD_I2C_ADDRESS, bits | self.ENABLE)
        time.sleep(0.0005)
        self.bus.write_byte(Config.LCD_I2C_ADDRESS, bits & ~self.ENABLE)
        time.sleep(0.0001)
