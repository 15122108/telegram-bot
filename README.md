# Visa eSIM Uzbekistan Bot

Telegram bot for selling travel eSIM packages, collecting flight ticket requests, and handling visa expiry reminders.

## Features

- Telegram menu with Uzbek, Russian, and English language support
- eSIM Go catalogue integration
- 211+ eSIM destinations from the provider catalogue
- Configurable markup with `ESIM_MARKUP_PERCENT`
- Manual payment verification flow
- Admin command to create a real eSIM after payment: `/fulfill ORDER_ID`
- Flight ticket request flow with admin offer, QR/card payment instructions, and ticket/PNR delivery
- Admin panel with users, eSIM orders, flight orders, profit KPIs, support, broadcast, packages, settings, and exports
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
ADMIN_TELEGRAM_NOTIFICATIONS=0
ADMIN_BOT_COMMANDS=0
ADMIN_PANEL_PASSWORD=
ADMIN_PANEL_SECRET=
ESIMGO_API_KEY=
ESIMGO_API_BASE=https://api.esim-go.com/v2.4
ESIM_MARKUP_PERCENT=30
ALLOW_MANUAL_ESIM_FALLBACK=0
FLIGHT_PROVIDER_MODE=manual
FLIGHT_MARKUP_PERCENT=10
FLIGHT_CURRENCY=USD
FLIGHT_API_PROVIDER=
FLIGHT_API_BASE=
FLIGHT_API_SEARCH_PATH=/search
FLIGHT_API_BOOKING_PATH=/bookings
FLIGHT_API_KEY=
CARD_QR_IMAGE=payment_qr.png
CARD_PAYMENT_NOTE=
```

`ALLOW_MANUAL_ESIM_FALLBACK=0` is real mode. The bot only uses eSIM Go catalogue/products and will not sell local demo packages if the provider API is unavailable.

`ADMIN_TELEGRAM_NOTIFICATIONS=0` keeps support/order management inside the admin panel. Set it to `1` only if you also want admin Telegram chat alerts.

`ADMIN_BOT_COMMANDS=0` keeps admin operations inside the admin panel. Set it to `1` only for emergency Telegram commands.

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

## Flight Ticket Flow

1. Customer opens `Avia biletlar` and sends route, dates, passenger count, and contact.
2. If `FLIGHT_PROVIDER_MODE=api`, the bot requests real flight offers from `FLIGHT_API_SEARCH_PATH`, adds `FLIGHT_MARKUP_PERCENT`, and shows customer-facing prices in Telegram.
3. Customer selects a ticket offer and pays to the owner card/QR account shown by the bot.
4. Admin confirms the card/QR payment in the panel.
5. If flight API is configured, admin can run automatic booking/issue from the panel. Otherwise admin sends PNR, ticket number, ticket URL, or ticket PDF/image manually.

`FLIGHT_PROVIDER_MODE=manual` is the default. Real ticket API automation can be connected later through `FLIGHT_API_PROVIDER`, `FLIGHT_API_BASE`, `FLIGHT_API_SEARCH_PATH`, `FLIGHT_API_BOOKING_PATH`, and `FLIGHT_API_KEY`.

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
