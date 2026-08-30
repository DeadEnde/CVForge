#!/usr/bin/env bash
# CVForge — one-command setup (local MCP server + playground deps)
set -e
cd "$(dirname "$0")"
echo "==> Installing Python dependencies..."
pip3 install --break-system-packages --quiet -r requirements.txt fastapi uvicorn
python3 -c "import cvforge, fastapi; print('✅ cvforge + fastapi OK')"
echo ""
echo "Done. Start:  ./run.sh   |  web UI:  python3 -m uvicorn playground.app:app --port 3500"
