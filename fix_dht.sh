#!/bin/bash
# Fix DHT sensor - reinstall adafruit libraries
cd ~/smartfarm
source venv/bin/activate
pip uninstall -y adafruit-circuitpython-dht adafruit-circuitpython-pulseio Adafruit-Blinka
pip install -r requirements-pi.txt
echo ""
echo "✅ Done! Now run: python3 -m backend.pi_gateway"
