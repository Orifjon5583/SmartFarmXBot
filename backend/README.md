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

## Ma'lumot oqimi

Raspberry Pi ichida backend GPIO va sensorlarni o'qiydi, frontend esa faqat API orqali buyruq beradi:

```text
DHT22 / tuproq ADC / fotorezistor -> backend SensorService -> GET /api/sensors -> React dashboard
React tugma yoki avto rejim -> POST /api/device/<device> -> backend DeviceController -> GPIO relay
GET /api/status -> qurilma holati, GPIO pinlar va loglar -> React dashboard
Socket.IO sensor:update/history:append/device:update -> real vaqt paneli
MQTT smartfarm/<greenhouse>/telemetry/state/command -> real IoT controller bilan almashuv
```

Qurilma API nomlari:

```text
drip_pump  -> tomchilatib sug'orish nasosi
rain_pump  -> yomg'irlatib sug'orish nasosi
photo_led  -> kechki fotosintez LED
insect_led -> hashoratga qarshi LED
cooler_1   -> birinchi kuler
cooler_2   -> ikkinchi kuler
```

Ikki tomondan buyruq kelishi ham hisobga olingan:

- Bir xil buyruq qayta kelsa, masalan relay yoniq paytda yana `enabled=true`, backend `changed=false` qaytaradi va GPIO qayta yozilmaydi.
- Saytdan yoki qo'l boshqaruvdan kelgan buyruqdan keyin `MANUAL_OVERRIDE_SECONDS` davomida auto rejim qarama-qarshi buyruq yuborsa, backend uni o'tkazib yuboradi.
- Bir vaqtda ikki so'rov kelsa, `DeviceController` ichidagi lock ularni navbat bilan bajaradi. Oxirgi haqiqiy buyruq holatni belgilaydi.

Buyruq namunasi:

```json
{
  "enabled": true,
  "source": "site"
}
```

`source` qiymatlari: `site`, `manual`, `ir`, `auto`. Kelajakda IR tugmalarini backendga ulaganda ham shu API yoki shu controller ishlatiladi.

Frontendni backendga ulash uchun `.env` fayl yarating:

```env
VITE_API_URL=http://127.0.0.1:5000
VITE_USE_MOCK_API=false
```

Keyin frontend dev serverni qayta ishga tushiring:

```powershell
npm run dev
```

## Real vaqt Socket.IO

Backend `Flask-SocketIO` orqali `/socket.io` endpointini ochadi. Ulanish auth token bilan amalga oshadi:

```js
io("http://127.0.0.1:5000", {
  auth: { token: "demo-token-..." }
})
```

Development rejimida frontend login yaratadigan `demo-token-*` tokenlari qabul qilinadi. Production uchun `.env` ichida qat'iy tokenlar belgilang:

```env
SOCKET_AUTH_REQUIRED=true
SOCKET_TOKENS=very-secret-token
SENSOR_BROADCAST_SECONDS=5
```

Server broadcast qiladigan eventlar:

```text
sensor:update  -> oxirgi sensor snapshot
history:init   -> ulanish paytidagi tarix
history:append -> yangi tarix nuqtasi
device:update  -> rele/GPIO holati
status:update  -> API, DB, uptime va qurilma statusi
```

Clientdan qurilma boshqarish uchun REST `POST /api/device/<device>` ishlaydi. Socket orqali ham `device:set` eventiga `{ "device": "drip_pump", "enabled": true, "source": "site" }` yuborish mumkin.

## MQTT IoT rejimi

Real server/VPS ishlatilganda Mosquitto yoki boshqa MQTT broker kerak bo'ladi. Backend MQTT orqali controllerdan telemetry oladi va sayt buyruqlarini controllerga yuboradi:

```env
MQTT_ENABLED=true
MQTT_HOST=127.0.0.1
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_TLS=false
MQTT_CLIENT_ID=smartfarm-backend
MQTT_PI_CLIENT_ID=smartfarm-pi
MQTT_GREENHOUSE_ID=greenhouse-1
MQTT_TOPIC_PREFIX=smartfarm
```

Topiclar:

```text
smartfarm/greenhouse-1/telemetry  -> controller sensor va device holatini yuboradi
smartfarm/greenhouse-1/state      -> manual switch, IR pult yoki lokal avtomatika holati
smartfarm/greenhouse-1/event      -> IR/manual/LCD/log eventlar
smartfarm/greenhouse-1/command    -> backend saytdan kelgan buyruqni yuboradi
```

Telemetry payload namunasi:

```json
{
  "temperature": 27.3,
  "humidity": 68,
  "soilMoisture": 44,
  "light": 520,
  "gasLevel": 9,
  "gasDetected": false,
  "devices": {
    "drip_pump": false,
    "rain_pump": false,
    "photo_led": true,
    "insect_led": false,
    "cooler_1": true,
    "cooler_2": true
  },
  "source": "raspberry-pi"
}
```

Command payload:

```json
{
  "device": "drip_pump",
  "enabled": true,
  "source": "site",
  "timestamp": "2026-05-23T12:00:00+05:00"
}
```

Raspberry Pi controller gateway:

```bash
python -m backend.pi_gateway
```

VPS/serverda `python -m backend.app` ishlaydi. Raspberry Pi ichida `python -m backend.pi_gateway` ishlaydi. Ikkalasi bir MQTT brokerga ulanadi.

Pi gateway ichida ustuvorlik tartibi:

```text
manual switch -> site/MQTT command -> auto mode
```

Qo'l switch o'zgarsa `source=manual` bilan device holati o'zgaradi va `MANUAL_OVERRIDE_SECONDS` davomida auto qarama-qarshi buyruq bera olmaydi. Saytdan kelgan MQTT command ham shu override mexanizmidan foydalanadi.

Pi lokal avtomatika sozlamalari:

```env
PI_AUTOMATION_ENABLED=true
PI_TEMPERATURE_LIMIT=30
PI_MOISTURE_LIMIT=40
PI_LIGHT_LIMIT=420
PI_GAS_DANGER_LIMIT=70
```

Qo'l boshqaruv switch pinlari:

```env
MANUAL_SWITCH_ACTIVE_LOW=true
MANUAL_SWITCH_DEBOUNCE_SECONDS=0.08
MANUAL_SWITCH_PINS=drip_pump:12,rain_pump:16,photo_led:20,insect_led:21,cooler_1:19,cooler_2:13
```

`MANUAL_SWITCH_ACTIVE_LOW=true` bo'lsa switch GPIO pinni GND ga tortganda `enabled=true` deb o'qiladi. Har bir switch uchun GPIO input ichki pull-up bilan sozlanadi.

LCD 16x2 I2C:

```env
LCD_ENABLED=true
LCD_I2C_ADDRESS=0x27
LCD_I2C_BUS=1
```

LCD birinchi qatorda harorat/namlikni, ikkinchi qatorda tuproq namligi, MQ2 va aktiv relay sonini ko'rsatadi.

IR receiver:

```env
IR_ENABLED=true
IR_PIN=18
IR_ACTIVE_LOW=true
IR_EVENT_COOLDOWN_SECONDS=0.45
```

Hozir IR signal kelganini event sifatida MQTTga yuboradi. Pult tugmalarini aniq boshqaruvga ulash uchun keyingi bosqichda pult kodlarini o'qib, `drip_pump`, `rain_pump`, `cooler_1` kabi commandlarga xaritalash kerak.

## PostgreSQL tarixi

PostgreSQL ishlatish uchun DB URL sozlang:

```env
DATABASE_URL=postgresql://smartfarm:smartfarm@127.0.0.1:5432/smartfarm
HISTORY_RETENTION_DAYS=30
HISTORY_DEFAULT_HOURS=24
HISTORY_QUERY_LIMIT=500
```

Backend start paytida `sensor_history` va `device_history` jadvallarini o'zi yaratadi. `DATABASE_URL` berilmasa yoki DB ulanmasa, tizim mock xotira bilan ishlashda davom etadi.

Tarixni vaqt bo'yicha filtrlash:

```text
GET /api/history?hours=6
GET /api/history?from=2026-05-23T00:00:00Z&to=2026-05-23T12:00:00Z&limit=200
```

Eski `sensor_history` va `device_history` yozuvlari `HISTORY_RETENTION_DAYS` dan keyin avtomatik tozalanadi.

## Raspberry Pi GPIO

Real GPIO va sensorlarni ishlatish uchun Raspberry Pi ichida:

```env
USE_GPIO=true
USE_REAL_SENSORS=true
GPIO_ACTIVE_LOW=true
MANUAL_OVERRIDE_SECONDS=120
GPIO_DRIP_PUMP_PIN=17
GPIO_RAIN_PUMP_PIN=27
GPIO_PHOTO_LED_PIN=5
GPIO_INSECT_LED_PIN=6
GPIO_COOLER_1_PIN=22
GPIO_COOLER_2_PIN=26
DHT_PIN=4
DHT_SENSOR=DHT22
IR_PIN=18
LIGHT_DIGITAL_PIN=23
LIGHT_DARK_SIGNAL=1
MQ2_DIGITAL_PIN=24
MQ2_DANGER_SIGNAL=0
SOIL_ADC_CHANNEL=0
LIGHT_ADC_CHANNEL=1
MQ2_ADC_CHANNEL=2
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
| Tomchilatib nasos relesi IN | GPIO17 | 11 | Relay IN1 |
| Yomg'irlatib nasos relesi IN | GPIO27 | 13 | Relay IN2 |
| Fotosintez LED relesi IN | GPIO5 | 29 | Relay IN3 |
| Hashorat LED relesi IN | GPIO6 | 31 | Relay IN4 |
| Kuler 1 relesi IN | GPIO22 | 15 | Relay IN5 |
| Kuler 2 relesi IN | GPIO26 | 37 | Relay IN6 |
| DHT22 DATA | GPIO4 | 7 | DHT22 data, 10k pull-up bilan 3.3V ga |
| DHT22 VCC | 3.3V | 1 | Sensor quvvati |
| DHT22 GND | GND | 6 | Umumiy minus |
| IR receiver OUT | GPIO18 | 12 | Arduino D2 o'rniga, kelajak IR boshqaruv uchun |
| Fotorezistor DO | GPIO23 | 16 | Arduino D3 o'rniga digital yorug'lik signali |
| MQ2 DO | GPIO24 | 18 | Gaz/tutun raqamli signal, `MQ2_DANGER_SIGNAL` bilan sozlanadi |
| MCP3008 VDD/VREF | 3.3V | 1 | ADC quvvati |
| MCP3008 AGND/DGND | GND | 9 | Umumiy minus |
| MCP3008 CLK | GPIO11/SCLK | 23 | SPI clock |
| MCP3008 DOUT | GPIO9/MISO | 21 | SPI MISO |
| MCP3008 DIN | GPIO10/MOSI | 19 | SPI MOSI |
| MCP3008 CS/SHDN | GPIO8/CE0 | 24 | SPI CE0 |
| Tuproq namligi AO | MCP3008 CH0 | - | Analog signal |
| LDR yorug'lik sensori AO | MCP3008 CH1 | - | Analog signal |
| MQ2 AO | MCP3008 CH2 | - | Analog gaz darajasi |

Relay moduliga tashqi 5V quvvat bering va Raspberry Pi GND bilan relay GND ni umumiy qiling. 6 ta relay ishlatiladi: 2 ta nasos, 2 ta LED va 2 ta kuler. Ko'p relay modullarda signal active-low bo'ladi: `GPIO_ACTIVE_LOW=true` Arduino kodidagi `RELAY_ON LOW` bilan bir xil ishlaydi. Nasos, chiroq yoki kuler 220V bo'lsa, ulashni xavfsizlik qoidalari bilan bajaring.

Raspberry Pi ichida SPI yoqilgan bo'lishi kerak:

```bash
sudo raspi-config
```

`Interface Options` -> `SPI` -> `Enable`.

Eski nomlar uchun alias qoldirilgan:

```text
POST /api/device/drip   -> drip_pump
POST /api/device/pump   -> drip_pump
POST /api/device/rain   -> rain_pump
POST /api/device/fan    -> cooler_1
POST /api/device/cooler -> cooler_1
POST /api/device/cooler1 -> cooler_1
POST /api/device/cooler2 -> cooler_2
POST /api/device/light  -> photo_led
POST /api/device/led    -> photo_led
```
