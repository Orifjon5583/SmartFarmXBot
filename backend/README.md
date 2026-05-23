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
```

Qurilma API nomlari:

```text
drip -> tomchilatib sug'orish
rain -> yomg'irlatib sug'orish
cooler -> 2 ta kuler uchun umumiy relay
led  -> LED chiroq
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

## Raspberry Pi GPIO

Real GPIO va sensorlarni ishlatish uchun Raspberry Pi ichida:

```env
USE_GPIO=true
USE_REAL_SENSORS=true
GPIO_ACTIVE_LOW=true
MANUAL_OVERRIDE_SECONDS=120
GPIO_DRIP_PIN=17
GPIO_RAIN_PIN=27
GPIO_COOLER_PIN=22
GPIO_LED_PIN=5
DHT_PIN=4
DHT_SENSOR=DHT22
IR_PIN=18
LIGHT_DIGITAL_PIN=23
LIGHT_DARK_SIGNAL=1
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
| Tomchilatib sug'orish relesi IN | GPIO17 | 11 | Relay IN1 |
| Yomg'irlatib sug'orish relesi IN | GPIO27 | 13 | Relay IN2 |
| 2 ta kuler umumiy relesi IN | GPIO22 | 15 | Relay IN3 |
| LED chiroq relesi IN | GPIO5 | 29 | Relay IN4 |
| DHT22 DATA | GPIO4 | 7 | DHT22 data, 10k pull-up bilan 3.3V ga |
| DHT22 VCC | 3.3V | 1 | Sensor quvvati |
| DHT22 GND | GND | 6 | Umumiy minus |
| IR receiver OUT | GPIO18 | 12 | Arduino D2 o'rniga, kelajak IR boshqaruv uchun |
| Fotorezistor DO | GPIO23 | 16 | Arduino D3 o'rniga digital yorug'lik signali |
| MCP3008 VDD/VREF | 3.3V | 1 | ADC quvvati |
| MCP3008 AGND/DGND | GND | 9 | Umumiy minus |
| MCP3008 CLK | GPIO11/SCLK | 23 | SPI clock |
| MCP3008 DOUT | GPIO9/MISO | 21 | SPI MISO |
| MCP3008 DIN | GPIO10/MOSI | 19 | SPI MOSI |
| MCP3008 CS/SHDN | GPIO8/CE0 | 24 | SPI CE0 |
| Tuproq namligi AO | MCP3008 CH0 | - | Analog signal |
| LDR yorug'lik sensori AO | MCP3008 CH1 | - | Analog signal |

Relay moduliga tashqi 5V quvvat bering va Raspberry Pi GND bilan relay GND ni umumiy qiling. 4 ta relay ishlatiladi: tomchilatib, yomg'irlatib, 2 ta kulerni birga boshqaradigan umumiy relay va LED chiroq. Ko'p relay modullarda signal active-low bo'ladi: `GPIO_ACTIVE_LOW=true` Arduino kodidagi `RELAY_ON LOW` bilan bir xil ishlaydi. Nasos, chiroq yoki kuler 220V bo'lsa, ulashni xavfsizlik qoidalari bilan bajaring.

Raspberry Pi ichida SPI yoqilgan bo'lishi kerak:

```bash
sudo raspi-config
```

`Interface Options` -> `SPI` -> `Enable`.

Eski nomlar uchun alias qoldirilgan:

```text
POST /api/device/pump  -> drip
POST /api/device/fan   -> cooler
POST /api/device/cooler1 -> cooler
POST /api/device/cooler2 -> cooler
POST /api/device/cooler3 -> cooler
POST /api/device/light -> led
```
