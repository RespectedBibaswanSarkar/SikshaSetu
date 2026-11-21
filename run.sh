#!/usr/bin/env bash
set -e
echo "Starting SikshaSetu..."
python3 -m pipeline.build_db
cd client && npm run build
cd ..
exec python3 -m hub.main --lan
