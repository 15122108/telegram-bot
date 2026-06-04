#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/visa-esim-uz-bot"
APP_USER="visa-bot"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo bash deploy_digitalocean.sh"
  exit 1
fi

cd "$(dirname "$0")"

if [ ! -f ".env" ]; then
  echo ".env file not found. Copy .env.example to .env and fill values first."
  exit 1
fi

apt-get update
apt-get install -y python3 ca-certificates curl

if ! id "$APP_USER" >/dev/null 2>&1; then
  useradd --system --home "$APP_DIR" --shell /usr/sbin/nologin "$APP_USER"
fi

mkdir -p "$APP_DIR"
install -m 0644 bot.py "$APP_DIR/bot.py"
install -m 0644 admin_panel.py "$APP_DIR/admin_panel.py"
if [ -f "payment_qr.png" ]; then
  install -m 0644 payment_qr.png "$APP_DIR/payment_qr.png"
fi
install -m 0600 .env "$APP_DIR/.env"

mkdir -p /etc/systemd/system
install -m 0644 systemd/visa-esim-uz-bot.service /etc/systemd/system/visa-esim-uz-bot.service
install -m 0644 systemd/visa-esim-admin.service /etc/systemd/system/visa-esim-admin.service

chown -R "$APP_USER:$APP_USER" "$APP_DIR"

systemctl daemon-reload
systemctl enable visa-esim-uz-bot visa-esim-admin
systemctl restart visa-esim-uz-bot visa-esim-admin

echo "Done."
echo "Bot status:   systemctl status visa-esim-uz-bot --no-pager"
echo "Admin status: systemctl status visa-esim-admin --no-pager"
echo "Bot logs:     journalctl -u visa-esim-uz-bot -f"
echo "Admin URL:    http://SERVER_IP:8088/login"
