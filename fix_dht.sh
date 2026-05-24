#!/bin/bash
# Fix DHT sensor on Raspberry Pi
# Creates libgpiod symlink + reinstalls packages
cd ~/smartfarm
source venv/bin/activate

echo "🔧 Creating libgpiod.so.2 symlink..."
sudo ln -sf /usr/lib/aarch64-linux-gnu/libgpiod.so.3 /usr/lib/aarch64-linux-gnu/libgpiod.so.2 2>/dev/null
sudo ln -sf /usr/lib/arm-linux-gnueabihf/libgpiod.so.3 /usr/lib/arm-linux-gnueabihf/libgpiod.so.2 2>/dev/null

echo "🔧 Reinstalling DHT packages..."
pip uninstall -y adafruit-circuitpython-dht adafruit-circuitpython-pulseio Adafruit-Blinka Adafruit_DHT 2>/dev/null
pip install -r requirements-pi.txt

echo ""
echo "✅ Done! Now run: python3 -m backend.pi_gateway"
