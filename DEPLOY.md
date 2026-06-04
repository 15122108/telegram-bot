# 24/7 Deploy: GitHub Student Pack + DigitalOcean

Bu loyiha sotiladigan Telegram bot uchun VPSda 24/7 ishlashga tayyorlangan.

## 1. Student Pack orqali credit olish

1. GitHub Student Developer Packga kiring.
2. DigitalOcean offerni tanlang.
3. DigitalOcean account ochib, student creditni aktiv qiling.

## 2. DigitalOcean droplet

Minimal droplet yetadi:

```text
Ubuntu 24.04 LTS
Basic shared CPU
1 vCPU / 512 MB yoki 1 GB RAM
```

Bot Python standard library bilan ishlaydi, katta server kerak emas.

## 3. Serverga fayllarni yuborish

Local kompyuterdan:

```powershell
scp -r "C:\Users\acer\Documents\New project\telegram-bot" root@SERVER_IP:/root/telegram-bot
```

`SERVER_IP` o'rniga DigitalOcean droplet IP manzilini yozing.

## 4. Serverda o'rnatish

Serverga kiring:

```bash
ssh root@SERVER_IP
cd /root/telegram-bot
bash deploy_digitalocean.sh
```

Script quyidagilarni qiladi:

- Python o'rnatadi
- bot fayllarini `/opt/visa-esim-uz-bot`ga ko'chiradi
- `visa-esim-uz-bot` user yaratadi
- bot service yaratadi
- admin panel service yaratadi
- restartdan keyin ham avtomatik yoqiladigan qiladi

## 5. Kerakli `.env`

Serverga yuborishdan oldin local `.env` ichida shular to'ldirilgan bo'lishi kerak:

```env
TELEGRAM_BOT_TOKEN=
ADMIN_CHAT_ID=
ADMIN_USERNAME=
ADMIN_PANEL_PASSWORD=
ADMIN_PANEL_SECRET=
ESIMGO_API_KEY=
CARD_QR_IMAGE=payment_qr.png
```

`.env` hech qachon GitHubga push qilinmaydi.

## 6. Status va log

```bash
systemctl status visa-esim-uz-bot --no-pager
systemctl status visa-esim-admin --no-pager
journalctl -u visa-esim-uz-bot -f
```

## 7. Admin panel

```text
http://SERVER_IP:8088/login
```

Firewall yoqilgan bo'lsa:

```bash
ufw allow OpenSSH
ufw allow 8088/tcp
ufw enable
```

## 8. Yangilash

Yangi kodni serverga yuborgandan keyin:

```bash
cd /root/telegram-bot
bash deploy_digitalocean.sh
```

Script service'larni qayta ishga tushiradi.
