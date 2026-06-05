# Visa eSIM Uzbekistan Bot

Telegram bot for selling travel eSIM packages and handling visa expiry reminders.

## Features

- Telegram menu with Uzbek, Russian, and English language support
- eSIM Go catalogue integration
- 211+ eSIM destinations from the provider catalogue
- Configurable markup with `ESIM_MARKUP_PERCENT`
- Manual payment verification flow
- Admin command to create a real eSIM after payment: `/fulfill ORDER_ID`
- Admin panel with users, orders, profit KPIs, support, broadcast, packages, settings, and exports
- Support inbox with text/photo/video/document attachments
- Broadcast text/photo/video messages
- User tracking after `/start` or any bot interaction
- Visa expiry reminder flow
- Buyer-ready $5000 sales package: [SALES_OFFER_5000.md](SALES_OFFER_5000.md)

## Required Environment Variables

```env
TELEGRAM_BOT_TOKEN=
ADMIN_CHAT_ID=
ADMIN_USERNAME=
ADMIN_PANEL_PASSWORD=
ADMIN_PANEL_SECRET=
ESIMGO_API_KEY=
ESIMGO_API_BASE=https://api.esim-go.com/v2.4
ESIM_MARKUP_PERCENT=30
CARD_QR_IMAGE=payment_qr.png
CARD_PAYMENT_NOTE=
```

## Order Flow

1. Customer selects an eSIM country and package.
2. Bot creates an order and sends payment instructions.
3. Customer sends the payment receipt.
4. Admin checks the payment.
5. Admin runs:

```text
/fulfill VE-YYYYMMDD-0001
```

The bot creates a real eSIM through eSIM Go and sends installation details to the customer.

## Local Run

```powershell
cd "C:\Users\acer\Documents\New project\telegram-bot"
.\run.bat
```

Admin panel shortcut:

```text
Visa eSIM Admin Panel
```

## 24/7 Deployment

Use a VPS or a cloud service that can run a persistent Python process. See [DEPLOY.md](DEPLOY.md).

Secrets must be stored in environment variables. Do not commit `.env`.
