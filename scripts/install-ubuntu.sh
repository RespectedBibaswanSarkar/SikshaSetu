#!/usr/bin/env bash
# SikshaSetu Ubuntu installer (no video/ffmpeg steps)
set -euo pipefail

echo "=== Installing SikshaSetu Dependencies ==="
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv sqlite3 nodejs npm curl

# Python virtual environment setup if desired
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo "Building Client PWA..."
cd client
npm install
npm run build
cd ..

echo "Ingesting MIT OCW content..."
python3 -m pipeline.build_db
python3 scripts/validate_content.py

echo "=== Installation complete! Run 'make run' or './run.sh' to start. ==="
