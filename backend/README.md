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

Real GPIO ishlatish uchun Raspberry Pi ichida:

```env
USE_GPIO=true
GPIO_FAN_PIN=4
GPIO_PUMP_PIN=17
GPIO_LIGHT_PIN=22
GPIO_CAMERA_PIN=27
```

`RPi.GPIO` Raspberry Pi muhitida o‘rnatilgan bo‘lishi kerak.

## Telegram bot funksiyalari

Dashboard Settings sahifasidan token va Chat ID saqlanadi.

Endpointlar:

```text
GET  /api/telegram/settings
POST /api/telegram/settings
POST /api/telegram/test
POST /api/telegram/notify
```

Qurilma holati `POST /api/device/fan`, `pump`, `light`, `camera` orqali o‘zgarsa, backend Telegramga qisqa bildirishnoma yuborishga urinadi.
