#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="student-api"
UNIT_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
PORT="${PORT:-8000}"
WORKDIR="$(pwd)"
RUN_USER="$(whoami)"

if [ -f "$UNIT_FILE" ]; then
  echo "Unit file already exists at $UNIT_FILE — restarting service with updated code"
  sudo systemctl restart "$SERVICE_NAME"
else
  echo "Unit file not found — creating $UNIT_FILE"
  sudo tee "$UNIT_FILE" > /dev/null <<UNIT_EOF
[Unit]
Description=Student API FastAPI Service
After=network.target

[Service]
User=$RUN_USER
WorkingDirectory=$WORKDIR
ExecStart=$WORKDIR/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port $PORT
Restart=always

[Install]
WantedBy=multi-user.target
UNIT_EOF

  sudo systemctl daemon-reload
  sudo systemctl enable --now "$SERVICE_NAME"
fi
