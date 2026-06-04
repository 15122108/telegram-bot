# Telegram Bot

Oddiy Telegram bot starter loyihasi. Tashqi Python paketlari kerak emas.

## Token olish

1. Telegramda `@BotFather` ni oching.
2. `/newbot` yuboring va bot nomini tanlang.
3. BotFather bergan tokenni nusxalang.

## Ishga tushirish

PowerShell:

```powershell
cd "C:\Users\acer\Documents\New project\telegram-bot"
Copy-Item .env.example .env
notepad .env
.\run.bat
```

Fon rejimida ishga tushirish:

```powershell
.\start-hidden.bat
```

Botni to'xtatish:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\stop-bot.ps1
```

Watchdog tekshiruvi:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\watchdog.ps1
```

Windows Task Scheduler orqali har 5 daqiqada watchdog ishga tushirish:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\create-watchdog-task.ps1
```

`.env` ichidagi `TELEGRAM_BOT_TOKEN` qiymatini haqiqiy token bilan almashtiring.

Admin va Wallet sozlamalari:

```env
ADMIN_CHAT_ID=123456789
TELEGRAM_WALLET_PAY_LINK=https://t.me/wallet
TELEGRAM_WALLET_ADDRESS=USDT_TRON_ADDRESS_YOKI_WALLET_MANZIL
```

`ADMIN_CHAT_ID` qo'yilsa, yangi eSIM buyurtmalar admin chatga yuboriladi.

## Buyruqlar

- `/start` - botni boshlash
- `/help` - yordam
- `/visa_list` - O'zbekiston fuqarolari uchun vizasiz davlatlar
- `/visa UAE` - bitta davlat bo'yicha viza holatini tekshiradi
- `/esim` - mavjud eSIM yo'nalishlari
- `/esim uae` - davlat bo'yicha paketlar
- `/buy uae 1GB` - eSIM buyurtma va to'lov yo'riqnomasi

## Muhim

Bu bot hozir manual sotuv oqimida ishlaydi: mijoz buyurtma qiladi, Telegram Wallet orqali to'laydi, chek yuboradi, admin tasdiqlaydi va eSIM QR/kodni beradi.

To'lovni avtomatik qabul qilish va pulni to'g'ridan-to'g'ri Telegram Wallet merchant hisobiga yig'ish uchun Wallet Pay merchant akkaunti va API integratsiyasi kerak. eSIMni avtomatik yetkazish uchun esa Airalo, Nomad, Dent, RedteaGO yoki boshqa eSIM provayderining reseller/API hisobini ulash kerak.

## 24/7 ishlash

Lokal kompyuterda bot faqat kompyuter yoqiq va internet bor paytda 24/7 ishlaydi. Haqiqiy 24/7 uchun botni VPS/cloud serverga joylash kerak.
