# Issiqxona Nexus Flask Backend

## Ishga tushirish

```powershell
python -m pip install -r requirements.txt
npm run backend
```

Backend default port:

```text
http://127.0.0.1:5000
```

Frontendni backendga ulash uchun `.env` fayl yarating:

```env
VITE_API_URL=http://127.0.0.1:5000
VITE_USE_MOCK_API=false
```

Keyin frontend dev serverni qayta ishga tushiring:

```powershell
npm run dev
```

## Raspberry Pi GPIO

Real GPIO va sensorlarni ishlatish uchun Raspberry Pi ichida:

```env
USE_GPIO=true
USE_REAL_SENSORS=true
GPIO_FAN_PIN=4
GPIO_PUMP_PIN=17
GPIO_LIGHT_PIN=22
GPIO_CAMERA_PIN=27
DHT_PIN=5
DHT_SENSOR=DHT22
SOIL_ADC_CHANNEL=0
LIGHT_ADC_CHANNEL=1
SOIL_DRY_VALUE=850
SOIL_WET_VALUE=350
```

Pi ichida Python kutubxonalarini o'rnatish:

```bash
python -m pip install -r requirements-pi.txt
```

`requirements.txt` oddiy kompyuterda mock rejim uchun, `requirements-pi.txt` esa Raspberry Pi uchun.

### Raspberry Pi 4 ulanish pinlari

Kod BCM raqamlashdan foydalanadi. Qavs ichida Raspberry Pi 4 platasidagi fizik pin raqami berilgan.

| Qurilma | GPIO BCM | Fizik pin | Ulanish |
| --- | ---: | ---: | --- |
| Ventilyator relesi IN | GPIO4 | 7 | Relay IN1 |
| Suv nasosi relesi IN | GPIO17 | 11 | Relay IN2 |
| O'stirish chirog'i relesi IN | GPIO22 | 15 | Relay IN3 |
| Kamera quvvat/rele IN | GPIO27 | 13 | Relay IN4 |
| DHT22 DATA | GPIO5 | 29 | DHT22 data, 10k pull-up bilan 3.3V ga |
| DHT22 VCC | 3.3V | 1 | Sensor quvvati |
| DHT22 GND | GND | 6 | Umumiy minus |
| MCP3008 VDD/VREF | 3.3V | 1 | ADC quvvati |
| MCP3008 AGND/DGND | GND | 9 | Umumiy minus |
| MCP3008 CLK | GPIO11/SCLK | 23 | SPI clock |
| MCP3008 DOUT | GPIO9/MISO | 21 | SPI MISO |
| MCP3008 DIN | GPIO10/MOSI | 19 | SPI MOSI |
| MCP3008 CS/SHDN | GPIO8/CE0 | 24 | SPI CE0 |
| Tuproq namligi AO | MCP3008 CH0 | - | Analog signal |
| LDR yorug'lik sensori AO | MCP3008 CH1 | - | Analog signal |

Relay moduliga tashqi 5V quvvat bering va Raspberry Pi GND bilan relay GND ni umumiy qiling. Nasos, chiroq yoki ventilyator 220V bo'lsa, ulashni xavfsizlik qoidalari bilan bajaring.

Raspberry Pi ichida SPI yoqilgan bo'lishi kerak:

```bash
sudo raspi-config
```

`Interface Options` -> `SPI` -> `Enable`.

## Telegram bot funksiyalari

Dashboard Settings sahifasidan token va Chat ID saqlanadi.

Endpointlar:

```text
GET  /api/telegram/settings
POST /api/telegram/settings
POST /api/telegram/test
POST /api/telegram/notify
```

Qurilma holati `POST /api/device/fan`, `pump`, `light`, `camera` orqali o'zgarsa, backend Telegramga qisqa bildirishnoma yuborishga urinadi.
