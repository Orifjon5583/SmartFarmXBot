# sayt.uz domenidan subdomen chiqarish

Bu loyiha uchun eng qulay sxema:

- `app.example.uz` - React frontend
- `api.example.uz` - Flask backend API

`example.uz` o'rniga sayt.uz'dan olgan domeningizni yozing.

## 1. sayt.uz DNS sozlash

sayt.uz panelida domeningiz DNS bo'limiga kiring va server IP manzilingizga ikkita yozuv qo'shing:

```text
Type  Name  Value
A     app   YOUR_SERVER_IP
A     api   YOUR_SERVER_IP
```

Agar saytni asosiy domenda ochmoqchi bo'lsangiz:

```text
A     @     YOUR_SERVER_IP
A     api   YOUR_SERVER_IP
```

DNS tarqalishi odatda bir necha daqiqadan bir necha soatgacha vaqt oladi.

## 2. Frontend API manzilini yozish

`.env` faylida backend subdomenini ko'rsating:

```env
VITE_API_URL=https://api.example.uz
VITE_USE_MOCK_API=false
```

Keyin frontendni qayta build qiling:

```bash
npm run build
```

## 3. Backendni serverda ishga tushirish

Serverda backend tashqi internetga to'g'ridan-to'g'ri emas, nginx orqali chiqishi uchun local portda ishlasin:

```bash
GREENHOUSE_HOST=127.0.0.1 GREENHOUSE_PORT=5000 GREENHOUSE_DEBUG=false python -m backend.app
```

Raspberry Pi yoki VPS ichida real sensor ishlatilsa kerakli GPIO env qiymatlarini ham qo'shing.

## 4. Nginx

`deploy/saytuz-nginx.conf` ichidagi `example.uz` va `/var/www/issiqxona/dist` qiymatlarini o'zingizning domen va loyiha yo'lingizga almashtiring.

So'ng nginx configga ulang va SSL qo'shing:

```bash
sudo ln -s /var/www/issiqxona/deploy/saytuz-nginx.conf /etc/nginx/sites-enabled/issiqxona
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d app.example.uz -d api.example.uz
```

SSL o'rnatilgandan keyin frontend `.env` ichida `https://api.example.uz` qolishi kerak.

## Tekshirish

Brauzerda:

```text
https://api.example.uz/api/health
https://app.example.uz
```

`/api/health` quyidagiga o'xshash javob qaytarsa backend ulangan:

```json
{"ok": true, "service": "greenhouse-api"}
```
