import html
import hmac
import hashlib
import json
import os
import secrets
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlencode, urlparse
from urllib.request import Request, urlopen
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR") or os.environ.get("RAILWAY_VOLUME_MOUNT_PATH") or str(BASE_DIR))
DATA_DIR.mkdir(parents=True, exist_ok=True)
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8088"))
SESSION_COOKIE = "admin_session"
SESSION_TTL_SECONDS = 60 * 60
PACKAGES_FILE = "esim_packages.json"
LANG_COOKIE = "admin_lang"
CURRENT_ADMIN_LANG = "uz"
ADMIN_TEXT = {
    "uz": {
        "dashboard": "Bosh sahifa",
        "orders": "Buyurtmalar",
        "visa_reminders": "Viza muddati",
        "users": "Foydalanuvchilar",
        "support": "Yordam",
        "packages": "eSIM paketlar",
        "settings": "Sozlamalar",
        "export": "Eksport",
        "broadcast": "Ommaviy xabar",
        "logout": "Logout",
        "login_title": "Visa eSIM Admin",
        "login_hint": "Panelga kirish uchun parolni kiriting.",
        "password": "Parol",
        "login": "Kirish",
        "wrong_password": "Parol noto'g'ri yoki sozlanmagan.",
        "panel_private": "Admin panel himoyalangan. Public link bo'lsa ham parolsiz ochilmaydi.",
        "pending": "Kutilmoqda",
        "order_sum": "Buyurtmalar summasi",
        "open_support": "Ochiq yordam xabarlari",
        "change_password": "Admin panel parolini almashtirish",
        "old_password": "Eski parol",
        "new_password": "Yangi parol",
        "repeat_password": "Yangi parolni takrorlang",
        "save": "Saqlash",
        "change_password_btn": "Parolni almashtirish",
        "bot_payment_settings": "Bot, to'lov va eSIM sozlamalari",
        "settings_saved": "Sozlamalar saqlandi.",
        "packages_title": "eSIM paketlar",
        "add_update_country": "Davlat qo'shish yoki yangilash",
        "code": "Kod",
        "country_name": "Davlat nomi",
        "download": "yuklab olish",
        "id": "ID",
        "country": "Davlat",
        "plan": "Paket",
        "price": "Narx",
        "status": "Holat",
        "user": "Foydalanuvchi",
        "action": "Amal",
        "done": "Bajarildi",
        "fulfill": "eSIM yuborish",
        "cancel": "Bekor qilish",
        "delete": "O'chirish",
        "created": "Yaratilgan",
        "sent": "Yuborilgan",
        "username": "Username",
        "name": "Ism",
        "language": "Til",
        "last_activity": "Oxirgi faollik",
        "sum": "Summa",
        "send_via_bot": "Bot orqali xabar yuborish",
        "reply_placeholder": "Mijozga javob matnini yozing...",
        "send": "Yuborish",
        "telegram_reply_hint": "Yoki Telegramdan",
        "support_questions": "Yordam savollari",
        "question": "Savol",
        "file": "Fayl",
        "answer": "Javob",
        "no_file": "Fayl yo'q",
        "open_download": "Ochish/yuklash",
        "select_support": "Yordam xabarini tanlang.",
        "client": "Mijoz",
        "reply_write": "Javob yozing...",
        "send_reply": "Javob yuborish",
        "support_state": "Yordam holati",
        "open_messages_suffix": "ta ochiq xabar.",
        "enable_notifications": "Bildirishnomani yoqish",
        "notify_unsupported": "Bu brauzer notification qo'llamaydi.",
        "notify_enabled": "Yoqildi.",
        "notify_denied": "Ruxsat berilmadi.",
        "new_support": "Yangi support xabar",
        "new_support_body": "Mijoz yangi xabar yubordi",
        "password_changed_hint": "Parol o'zgargandan keyin xavfsizlik uchun qayta login qilish kerak bo'ladi.",
        "payment_settings_hint": "To'lov va eSIM Go sozlamalari .env faylga yoziladi. Bot ularni keyingi so'rovlarda o'qiydi.",
        "card_holder": "Karta egasi",
        "card_number": "Karta raqami",
        "qr_image_file": "QR rasm fayli",
        "qr_link": "QR link",
        "payment_note": "To'lov izohi",
        "card_payment_link": "Visa/Mastercard payment link",
        "payme_link": "Payme link",
        "click_link": "Click link",
        "esimgo_api_key": "eSIM Go API Key",
        "esim_markup_percent": "eSIM ustama foizi",
        "package_hint": "3 tagacha paket kiriting. Bo'sh paketlar saqlanmaydi.",
        "package_1": "1-paket",
        "package_2": "2-paket",
        "package_3": "3-paket",
        "package_saved": "Paket saqlandi.",
        "package_need_code": "Kod va davlat nomi kerak.",
        "package_incomplete": "Har bir paketda data, kun va narx to'liq bo'lishi kerak.",
        "price_number": "Narx raqam bo'lishi kerak.",
        "package_need_one": "Kamida bitta paket kiriting.",
        "old_password_wrong": "Eski parol noto'g'ri.",
        "new_password_short": "Yangi parol kamida 8 ta belgi bo'lishi kerak.",
        "new_password_mismatch": "Yangi parollar bir xil emas.",
        "password_changed": "Parol almashtirildi.",
        "broadcast_title": "Ommaviy xabar yuborish",
        "broadcast_hint": "Botni /start qilgan va botni bloklamagan foydalanuvchilarga yuboriladi. Telegram profili yopiq bo'lsa ham chat ID bor bo'lsa yuboriladi.",
        "broadcast_text": "Xabar matni",
        "broadcast_media": "Rasm/video",
        "broadcast_media_hint": "Ixtiyoriy: rasm yoki video tanlang. Matn caption sifatida yuboriladi.",
        "broadcast_content_required": "Matn yozing yoki rasm/video tanlang.",
        "target_lang": "Til bo'yicha",
        "all_users": "Hamma foydalanuvchilar",
        "send_broadcast": "Hammaga yuborish",
        "broadcast_done": "Yuborildi: {sent}. Xato/bloklagan: {failed}.",
        "esim_countries": "eSIM davlatlar",
        "no_users_hint": "Hali foydalanuvchi yo'q. Botni /start qilgan odamlar shu yerda ko'rinadi.",
        "esimgo_api_base": "eSIM Go API manzili",
        "new_user": "Yangi foydalanuvchi",
        "new_user_body": "Botga yangi foydalanuvchi qo'shildi",
        "users_state": "Foydalanuvchilar holati",
        "paid_revenue": "To'langan tushum",
        "cost": "Tan narx",
        "profit": "Sof foyda",
        "margin": "Marja",
        "avg_order": "O'rtacha chek",
        "conversion": "Konversiya",
        "provider": "Provider",
        "business_metrics": "Biznes ko'rsatkichlar",
        "business_metrics_hint": "Bu blok xaridorga tizim faqat bot emas, eSIM savdo CRM ekanini ko'rsatadi: tushum, tan narx, foyda, marja va konversiya bitta panelda.",
    },
    "ru": {
        "dashboard": "Панель",
        "orders": "Заказы",
        "visa_reminders": "Срок визы",
        "users": "Пользователи",
        "support": "Поддержка",
        "packages": "eSIM пакеты",
        "settings": "Настройки",
        "export": "Экспорт",
        "broadcast": "Рассылка",
        "logout": "Выйти",
        "login_title": "Visa eSIM Admin",
        "login_hint": "Введите пароль для входа в панель.",
        "password": "Пароль",
        "login": "Войти",
        "wrong_password": "Неверный пароль или пароль не настроен.",
        "panel_private": "Панель работает через localhost и не открыта в интернет.",
        "pending": "Ожидают",
        "order_sum": "Сумма заказов",
        "open_support": "Открытая поддержка",
        "change_password": "Изменить пароль админ панели",
        "old_password": "Старый пароль",
        "new_password": "Новый пароль",
        "repeat_password": "Повторите новый пароль",
        "save": "Сохранить",
        "change_password_btn": "Изменить пароль",
        "bot_payment_settings": "Настройки бота и оплаты",
        "settings_saved": "Настройки сохранены.",
        "packages_title": "eSIM пакеты",
        "add_update_country": "Добавить или обновить страну",
        "code": "Код",
        "country_name": "Название страны",
        "download": "скачать",
        "id": "ID",
        "country": "Страна",
        "plan": "Пакет",
        "price": "Цена",
        "status": "Статус",
        "user": "Пользователь",
        "action": "Действие",
        "done": "Готово",
        "cancel": "Отмена",
        "delete": "Удалить",
        "created": "Создано",
        "sent": "Отправлено",
        "username": "Username",
        "name": "Имя",
        "language": "Язык",
        "last_activity": "Последняя активность",
        "sum": "Сумма",
        "send_via_bot": "Отправить через бота",
        "reply_placeholder": "Введите ответ клиенту...",
        "send": "Отправить",
        "telegram_reply_hint": "Или через Telegram",
        "support_questions": "Вопросы поддержки",
        "question": "Вопрос",
        "file": "Файл",
        "answer": "Ответ",
        "no_file": "Файла нет",
        "open_download": "Открыть/скачать",
        "select_support": "Выберите сообщение поддержки.",
        "client": "Клиент",
        "reply_write": "Напишите ответ...",
        "send_reply": "Отправить ответ",
        "support_state": "Состояние поддержки",
        "open_messages_suffix": "открытых сообщений.",
        "enable_notifications": "Включить уведомления",
        "notify_unsupported": "Этот браузер не поддерживает уведомления.",
        "notify_enabled": "Включено.",
        "notify_denied": "Разрешение не выдано.",
        "new_support": "Новое сообщение поддержки",
        "new_support_body": "Клиент отправил новое сообщение",
        "password_changed_hint": "После смены пароля нужно войти заново.",
        "payment_settings_hint": "Настройки оплаты и eSIM Go сохраняются в .env. Бот прочитает их при следующих запросах.",
        "card_holder": "Владелец карты",
        "card_number": "Номер карты",
        "qr_image_file": "Файл QR изображения",
        "qr_link": "QR ссылка",
        "payment_note": "Примечание к оплате",
        "card_payment_link": "Visa/Mastercard payment link",
        "payme_link": "Payme ссылка",
        "click_link": "Click ссылка",
        "esimgo_api_key": "eSIM Go API Key",
        "esim_markup_percent": "Наценка eSIM, %",
        "package_hint": "Введите до 3 пакетов. Пустые пакеты не сохраняются.",
        "package_1": "1-пакет",
        "package_2": "2-пакет",
        "package_3": "3-пакет",
        "package_saved": "Пакет сохранен.",
        "package_need_code": "Нужны код и название страны.",
        "package_incomplete": "В каждом пакете должны быть data, дни и цена.",
        "price_number": "Цена должна быть числом.",
        "package_need_one": "Добавьте хотя бы один пакет.",
        "old_password_wrong": "Старый пароль неверный.",
        "new_password_short": "Новый пароль должен быть минимум 8 символов.",
        "new_password_mismatch": "Новые пароли не совпадают.",
        "password_changed": "Пароль изменен.",
        "broadcast_title": "Массовая рассылка",
        "broadcast_hint": "Отправляется пользователям, которые нажали /start и не заблокировали бота. Если профиль закрыт, сообщение все равно уйдет при наличии chat ID.",
        "broadcast_text": "Текст сообщения",
        "broadcast_media": "Фото/видео",
        "broadcast_media_hint": "Необязательно: выберите фото или видео. Текст будет отправлен как caption.",
        "broadcast_content_required": "Введите текст или выберите фото/видео.",
        "target_lang": "По языку",
        "all_users": "Все пользователи",
        "send_broadcast": "Отправить всем",
        "broadcast_done": "Отправлено: {sent}. Ошибок/блокировок: {failed}.",
        "esim_countries": "eSIM страны",
        "no_users_hint": "Пока нет пользователей. Люди появятся здесь после /start в боте.",
        "esimgo_api_base": "eSIM Go API Base",
        "new_user": "Новый пользователь",
        "new_user_body": "В боте появился новый пользователь",
        "users_state": "Состояние пользователей",
    },
    "en": {
        "dashboard": "Dashboard",
        "orders": "Orders",
        "visa_reminders": "Visa expiry",
        "users": "Users",
        "support": "Support",
        "packages": "eSIM Packages",
        "settings": "Settings",
        "export": "Export",
        "broadcast": "Broadcast",
        "logout": "Logout",
        "login_title": "Visa eSIM Admin",
        "login_hint": "Enter the password to open the panel.",
        "password": "Password",
        "login": "Login",
        "wrong_password": "Wrong password or password is not configured.",
        "panel_private": "The panel runs through localhost and is not public.",
        "pending": "Pending",
        "order_sum": "Order sum",
        "open_support": "Open support",
        "change_password": "Change admin panel password",
        "old_password": "Old password",
        "new_password": "New password",
        "repeat_password": "Repeat new password",
        "save": "Save",
        "change_password_btn": "Change password",
        "bot_payment_settings": "Bot and payment settings",
        "settings_saved": "Settings saved.",
        "packages_title": "eSIM Packages",
        "add_update_country": "Add or update country",
        "code": "Code",
        "country_name": "Country name",
        "download": "download",
        "id": "ID",
        "country": "Country",
        "plan": "Plan",
        "price": "Price",
        "status": "Status",
        "user": "User",
        "action": "Action",
        "done": "Done",
        "fulfill": "Send eSIM",
        "cancel": "Cancel",
        "delete": "Delete",
        "created": "Created",
        "sent": "Sent",
        "username": "Username",
        "name": "Name",
        "language": "Language",
        "last_activity": "Last activity",
        "sum": "Sum",
        "send_via_bot": "Send via bot",
        "reply_placeholder": "Write a reply to the customer...",
        "send": "Send",
        "telegram_reply_hint": "Or via Telegram",
        "support_questions": "Support questions",
        "question": "Question",
        "file": "File",
        "answer": "Answer",
        "no_file": "No file",
        "open_download": "Open/download",
        "select_support": "Select a support message.",
        "client": "Customer",
        "reply_write": "Write a reply...",
        "send_reply": "Send reply",
        "support_state": "Support status",
        "open_messages_suffix": "open messages.",
        "enable_notifications": "Enable notifications",
        "notify_unsupported": "This browser does not support notifications.",
        "notify_enabled": "Enabled.",
        "notify_denied": "Permission denied.",
        "new_support": "New support message",
        "new_support_body": "A customer sent a new message",
        "password_changed_hint": "After changing the password, you need to log in again.",
        "payment_settings_hint": "Payment and eSIM Go settings are saved to .env. The bot reads them on the next requests.",
        "card_holder": "Card holder",
        "card_number": "Card number",
        "qr_image_file": "QR image file",
        "qr_link": "QR link",
        "payment_note": "Payment note",
        "card_payment_link": "Visa/Mastercard payment link",
        "payme_link": "Payme link",
        "click_link": "Click link",
        "esimgo_api_key": "eSIM Go API Key",
        "esim_markup_percent": "eSIM markup percent",
        "package_hint": "Enter up to 3 packages. Empty packages are not saved.",
        "package_1": "Package 1",
        "package_2": "Package 2",
        "package_3": "Package 3",
        "package_saved": "Package saved.",
        "package_need_code": "Code and country name are required.",
        "package_incomplete": "Each package must include data, days, and price.",
        "price_number": "Price must be a number.",
        "package_need_one": "Enter at least one package.",
        "old_password_wrong": "Old password is wrong.",
        "new_password_short": "New password must be at least 8 characters.",
        "new_password_mismatch": "New passwords do not match.",
        "password_changed": "Password changed.",
        "broadcast_title": "Send broadcast",
        "broadcast_hint": "Sent to users who pressed /start and have not blocked the bot. Private Telegram profiles still work if the bot has their chat ID.",
        "broadcast_text": "Message text",
        "broadcast_media": "Photo/video",
        "broadcast_media_hint": "Optional: choose a photo or video. The text is sent as the caption.",
        "broadcast_content_required": "Enter text or choose a photo/video.",
        "target_lang": "By language",
        "all_users": "All users",
        "send_broadcast": "Send to all",
        "broadcast_done": "Sent: {sent}. Failed/blocked: {failed}.",
        "esim_countries": "eSIM countries",
        "no_users_hint": "No users yet. People who press /start in the bot appear here.",
        "esimgo_api_base": "eSIM Go API Base",
        "new_user": "New user",
        "new_user_body": "A new user joined the bot",
        "users_state": "Users status",
        "paid_revenue": "Paid revenue",
        "cost": "Cost",
        "profit": "Net profit",
        "margin": "Margin",
        "avg_order": "Average order",
        "conversion": "Conversion",
        "provider": "Provider",
        "business_metrics": "Business metrics",
        "business_metrics_hint": "This block shows buyers that the product is not just a bot, but an eSIM sales CRM with revenue, cost, profit, margin, and conversion in one panel.",
    },
}
ADMIN_TEXT["ru"] = {
    "dashboard": "Панель",
    "orders": "Заказы",
    "visa_reminders": "Срок визы",
    "users": "Пользователи",
    "support": "Поддержка",
    "packages": "eSIM пакеты",
    "settings": "Настройки",
    "export": "Экспорт",
    "broadcast": "Рассылка",
    "logout": "Выйти",
    "login_title": "Visa eSIM Admin",
    "login_hint": "Введите пароль для входа в панель.",
    "password": "Пароль",
    "login": "Войти",
    "wrong_password": "Неверный пароль или пароль не настроен.",
    "panel_private": "Админ-панель защищена. Даже по публичной ссылке она не откроется без пароля.",
    "pending": "Ожидают",
    "order_sum": "Сумма заказов",
    "open_support": "Открытые обращения",
    "change_password": "Сменить пароль админ-панели",
    "old_password": "Старый пароль",
    "new_password": "Новый пароль",
    "repeat_password": "Повторите новый пароль",
    "save": "Сохранить",
    "change_password_btn": "Сменить пароль",
    "bot_payment_settings": "Настройки бота, оплаты и eSIM",
    "settings_saved": "Настройки сохранены.",
    "packages_title": "eSIM пакеты",
    "add_update_country": "Добавить или обновить страну",
    "code": "Код",
    "country_name": "Название страны",
    "download": "скачать",
    "id": "ID",
    "country": "Страна",
    "plan": "Пакет",
    "price": "Цена",
    "status": "Статус",
    "user": "Пользователь",
    "action": "Действие",
    "done": "Готово",
    "fulfill": "Отправить eSIM",
    "cancel": "Отменить",
    "delete": "Удалить",
    "created": "Создано",
    "sent": "Отправлено",
    "username": "Username",
    "name": "Имя",
    "language": "Язык",
    "last_activity": "Последняя активность",
    "sum": "Сумма",
    "send_via_bot": "Отправить через бота",
    "reply_placeholder": "Напишите ответ клиенту...",
    "send": "Отправить",
    "telegram_reply_hint": "Или через Telegram",
    "support_questions": "Вопросы поддержки",
    "question": "Вопрос",
    "file": "Файл",
    "answer": "Ответ",
    "no_file": "Файла нет",
    "open_download": "Открыть/скачать",
    "select_support": "Выберите обращение.",
    "client": "Клиент",
    "reply_write": "Напишите ответ...",
    "send_reply": "Отправить ответ",
    "support_state": "Статус поддержки",
    "open_messages_suffix": "открытых сообщений.",
    "enable_notifications": "Включить уведомления",
    "notify_unsupported": "Этот браузер не поддерживает уведомления.",
    "notify_enabled": "Включено.",
    "notify_denied": "Разрешение не выдано.",
    "new_support": "Новое обращение",
    "new_support_body": "Клиент отправил новое сообщение",
    "password_changed_hint": "После смены пароля нужно войти заново.",
    "payment_settings_hint": "Настройки оплаты и eSIM Go сохраняются в .env. Бот прочитает их при следующих запросах.",
    "card_holder": "Владелец карты",
    "card_number": "Номер карты",
    "qr_image_file": "Файл QR изображения",
    "qr_link": "QR ссылка",
    "payment_note": "Примечание к оплате",
    "card_payment_link": "Visa/Mastercard payment link",
    "payme_link": "Payme ссылка",
    "click_link": "Click ссылка",
    "esimgo_api_key": "eSIM Go API Key",
    "esim_markup_percent": "Наценка eSIM, %",
    "package_hint": "Введите до 3 пакетов. Пустые пакеты не сохраняются.",
    "package_1": "Пакет 1",
    "package_2": "Пакет 2",
    "package_3": "Пакет 3",
    "package_saved": "Пакет сохранен.",
    "package_need_code": "Нужны код и название страны.",
    "package_incomplete": "В каждом пакете должны быть data, дни и цена.",
    "price_number": "Цена должна быть числом.",
    "package_need_one": "Добавьте хотя бы один пакет.",
    "old_password_wrong": "Старый пароль неверный.",
    "new_password_short": "Новый пароль должен быть минимум 8 символов.",
    "new_password_mismatch": "Новые пароли не совпадают.",
    "password_changed": "Пароль изменен.",
    "broadcast_title": "Массовая рассылка",
    "broadcast_hint": "Отправляется пользователям, которые нажали /start и не заблокировали бота. Если профиль закрыт, сообщение все равно уйдет при наличии chat ID.",
    "broadcast_text": "Текст сообщения",
    "broadcast_media": "Фото/видео",
    "broadcast_media_hint": "Необязательно: выберите фото или видео. Текст будет отправлен как caption.",
    "broadcast_content_required": "Введите текст или выберите фото/видео.",
    "target_lang": "По языку",
    "all_users": "Все пользователи",
    "send_broadcast": "Отправить всем",
    "broadcast_done": "Отправлено: {sent}. Ошибок/блокировок: {failed}.",
    "esim_countries": "eSIM страны",
    "no_users_hint": "Пока нет пользователей. Люди появятся здесь после /start в боте.",
    "esimgo_api_base": "eSIM Go API адрес",
    "new_user": "Новый пользователь",
    "new_user_body": "В боте появился новый пользователь",
    "users_state": "Статус пользователей",
    "paid_revenue": "Оплаченная выручка",
    "cost": "Себестоимость",
    "profit": "Чистая прибыль",
    "margin": "Маржа",
    "avg_order": "Средний чек",
    "conversion": "Конверсия",
    "provider": "Провайдер",
    "business_metrics": "Бизнес-показатели",
    "business_metrics_hint": "Этот блок показывает покупателю, что продукт не просто бот, а CRM для продаж eSIM с выручкой, себестоимостью, прибылью, маржой и конверсией в одной панели.",
}

DEFAULT_PACKAGES = {
    "uae": {"country": "United Arab Emirates / Dubai", "plans": [{"data": "1GB", "days": "7 kun", "price_usd": 5}, {"data": "3GB", "days": "15 kun", "price_usd": 11}, {"data": "5GB", "days": "30 kun", "price_usd": 16}]},
    "turkiye": {"country": "Turkiye", "plans": [{"data": "1GB", "days": "7 kun", "price_usd": 4}, {"data": "3GB", "days": "15 kun", "price_usd": 9}, {"data": "5GB", "days": "30 kun", "price_usd": 14}]},
    "kazakhstan": {"country": "Kazakhstan", "plans": [{"data": "1GB", "days": "7 kun", "price_usd": 3}, {"data": "3GB", "days": "15 kun", "price_usd": 8}, {"data": "5GB", "days": "30 kun", "price_usd": 12}]},
    "china": {"country": "China", "plans": [{"data": "1GB", "days": "7 kun", "price_usd": 6}, {"data": "3GB", "days": "15 kun", "price_usd": 13}, {"data": "5GB", "days": "30 kun", "price_usd": 19}]},
    "malaysia": {"country": "Malaysia", "plans": [{"data": "1GB", "days": "7 kun", "price_usd": 4}, {"data": "3GB", "days": "15 kun", "price_usd": 9}, {"data": "5GB", "days": "30 kun", "price_usd": 13}]},
    "thailand": {"country": "Thailand", "plans": [{"data": "1GB", "days": "7 kun", "price_usd": 4}, {"data": "3GB", "days": "15 kun", "price_usd": 9}, {"data": "5GB", "days": "30 kun", "price_usd": 13}]},
}


def read_json(name: str, default):
    path = DATA_DIR / name
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json(name: str, value) -> None:
    (DATA_DIR / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def read_env(name: str, default: str = "") -> str:
    if os.environ.get(name):
        return os.environ[name]
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return default
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == name:
            return value.strip().strip('"').strip("'")
    return default


def write_env_values(values: dict[str, str]) -> None:
    env_path = BASE_DIR / ".env"
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    seen = set()
    updated_lines = []
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#") or "=" not in line:
            updated_lines.append(line)
            continue
        key = line.split("=", 1)[0].strip()
        if key in values:
            updated_lines.append(f"{key}={values[key]}")
            seen.add(key)
        else:
            updated_lines.append(line)
    for key, value in values.items():
        if key not in seen:
            updated_lines.append(f"{key}={value}")
    env_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def normalize_code(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("'", "")


def read_packages() -> dict:
    packages = read_json(PACKAGES_FILE, None)
    if not isinstance(packages, dict) or not packages:
        packages = DEFAULT_PACKAGES
        write_json(PACKAGES_FILE, packages)
    return packages


def write_packages(packages: dict) -> None:
    write_json(PACKAGES_FILE, packages)


def esc(value) -> str:
    return html.escape("" if value is None else str(value))


def admin_t(key: str) -> str:
    lang = CURRENT_ADMIN_LANG if CURRENT_ADMIN_LANG in ADMIN_TEXT else "uz"
    return ADMIN_TEXT[lang].get(key, ADMIN_TEXT["uz"].get(key, key))


def user_lang(user_id: str) -> str:
    user = read_json("users.json", {}).get(str(user_id), {})
    lang = user.get("lang") or "uz"
    return lang if lang in ADMIN_TEXT else "uz"


def translate_text(text: str, target_lang: str) -> str:
    text = (text or "").strip()
    if not text or target_lang not in ADMIN_TEXT:
        return text
    try:
        query = urlencode({
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text,
        })
        with urlopen(f"https://translate.googleapis.com/translate_a/single?{query}", timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
        return "".join(part[0] for part in data[0] if part and part[0]).strip() or text
    except Exception:
        return text


def display_text(text: str) -> str:
    return translate_text(text, CURRENT_ADMIN_LANG)


def admin_password() -> str:
    return read_env("ADMIN_PANEL_PASSWORD")


def session_secret() -> str:
    return read_env("ADMIN_PANEL_SECRET", admin_password())


def sign_session(expiry: int) -> str:
    secret = session_secret().encode("utf-8")
    payload = str(expiry)
    signature = hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def valid_session(token: str) -> bool:
    if not token or "." not in token or not session_secret():
        return False
    expiry_text, signature = token.split(".", 1)
    expected = hmac.new(
        session_secret().encode("utf-8"),
        expiry_text.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return False
    try:
        return int(expiry_text) > int(time.time())
    except ValueError:
        return False


def login_page(error: str = "") -> bytes:
    error_html = f"<p class='danger-text'>{esc(error)}</p>" if error else ""
    body = f"""<!doctype html>
<html lang="uz">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Visa eSIM Admin Panel</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; background: #f5f7fb; color: #172033; display: grid; min-height: 100vh; place-items: center; }}
    .box {{ width: min(420px, calc(100vw - 32px)); background: white; border: 1px solid #dde3ee; border-radius: 8px; padding: 22px; }}
    input {{ width: 100%; padding: 12px; border: 1px solid #cdd8ea; border-radius: 6px; box-sizing: border-box; }}
    button {{ width: 100%; margin-top: 12px; border: 0; border-radius: 6px; padding: 11px; background: #123d76; color: white; cursor: pointer; }}
    .muted {{ color: #667085; }}
    .danger-text {{ color: #b42318; }}
  </style>
</head>
<body>
  <form class="box" method="post" action="/login">
    <h2>{esc(admin_t("login_title"))}</h2>
    <p class="muted">UZ · <a href="/set-lang?lang=ru">RU</a> · <a href="/set-lang?lang=en">EN</a></p>
    <p class="muted">{esc(admin_t("login_hint"))}</p>
    {error_html}
    <input type="password" name="password" placeholder="{esc(admin_t("password"))}" autofocus required>
    <button>{esc(admin_t("login"))}</button>
  </form>
</body>
</html>"""
    return body.encode("utf-8")


def layout(title: str, body: str) -> bytes:
    nav_items = [
        ("/", admin_t("dashboard")),
        ("/orders", admin_t("orders")),
        ("/reminders", admin_t("visa_reminders")),
        ("/users", admin_t("users")),
        ("/support", admin_t("support")),
        ("/broadcast", admin_t("broadcast")),
        ("/packages", admin_t("packages")),
        ("/settings", admin_t("settings")),
        ("/export", admin_t("export")),
    ]
    nav_html = "\n".join(f'<a href="{href}">{esc(label)}</a>' for href, label in nav_items)
    page = f"""<!doctype html>
<html lang="uz">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Visa eSIM Admin Panel - {esc(title)}</title>
  <style>
    :root {{ --blue: #123d76; --line: #dde3ee; --bg: #f5f7fb; --text: #172033; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--text); }}
    .shell {{ display: grid; grid-template-columns: 248px minmax(0, 1fr); min-height: 100vh; }}
    aside {{ background: #0f2f5f; color: white; padding: 18px 14px; }}
    .brand {{ display: flex; align-items: center; gap: 10px; padding: 8px 10px 18px; border-bottom: 1px solid rgba(255,255,255,.18); margin-bottom: 14px; }}
    .brand-mark {{ width: 34px; height: 34px; border-radius: 8px; display: grid; place-items: center; background: #1f63b5; font-weight: 700; }}
    .brand-title {{ font-weight: 700; line-height: 1.2; }}
    .brand-sub {{ color: #b9c8dc; font-size: 12px; margin-top: 2px; }}
    nav {{ display: grid; gap: 6px; }}
    nav a {{ color: #edf5ff; text-decoration: none; padding: 10px 11px; border-radius: 7px; display: block; }}
    nav a:hover {{ background: rgba(255,255,255,.12); }}
    .sidebar-foot {{ margin-top: 18px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,.18); display: grid; gap: 8px; }}
    .sidebar-foot a {{ color: #d9e8fb; text-decoration: none; font-size: 13px; }}
    .content {{ min-width: 0; }}
    header {{ background: white; border-bottom: 1px solid var(--line); padding: 16px 22px; display: flex; justify-content: space-between; align-items: center; gap: 14px; }}
    header h2 {{ margin: 0; font-size: 20px; }}
    .langbar {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .langbar a {{ color: var(--blue); text-decoration: none; border: 1px solid #cdd8ea; border-radius: 6px; padding: 6px 8px; background: #fff; }}
    main {{ padding: 22px; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #dde3ee; }}
    th, td {{ padding: 10px; border-bottom: 1px solid #edf1f7; text-align: left; vertical-align: top; }}
    th {{ background: #eef4ff; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 18px; }}
    .card {{ background: white; border: 1px solid #dde3ee; border-radius: 8px; padding: 14px; box-shadow: 0 1px 2px rgba(16,24,40,.04); }}
    .panel-section {{ background: white; border: 1px solid #dde3ee; border-radius: 8px; padding: 16px; margin: 0 0 18px; }}
    .profit {{ color: #067647; font-weight: 700; }}
    .loss {{ color: #b42318; font-weight: 700; }}
    .num {{ font-size: 28px; font-weight: 700; }}
    form {{ display: inline; }}
    textarea {{ width: 100%; min-height: 110px; padding: 10px; border: 1px solid #cdd8ea; border-radius: 6px; resize: vertical; box-sizing: border-box; }}
    input[type="text"], input[type="password"] {{ width: 100%; padding: 10px; border: 1px solid #cdd8ea; border-radius: 6px; box-sizing: border-box; }}
    input[type="number"], input[type="url"] {{ width: 100%; padding: 10px; border: 1px solid #cdd8ea; border-radius: 6px; box-sizing: border-box; }}
    button {{ border: 0; border-radius: 6px; padding: 7px 10px; background: #123d76; color: white; cursor: pointer; }}
    .danger {{ background: #b42318; }}
    .muted {{ color: #667085; }}
    .badge {{ display: inline-block; padding: 3px 8px; border-radius: 999px; background: #eef4ff; color: #123d76; font-size: 12px; }}
    .open {{ background: #fff3cd; color: #8a5a00; }}
    .replied {{ background: #dcfce7; color: #166534; }}
    .preview {{ max-width: 360px; max-height: 260px; display: block; border: 1px solid #dde3ee; border-radius: 8px; margin-top: 8px; cursor: zoom-in; }}
    .modal {{ position: fixed; inset: 0; background: rgba(12, 18, 32, .82); display: none; align-items: center; justify-content: center; z-index: 50; padding: 22px; }}
    .modal.opened {{ display: flex; }}
    .modal-content {{ max-width: 94vw; max-height: 90vh; }}
    .modal-content img, .modal-content video {{ max-width: 94vw; max-height: 90vh; border-radius: 8px; background: #000; }}
    .modal-close {{ position: fixed; top: 16px; right: 18px; font-size: 28px; background: white; color: #172033; border-radius: 999px; width: 44px; height: 44px; }}
    @media (max-width: 820px) {{
      .shell {{ grid-template-columns: 1fr; }}
      aside {{ position: static; }}
      nav {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      header {{ align-items: flex-start; flex-direction: column; }}
      main {{ padding: 14px; overflow-x: auto; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <aside>
      <div class="brand">
        <div class="brand-mark">VE</div>
        <div>
          <div class="brand-title">Visa eSIM</div>
          <div class="brand-sub">Admin Panel</div>
        </div>
      </div>
      <nav>
        {nav_html}
      </nav>
      <div class="sidebar-foot">
        <a href="/logout">{esc(admin_t("logout"))}</a>
      </div>
    </aside>
    <div class="content">
      <header>
        <h2>{esc(title)}</h2>
        <div class="langbar">
          <a href="/set-lang?lang=uz">UZ</a>
          <a href="/set-lang?lang=ru">RU</a>
          <a href="/set-lang?lang=en">EN</a>
        </div>
      </header>
      <main>{body}</main>
    </div>
  </div>
</body>
</html>"""
    return page.encode("utf-8")


def dashboard():
    orders = read_json("orders.json", [])
    reminders = read_json("reminders.json", [])
    users = collect_users()
    support_messages = read_json("support_messages.json", [])
    active_orders = [order for order in orders if order.get("status") != "cancelled"]
    paid_orders = [
        order
        for order in orders
        if order.get("status") in {"completed", "fulfilled", "done"}
    ]
    pending = sum(1 for order in active_orders if order.get("status") == "pending_payment")
    open_support = sum(1 for item in support_messages if item.get("status") != "replied")
    revenue = sum(float(order.get("price_usd", 0) or 0) for order in active_orders)
    paid_revenue = sum(float(order.get("price_usd", 0) or 0) for order in paid_orders)
    cost = sum(float(order.get("cost_usd", order.get("price_usd", 0)) or 0) for order in active_orders)
    profit = sum(float(order.get("profit_usd", 0) or 0) for order in active_orders)
    margin = (profit / revenue * 100) if revenue else 0
    avg_order = (revenue / len(active_orders)) if active_orders else 0
    conversion = (len(active_orders) / len(users) * 100) if users else 0
    esim_count = esim_country_count()
    body = f"""
<div class="cards">
  <div class="card"><div class="muted">{esc(admin_t("orders"))}</div><div class="num">{len(orders)}</div></div>
  <div class="card"><div class="muted">{esc(admin_t("pending"))}</div><div class="num">{pending}</div></div>
  <div class="card"><div class="muted">{esc(admin_t("order_sum"))}</div><div class="num">${revenue:.2f}</div></div>
  <div class="card"><div class="muted">{esc(admin_t("paid_revenue"))}</div><div class="num">${paid_revenue:.2f}</div></div>
  <div class="card"><div class="muted">{esc(admin_t("cost"))}</div><div class="num">${cost:.2f}</div></div>
  <div class="card"><div class="muted">{esc(admin_t("profit"))}</div><div class="num">${profit:.2f}</div></div>
  <div class="card"><div class="muted">{esc(admin_t("margin"))}</div><div class="num">{margin:.1f}%</div></div>
  <div class="card"><div class="muted">{esc(admin_t("avg_order"))}</div><div class="num">${avg_order:.2f}</div></div>
  <div class="card"><div class="muted">{esc(admin_t("conversion"))}</div><div class="num">{conversion:.1f}%</div></div>
  <div class="card"><div class="muted">{esc(admin_t("esim_countries"))}</div><div class="num">{esim_count}</div></div>
  <div class="card"><div class="muted">{esc(admin_t("visa_reminders"))}</div><div class="num">{len(reminders)}</div></div>
  <div class="card"><div class="muted">{esc(admin_t("users"))}</div><div class="num" id="dashboard-users-count">{len(users)}</div></div>
  <div class="card"><div class="muted">{esc(admin_t("open_support"))}</div><div class="num">{open_support}</div></div>
</div>
<section class="panel-section">
  <h3>{esc(admin_t("business_metrics"))}</h3>
  <p class="muted">{esc(admin_t("business_metrics_hint"))}</p>
</section>
<p class="muted">{esc(admin_t("panel_private"))}</p>
<script>
async function pollDashboardUsers() {{
  try {{
    const response = await fetch("/users-state", {{cache: "no-store"}});
    const data = await response.json();
    const node = document.getElementById("dashboard-users-count");
    if (node) node.textContent = data.count;
  }} catch (error) {{}}
}}
pollDashboardUsers();
setInterval(pollDashboardUsers, 1000);
</script>
"""
    return layout(admin_t("dashboard"), body)


def esim_country_count() -> int:
    cache = read_json("esimgo_catalogue_cache.json", {})
    if isinstance(cache, dict) and isinstance(cache.get("packages"), dict):
        return len(cache["packages"])
    packages = read_packages()
    return len(packages)


def orders_page():
    rows = []
    for order in reversed(read_json("orders.json", [])):
        price = float(order.get("price_usd", 0) or 0)
        cost = float(order.get("cost_usd", price) or 0)
        profit = float(order.get("profit_usd", price - cost) or 0)
        profit_class = "profit" if profit >= 0 else "loss"
        provider = order.get("provider") or "manual"
        bundle = order.get("bundle_name") or ""
        rows.append(
            f"<tr><td>{esc(order.get('id'))}</td><td>{esc(order.get('country'))}</td>"
            f"<td>{esc(order.get('data'))}, {esc(order.get('days'))}</td>"
            f"<td>${price:.2f}</td><td>${cost:.2f}</td><td class='{profit_class}'>${profit:.2f}</td>"
            f"<td>{esc(provider)}<br><span class='muted'>{esc(bundle)}</span></td>"
            f"<td>{esc(order.get('status'))}</td>"
            f"<td>{esc(order.get('username') or order.get('user_id'))}</td>"
            f"<td><form method='post' action='/order-fulfill'><input type='hidden' name='id' value='{esc(order.get('id'))}'><button>{esc(admin_t('fulfill'))}</button></form> "
            f"<form method='post' action='/order-status'><input type='hidden' name='id' value='{esc(order.get('id'))}'><input type='hidden' name='status' value='completed'><button>{esc(admin_t('done'))}</button></form> "
            f"<form method='post' action='/order-status'><input type='hidden' name='id' value='{esc(order.get('id'))}'><input type='hidden' name='status' value='cancelled'><button class='danger'>{esc(admin_t('cancel'))}</button></form></td></tr>"
        )
    body = (
        f"<h3>{esc(admin_t('orders'))}</h3>"
        f"<table><tr><th>{esc(admin_t('id'))}</th><th>{esc(admin_t('country'))}</th>"
        f"<th>{esc(admin_t('plan'))}</th><th>{esc(admin_t('price'))}</th><th>{esc(admin_t('cost'))}</th>"
        f"<th>{esc(admin_t('profit'))}</th><th>{esc(admin_t('provider'))}</th><th>{esc(admin_t('status'))}</th>"
        f"<th>{esc(admin_t('user'))}</th><th>{esc(admin_t('action'))}</th></tr>"
        + "".join(rows)
        + "</table>"
    )
    return layout(admin_t("orders"), body)


def reminders_page():
    rows = []
    for reminder in reversed(read_json("reminders.json", [])):
        rows.append(
            f"<tr><td>{esc(reminder.get('id'))}</td><td>{esc(reminder.get('expiry_date'))}</td>"
            f"<td>{esc(reminder.get('username') or reminder.get('user_id'))}</td>"
            f"<td>{esc(', '.join(reminder.get('sent', [])))}</td></tr>"
        )
    body = f"<h3>{esc(admin_t('visa_reminders'))}</h3><table><tr><th>{esc(admin_t('id'))}</th><th>{esc(admin_t('visa_reminders'))}</th><th>{esc(admin_t('user'))}</th><th>{esc(admin_t('sent'))}</th></tr>" + "".join(rows) + "</table>"
    return layout(admin_t("visa_reminders"), body)


def collect_users():
    users = {}
    raw_users = read_json("users.json", {})
    orders = read_json("orders.json", [])
    reminders = read_json("reminders.json", [])
    support_messages = read_json("support_messages.json", [])

    for user_id, user in raw_users.items():
        users[str(user_id)] = {
            "user_id": str(user_id),
            "username": user.get("username", ""),
            "first_name": user.get("first_name", ""),
            "lang": user.get("lang", ""),
            "updated_at": user.get("updated_at", ""),
            "orders_count": 0,
            "pending_count": 0,
            "orders_sum": 0.0,
            "reminders_count": 0,
            "support_count": 0,
            "last_activity": user.get("updated_at", ""),
        }

    def ensure_user(source):
        user_id = str(source.get("user_id") or "")
        if not user_id:
            return None
        if user_id not in users:
            users[user_id] = {
                "user_id": user_id,
                "username": "",
                "first_name": "",
                "lang": "",
                "updated_at": "",
                "orders_count": 0,
                "pending_count": 0,
                "orders_sum": 0.0,
                "reminders_count": 0,
                "support_count": 0,
                "last_activity": "",
            }
        user = users[user_id]
        if source.get("username"):
            user["username"] = source.get("username")
        if source.get("first_name"):
            user["first_name"] = source.get("first_name")
        activity = source.get("updated_at") or source.get("created_at") or ""
        if activity and activity > user.get("last_activity", ""):
            user["last_activity"] = activity
        return user

    for order in orders:
        user = ensure_user(order)
        if not user:
            continue
        user["orders_count"] += 1
        if order.get("status") == "pending_payment":
            user["pending_count"] += 1
        try:
            user["orders_sum"] += float(order.get("price_usd") or 0)
        except (TypeError, ValueError):
            pass

    for reminder in reminders:
        user = ensure_user(reminder)
        if user:
            user["reminders_count"] += 1

    for item in support_messages:
        user = ensure_user(item)
        if user:
            user["support_count"] += 1

    return sorted(users.values(), key=lambda item: item.get("last_activity", ""), reverse=True)


def users_page():
    users = collect_users()
    rows = []
    for user in users:
        user_id = user.get("user_id")
        username = f"@{user.get('username')}" if user.get("username") else ""
        rows.append(
            f"<tr><td><a href='/user?id={esc(user_id)}'>{esc(user_id)}</a></td><td>{esc(username)}</td>"
            f"<td>{esc(user.get('first_name'))}</td><td>{esc(user.get('lang'))}</td>"
            f"<td>{esc(user.get('orders_count'))}</td><td>{esc(user.get('pending_count'))}</td>"
            f"<td>${user.get('orders_sum', 0):.2f}</td><td>{esc(user.get('reminders_count'))}</td>"
            f"<td>{esc(user.get('support_count'))}</td><td>{esc(user.get('last_activity'))}</td></tr>"
        )
    empty = "" if rows else f"<p class='muted'>{esc(admin_t('no_users_hint'))}</p>"
    latest = users[0] if users else {}
    body = f"""
<h3>{esc(admin_t('users'))}</h3>
<p class="muted"><b>{esc(admin_t('users_state'))}:</b> <span id="users-count">{len(users)}</span></p>
{empty}
<table><tr><th>{esc(admin_t('id'))}</th><th>{esc(admin_t('username'))}</th><th>{esc(admin_t('name'))}</th><th>{esc(admin_t('language'))}</th><th>{esc(admin_t('orders'))}</th><th>{esc(admin_t('pending'))}</th><th>{esc(admin_t('sum'))}</th><th>{esc(admin_t('visa_reminders'))}</th><th>{esc(admin_t('support'))}</th><th>{esc(admin_t('last_activity'))}</th></tr>{"".join(rows)}</table>
<script>
let latestUserId = {json.dumps(latest.get("user_id", ""))};
let usersCount = {len(users)};
const userNotifyTitle = {json.dumps(admin_t("new_user"))};
const userNotifyBody = {json.dumps(admin_t("new_user_body"))};

function notifyUserJoined(data) {{
  try {{
    if ("Notification" in window && Notification.permission === "granted") {{
      new Notification(userNotifyTitle, {{ body: data.latest_user || userNotifyBody }});
    }}
  }} catch (error) {{}}
}}

async function pollUsers() {{
  try {{
    const response = await fetch("/users-state?latest=" + encodeURIComponent(latestUserId), {{cache: "no-store"}});
    const data = await response.json();
    document.getElementById("users-count").textContent = data.count;
    if (data.count > usersCount || (data.latest_id && data.latest_id !== latestUserId)) {{
      notifyUserJoined(data);
      setTimeout(function() {{ window.location.reload(); }}, 900);
      return;
    }}
    usersCount = data.count;
    latestUserId = data.latest_id || latestUserId;
  }} catch (error) {{}}
}}

pollUsers();
setInterval(pollUsers, 1000);
</script>
"""
    return layout(admin_t("users"), body)


def users_state() -> bytes:
    users = collect_users()
    latest = users[0] if users else {}
    username = latest.get("username") or latest.get("first_name") or latest.get("user_id") or ""
    payload = {
        "count": len(users),
        "latest_id": latest.get("user_id", ""),
        "latest_user": f"@{username}" if latest.get("username") else username,
        "latest_activity": latest.get("last_activity", ""),
    }
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def user_detail_page(user_id: str):
    users = read_json("users.json", {})
    orders = [order for order in read_json("orders.json", []) if str(order.get("user_id")) == user_id]
    reminders = [
        reminder for reminder in read_json("reminders.json", []) if str(reminder.get("user_id")) == user_id
    ]
    support_messages = [
        item for item in read_json("support_messages.json", []) if str(item.get("user_id")) == user_id
    ]
    user = users.get(user_id, {})
    if not user:
        for item in collect_users():
            if item.get("user_id") == user_id:
                user = item
                break

    order_rows = []
    for order in reversed(orders):
        price = float(order.get("price_usd", 0) or 0)
        cost = float(order.get("cost_usd", price) or 0)
        profit = float(order.get("profit_usd", price - cost) or 0)
        profit_class = "profit" if profit >= 0 else "loss"
        order_rows.append(
            f"<tr><td>{esc(order.get('id'))}</td><td>{esc(order.get('country'))}</td>"
            f"<td>{esc(order.get('data'))}, {esc(order.get('days'))}</td>"
            f"<td>${price:.2f}</td><td>${cost:.2f}</td><td class='{profit_class}'>${profit:.2f}</td>"
            f"<td>{esc(order.get('status'))}</td><td>{esc(order.get('created_at'))}</td>"
            f"<td><form method='post' action='/order-fulfill'><input type='hidden' name='id' value='{esc(order.get('id'))}'><input type='hidden' name='back' value='/user?id={esc(user_id)}'><button>{esc(admin_t('fulfill'))}</button></form> "
            f"<form method='post' action='/order-status'><input type='hidden' name='id' value='{esc(order.get('id'))}'><input type='hidden' name='status' value='completed'><input type='hidden' name='back' value='/user?id={esc(user_id)}'><button>{esc(admin_t('done'))}</button></form> "
            f"<form method='post' action='/order-status'><input type='hidden' name='id' value='{esc(order.get('id'))}'><input type='hidden' name='status' value='cancelled'><input type='hidden' name='back' value='/user?id={esc(user_id)}'><button class='danger'>{esc(admin_t('cancel'))}</button></form></td></tr>"
        )

    reminder_rows = []
    for reminder in reversed(reminders):
        reminder_rows.append(
            f"<tr><td>{esc(reminder.get('id'))}</td><td>{esc(reminder.get('expiry_date'))}</td>"
            f"<td>{esc(', '.join(reminder.get('sent', [])))}</td><td>{esc(reminder.get('created_at'))}</td></tr>"
        )

    support_rows = []
    for item in reversed(support_messages):
        attachment = item.get("attachment") or {}
        support_rows.append(
            f"<tr><td><a href='/support?id={esc(item.get('id'))}'>{esc(item.get('id'))}</a></td>"
            f"<td><span class='badge {esc(item.get('status'))}'>{esc(item.get('status'))}</span></td>"
            f"<td>{esc(display_text(item.get('text')))}</td><td>{esc(attachment.get('type'))}</td><td>{esc(display_text(item.get('answer')))}</td>"
            f"<td>{esc(item.get('created_at'))}</td></tr>"
        )

    body = f"""
<h3>{esc(admin_t('user'))} {esc(user_id)}</h3>
<div class="cards">
  <div class="card"><div class="muted">{esc(admin_t('username'))}</div><div>@{esc(user.get('username'))}</div></div>
  <div class="card"><div class="muted">{esc(admin_t('name'))}</div><div>{esc(user.get('first_name'))}</div></div>
  <div class="card"><div class="muted">{esc(admin_t('language'))}</div><div>{esc(user.get('lang'))}</div></div>
  <div class="card"><div class="muted">{esc(admin_t('last_activity'))}</div><div>{esc(user.get('last_activity') or user.get('updated_at'))}</div></div>
</div>
<div class="card">
  <h4>{esc(admin_t('send_via_bot'))}</h4>
  <form method="post" action="/send-message">
    <input type="hidden" name="user_id" value="{esc(user_id)}">
    <textarea name="text" placeholder="{esc(admin_t('reply_placeholder'))}" required></textarea>
    <div style="margin-top:10px"><button>{esc(admin_t('send'))}</button></div>
  </form>
  <p class="muted">{esc(admin_t('telegram_reply_hint'))}: /reply {esc(user_id)} javob matni</p>
</div>
<h4>{esc(admin_t('orders'))}</h4>
<table><tr><th>{esc(admin_t('id'))}</th><th>{esc(admin_t('country'))}</th><th>{esc(admin_t('plan'))}</th><th>{esc(admin_t('price'))}</th><th>{esc(admin_t('cost'))}</th><th>{esc(admin_t('profit'))}</th><th>{esc(admin_t('status'))}</th><th>{esc(admin_t('created'))}</th><th>{esc(admin_t('action'))}</th></tr>{''.join(order_rows)}</table>
<h4>{esc(admin_t('visa_reminders'))}</h4>
<table><tr><th>{esc(admin_t('id'))}</th><th>{esc(admin_t('visa_reminders'))}</th><th>{esc(admin_t('sent'))}</th><th>{esc(admin_t('created'))}</th></tr>{''.join(reminder_rows)}</table>
<h4>{esc(admin_t('support_questions'))}</h4>
<table><tr><th>{esc(admin_t('id'))}</th><th>{esc(admin_t('status'))}</th><th>{esc(admin_t('question'))}</th><th>{esc(admin_t('file'))}</th><th>{esc(admin_t('answer'))}</th><th>{esc(admin_t('created'))}</th></tr>{''.join(support_rows)}</table>
"""
    return layout(f"{admin_t('user')} {user_id}", body)


def attachment_html(item: dict) -> str:
    attachment = item.get("attachment") or {}
    file_id = attachment.get("file_id")
    if not file_id:
        return f"<span class='muted'>{esc(admin_t('no_file'))}</span>"
    file_name = attachment.get("file_name") or "file"
    url = f"/file?file_id={quote(file_id)}&name={quote(file_name)}"
    file_type = attachment.get("type") or "file"
    link = f"<a href='{url}' target='_blank'>{esc(admin_t('open_download'))}: {esc(file_name)}</a>"
    if file_type == "photo":
        return f"{link}<img class='preview' src='{url}' alt='support image' onclick=\"openMedia('{url}', 'photo')\">"
    if file_type in {"video", "animation"}:
        return f"{link}<video class='preview' controls src='{url}' onclick=\"openMedia('{url}', 'video')\"></video>"
    return link


def support_page(selected_id: str = ""):
    messages = read_json("support_messages.json", [])
    latest_id = messages[-1].get("id") if messages else ""
    open_count = sum(1 for item in messages if item.get("status") != "replied")
    selected = None
    if selected_id:
        selected = next((item for item in messages if item.get("id") == selected_id), None)
    elif messages:
        selected = next((item for item in reversed(messages) if item.get("status") != "replied"), None)
        if selected is None:
            selected = messages[-1]

    rows = []
    for item in reversed(messages):
        username = f"@{item.get('username')}" if item.get("username") else item.get("user_id")
        attachment = item.get("attachment") or {}
        rows.append(
            f"<tr><td><a href='/support?id={esc(item.get('id'))}'>{esc(item.get('id'))}</a></td>"
            f"<td><span class='badge {esc(item.get('status'))}'>{esc(item.get('status'))}</span></td>"
            f"<td><a href='/user?id={esc(item.get('user_id'))}'>{esc(username)}</a></td>"
            f"<td>{esc(display_text(item.get('text')))}</td><td>{esc(attachment.get('type'))}</td><td>{esc(item.get('created_at'))}</td></tr>"
        )

    selected_html = f"<p class='muted'>{esc(admin_t('select_support'))}</p>"
    if selected:
        username = f"@{selected.get('username')}" if selected.get("username") else f"id:{selected.get('user_id')}"
        selected_html = f"""
<div class="card">
  <h3>{esc(admin_t('support'))}: {esc(selected.get('id'))}</h3>
  <p><b>{esc(admin_t('client'))}:</b> <a href="/user?id={esc(selected.get('user_id'))}">{esc(username)}</a></p>
  <p><b>{esc(admin_t('status'))}:</b> <span class="badge {esc(selected.get('status'))}">{esc(selected.get('status'))}</span></p>
  <p><b>{esc(admin_t('question'))}:</b><br>{esc(display_text(selected.get('text')))}</p>
  <p><b>{esc(admin_t('file'))}:</b><br>{attachment_html(selected)}</p>
  <form method="post" action="/send-message">
    <input type="hidden" name="user_id" value="{esc(selected.get('user_id'))}">
    <input type="hidden" name="support_id" value="{esc(selected.get('id'))}">
    <textarea name="text" placeholder="{esc(admin_t('reply_write'))}" required></textarea>
    <div style="margin-top:10px"><button>{esc(admin_t('send_reply'))}</button></div>
  </form>
</div>
"""
    body = f"""
<div class="card" id="support-alert">
  <b>{esc(admin_t('support_state'))}:</b> <span id="support-open-count">{open_count}</span> {esc(admin_t('open_messages_suffix'))}
  <button type="button" onclick="enableNotifications()">{esc(admin_t('enable_notifications'))}</button>
  <span class="muted" id="notify-status"></span>
</div>
{selected_html}
<h3>{esc(admin_t('support'))} inbox</h3>
<table><tr><th>{esc(admin_t('id'))}</th><th>{esc(admin_t('status'))}</th><th>{esc(admin_t('user'))}</th><th>{esc(admin_t('question'))}</th><th>{esc(admin_t('file'))}</th><th>{esc(admin_t('created'))}</th></tr>{''.join(rows)}</table>
<div class="modal" id="media-modal" onclick="closeMedia()">
  <button type="button" class="modal-close" onclick="closeMedia()">x</button>
  <div class="modal-content" id="media-content" onclick="event.stopPropagation()"></div>
</div>
<script>
let latestSupportId = {json.dumps(latest_id)};
let lastOpenCount = {open_count};
let originalTitle = document.title;

function openMedia(url, type) {{
  const modal = document.getElementById("media-modal");
  const content = document.getElementById("media-content");
  if (type === "video") {{
    content.innerHTML = '<video controls autoplay src="' + url + '"></video>';
  }} else {{
    content.innerHTML = '<img src="' + url + '" alt="support media">';
  }}
  modal.classList.add("opened");
}}

function closeMedia() {{
  const modal = document.getElementById("media-modal");
  const content = document.getElementById("media-content");
  modal.classList.remove("opened");
  content.innerHTML = "";
}}

document.addEventListener("keydown", function(event) {{
  if (event.key === "Escape") closeMedia();
}});

function enableNotifications() {{
  if (!("Notification" in window)) {{
    document.getElementById("notify-status").textContent = {json.dumps(admin_t('notify_unsupported'))};
    return;
  }}
  Notification.requestPermission().then(function(permission) {{
    document.getElementById("notify-status").textContent =
      permission === "granted" ? {json.dumps(admin_t('notify_enabled'))} : {json.dumps(admin_t('notify_denied'))};
  }});
}}

function beep() {{
  try {{
    const audio = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audio.createOscillator();
    const gain = audio.createGain();
    oscillator.connect(gain);
    gain.connect(audio.destination);
    oscillator.frequency.value = 880;
    gain.gain.value = 0.08;
    oscillator.start();
    setTimeout(function() {{
      oscillator.stop();
      audio.close();
    }}, 180);
  }} catch (error) {{}}
}}

function notifyNewSupport(data) {{
  document.title = "(" + data.open_count + ") " + {json.dumps(admin_t('new_support'))};
  beep();
  if ("Notification" in window && Notification.permission === "granted") {{
    new Notification({json.dumps(admin_t('new_support'))}, {{
      body: data.latest_text || {json.dumps(admin_t('new_support_body'))}
    }});
  }}
}}

async function pollSupport() {{
  try {{
    const response = await fetch("/support-state?latest=" + encodeURIComponent(latestSupportId), {{cache: "no-store"}});
    const data = await response.json();
    document.getElementById("support-open-count").textContent = data.open_count;
    if (data.latest_id && data.latest_id !== latestSupportId) {{
      notifyNewSupport(data);
      setTimeout(function() {{
        window.location.reload();
      }}, 900);
      return;
    }}
    if (data.open_count !== lastOpenCount) {{
      document.title = data.open_count ? "(" + data.open_count + ") " + originalTitle : originalTitle;
      lastOpenCount = data.open_count;
    }}
  }} catch (error) {{}}
}}

setInterval(pollSupport, 3000);
</script>
"""
    return layout(admin_t("support"), body)


def support_state() -> bytes:
    messages = read_json("support_messages.json", [])
    latest = messages[-1] if messages else {}
    open_count = sum(1 for item in messages if item.get("status") != "replied")
    payload = {
        "count": len(messages),
        "open_count": open_count,
        "latest_id": latest.get("id", ""),
        "latest_text": display_text(latest.get("text", "")),
        "latest_user": latest.get("username") or latest.get("user_id") or "",
    }
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def settings_page(message: str = "", error: str = ""):
    message_html = f"<p class='badge replied'>{esc(message)}</p>" if message else ""
    error_html = f"<p class='badge open'>{esc(error)}</p>" if error else ""
    env_fields = [
        ("CARD_HOLDER", admin_t("card_holder")),
        ("CARD_NUMBER", admin_t("card_number")),
        ("CARD_QR_IMAGE", admin_t("qr_image_file")),
        ("CARD_QR_LINK", admin_t("qr_link")),
        ("CARD_PAYMENT_NOTE", admin_t("payment_note")),
        ("CARD_PAYMENT_LINK", admin_t("card_payment_link")),
        ("PAYME_PAYMENT_LINK", admin_t("payme_link")),
        ("CLICK_PAYMENT_LINK", admin_t("click_link")),
        ("ADMIN_TELEGRAM_NOTIFICATIONS", "Telegram admin notify (0/1)"),
        ("ESIMGO_API_KEY", admin_t("esimgo_api_key")),
        ("ESIMGO_API_BASE", admin_t("esimgo_api_base")),
        ("ESIM_MARKUP_PERCENT", admin_t("esim_markup_percent")),
    ]
    settings_inputs = "\n".join(
        f"<p><label>{esc(label)}</label><br><input type='text' name='{esc(key)}' value='{esc(read_env(key))}'></p>"
        for key, label in env_fields
    )
    body = f"""
<h3>{esc(admin_t("settings"))}</h3>
<div class="card">
  <h4>{esc(admin_t("change_password"))}</h4>
  {message_html}
  {error_html}
  <form method="post" action="/settings">
    <p>
      <label>{esc(admin_t("old_password"))}</label><br>
      <input type="password" name="current_password" required>
    </p>
    <p>
      <label>{esc(admin_t("new_password"))}</label><br>
      <input type="password" name="new_password" minlength="8" required>
    </p>
    <p>
      <label>{esc(admin_t("repeat_password"))}</label><br>
      <input type="password" name="confirm_password" minlength="8" required>
    </p>
    <button>{esc(admin_t("change_password_btn"))}</button>
  </form>
  <p class="muted">{esc(admin_t('password_changed_hint'))}</p>
</div>
<div class="card">
  <h4>{esc(admin_t("bot_payment_settings"))}</h4>
  <form method="post" action="/settings-update">
    {settings_inputs}
    <button>{esc(admin_t("save"))}</button>
  </form>
  <p class="muted">{esc(admin_t('payment_settings_hint'))}</p>
</div>
"""
    return layout(admin_t("settings"), body)


def change_admin_password(current_password: str, new_password: str, confirm_password: str) -> tuple[bool, str]:
    configured = admin_password()
    if not configured or not hmac.compare_digest(current_password, configured):
        return False, admin_t("old_password_wrong")
    if len(new_password) < 8:
        return False, admin_t("new_password_short")
    if new_password != confirm_password:
        return False, admin_t("new_password_mismatch")
    write_env_values({
        "ADMIN_PANEL_PASSWORD": new_password,
        "ADMIN_PANEL_SECRET": secrets.token_urlsafe(32),
    })
    return True, admin_t("password_changed")


def update_bot_settings(params: dict) -> None:
    keys = [
        "CARD_HOLDER",
        "CARD_NUMBER",
        "CARD_QR_IMAGE",
        "CARD_QR_LINK",
        "CARD_PAYMENT_NOTE",
        "CARD_PAYMENT_LINK",
        "PAYME_PAYMENT_LINK",
        "CLICK_PAYMENT_LINK",
        "ADMIN_TELEGRAM_NOTIFICATIONS",
        "ESIMGO_API_KEY",
        "ESIMGO_API_BASE",
        "ESIM_MARKUP_PERCENT",
    ]
    write_env_values({key: params.get(key, [""])[0].strip() for key in keys})


def packages_page(message: str = "", error: str = ""):
    packages = read_packages()
    message_html = f"<p class='badge replied'>{esc(message)}</p>" if message else ""
    error_html = f"<p class='badge open'>{esc(error)}</p>" if error else ""
    rows = []
    for code, package in sorted(packages.items()):
        plans = package.get("plans", [])
        plan_text = "<br>".join(
            f"{esc(plan.get('data'))} / {esc(plan.get('days'))} / ${esc(plan.get('price_usd'))}"
            for plan in plans
        )
        rows.append(
            f"<tr><td>{esc(code)}</td><td>{esc(package.get('country'))}</td><td>{plan_text}</td>"
            f"<td><form method='post' action='/package-delete'><input type='hidden' name='code' value='{esc(code)}'><button class='danger'>{esc(admin_t('delete'))}</button></form></td></tr>"
        )
    body = f"""
<h3>{esc(admin_t("packages_title"))}</h3>
{message_html}
{error_html}
<div class="card">
  <h4>{esc(admin_t("add_update_country"))}</h4>
  <form method="post" action="/package-save">
    <p><label>{esc(admin_t("code"))}</label><br><input type="text" name="code" placeholder="masalan: uae" required></p>
    <p><label>{esc(admin_t("country_name"))}</label><br><input type="text" name="country" placeholder="United Arab Emirates / Dubai" required></p>
    <p class="muted">{esc(admin_t('package_hint'))}</p>
    <div class="cards">
      <div class="card"><b>{esc(admin_t('package_1'))}</b><p><input type="text" name="data_1" placeholder="1GB"></p><p><input type="text" name="days_1" placeholder="7 kun"></p><p><input type="number" step="0.01" name="price_1" placeholder="5"></p></div>
      <div class="card"><b>{esc(admin_t('package_2'))}</b><p><input type="text" name="data_2" placeholder="3GB"></p><p><input type="text" name="days_2" placeholder="15 kun"></p><p><input type="number" step="0.01" name="price_2" placeholder="11"></p></div>
      <div class="card"><b>{esc(admin_t('package_3'))}</b><p><input type="text" name="data_3" placeholder="5GB"></p><p><input type="text" name="days_3" placeholder="30 kun"></p><p><input type="number" step="0.01" name="price_3" placeholder="16"></p></div>
    </div>
    <button>{esc(admin_t("save"))}</button>
  </form>
</div>
<table><tr><th>{esc(admin_t("code"))}</th><th>{esc(admin_t("country_name"))}</th><th>{esc(admin_t("packages"))}</th><th>{esc(admin_t("action"))}</th></tr>{''.join(rows)}</table>
"""
    return layout(admin_t("packages"), body)


def save_package(params: dict) -> tuple[bool, str]:
    code = normalize_code(params.get("code", [""])[0])
    country = params.get("country", [""])[0].strip()
    if not code or not country:
        return False, admin_t("package_need_code")
    plans = []
    for index in range(1, 4):
        data = params.get(f"data_{index}", [""])[0].strip()
        days = params.get(f"days_{index}", [""])[0].strip()
        price = params.get(f"price_{index}", [""])[0].strip()
        if not data and not days and not price:
            continue
        if not data or not days or not price:
            return False, admin_t("package_incomplete")
        try:
            price_value = float(price)
        except ValueError:
            return False, admin_t("price_number")
        plans.append({"data": data, "days": days, "price_usd": price_value})
    if not plans:
        return False, admin_t("package_need_one")
    packages = read_packages()
    packages[code] = {"country": country, "plans": plans}
    write_packages(packages)
    return True, admin_t("package_saved")


def delete_package(code: str) -> None:
    packages = read_packages()
    packages.pop(code, None)
    write_packages(packages)


def export_page():
    body = """
<h3>{esc(admin_t("export"))} / Backup</h3>
<div class="cards">
  <div class="card"><h4>{esc(admin_t("orders"))}</h4><p><a href="/export-file?name=orders.json">orders.json {esc(admin_t("download"))}</a></p></div>
  <div class="card"><h4>{esc(admin_t("users"))}</h4><p><a href="/export-file?name=users.json">users.json {esc(admin_t("download"))}</a></p></div>
  <div class="card"><h4>{esc(admin_t("support"))}</h4><p><a href="/export-file?name=support_messages.json">support_messages.json {esc(admin_t("download"))}</a></p></div>
  <div class="card"><h4>{esc(admin_t("visa_reminders"))}</h4><p><a href="/export-file?name=reminders.json">reminders.json {esc(admin_t("download"))}</a></p></div>
  <div class="card"><h4>{esc(admin_t("packages"))}</h4><p><a href="/export-file?name=esim_packages.json">esim_packages.json {esc(admin_t("download"))}</a></p></div>
</div>
"""
    return layout(admin_t("export"), body)


def fetch_telegram_file(file_id: str):
    token = read_env("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN topilmadi")
    info_url = f"https://api.telegram.org/bot{token}/getFile?file_id={quote(file_id)}"
    with urlopen(info_url, timeout=10) as response:
        info = json.loads(response.read().decode("utf-8"))
    file_path = info.get("result", {}).get("file_path")
    if not file_path:
        raise RuntimeError("Telegram file_path topilmadi")
    file_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
    response = urlopen(file_url, timeout=20)
    return response


def update_order_status(order_id: str, status: str) -> None:
    orders = read_json("orders.json", [])
    for order in orders:
        if order.get("id") == order_id:
            order["status"] = status
    write_json("orders.json", orders)


def fulfill_order_from_panel(order_id: str) -> str:
    import bot

    bot.DATA_DIR = DATA_DIR
    bot.ORDERS_FILE = DATA_DIR / "orders.json"
    bot.USERS_FILE = DATA_DIR / "users.json"
    bot.REMINDERS_FILE = DATA_DIR / "reminders.json"
    bot.STATES_FILE = DATA_DIR / "states.json"
    bot.SUPPORT_FILE = DATA_DIR / "support_messages.json"
    bot.PACKAGES_FILE = DATA_DIR / "esim_packages.json"
    bot.ESIMGO_CATALOGUE_CACHE_FILE = DATA_DIR / "esimgo_catalogue_cache.json"

    order, message = bot.fulfill_order_with_esimgo(order_id)
    if not order:
        return message

    customer_lang = bot.get_user_lang(order.get("user_id"))
    send_plain_bot_message(
        str(order["user_id"]),
        bot.customer_esim_text(order, customer_lang),
        auto_translate=False,
    )
    return f"{message} Mijozga yuborildi: #{order['id']}"


def send_bot_message(user_id: str, text: str, auto_translate: bool = True) -> None:
    token = read_env("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN topilmadi")
    lang = user_lang(user_id)
    prefixes = {
        "uz": "Admin javobi",
        "ru": "Ответ администратора",
        "ru": "Ответ администратора",
        "en": "Admin reply",
    }
    outgoing_text = translate_text(text, lang) if auto_translate else text
    payload = json.dumps({
        "chat_id": int(user_id),
        "text": f"{prefixes.get(lang, prefixes['uz'])}:\n{outgoing_text}",
    }).encode("utf-8")
    request = Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        response.read()


def send_plain_bot_message(user_id: str, text: str, auto_translate: bool = True) -> None:
    token = read_env("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN topilmadi")
    lang = user_lang(user_id)
    outgoing_text = translate_text(text, lang) if auto_translate else text
    payload = json.dumps({
        "chat_id": int(user_id),
        "text": outgoing_text,
    }).encode("utf-8")
    request = Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        response.read()


def telegram_multipart(method: str, fields: dict[str, str], file_field: str, filename: str, content_type: str, file_bytes: bytes) -> None:
    token = read_env("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN topilmadi")
    boundary = f"----VisaEsimBoundary{secrets.token_hex(12)}"
    chunks: list[bytes] = []
    for key, value in fields.items():
        if value is None:
            continue
        chunks.append(f"--{boundary}\r\n".encode("utf-8"))
        chunks.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"))
        chunks.append(str(value).encode("utf-8"))
        chunks.append(b"\r\n")
    chunks.append(f"--{boundary}\r\n".encode("utf-8"))
    chunks.append(
        f'Content-Disposition: form-data; name="{file_field}"; filename="{filename or file_field}"\r\n'.encode("utf-8")
    )
    chunks.append(f"Content-Type: {content_type or 'application/octet-stream'}\r\n\r\n".encode("utf-8"))
    chunks.append(file_bytes)
    chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(chunks)
    request = Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "Content-Length": str(len(body))},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        response.read()


def multipart_param(value: str, key: str) -> str:
    for part in value.split(";"):
        part = part.strip()
        if not part.startswith(f"{key}="):
            continue
        raw = part.split("=", 1)[1].strip()
        if len(raw) >= 2 and raw[0] == raw[-1] == '"':
            raw = raw[1:-1]
        return raw
    return ""


def parse_multipart_form(content_type: str, body: bytes) -> tuple[dict[str, str], dict[str, dict]]:
    boundary = multipart_param(content_type, "boundary")
    fields: dict[str, str] = {}
    files: dict[str, dict] = {}
    if not boundary:
        return fields, files
    marker = b"--" + boundary.encode("utf-8")
    for raw_part in body.split(marker):
        part = raw_part.strip(b"\r\n")
        if not part or part == b"--":
            continue
        if part.endswith(b"--"):
            part = part[:-2].rstrip(b"\r\n")
        if b"\r\n\r\n" not in part:
            continue
        header_block, value = part.split(b"\r\n\r\n", 1)
        headers = {}
        for line in header_block.decode("utf-8", "ignore").split("\r\n"):
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            headers[key.strip().lower()] = val.strip()
        disposition = headers.get("content-disposition", "")
        name = multipart_param(disposition, "name")
        if not name:
            continue
        filename = multipart_param(disposition, "filename")
        if filename:
            files[name] = {
                "filename": Path(filename).name,
                "content_type": headers.get("content-type", "application/octet-stream"),
                "bytes": value,
            }
        else:
            fields[name] = value.decode("utf-8", "ignore")
    return fields, files


def send_bot_media(user_id: str, text: str, filename: str, content_type: str, file_bytes: bytes) -> None:
    lang = user_lang(user_id)
    caption = translate_text(text, lang) if text else ""
    lower_name = (filename or "").lower()
    is_video = content_type.startswith("video/") or lower_name.endswith((".mp4", ".mov", ".m4v", ".webm"))
    method = "sendVideo" if is_video else "sendPhoto"
    file_field = "video" if is_video else "photo"
    fields = {"chat_id": str(int(user_id))}
    if caption:
        fields["caption"] = caption[:1024]
    telegram_multipart(method, fields, file_field, filename, content_type, file_bytes)


def broadcast_page(message: str = "", error: str = ""):
    users = read_json("users.json", {})
    message_html = f"<p class='badge replied'>{esc(message)}</p>" if message else ""
    error_html = f"<p class='badge open'>{esc(error)}</p>" if error else ""
    total = len(users)
    body = f"""
<h3>{esc(admin_t('broadcast_title'))}</h3>
<div class="card">
  {message_html}
  {error_html}
  <p class="muted">{esc(admin_t('broadcast_hint'))}</p>
  <p class="muted">{esc(admin_t('users'))}: {total}</p>
  <form method="post" action="/broadcast" enctype="multipart/form-data">
    <p>
      <label>{esc(admin_t('target_lang'))}</label><br>
      <select name="target_lang">
        <option value="all">{esc(admin_t('all_users'))}</option>
        <option value="uz">UZ</option>
        <option value="ru">RU</option>
        <option value="en">EN</option>
      </select>
    </p>
    <p>
      <label>{esc(admin_t('broadcast_text'))}</label><br>
      <textarea name="text"></textarea>
    </p>
    <p>
      <label>{esc(admin_t('broadcast_media'))}</label><br>
      <input type="file" name="media" accept="image/*,video/*">
      <span class="muted">{esc(admin_t('broadcast_media_hint'))}</span>
    </p>
    <button>{esc(admin_t('send_broadcast'))}</button>
  </form>
</div>
"""
    return layout(admin_t("broadcast"), body)


def send_broadcast(text: str, target_lang: str = "all", media: dict | None = None) -> tuple[int, int]:
    users = read_json("users.json", {})
    sent = 0
    failed = 0
    for user_id, user in users.items():
        if target_lang != "all" and user.get("lang") != target_lang:
            continue
        try:
            if media and media.get("bytes"):
                send_bot_media(
                    str(user_id),
                    text,
                    media.get("filename", "media"),
                    media.get("content_type", "application/octet-stream"),
                    media["bytes"],
                )
            elif text:
                send_plain_bot_message(str(user_id), text, auto_translate=True)
            sent += 1
        except Exception:
            failed += 1
    return sent, failed


def mark_support_replied(support_id: str, answer: str) -> None:
    if not support_id:
        return
    messages = read_json("support_messages.json", [])
    for item in messages:
        if item.get("id") == support_id:
            item["status"] = "replied"
            item["answer"] = answer
            item["answered_at"] = datetime.now(timezone.utc).isoformat()
            break
    write_json("support_messages.json", messages)


class Handler(BaseHTTPRequestHandler):
    def current_session(self) -> str:
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            if "=" not in part:
                continue
            key, value = part.strip().split("=", 1)
            if key == SESSION_COOKIE:
                return value
        return ""

    def current_lang(self) -> str:
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            if "=" not in part:
                continue
            key, value = part.strip().split("=", 1)
            if key == LANG_COOKIE and value in ADMIN_TEXT:
                return value
        return "uz"

    def is_authenticated(self) -> bool:
        return valid_session(self.current_session())

    def redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def send_html(self, content: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        global CURRENT_ADMIN_LANG
        CURRENT_ADMIN_LANG = self.current_lang()
        path = urlparse(self.path).path
        if path == "/health":
            data = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if path == "/set-lang":
            query = parse_qs(urlparse(self.path).query)
            lang = query.get("lang", ["uz"])[0]
            if lang not in ADMIN_TEXT:
                lang = "uz"
            back = self.headers.get("Referer") or "/"
            self.send_response(303)
            self.send_header("Location", back)
            self.send_header("Set-Cookie", f"{LANG_COOKIE}={lang}; Max-Age=31536000; Path=/; SameSite=Lax")
            self.end_headers()
            return
        if path == "/login":
            self.send_html(login_page())
            return
        if path == "/logout":
            self.send_response(303)
            self.send_header("Location", "/login")
            self.send_header("Set-Cookie", f"{SESSION_COOKIE}=; Max-Age=0; Path=/; HttpOnly; SameSite=Lax")
            self.end_headers()
            return
        if not self.is_authenticated():
            self.redirect("/login")
            return

        if path == "/":
            content = dashboard()
        elif path == "/orders":
            content = orders_page()
        elif path == "/reminders":
            content = reminders_page()
        elif path == "/users":
            content = users_page()
        elif path == "/support":
            query = parse_qs(urlparse(self.path).query)
            content = support_page(query.get("id", [""])[0])
        elif path == "/broadcast":
            content = broadcast_page()
        elif path == "/settings":
            content = settings_page()
        elif path == "/packages":
            content = packages_page()
        elif path == "/export":
            content = export_page()
        elif path == "/export-file":
            query = parse_qs(urlparse(self.path).query)
            name = query.get("name", [""])[0]
            allowed = {"orders.json", "users.json", "support_messages.json", "reminders.json", "esim_packages.json"}
            if name not in allowed:
                self.send_response(400)
                self.end_headers()
                return
            path_obj = DATA_DIR / name
            data = path_obj.read_bytes() if path_obj.exists() else b"{}"
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Disposition", f"attachment; filename={name}")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        elif path == "/support-state":
            content = support_state()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        elif path == "/users-state":
            content = users_state()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        elif path == "/user":
            query = parse_qs(urlparse(self.path).query)
            content = user_detail_page(query.get("id", [""])[0])
        elif path == "/file":
            query = parse_qs(urlparse(self.path).query)
            file_id = query.get("file_id", [""])[0]
            if not file_id:
                self.send_response(400)
                self.end_headers()
                return
            try:
                response = fetch_telegram_file(file_id)
                data = response.read()
            except Exception as exc:
                self.send_response(502)
                self.end_headers()
                self.wfile.write(str(exc).encode("utf-8"))
                return
            self.send_response(200)
            self.send_header("Content-Type", response.headers.get("Content-Type", "application/octet-stream"))
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return
        self.send_html(content)

    def do_POST(self):
        global CURRENT_ADMIN_LANG
        CURRENT_ADMIN_LANG = self.current_lang()
        path = urlparse(self.path).path
        content_type = self.headers.get("Content-Type", "")
        is_multipart_broadcast = path == "/broadcast" and content_type.startswith("multipart/form-data")
        params = {}
        if not is_multipart_broadcast:
            length = int(self.headers.get("Content-Length", "0"))
            params = parse_qs(self.rfile.read(length).decode("utf-8"))
        if path == "/login":
            password = params.get("password", [""])[0]
            configured = admin_password()
            if configured and hmac.compare_digest(password, configured):
                expiry = int(time.time()) + SESSION_TTL_SECONDS
                token = sign_session(expiry)
                self.send_response(303)
                self.send_header("Location", "/")
                self.send_header("Set-Cookie", f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax")
                self.end_headers()
                return
            self.send_html(login_page(admin_t("wrong_password")))
            return

        if not self.is_authenticated():
            self.redirect("/login")
            return

        if path == "/order-status":
            update_order_status(params.get("id", [""])[0], params.get("status", [""])[0])
            self.send_response(303)
            back = params.get("back", ["/orders"])[0]
            if not back.startswith("/"):
                back = "/orders"
            self.send_header("Location", back)
            self.end_headers()
            return
        if path == "/order-fulfill":
            back = params.get("back", ["/orders"])[0]
            if not back.startswith("/"):
                back = "/orders"
            try:
                fulfill_order_from_panel(params.get("id", [""])[0])
            except Exception as exc:
                print(f"Panel fulfill xatosi: {exc}")
            self.send_response(303)
            self.send_header("Location", back)
            self.end_headers()
            return
        if path == "/send-message":
            user_id = params.get("user_id", [""])[0]
            text = params.get("text", [""])[0].strip()
            support_id = params.get("support_id", [""])[0]
            if user_id and text:
                send_bot_message(user_id, text)
                mark_support_replied(support_id, text)
            self.send_response(303)
            self.send_header("Location", f"/support?id={support_id}" if support_id else f"/user?id={user_id}")
            self.end_headers()
            return
        if path == "/broadcast":
            media = None
            if is_multipart_broadcast:
                length = int(self.headers.get("Content-Length", "0"))
                fields, files = parse_multipart_form(content_type, self.rfile.read(length))
                text = fields.get("text", "").strip()
                target_lang = fields.get("target_lang", "all") or "all"
                file_item = files.get("media")
                if file_item and file_item.get("bytes"):
                    media = file_item
            else:
                text = params.get("text", [""])[0].strip()
                target_lang = params.get("target_lang", ["all"])[0]
            if not text and not media:
                self.send_html(broadcast_page(error=admin_t("broadcast_content_required")))
                return
            sent, failed = send_broadcast(text, target_lang, media)
            self.send_html(broadcast_page(message=admin_t("broadcast_done").format(sent=sent, failed=failed)))
            return
        if path == "/settings":
            ok, message = change_admin_password(
                params.get("current_password", [""])[0],
                params.get("new_password", [""])[0],
                params.get("confirm_password", [""])[0],
            )
            if ok:
                self.send_response(303)
                self.send_header("Location", "/login")
                self.send_header("Set-Cookie", f"{SESSION_COOKIE}=; Max-Age=0; Path=/; HttpOnly; SameSite=Lax")
                self.end_headers()
                return
            self.send_html(settings_page(error=message))
            return
        if path == "/settings-update":
            update_bot_settings(params)
            self.send_html(settings_page(message=admin_t("settings_saved")))
            return
        if path == "/package-save":
            ok, message = save_package(params)
            self.send_html(packages_page(message=message if ok else "", error="" if ok else message))
            return
        if path == "/package-delete":
            delete_package(params.get("code", [""])[0])
            self.send_response(303)
            self.send_header("Location", "/packages")
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    HTTPServer((HOST, PORT), Handler).serve_forever()
