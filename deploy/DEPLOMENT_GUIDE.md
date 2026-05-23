# AWS va Raspberry Pi Ulanish Qo'llanmasi

Ushbu qo'llanmada loyihani AWS serveriga yuklash va Raspberry Pi bilan MQTT orqali ulash tushuntiriladi. Barcha mock (soxta) ma'lumotlar olib tashlandi, endi tizim faqat real ma'lumotlar bilan ishlaydi.

## 1. AWS Portlarni Ochish

AWS Security Group panelida (Inbound rules) quyidagi portlarni ochishingiz shart:
- **80 (TCP)** - HTTP va Certbot uchun (BUNI QO'SHISH EHTIYOJ!)
- **443 (TCP)** - HTTPS uchun (Sizda bor)
- **22 (TCP)** - SSH uchun (Sizda bor)
- **1883 (TCP)** - MQTT uchun (Sizda bor)

> **Diqqat**: 80 porti yopiq bo'lsa, SSL sertifikat (HTTPS) ololmaysiz! 

## 2. Serverni Tayyorlash (AWS)

Serveringizga (56.228.24.251) SSH orqali kiring va kerakli dasturlarni o'rnating:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx mosquitto mosquitto-clients certbot python3-certbot-nginx nodejs npm
```

## 3. MQTT Broker (Mosquitto) Sozlash

Serverda MQTT brokerni xavfsiz holatga keltiramiz:

```bash
sudo nano /etc/mosquitto/conf.d/smartfarm.conf
```
Quyidagilarni yozing:
```
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd
```

Parol o'rnatamiz (parolni eslab qoling, masalan `MqttPass123`):
```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd smartfarm
sudo systemctl restart mosquitto
```

## 4. Loyihani Serverga Yuklash

Loyiha papkasini serverdagi `/var/www/smartfarm` jildiga joylashtiring.

### Frontendni build qilish:
```bash
cd /var/www/smartfarm
npm install
npm run build
```

### Backendni sozlash:
```bash
cd /var/www/smartfarm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`.env` faylini yarating (`deploy/.env.prod` asosida):
```bash
cp deploy/.env.prod .env
nano .env # Parollarni to'g'rilang!
```

## 5. Nginx va SSL Sozlash

Nginx konfiguratsiyasini ulash:
```bash
sudo cp deploy/smartfarm-nginx.conf /etc/nginx/sites-available/smartfarm
sudo ln -s /etc/nginx/sites-available/smartfarm /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

SSL sertifikat olish:
```bash
sudo certbot --nginx -d smartfarm.orifdev.uz -d api.smartfarm.orifdev.uz
```

## 6. Backendni Orqa Fonda Ishga Tushirish

Backend doim ishlab turishi uchun `systemd` xizmati yaratamiz:

```bash
sudo nano /etc/systemd/system/smartfarm.service
```
Ichiga quyidagilarni yozing:
```ini
[Unit]
Description=SmartFarm Backend API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/smartfarm
Environment="PATH=/var/www/smartfarm/venv/bin"
ExecStart=/var/www/smartfarm/venv/bin/python -m backend.app
Restart=always

[Install]
WantedBy=multi-user.target
```

Xizmatni ishga tushirish:
```bash
sudo systemctl daemon-reload
sudo systemctl enable smartfarm
sudo systemctl start smartfarm
```

## 7. Raspberry Pi Sozlamalari

Malinaga (Raspberry Pi) kirgach, terminalda quyidagilarni qiling:

```bash
git clone <sizning-github-repo> smartfarm
cd smartfarm
python -m venv venv
source venv/bin/activate
pip install -r requirements-pi.txt
```

Raspberry Pi uchun maxsus `.env` yarating:
```env
MQTT_ENABLED=true
MQTT_HOST=56.228.24.251
MQTT_PORT=1883
MQTT_USERNAME=smartfarm
MQTT_PASSWORD=yashirin_parol_kiriting
MQTT_TLS=false
MQTT_CLIENT_ID=smartfarm-pi
MQTT_GREENHOUSE_ID=greenhouse-1
MQTT_TOPIC_PREFIX=smartfarm

USE_GPIO=true
USE_REAL_SENSORS=true
PI_AUTOMATION_ENABLED=true
```

Malinada scriptni ishga tushirish:
```bash
python -m backend.pi_gateway
```

## Tizim Qanday Ishlaydi?

1. **Malina (Pi)** datchiklardan harorat, namlikni o'qiydi.
2. Malina bu ma'lumotlarni **MQTT** orqali `56.228.24.251:1883` ga yuboradi.
3. Serverdagi **Flask backend** MQTT xabarni qabul qilib, WebSocket orqali frontendga uzatadi.
4. **React sayti** (`smartfarm.orifdev.uz`) MQTT'dan kelgan ma'lumotlarni ko'rsatadi.
5. Saytdan "Nasosni yoqish" bosilsa, backend API chaqiriladi -> backend MQTT ga xabar yozadi -> Malina bu xabarni olib nasos relesini yoqadi.
