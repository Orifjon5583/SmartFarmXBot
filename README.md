# SmartFarmXBot

SmartFarmXBot - React va Flask asosidagi aqlli issiqxona IoT boshqaruv paneli.

## Asosiy imkoniyatlar

- Raspberry Pi uchun sensor monitoring
- Tomchilatib sug'orish, yomg'irlatib sug'orish, 2 ta kuler va LED chiroq boshqaruvi
- PWA sifatida o'rnatish
- Flask API backend
- Dark glassmorphism admin dashboard

## Ishga tushirish

Frontend:

```powershell
npm install
npm run dev
```

Backend:

```powershell
python -m pip install -r requirements.txt
npm run backend
```

Raspberry Pi 4 real GPIO/sensor rejimi:

```powershell
python -m pip install -r requirements-pi.txt
```

Ulanish pinlari va `.env` sozlamalari [backend/README.md](backend/README.md) ichida yozilgan.

sayt.uz domenidan subdomen chiqarib ishlatish bo'yicha yo'riqnoma:
[deploy/README-saytuz.md](deploy/README-saytuz.md).

Production build:

```powershell
npm run build
```
