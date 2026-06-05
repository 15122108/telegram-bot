import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from datetime import timedelta
from pathlib import Path
import re


API_ROOT = "https://api.telegram.org/bot"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR") or os.environ.get("RAILWAY_VOLUME_MOUNT_PATH") or str(BASE_DIR))
DATA_DIR.mkdir(parents=True, exist_ok=True)
ORDERS_FILE = DATA_DIR / "orders.json"
USERS_FILE = DATA_DIR / "users.json"
REMINDERS_FILE = DATA_DIR / "reminders.json"
STATES_FILE = DATA_DIR / "states.json"
SUPPORT_FILE = DATA_DIR / "support_messages.json"
PACKAGES_FILE = DATA_DIR / "esim_packages.json"
ESIMGO_CATALOGUE_CACHE_FILE = DATA_DIR / "esimgo_catalogue_cache.json"
USERS_CACHE: dict | None = None
STATES_CACHE: dict | None = None
ESIMGO_CATALOGUE_CACHE: dict | None = None

DEFAULT_LANG = "uz"
SUPPORTED_LANGS = {"uz", "ru", "en"}

TEXT = {
    "uz": {
        "choose_lang": "Tilni tanlang:",
        "main": "Kerakli bo'limni menyudan tanlang.",
        "visa_free": "Vizasiz davlatlar",
        "visa_check": "Viza muddati",
        "esim": "eSIM paketlar",
        "help": "Yordam",
        "how": "Qanday ishlaydi",
        "support": "Support",
        "faq": "FAQ",
        "compat": "Telefon mosligi",
        "back_main": "Asosiy menyu",
        "back_countries": "Davlatlarga qaytish",
        "select_country": "Davlatni tanlang:",
        "select_esim_country": "eSIM uchun davlatni tanlang:",
        "select_plan": "Paketni tanlang:",
        "not_found": "Bu paket topilmadi. eSIM menyusidan paket tanlang.",
        "admin_only": "Bu komanda faqat admin uchun.",
        "order_format_done": "Format: /done VE-20260526-0001",
        "order_format_cancel": "Format: /cancel VE-20260526-0001",
    },
    "ru": {
        "choose_lang": "Выберите язык:",
        "main": "Выберите нужный раздел в меню.",
        "visa_free": "Безвизовые страны",
        "visa_check": "Срок визы",
        "esim": "Пакеты eSIM",
        "help": "Помощь",
        "how": "Как это работает",
        "support": "Поддержка",
        "faq": "FAQ",
        "compat": "Совместимость телефона",
        "back_main": "Главное меню",
        "back_countries": "Назад к странам",
        "select_country": "Выберите страну:",
        "select_esim_country": "Выберите страну для eSIM:",
        "select_plan": "Выберите пакет:",
        "not_found": "Пакет не найден. Выберите пакет через меню eSIM.",
        "admin_only": "Эта команда доступна только админу.",
        "order_format_done": "Формат: /done VE-20260526-0001",
        "order_format_cancel": "Формат: /cancel VE-20260526-0001",
    },
    "en": {
        "choose_lang": "Choose language:",
        "main": "Choose a section from the menu.",
        "visa_free": "Visa-free countries",
        "visa_check": "Visa expiry",
        "esim": "eSIM packages",
        "help": "Help",
        "how": "How it works",
        "support": "Support",
        "faq": "FAQ",
        "compat": "Phone compatibility",
        "back_main": "Main menu",
        "back_countries": "Back to countries",
        "select_country": "Choose a country:",
        "select_esim_country": "Choose an eSIM country:",
        "select_plan": "Choose a package:",
        "not_found": "Package not found. Choose a package from the eSIM menu.",
        "admin_only": "This command is admin only.",
        "order_format_done": "Format: /done VE-20260526-0001",
        "order_format_cancel": "Format: /cancel VE-20260526-0001",
    },
}

VISA_FREE_COUNTRIES = {
    "antigua": ("Antigua and Barbuda", "visa-free, 180 kun"),
    "armenia": ("Armenia", "visa-free, 180 kun"),
    "azerbaijan": ("Azerbaijan", "visa-free, 90 kun"),
    "barbados": ("Barbados", "visa-free, 28 kun"),
    "belarus": ("Belarus", "visa-free"),
    "china": ("China", "visa-free, 30 kun"),
    "dominica": ("Dominica", "visa-free, 21 kun"),
    "georgia": ("Georgia", "visa-free, 360 kun"),
    "grenada": ("Grenada", "visa-free"),
    "haiti": ("Haiti", "visa-free, 90 kun"),
    "iran": ("Iran", "visa-free, 15 kun"),
    "kazakhstan": ("Kazakhstan", "visa-free, 30 kun"),
    "kyrgyzstan": ("Kyrgyzstan", "visa-free, 60 kun"),
    "micronesia": ("Micronesia", "visa-free, 30 kun"),
    "moldova": ("Moldova", "visa-free, 90 kun"),
    "mongolia": ("Mongolia", "visa-free, 30 kun"),
    "oman": ("Oman", "visa-free, 14 kun"),
    "palestine": ("Palestinian Territories", "visa-free"),
    "philippines": ("Philippines", "visa-free, 30 kun"),
    "russia": ("Russian Federation", "visa-free, 90 kun"),
    "st vincent": ("St. Vincent and the Grenadines", "visa-free, 90 kun"),
    "tajikistan": ("Tajikistan", "visa-free, 30 kun"),
    "turkiye": ("Turkiye", "visa-free, 90 kun"),
    "turkey": ("Turkiye", "visa-free, 90 kun"),
    "ukraine": ("Ukraine", "visa-free"),
    "uae": ("United Arab Emirates", "visa-free, 30 kun"),
    "dubai": ("United Arab Emirates", "visa-free, 30 kun"),
}

VISA_ON_ARRIVAL_OR_EVISA = {
    "indonesia": ("Indonesia", "eVisa yoki visa on arrival, 30 kun"),
    "maldives": ("Maldives", "visa on arrival, 30 kun"),
    "qatar": ("Qatar", "visa on arrival, 30 kun"),
    "saudi": ("Saudi Arabia", "eVisa yoki visa on arrival, 90 kun"),
    "thailand": ("Thailand", "Arrival Card, 60 kun"),
    "malaysia": ("Malaysia", "Arrival Card, 30 kun"),
    "vietnam": ("Viet Nam", "eVisa, 90 kun"),
    "india": ("India", "eVisa, 30 kun"),
    "sri lanka": ("Sri Lanka", "eTA yoki visa on arrival, 30 kun"),
    "jordan": ("Jordan", "eVisa yoki visa on arrival, 30 kun"),
    "cambodia": ("Cambodia", "eVisa yoki visa on arrival, 30 kun"),
    "laos": ("Laos", "eVisa yoki visa on arrival, 30 kun"),
}

DEFAULT_ESIM_PACKAGES = {
    "uae": {
        "country": "United Arab Emirates / Dubai",
        "plans": [("1GB", "7 kun", 5), ("3GB", "15 kun", 11), ("5GB", "30 kun", 16)],
    },
    "turkiye": {
        "country": "Turkiye",
        "plans": [("1GB", "7 kun", 4), ("3GB", "15 kun", 9), ("5GB", "30 kun", 14)],
    },
    "kazakhstan": {
        "country": "Kazakhstan",
        "plans": [("1GB", "7 kun", 3), ("3GB", "15 kun", 8), ("5GB", "30 kun", 12)],
    },
    "china": {
        "country": "China",
        "plans": [("1GB", "7 kun", 6), ("3GB", "15 kun", 13), ("5GB", "30 kun", 19)],
    },
    "malaysia": {
        "country": "Malaysia",
        "plans": [("1GB", "7 kun", 4), ("3GB", "15 kun", 9), ("5GB", "30 kun", 13)],
    },
    "thailand": {
        "country": "Thailand",
        "plans": [("1GB", "7 kun", 4), ("3GB", "15 kun", 9), ("5GB", "30 kun", 13)],
    },
}


def esim_packages() -> dict:
    if esimgo_enabled():
        try:
            packages = esimgo_catalogue()
            if packages:
                return packages
        except Exception as exc:
            print(f"eSIM Go catalogue error: {exc}")
    packages = read_json_file(PACKAGES_FILE, None)
    if not isinstance(packages, dict) or not packages:
        return DEFAULT_ESIM_PACKAGES
    cleaned = {}
    for code, package in packages.items():
        if not isinstance(package, dict):
            continue
        country = str(package.get("country") or "").strip()
        plans = package.get("plans") or []
        valid_plans = []
        for plan in plans:
            if isinstance(plan, dict):
                data = str(plan.get("data") or "").strip()
                days = str(plan.get("days") or "").strip()
                price = plan.get("price_usd")
            else:
                try:
                    data, days, price = plan
                except (TypeError, ValueError):
                    continue
            if not data or not days:
                continue
            try:
                price = float(price)
            except (TypeError, ValueError):
                continue
            valid_plans.append((data, days, price))
        if country and valid_plans:
            cleaned[normalize_query(str(code))] = {"country": country, "plans": valid_plans}
    return cleaned or DEFAULT_ESIM_PACKAGES


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


def telegram_request(token: str, method: str, payload: dict | None = None) -> dict:
    data = None
    headers = {}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        f"{API_ROOT}{token}/{method}",
        data=data,
        headers=headers,
        method="POST" if payload is not None else "GET",
    )

    with urllib.request.urlopen(request, timeout=12) as response:
        body = response.read().decode("utf-8")
        result = json.loads(body)

    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result}")

    return result


def esimgo_api_key() -> str:
    load_env_file(Path(__file__).with_name(".env"))
    return os.environ.get("ESIMGO_API_KEY", "").strip()


def esimgo_api_base() -> str:
    load_env_file(Path(__file__).with_name(".env"))
    return os.environ.get("ESIMGO_API_BASE", "https://api.esim-go.com/v2.4").rstrip("/")


def esimgo_request(path: str, payload: dict | None = None, timeout: int = 25) -> dict:
    api_key = esimgo_api_key()
    if not api_key:
        raise RuntimeError("ESIMGO_API_KEY topilmadi")

    data = None
    headers = {
        "X-API-Key": api_key,
        "User-Agent": "visa-esim-uz-bot/1.0",
        "Accept": "application/json",
    }
    method = "GET"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
        method = "POST"

    request = urllib.request.Request(
        f"{esimgo_api_base()}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore")
        raise RuntimeError(f"eSIM Go API error {exc.code}: {detail or exc.reason}") from exc
    return json.loads(body) if body else {}


def mb_to_label(amount_mb: int | float | str) -> str:
    try:
        amount = float(amount_mb)
    except (TypeError, ValueError):
        return str(amount_mb)
    if amount < 0:
        return "Cheksiz"
    if amount >= 1024 and amount % 1024 == 0:
        return f"{int(amount / 1024)}GB"
    if amount >= 1024:
        return f"{amount / 1024:.1f}GB"
    return f"{int(amount)}MB"


def price_to_usd(price) -> float:
    try:
        value = float(price)
    except (TypeError, ValueError):
        return 0.0
    if value > 100:
        return round(value / 10000, 2)
    return round(value, 2)


def esim_markup_percent() -> float:
    load_env_file(Path(__file__).with_name(".env"))
    try:
        return max(0.0, float(os.environ.get("ESIM_MARKUP_PERCENT", "30")))
    except ValueError:
        return 30.0


def sale_price(cost_usd: float) -> float:
    return round(float(cost_usd) * (1 + esim_markup_percent() / 100), 2)


def esimgo_bundle_country(bundle: dict) -> tuple[str, str]:
    countries = bundle.get("countries") or bundle.get("roamingEnabled") or []
    if countries and isinstance(countries[0], dict):
        country = countries[0]
        code = normalize_query(country.get("iso") or country.get("name") or bundle.get("name") or "")
        name = str(country.get("name") or code).strip()
        return code, name
    name = str(bundle.get("description") or bundle.get("name") or "Global").strip()
    return normalize_query(name), name


def normalize_esimgo_catalogue(raw) -> dict:
    if isinstance(raw, dict):
        bundles = raw.get("bundles") or raw.get("data") or raw.get("items") or raw.get("results") or []
    else:
        bundles = raw
    packages: dict[str, dict] = {}
    for bundle in bundles:
        if not isinstance(bundle, dict):
            continue
        bundle_name = str(bundle.get("name") or bundle.get("bundleName") or "").strip()
        if not bundle_name:
            continue
        code, country_name = esimgo_bundle_country(bundle)
        data_label = mb_to_label(bundle.get("dataAmount") or bundle.get("data") or "")
        duration = bundle.get("duration") or bundle.get("days") or ""
        days_label = f"{duration} kun" if str(duration).isdigit() else str(duration)
        cost = price_to_usd(bundle.get("price") or bundle.get("priceUsd") or bundle.get("cost") or 0)
        if not code or not country_name or not data_label or not days_label:
            continue
        plan = {
            "data": data_label,
            "days": days_label,
            "cost_usd": cost,
            "price_usd": sale_price(cost),
            "bundle_name": bundle_name,
            "description": str(bundle.get("description") or "").strip(),
        }
        packages.setdefault(code, {"country": country_name, "plans": []})["plans"].append(plan)

    for package in packages.values():
        package["plans"].sort(key=lambda p: (p.get("price_usd", 0), p.get("data", "")))
        package["plans"] = package["plans"][:8]
    return dict(sorted(packages.items(), key=lambda item: item[1]["country"]))


def esimgo_catalogue(force_refresh: bool = False) -> dict:
    global ESIMGO_CATALOGUE_CACHE
    if ESIMGO_CATALOGUE_CACHE is not None and not force_refresh:
        return ESIMGO_CATALOGUE_CACHE
    cached = read_json_file(ESIMGO_CATALOGUE_CACHE_FILE, {})
    now = time.time()
    if not force_refresh and isinstance(cached, dict) and cached.get("packages"):
        if now - float(cached.get("updated_at", 0)) < 24 * 3600:
            ESIMGO_CATALOGUE_CACHE = cached["packages"]
            return ESIMGO_CATALOGUE_CACHE
    raw = esimgo_request("/catalogue?page=1&perPage=500&direction=asc&orderBy=description")
    packages = normalize_esimgo_catalogue(raw)
    if packages:
        write_json_file(
            ESIMGO_CATALOGUE_CACHE_FILE,
            {"updated_at": now, "packages": packages},
        )
        ESIMGO_CATALOGUE_CACHE = packages
        return packages
    return {}


def esimgo_enabled() -> bool:
    return bool(esimgo_api_key())


def esimgo_create_esim(bundle_name: str) -> dict:
    return esimgo_request(
        "/orders",
        {
            "type": "transaction",
            "assign": True,
            "order": [
                {
                    "type": "bundle",
                    "quantity": 1,
                    "item": bundle_name,
                    "allowReassign": False,
                }
            ],
        },
        timeout=40,
    )


def first_esim_from_order(response: dict) -> dict:
    for item in response.get("order", []) or []:
        esims = item.get("esims") or []
        if esims and isinstance(esims[0], dict):
            return esims[0]
    return {}


def plan_tuple(plan) -> tuple[str, str, float]:
    if isinstance(plan, dict):
        return (
            str(plan.get("data") or "").strip(),
            str(plan.get("days") or "").strip(),
            float(plan.get("price_usd") or 0),
        )
    data, days, price = plan
    return str(data), str(days), float(price)


def plan_cost(plan) -> float:
    if isinstance(plan, dict):
        return float(plan.get("cost_usd") or plan.get("price_usd") or 0)
    return float(plan[2])


def send_message(token: str, chat_id: int, text: str, reply_markup: dict | None = None) -> None:
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    telegram_request(
        token,
        "sendMessage",
        payload,
    )


def send_photo(token: str, chat_id: int, photo_path: Path, caption: str) -> None:
    boundary = f"----VisaEsimBot{int(time.time() * 1000)}"
    photo_bytes = photo_path.read_bytes()
    filename = photo_path.name
    fields = {
        "chat_id": str(chat_id),
        "caption": caption,
    }

    body = bytearray()
    for key, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"))
        body.extend(str(value).encode("utf-8"))
        body.extend(b"\r\n")

    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(
        f'Content-Disposition: form-data; name="photo"; filename="{filename}"\r\n'.encode("utf-8")
    )
    content_type = "image/png" if photo_path.suffix.lower() == ".png" else "image/jpeg"
    body.extend(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
    body.extend(photo_bytes)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    request = urllib.request.Request(
        f"{API_ROOT}{token}/sendPhoto",
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result}")


def answer_callback_query(token: str, callback_query_id: str) -> None:
    telegram_request(token, "answerCallbackQuery", {"callback_query_id": callback_query_id})


def t(lang: str, key: str) -> str:
    return TEXT.get(lang, TEXT[DEFAULT_LANG]).get(key, TEXT[DEFAULT_LANG][key])


def read_users() -> dict:
    global USERS_CACHE
    if USERS_CACHE is None:
        USERS_CACHE = read_json_file(USERS_FILE, {})
    return USERS_CACHE


def write_users(users: dict) -> None:
    global USERS_CACHE
    USERS_CACHE = users
    USERS_FILE.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json_file(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json_file(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def get_user_state(user_id: int | None) -> dict | None:
    if user_id is None:
        return None
    global STATES_CACHE
    if STATES_CACHE is None:
        STATES_CACHE = read_json_file(STATES_FILE, {})
    states = STATES_CACHE
    return states.get(str(user_id))


def set_user_state(user_id: int | None, state: dict | None) -> None:
    if user_id is None:
        return
    global STATES_CACHE
    if STATES_CACHE is None:
        STATES_CACHE = read_json_file(STATES_FILE, {})
    states = STATES_CACHE
    if state is None:
        states.pop(str(user_id), None)
    else:
        states[str(user_id)] = state
    STATES_CACHE = states
    write_json_file(STATES_FILE, states)


def get_user_lang(user_id: int | None) -> str:
    if user_id is None:
        return DEFAULT_LANG
    users = read_users()
    return users.get(str(user_id), {}).get("lang", DEFAULT_LANG)


def set_user_lang(user: dict, lang: str) -> None:
    if lang not in SUPPORTED_LANGS or user.get("id") is None:
        return
    users = read_users()
    current = users.get(str(user["id"]), {})
    users[str(user["id"])] = {
        "lang": lang,
        "username": user.get("username") or current.get("username"),
        "first_name": user.get("first_name") or current.get("first_name"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_users(users)


def remember_user(user: dict) -> None:
    user_id = user.get("id")
    if user_id is None:
        return
    users = read_users()
    current = users.get(str(user_id), {})
    lang = current.get("lang", DEFAULT_LANG)
    users[str(user_id)] = {
        "lang": lang if lang in SUPPORTED_LANGS else DEFAULT_LANG,
        "username": user.get("username") or current.get("username"),
        "first_name": user.get("first_name") or current.get("first_name"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_users(users)


def language_menu() -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "O'zbekcha", "callback_data": "lang:uz"},
                {"text": "Русский", "callback_data": "lang:ru"},
                {"text": "English", "callback_data": "lang:en"},
            ]
        ]
    }


def bottom_keyboard(lang: str = DEFAULT_LANG) -> dict:
    labels = {
        "uz": ["/start", "/esim", "/visa", "FAQ", "Support", "Til"],
        "ru": ["/start", "/esim", "/visa", "FAQ", "Support", "Язык"],
        "en": ["/start", "/esim", "/visa", "FAQ", "Support", "Language"],
    }[lang]
    return {
        "keyboard": [
            [{"text": labels[0]}],
            [{"text": labels[1]}, {"text": labels[2]}],
            [{"text": labels[3]}, {"text": labels[4]}],
            [{"text": labels[5]}],
        ],
        "resize_keyboard": True,
        "is_persistent": True,
    }


def menu_keyboard(lang: str = DEFAULT_LANG) -> dict:
    labels = {
        "uz": [
            "🌐 eSIM paketlar",
            "🛂 Viza muddati",
            "❓ FAQ",
            "📱 Telefon mosligi",
            "🧾 Qanday ishlaydi",
            "👨‍💻 Support",
            "🌍 Til",
        ],
        "ru": [
            "🌐 Пакеты eSIM",
            "🛂 Проверить визу",
            "❓ FAQ",
            "📱 Совместимость",
            "🧾 Как работает",
            "👨‍💻 Support",
            "🌍 Язык",
        ],
        "en": [
            "🌐 eSIM packages",
            "🛂 Visa expiry",
            "❓ FAQ",
            "📱 Compatibility",
            "🧾 How it works",
            "👨‍💻 Support",
            "🌍 Language",
        ],
    }[lang]
    return {
        "keyboard": [
            [{"text": labels[0]}, {"text": labels[1]}],
            [{"text": labels[2]}, {"text": labels[3]}],
            [{"text": labels[4]}, {"text": labels[5]}],
            [{"text": labels[6]}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
        "input_field_placeholder": "Menyu tanlang",
    }


def main_menu(lang: str = DEFAULT_LANG) -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": t(lang, "visa_free"), "callback_data": "menu:visa_free"},
                {"text": t(lang, "visa_check"), "callback_data": "menu:visa_check"},
            ],
            [
                {"text": t(lang, "esim"), "callback_data": "menu:esim"},
                {"text": t(lang, "help"), "callback_data": "menu:help"},
            ],
            [
                {"text": t(lang, "how"), "callback_data": "menu:how"},
                {"text": t(lang, "support"), "callback_data": "menu:support"},
            ],
            [
                {"text": t(lang, "faq"), "callback_data": "menu:faq"},
                {"text": t(lang, "compat"), "callback_data": "menu:compat"},
            ],
            [
                {"text": "Til / Язык / Language", "callback_data": "menu:lang"},
            ],
        ]
    }


def esim_country_menu(lang: str = DEFAULT_LANG) -> dict:
    buttons = [(package["country"][:45], f"esim:{code}") for code, package in list(esim_packages().items())[:80]]
    return inline_menu(buttons, back=True, lang=lang)


def esim_plan_menu(country_code: str, lang: str = DEFAULT_LANG) -> dict:
    package = esim_packages().get(country_code)
    if not package:
        return esim_country_menu(lang)

    buttons = []
    for index, plan in enumerate(package["plans"][:8]):
        data, days, price = plan_tuple(plan)
        buttons.append((f"{data} / {days} / ${price}", f"buy:{country_code}:p{index}"))
    buttons.append((t(lang, "back_countries"), "menu:esim"))
    buttons.append((t(lang, "back_main"), "menu:main"))
    return inline_menu(buttons)


def inline_menu(buttons: list[tuple[str, str]], back: bool = False, lang: str = DEFAULT_LANG) -> dict:
    rows = []
    for index in range(0, len(buttons), 2):
        rows.append(
            [
                {"text": text, "callback_data": data}
                for text, data in buttons[index : index + 2]
            ]
        )
    if back:
        rows.append([{"text": t(lang, "back_main"), "callback_data": "menu:main"}])
    return {"inline_keyboard": rows}


def normalize_query(value: str) -> str:
    return value.strip().lower().replace("o'z", "oz").replace("'", "")


def format_esim_list() -> str:
    lines = []
    for code, package in esim_packages().items():
        cheapest = min(plan_tuple(plan)[2] for plan in package["plans"])
        lines.append(f"- {package['country']}: ${cheapest} dan, /esim {code}")

    return "Mavjud eSIM yo'nalishlari:\n" + "\n".join(lines)


def format_esim_country(country_code: str) -> str:
    key = normalize_query(country_code)
    package = esim_packages().get(key)
    if not package:
        return format_esim_list()

    lines = "\n".join(
        f"- {plan_tuple(plan)[0]}, {plan_tuple(plan)[1]}: ${plan_tuple(plan)[2]} - menyudan tanlang"
        for plan in package["plans"]
    )
    return f"{package['country']} eSIM paketlari:\n{lines}"


def build_payment_text(country_code: str, data: str, lang: str = DEFAULT_LANG) -> str:
    load_env_file(Path(__file__).with_name(".env"))
    card_link = os.environ.get("CARD_PAYMENT_LINK", "").strip()
    payme_link = os.environ.get("PAYME_PAYMENT_LINK", "").strip()
    click_link = os.environ.get("CLICK_PAYMENT_LINK", "").strip()
    card_holder = os.environ.get("CARD_HOLDER", "").strip()
    card_number = os.environ.get("CARD_NUMBER", "").strip()
    card_qr_link = os.environ.get("CARD_QR_LINK", "").strip()
    card_note = os.environ.get("CARD_PAYMENT_NOTE", "").strip()
    package = esim_packages().get(country_code)

    if not package:
        return {
            "uz": "Bu davlat uchun eSIM paketi topilmadi. eSIM menyusini oching.",
            "ru": "Для этой страны пакет eSIM не найден. Откройте меню eSIM.",
            "en": "No eSIM package was found for this country. Open the eSIM menu.",
        }[lang]

    selected_plan = find_plan(package, data)

    if selected_plan is None:
        return format_esim_country(country_code)

    data, days, price = plan_tuple(selected_plan)
    if lang == "ru":
        payment_lines = [
            f"Заказ: {package['country']} eSIM {data}, {days}",
            f"Цена: ${price}",
            "",
            "Оплатите через QR/карту. QR будет отправлен ниже.",
        ]
    elif lang == "en":
        payment_lines = [
            f"Order: {package['country']} eSIM {data}, {days}",
            f"Price: ${price}",
            "",
            "Pay by QR/card. The QR image is sent below.",
        ]
    else:
        payment_lines = [
            f"Buyurtma: {package['country']} eSIM {data}, {days}",
            f"Narx: ${price}",
            "",
            "To'lovni QR/karta orqali qiling. QR rasm pastda yuboriladi.",
        ]

    extra_links = []
    if card_link:
        extra_links.append(f"Visa/Mastercard: {card_link}")
    if card_number:
        extra_links.append(f"Karta: {card_number}" + (f" ({card_holder})" if card_holder else ""))
    if card_qr_link:
        extra_links.append(f"QR: {card_qr_link}")
    elif os.environ.get("CARD_QR_IMAGE", "").strip():
        if lang == "ru":
            extra_links.append("QR: отправляется картинкой ниже")
        elif lang == "en":
            extra_links.append("QR: sent as an image below")
        else:
            extra_links.append("QR: pastda rasm ko'rinishida yuboriladi")
    if payme_link:
        extra_links.append(f"Payme: {payme_link}")
    if click_link:
        extra_links.append(f"Click: {click_link}")

    if extra_links:
        if lang == "ru":
            payment_lines.extend(["", "Другие способы оплаты:", *extra_links])
        elif lang == "en":
            payment_lines.extend(["", "Other payment methods:", *extra_links])
        else:
            payment_lines.extend(["", "Boshqa to'lov usullari:", *extra_links])
        if card_note:
            payment_lines.extend(["", card_note])

    payment_lines.extend(
        {
            "uz": [
                "",
                "To'lovdan keyin chek screenshotini shu chatga yuboring. Admin tasdiqlagach eSIM QR/kod beriladi.",
            ],
            "ru": [
                "",
                "После оплаты отправьте скриншот чека в этот чат. После подтверждения админ отправит QR/код eSIM.",
            ],
            "en": [
                "",
                "After payment, send the receipt screenshot to this chat. After admin confirmation, the eSIM QR/code will be sent.",
            ],
        }[lang]
    )
    return "\n".join(payment_lines)


def read_orders() -> list[dict]:
    if not ORDERS_FILE.exists():
        return []
    try:
        return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def write_orders(orders: list[dict]) -> None:
    ORDERS_FILE.write_text(json.dumps(orders, ensure_ascii=False, indent=2), encoding="utf-8")


def update_order_status(order_id: str, status: str) -> dict | None:
    orders = read_orders()
    normalized_id = order_id.strip().upper().lstrip("#")
    for order in orders:
        if order.get("id", "").upper() == normalized_id:
            order["status"] = status
            order["updated_at"] = datetime.now(timezone.utc).isoformat()
            write_orders(orders)
            return order
    return None


def find_order(order_id: str) -> dict | None:
    normalized_id = order_id.strip().upper().lstrip("#")
    for order in read_orders():
        if order.get("id", "").upper() == normalized_id:
            return order
    return None


def save_order(updated_order: dict) -> None:
    orders = read_orders()
    for index, order in enumerate(orders):
        if order.get("id") == updated_order.get("id"):
            orders[index] = updated_order
            write_orders(orders)
            return
    orders.append(updated_order)
    write_orders(orders)


def find_plan(package: dict, plan_key: str):
    plans = package.get("plans") or []
    if plan_key.startswith("p") and plan_key[1:].isdigit():
        index = int(plan_key[1:])
        if 0 <= index < len(plans):
            return plans[index]
    for plan in plans:
        data, _days, _price = plan_tuple(plan)
        if data.lower() == plan_key.lower():
            return plan
    return None


def customer_esim_text(order: dict, lang: str = DEFAULT_LANG) -> str:
    smdp = order.get("smdpAddress", "")
    matching = order.get("matchingId", "")
    iccid = order.get("iccid", "")
    lpa = f"LPA:1${smdp}${matching}" if smdp and matching else ""
    if lang == "ru":
        lines = [
            f"Ваш eSIM готов. Заказ #{order['id']}",
            f"Пакет: {order.get('country')} - {order.get('data')}, {order.get('days')}",
            "",
            "Данные для установки:",
        ]
    elif lang == "en":
        lines = [
            f"Your eSIM is ready. Order #{order['id']}",
            f"Plan: {order.get('country')} - {order.get('data')}, {order.get('days')}",
            "",
            "Installation details:",
        ]
    else:
        lines = [
            f"eSIM tayyor. Buyurtma #{order['id']}",
            f"Paket: {order.get('country')} - {order.get('data')}, {order.get('days')}",
            "",
            "O'rnatish ma'lumotlari:",
        ]
    if iccid:
        lines.append(f"ICCID: {iccid}")
    if smdp:
        lines.append(f"SMDP+: {smdp}")
    if matching:
        lines.append(f"Activation code: {matching}")
    if lpa:
        lines.extend(["", f"Manual install code:\n{lpa}"])
    return "\n".join(lines)


def fulfill_order_with_esimgo(order_id: str) -> tuple[dict | None, str]:
    order = find_order(order_id)
    if not order:
        return None, "Buyurtma topilmadi."
    if order.get("status") == "fulfilled" and order.get("matchingId"):
        return order, "Bu buyurtma avval fulfill qilingan."
    bundle_name = order.get("bundle_name")
    if not bundle_name:
        return None, "Bu order eSIM Go bundle bilan bog'lanmagan."
    response = esimgo_create_esim(bundle_name)
    esim = first_esim_from_order(response)
    if not esim:
        return None, f"eSIM Go javobida eSIM ma'lumoti topilmadi: {response}"
    order.update(
        {
            "status": "fulfilled",
            "fulfilled_at": datetime.now(timezone.utc).isoformat(),
            "provider_order_reference": response.get("orderReference", ""),
            "provider_status": response.get("status", ""),
            "iccid": esim.get("iccid", ""),
            "matchingId": esim.get("matchingId", ""),
            "smdpAddress": esim.get("smdpAddress", ""),
            "provider_response": response,
        }
    )
    save_order(order)
    return order, "eSIM yaratildi."


def create_order(user: dict, country_code: str, data: str) -> dict | None:
    package = esim_packages().get(country_code)
    if not package:
        return None

    selected_plan = find_plan(package, data)

    if selected_plan is None:
        return None

    orders = read_orders()
    order_id = f"VE-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{len(orders) + 1:04d}"
    plan_data, days, price = plan_tuple(selected_plan)
    cost = plan_cost(selected_plan)
    order = {
        "id": order_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending_payment",
        "user_id": user.get("id"),
        "username": user.get("username"),
        "first_name": user.get("first_name"),
        "country_code": country_code,
        "country": package["country"],
        "data": plan_data,
        "days": days,
        "price_usd": price,
        "cost_usd": cost,
        "profit_usd": round(price - cost, 2),
        "provider": "esimgo" if isinstance(selected_plan, dict) and selected_plan.get("bundle_name") else "manual",
        "bundle_name": selected_plan.get("bundle_name", "") if isinstance(selected_plan, dict) else "",
    }
    orders.append(order)
    write_orders(orders)
    return order


def format_order_for_admin(order: dict) -> str:
    username = order.get("username")
    user_ref = f"@{username}" if username else f"id:{order.get('user_id')}"
    provider_line = f"\nProvider: {order.get('provider') or 'manual'}"
    if order.get("bundle_name"):
        provider_line += f"\nBundle: {order['bundle_name']}"
    return (
        f"Yangi eSIM buyurtma #{order['id']}\n"
        f"Davlat: {order['country']}\n"
        f"Paket: {order['data']}, {order['days']}\n"
        f"Narx: ${order['price_usd']}\n"
        f"Tan narx: ${order.get('cost_usd', order.get('price_usd'))}\n"
        f"Foyda: ${order.get('profit_usd', 0)}\n"
        f"Status: {order['status']}\n"
        f"Mijoz: {user_ref}"
        f"{provider_line}\n"
        f"Tasdiqlash: /fulfill {order['id']} yoki /done {order['id']}"
    )


def notify_admin(token: str, order: dict) -> None:
    admin_chat_id = os.environ.get("ADMIN_CHAT_ID", "").strip()
    if not admin_chat_id:
        return

    send_message(token, int(admin_chat_id), format_order_for_admin(order))


def notify_admin_support(token: str, message: dict) -> None:
    admin_chat_id = os.environ.get("ADMIN_CHAT_ID", "").strip()
    if not admin_chat_id:
        return

    user = message.get("from", {})
    text = message.get("text", "")
    username = user.get("username")
    user_ref = f"@{username}" if username else f"id:{user.get('id')}"
    support_message = (
        "Support xabar:\n"
        f"Mijoz: {user_ref}\n"
        f"User ID: {user.get('id')}\n\n"
        f"{text}\n\n"
        f"Javob berish: /reply {user.get('id')} javob matni"
    )
    send_message(token, int(admin_chat_id), support_message)


def support_attachment(message: dict) -> dict:
    if message.get("photo"):
        photo = message["photo"][-1]
        return {
            "type": "photo",
            "file_id": photo.get("file_id"),
            "file_name": "photo.jpg",
        }
    if message.get("video"):
        video = message["video"]
        return {
            "type": "video",
            "file_id": video.get("file_id"),
            "file_name": video.get("file_name") or "video.mp4",
        }
    if message.get("document"):
        document = message["document"]
        return {
            "type": "document",
            "file_id": document.get("file_id"),
            "file_name": document.get("file_name") or "document",
        }
    if message.get("animation"):
        animation = message["animation"]
        return {
            "type": "animation",
            "file_id": animation.get("file_id"),
            "file_name": animation.get("file_name") or "animation.mp4",
        }
    return {}


def append_support_message(
    user: dict,
    text: str,
    message_id: int | None = None,
    attachment: dict | None = None,
) -> dict:
    messages = read_json_file(SUPPORT_FILE, [])
    item = {
        "id": f"SP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{len(messages) + 1:04d}",
        "status": "open",
        "user_id": user.get("id"),
        "username": user.get("username"),
        "first_name": user.get("first_name"),
        "text": text,
        "message_id": message_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "answered_at": "",
        "answer": "",
        "attachment": attachment or {},
    }
    messages.append(item)
    write_json_file(SUPPORT_FILE, messages)
    return item


def save_support_message(message: dict) -> dict:
    return append_support_message(
        message.get("from", {}),
        message.get("text") or message.get("caption") or "",
        message.get("message_id"),
        support_attachment(message),
    )


def build_order_response(
    token: str,
    user: dict,
    country_code: str,
    data: str,
    lang: str = DEFAULT_LANG,
) -> str:
    order = create_order(user, country_code, data)
    if order is None:
        return t(lang, "not_found")

    notify_admin(token, order)

    if lang == "ru":
        prefix = f"Заказ #{order['id']} создан.\n\n"
        suffix = "\n\nПри отправке чека также укажите номер заказа."
    elif lang == "en":
        prefix = f"Order #{order['id']} has been created.\n\n"
        suffix = "\n\nWhen sending the receipt, include the order number too."
    else:
        prefix = f"Buyurtma #{order['id']} yaratildi.\n\n"
        suffix = "\n\nChek yuborganingizda order raqamini ham yozing."
    return prefix + build_payment_text(country_code, data, lang) + suffix


def extract_order_id(text: str) -> str | None:
    marker = "#"
    if marker not in text:
        return None
    order_id = text.split(marker, 1)[1].split()[0].strip()
    if not order_id.startswith("VE-"):
        return None
    return order_id


def format_stats() -> str:
    orders = read_orders()
    total = len(orders)
    pending = sum(1 for order in orders if order.get("status") == "pending_payment")
    revenue = sum(float(order.get("price_usd", 0)) for order in orders)
    cost = sum(float(order.get("cost_usd", order.get("price_usd", 0)) or 0) for order in orders)
    profit = sum(float(order.get("profit_usd", 0) or 0) for order in orders)
    return (
        "Admin statistika:\n"
        f"Buyurtmalar: {total}\n"
        f"To'lov kutayotgan: {pending}\n"
        f"Jami order summasi: ${revenue:.2f}\n"
        f"Tan narx: ${cost:.2f}\n"
        f"Taxminiy foyda: ${profit:.2f}"
    )


def format_recent_orders(limit: int = 10) -> str:
    orders = read_orders()[-limit:]
    if not orders:
        return "Hali buyurtma yo'q."

    lines = []
    for order in reversed(orders):
        lines.append(
            f"#{order['id']} | {order['country']} | {order['data']} | ${order['price_usd']} | foyda ${order.get('profit_usd', 0)} | {order['status']}"
        )
    return "Oxirgi buyurtmalar:\n" + "\n".join(lines)


def read_reminders() -> list[dict]:
    return read_json_file(REMINDERS_FILE, [])


def write_reminders(reminders: list[dict]) -> None:
    write_json_file(REMINDERS_FILE, reminders)


def create_visa_expiry_reminder(user: dict, expiry_date_text: str) -> str:
    try:
        expiry_date = datetime.strptime(expiry_date_text.strip(), "%Y-%m-%d").date()
    except ValueError:
        return "Sana formati noto'g'ri. Masalan: 2026-06-15"

    today = datetime.now(timezone.utc).date()
    if expiry_date < today:
        return (
            "Bu sana allaqachon o'tib ketgan.\n"
            f"Bugungi sana: {today.isoformat()}\n"
            "Iltimos, kelajakdagi viza tugash sanasini kiriting. Masalan: 2026-06-15"
        )

    reminders = read_reminders()
    reminder_id = f"VM-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{len(reminders) + 1:04d}"
    reminders.append(
        {
            "id": reminder_id,
            "user_id": user.get("id"),
            "username": user.get("username"),
            "expiry_date": expiry_date.isoformat(),
            "sent": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    write_reminders(reminders)
    return (
        f"Viza muddati eslatmasi yaratildi: #{reminder_id}\n"
        f"Tugash sanasi: {expiry_date.isoformat()}\n\n"
        "Bot 7 kun, 3 kun, 1 kun qolganda va tugash kuni ogohlantiradi."
    )


def format_user_reminders(user_id: int | None) -> str:
    reminders = [r for r in read_reminders() if r.get("user_id") == user_id]
    if not reminders:
        return "Sizda aktiv viza muddati eslatmalari yo'q."

    lines = []
    for reminder in reminders[-10:]:
        lines.append(
            f"#{reminder['id']} | tugash: {reminder['expiry_date']}"
        )
    return "Viza muddati eslatmalaringiz:\n" + "\n".join(lines)


def process_polis_reminders(token: str) -> None:
    reminders = read_reminders()
    if not reminders:
        return

    today = datetime.now(timezone.utc).date()
    changed = False
    for reminder in reminders:
        expiry_date = datetime.strptime(reminder["expiry_date"], "%Y-%m-%d").date()
        days_left = (expiry_date - today).days
        if days_left not in {7, 3, 1, 0}:
            continue

        marker = str(days_left)
        if marker in reminder.get("sent", []):
            continue

        if days_left == 0:
            text = (
                f"Viza muddati ogohlantirish #{reminder['id']}\n"
                "Vizangiz muddati BUGUN tugaydi.\n"
                "Iltimos, mamlakatdan chiqish yoki muddatni uzaytirish masalasini tekshiring."
            )
        else:
            text = (
                f"Viza muddati ogohlantirish #{reminder['id']}\n"
                f"Vizangiz muddati tugashiga {days_left} kun qoldi.\n"
                f"Tugash sanasi: {reminder['expiry_date']}"
            )
        send_message(token, int(reminder["user_id"]), text)
        reminder.setdefault("sent", []).append(marker)
        changed = True

    if changed:
        write_reminders(reminders)


def is_admin_chat(chat_id: int | None) -> bool:
    admin_chat_id = os.environ.get("ADMIN_CHAT_ID", "").strip()
    return bool(admin_chat_id and chat_id is not None and str(chat_id) == admin_chat_id)


def help_text(lang: str = DEFAULT_LANG) -> str:
    if lang == "ru":
        return (
            "Выберите раздел в меню:\n"
            "- Безвизовые страны: направления для паспорта Узбекистана\n"
            "- Проверить визу: популярные страны\n"
            "- Пакеты eSIM: выбор страны и интернет-пакета\n\n"
            "После заказа отправьте чек оплаты в этот чат."
        )
    if lang == "en":
        return (
            "Choose a section from the menu:\n"
            "- Visa-free countries: destinations for Uzbekistan passport holders\n"
            "- Visa expiry: get reminders before your visa expires\n"
            "- eSIM packages: choose country and data package\n\n"
            "After ordering, send the payment receipt to this chat."
        )
    return (
        "Menyudan tanlang:\n"
        "- Vizasiz davlatlar: O'zbekiston pasporti uchun vizasiz yo'nalishlar\n"
        "- Viza muddati: viza tugash sanasi bo'yicha eslatma\n"
        "- eSIM paketlar: davlat va internet paket tanlash\n\n"
        "Buyurtma qilgandan keyin to'lov chekini shu chatga yuboring."
    )


def admin_help_text() -> str:
    return (
        "Admin komandalar:\n"
        "/stats - statistika\n"
        "/orders - oxirgi buyurtmalar\n"
        "/refresh_esim - eSIM Go katalogni yangilash\n"
        "/fulfill ORDER_ID - eSIM Go orqali real eSIM yaratish va mijozga yuborish\n"
        "/done ORDER_ID - buyurtmani bajarildi qilish\n"
        "/cancel ORDER_ID - buyurtmani bekor qilish\n"
        "/reply USER_ID matn - mijozga javob yozish"
    )


def how_it_works_text(lang: str = DEFAULT_LANG) -> str:
    if lang == "ru":
        return (
            "Как это работает:\n"
            "1. Вы выбираете страну.\n"
            "2. Вы выбираете пакет eSIM.\n"
            "3. Оплачиваете через QR/карту.\n"
            "4. Отправляете чек в этот чат.\n"
            "5. После подтверждения админ отправляет QR/код eSIM.\n\n"
            "После подтверждения оплаты QR/код eSIM будет отправлен."
        )
    if lang == "en":
        return (
            "How it works:\n"
            "1. Choose a country.\n"
            "2. Choose an eSIM data package.\n"
            "3. Pay by QR/card.\n"
            "4. Send the receipt to this chat.\n"
            "5. After admin confirmation, the eSIM QR/code is sent.\n\n"
            "After payment is confirmed, the eSIM QR/code will be sent."
        )
    return (
        "Qanday ishlaydi:\n"
        "1. Davlatni tanlaysiz.\n"
        "2. eSIM internet paketini tanlaysiz.\n"
        "3. QR/karta orqali to'lov qilasiz.\n"
        "4. Chekni shu chatga yuborasiz.\n"
        "5. Admin tasdiqlagach eSIM QR/kod yuboriladi.\n\n"
        "To'lov tasdiqlangandan keyin eSIM QR/kod yuboriladi."
    )


def support_text(lang: str = DEFAULT_LANG) -> str:
    load_env_file(Path(__file__).with_name(".env"))
    if lang == "ru":
        return (
            "Поддержка:\n"
            "Напишите вопрос в этот чат. Админ получит сообщение и ответит здесь."
        )
    if lang == "en":
        return (
            "Support:\n"
            "Write your question in this chat. Admin will receive it and reply here."
        )
    return (
        "Support:\n"
        "Savolingizni shu chatga yozing. Xabaringiz adminga boradi va admin shu yerda javob beradi."
    )


def set_support_state(user: dict) -> None:
    user_id = user.get("id")
    set_user_state(
        user_id,
        {
            "type": "awaiting_support_message",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    append_support_message(
        user,
        "Support bo'limi ochildi. Mijoz savol yozishini kuting.",
        None,
    )


def payment_methods_text(lang: str = DEFAULT_LANG) -> str:
    load_env_file(Path(__file__).with_name(".env"))
    card_link = os.environ.get("CARD_PAYMENT_LINK", "").strip()
    payme_link = os.environ.get("PAYME_PAYMENT_LINK", "").strip()
    click_link = os.environ.get("CLICK_PAYMENT_LINK", "").strip()
    card_holder = os.environ.get("CARD_HOLDER", "").strip()
    card_number = os.environ.get("CARD_NUMBER", "").strip()
    card_qr_link = os.environ.get("CARD_QR_LINK", "").strip()
    card_qr_image = os.environ.get("CARD_QR_IMAGE", "").strip()
    card_note = os.environ.get("CARD_PAYMENT_NOTE", "").strip()

    lines = []
    if lang == "ru":
        lines.append("Доступные способы оплаты:")
        lines.extend([
            f"- Visa/Mastercard: {card_link or 'будет добавлено после подключения merchant'}",
            f"- Card transfer: {card_number or 'add your card number'}" + (f" ({card_holder})" if card_holder else ""),
            f"- QR payment: {card_qr_link or card_qr_image or 'add your bank QR link/image'}",
            f"- Payme: {payme_link or 'будет добавлено после подключения merchant'}",
            f"- Click: {click_link or 'будет добавлено после подключения merchant'}",
            "",
            "Не отправляйте данные карты в чат. Оплата картой должна проходить только через защищенную платежную страницу.",
        ])
        if card_note:
            lines.append(card_note)
    elif lang == "en":
        lines.append("Available payment methods:")
        lines.extend([
            f"- Visa/Mastercard: {card_link or 'will be added after merchant setup'}",
            f"- Card transfer: {card_number or 'add your card number'}" + (f" ({card_holder})" if card_holder else ""),
            f"- QR payment: {card_qr_link or card_qr_image or 'add your bank QR link/image'}",
            f"- Payme: {payme_link or 'will be added after merchant setup'}",
            f"- Click: {click_link or 'will be added after merchant setup'}",
            "",
            "Do not send card details in chat. Card payments must go through a secure payment page.",
        ])
        if card_note:
            lines.append(card_note)
    else:
        lines.append("Mavjud to'lov usullari:")
        lines.extend([
            f"- Visa/Mastercard: {card_link or 'merchant ulangandan keyin qo`shiladi'}",
            f"- Karta transfer: {card_number or 'karta raqamingiz qo`shiladi'}" + (f" ({card_holder})" if card_holder else ""),
            f"- QR to'lov: {card_qr_link or card_qr_image or 'bank QR link/rasm qo`shiladi'}",
            f"- Payme: {payme_link or 'merchant ulangandan keyin qo`shiladi'}",
            f"- Click: {click_link or 'merchant ulangandan keyin qo`shiladi'}",
            "",
            "CVV/karta paroli kabi maxfiy ma'lumotlarni chatga yubormang. Merchant bo'lmasa karta to'lovi P2P transfer sifatida manual tekshiriladi.",
        ])
        if card_note:
            lines.append(card_note)
    return "\n".join(lines)


def faq_text(lang: str = DEFAULT_LANG) -> str:
    if lang == "ru":
        return (
            "FAQ:\n\n"
            "Что такое eSIM?\n"
            "eSIM - цифровая SIM, которая устанавливается по QR/коду.\n\n"
            "Когда она работает?\n"
            "В выбранной стране как мобильный интернет.\n\n"
            "Есть звонки/SMS?\n"
            "Большинство eSIM пакетов только для интернета.\n\n"
            "Как установить?\n"
            "Settings -> Mobile/Cellular -> Add eSIM, затем сканируйте QR.\n\n"
            "Что после оплаты?\n"
            "Чек проверяется, затем отправляется QR/код eSIM."
        )
    if lang == "en":
        return (
            "FAQ:\n\n"
            "What is eSIM?\n"
            "eSIM is a digital SIM installed by QR/code.\n\n"
            "When does it work?\n"
            "It works as mobile internet in the selected country.\n\n"
            "Calls/SMS included?\n"
            "Most travel eSIM packages are data-only.\n\n"
            "How to install?\n"
            "Settings -> Mobile/Cellular -> Add eSIM, then scan the QR.\n\n"
            "What happens after payment?\n"
            "The receipt is checked, then the admin creates a real eSIM through eSIM Go and the bot sends the install details."
        )
    return (
        "FAQ:\n\n"
        "eSIM nima?\n"
        "eSIM - telefonga QR/kod orqali o'rnatiladigan raqamli SIM.\n\n"
        "Qachon ishlaydi?\n"
        "Ko'rsatilgan davlatga borganda mobil internet sifatida ishlaydi.\n\n"
        "Qo'ng'iroq/SMS bormi?\n"
        "Ko'p eSIM paketlar faqat internet uchun bo'ladi.\n\n"
        "Qanday o'rnatiladi?\n"
        "Telefon sozlamalarida Add eSIM / Add Mobile Plan bo'limidan QR code skaner qilinadi.\n\n"
        "To'lovdan keyin nima bo'ladi?\n"
        "Chek tekshiriladi, admin eSIM Go orqali real eSIM yaratadi va bot o'rnatish ma'lumotlarini yuboradi."
    )


def compatibility_text(lang: str = DEFAULT_LANG) -> str:
    if lang == "ru":
        return (
            "Телефон поддерживает eSIM?\n\n"
            "iPhone: iPhone XS, XR и новее обычно поддерживают eSIM.\n\n"
            "Samsung: многие Galaxy S20/S21/S22/S23/S24, Z Fold, Z Flip поддерживают eSIM.\n\n"
            "Google Pixel: многие модели Pixel 3 и новее поддерживают eSIM.\n\n"
            "Проверка: если есть Settings -> Mobile/Cellular -> Add eSIM, телефон может быть совместим.\n\n"
            "Важно: в некоторых версиях для стран/операторов eSIM может быть заблокирована."
        )
    if lang == "en":
        return (
            "Does your phone support eSIM?\n\n"
            "iPhone: iPhone XS, XR and newer usually support eSIM.\n\n"
            "Samsung: many Galaxy S20/S21/S22/S23/S24, Z Fold, Z Flip models support eSIM.\n\n"
            "Google Pixel: many Pixel 3 and newer models support eSIM.\n\n"
            "Check: if Settings -> Mobile/Cellular -> Add eSIM exists, the phone may be compatible.\n\n"
            "Note: some country/operator versions may have eSIM disabled."
        )
    return (
        "Telefon eSIM qo'llaydimi?\n\n"
        "iPhone:\n"
        "iPhone XS, XR va undan yangi modellar odatda eSIM qo'llaydi.\n\n"
        "Samsung:\n"
        "Galaxy S20/S21/S22/S23/S24, Z Fold, Z Flip seriyalarida ko'p modellar qo'llaydi.\n\n"
        "Google Pixel:\n"
        "Pixel 3 va undan yangi ko'p modellar qo'llaydi.\n\n"
        "Tekshirish:\n"
        "Telefoningizda Settings -> Mobile/Cellular -> Add eSIM bo'lsa, mos bo'lishi mumkin.\n\n"
        "Eslatma: ayrim mamlakat/operator versiyalarida eSIM bloklangan bo'lishi mumkin."
    )


def start_text(first_name: str, lang: str = DEFAULT_LANG) -> str:
    greeting = {"uz": "Assalomu alaykum", "ru": "Здравствуйте", "en": "Hello"}[lang]
    return f"{greeting}, {first_name}!\n\n{t(lang, 'main')}"


def build_reply(token: str, message: dict) -> tuple[str, dict | None]:
    text = (message.get("text") or message.get("caption") or "").strip()
    user = message.get("from", {})
    first_name = user.get("first_name", "do'stim")
    lang = get_user_lang(user.get("id"))
    text_key = text.casefold()
    state = get_user_state(user.get("id"))

    if state and state.get("type") == "awaiting_support_message" and not text.startswith("/"):
        set_user_state(user.get("id"), None)
        save_support_message(message)
        return (
            "Xabaringiz adminga yuborildi. Tez orada shu chatda javob olasiz.",
            main_menu(lang),
        )

    if state and state.get("type") == "awaiting_visa_expiry_date":
        set_user_state(user.get("id"), None)
        return create_visa_expiry_reminder(user, text), menu_keyboard(lang)

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return create_visa_expiry_reminder(user, text), menu_keyboard(lang)

    if text.startswith("/start") or text_key == "start":
        return start_text(first_name, lang), menu_keyboard(lang)

    if text.startswith("/help") or text_key in {"yordam", "help", "помощь"}:
        help_body = help_text(lang)
        if is_admin_chat(message.get("chat", {}).get("id")):
            help_body += "\n\n" + admin_help_text()
        return help_body, main_menu(lang)

    if text.startswith("/lang") or "til" in text_key or "язык" in text_key or "language" in text_key:
        return t(lang, "choose_lang"), language_menu()

    if text.startswith("/how") or "qanday" in text_key or "как" in text_key or "how" in text_key:
        return how_it_works_text(lang), main_menu(lang)

    if text.startswith("/faq") or "faq" in text_key:
        return faq_text(lang), main_menu(lang)

    if text.startswith("/support") or "support" in text_key or "поддерж" in text_key:
        set_support_state(user)
        return support_text(lang), main_menu(lang)

    if text.startswith("/compat") or "telefon" in text_key or "совмест" in text_key or "compat" in text_key:
        return compatibility_text(lang), main_menu(lang)

    if "esim" in text_key:
        return t(lang, "select_esim_country"), esim_country_menu(lang)

    if "viza" in text_key or "visa" in text_key or "виз" in text_key:
        set_user_state(
            user.get("id"),
            {
                "type": "awaiting_visa_expiry_date",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return (
            "Vizangiz tugash sanasini kiriting.\n"
            "Format: YYYY-MM-DD\n"
            "Masalan: 2026-06-15",
            None,
        )

    if text.startswith("/visa_list"):
        return (
            "Viza muddati eslatmasi uchun /visa ni bosing va tugash sanasini kiriting.",
            menu_keyboard(lang),
        )

    if text.startswith("/visa"):
        set_user_state(
            user.get("id"),
            {
                "type": "awaiting_visa_expiry_date",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return (
            "Vizangiz tugash sanasini kiriting.\n"
            "Format: YYYY-MM-DD\n"
            "Masalan: 2026-06-15",
            None,
        )

    if text.startswith("/esim"):
        country_code = normalize_query(text.removeprefix("/esim"))
        if country_code:
            return format_esim_country(country_code), esim_plan_menu(country_code, lang)
        return t(lang, "select_esim_country"), esim_country_menu(lang)

    if text.startswith("/buy"):
        parts = text.split()
        if len(parts) < 3:
            return "Buyurtma uchun menyudan paket tanlang.", esim_country_menu()
        order_text = build_order_response(
            token,
            user,
            normalize_query(parts[1]),
            parts[2],
            lang,
        )
        return order_text, main_menu(lang)

    if text.startswith("/stats"):
        if not is_admin_chat(message.get("chat", {}).get("id")):
            return t(lang, "admin_only"), main_menu(lang)
        return format_stats(), main_menu(lang)

    if text.startswith("/orders"):
        if not is_admin_chat(message.get("chat", {}).get("id")):
            return t(lang, "admin_only"), main_menu(lang)
        return format_recent_orders(), main_menu(lang)

    if text.startswith("/refresh_esim"):
        if not is_admin_chat(message.get("chat", {}).get("id")):
            return t(lang, "admin_only"), main_menu(lang)
        try:
            packages = esimgo_catalogue(force_refresh=True)
        except Exception as exc:
            return f"eSIM Go katalog yangilanmadi: {exc}", main_menu(lang)
        return f"eSIM Go katalog yangilandi. Davlatlar: {len(packages)}", main_menu(lang)

    if text.startswith("/fulfill"):
        if not is_admin_chat(message.get("chat", {}).get("id")):
            return t(lang, "admin_only"), main_menu(lang)
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            return "Format: /fulfill VE-20260526-0001", main_menu(lang)
        try:
            order, message_text = fulfill_order_with_esimgo(parts[1])
        except Exception as exc:
            return f"eSIM yaratilmadi: {exc}", main_menu(lang)
        if not order:
            return message_text, main_menu(lang)
        try:
            customer_lang = get_user_lang(order.get("user_id"))
            send_message(token, int(order["user_id"]), customer_esim_text(order, customer_lang))
        except Exception as exc:
            return f"{message_text}\nLekin mijozga yuborilmadi: {exc}", main_menu(lang)
        return f"{message_text}\nMijozga yuborildi: #{order['id']}", main_menu(lang)

    if text.startswith("/done"):
        if not is_admin_chat(message.get("chat", {}).get("id")):
            return t(lang, "admin_only"), main_menu(lang)
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            return t(lang, "order_format_done"), main_menu(lang)
        order = update_order_status(parts[1], "completed")
        if not order:
            return "Buyurtma topilmadi.", main_menu(lang)
        return f"Buyurtma #{order['id']} completed qilindi.", main_menu(lang)

    if text.startswith("/cancel"):
        if not is_admin_chat(message.get("chat", {}).get("id")):
            return t(lang, "admin_only"), main_menu(lang)
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            return t(lang, "order_format_cancel"), main_menu(lang)
        order = update_order_status(parts[1], "cancelled")
        if not order:
            return "Buyurtma topilmadi.", main_menu(lang)
        return f"Buyurtma #{order['id']} cancelled qilindi.", main_menu(lang)

    if text.startswith("/reply"):
        if not is_admin_chat(message.get("chat", {}).get("id")):
            return t(lang, "admin_only"), main_menu(lang)
        parts = text.split(maxsplit=2)
        if len(parts) < 3:
            return "Format: /reply USER_ID javob matni", main_menu(lang)
        target_user_id = parts[1]
        reply_message = parts[2]
        try:
            send_message(token, int(target_user_id), f"Admin javobi:\n{reply_message}")
        except Exception as exc:
            return f"Javob yuborilmadi: {exc}", main_menu(lang)
        return f"Javob yuborildi: {target_user_id}", main_menu(lang)

    if text.startswith("/id"):
        chat = message.get("chat", {})
        user = message.get("from", {})
        return f"Chat ID: {chat.get('id')}\nUser ID: {user.get('id')}", main_menu(lang)

    if text.startswith("/echo"):
        message = text.removeprefix("/echo").strip()
        return message or "Qaytarish uchun matn yozing: /echo Salom", main_menu(lang)

    if not is_admin_chat(message.get("chat", {}).get("id")):
        save_support_message(message)
        return (
            "Xabaringiz adminga yuborildi. Tez orada shu chatda javob olasiz.",
            main_menu(lang),
        )

    return t(lang, "main"), main_menu(lang)


def build_callback_reply(token: str, callback_query: dict) -> tuple[str, dict | None]:
    data = callback_query.get("data", "")
    message = callback_query.get("message", {})
    user = callback_query.get("from", {})
    lang = get_user_lang(user.get("id"))

    if data.startswith("lang:"):
        selected_lang = data.split(":", 1)[1]
        set_user_lang(user, selected_lang)
        first_name = user.get("first_name", "do'stim")
        return start_text(first_name, selected_lang), menu_keyboard(selected_lang)

    if data == "menu:main":
        first_name = user.get("first_name", "do'stim")
        return start_text(first_name, lang), main_menu(lang)

    if data == "menu:lang":
        return t(lang, "choose_lang"), language_menu()

    if data == "menu:help":
        return help_text(lang), main_menu(lang)

    if data == "menu:how":
        return how_it_works_text(lang), main_menu(lang)

    if data == "menu:support":
        set_support_state(user)
        return support_text(lang), main_menu(lang)

    if data == "menu:faq":
        return faq_text(lang), main_menu(lang)

    if data == "menu:compat":
        return compatibility_text(lang), main_menu(lang)

    if data == "menu:visa_free":
        return (
            "Viza muddati eslatmasi uchun tugash sanasini kiritish kerak. /visa ni bosing.",
            menu_keyboard(lang),
        )

    if data == "menu:visa_check":
        set_user_state(
            user.get("id"),
            {
                "type": "awaiting_visa_expiry_date",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return (
            "Vizangiz tugash sanasini kiriting.\n"
            "Format: YYYY-MM-DD\n"
            "Masalan: 2026-06-15",
            None,
        )

    if data.startswith("visa:"):
        return (
            "Viza muddati eslatmasi uchun tugash sanasini kiritish kerak. /visa ni bosing.",
            menu_keyboard(lang),
        )

    if data == "menu:esim":
        return t(lang, "select_esim_country"), esim_country_menu(lang)

    if data.startswith("esim:"):
        country = data.split(":", 1)[1]
        package = esim_packages().get(country)
        if not package:
            return t(lang, "not_found"), esim_country_menu(lang)
        lines = "\n".join(
            f"- {plan_tuple(plan)[0]}, {plan_tuple(plan)[1]}: ${plan_tuple(plan)[2]}"
            for plan in package["plans"]
        )
        return (
            f"{package['country']} eSIM paketlari:\n{lines}\n\n{t(lang, 'select_plan')}",
            esim_plan_menu(country, lang),
        )

    if data.startswith("buy:"):
        _, country, plan_data = data.split(":", 2)
        order_text = build_order_response(
            token,
            user,
            country,
            plan_data,
            lang,
        )
        return order_text, main_menu(lang)

    return t(lang, "main"), main_menu(lang)


def maybe_send_payment_qr(token: str, chat_id: int, order_id: str, lang: str) -> None:
    load_env_file(Path(__file__).with_name(".env"))
    qr_image = os.environ.get("CARD_QR_IMAGE", "").strip()
    if not qr_image:
        return

    qr_path = DATA_DIR / qr_image
    if not qr_path.exists():
        qr_path = BASE_DIR / qr_image
    if not qr_path.exists():
        return

    captions = {
        "uz": f"Order #{order_id} uchun QR orqali to'lov. To'lovdan keyin chek screenshotini shu chatga yuboring.",
        "ru": f"QR для оплаты заказа #{order_id}. После оплаты отправьте скриншот чека в этот чат.",
        "en": f"QR payment for order #{order_id}. After payment, send the receipt screenshot to this chat.",
    }
    send_photo(token, chat_id, qr_path, captions.get(lang, captions[DEFAULT_LANG]))


def handle_update(token: str, update: dict) -> None:
    callback_query = update.get("callback_query")
    if callback_query:
        answer_callback_query(token, callback_query["id"])
        remember_user(callback_query.get("from", {}))
        message = callback_query.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        if chat_id is None:
            return
        text, reply_markup = build_callback_reply(token, callback_query)
        send_message(token, chat_id, text, reply_markup)
        order_id = extract_order_id(text)
        if order_id:
            lang = get_user_lang(callback_query.get("from", {}).get("id"))
            try:
                maybe_send_payment_qr(token, chat_id, order_id, lang)
            except Exception as exc:
                print(f"QR yuborish xatosi: {exc}")
        return

    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    chat = message.get("chat", {})
    chat_id = chat.get("id")

    if chat_id is None:
        return

    user_id = message.get("from", {}).get("id")
    remember_user(message.get("from", {}))
    text = message.get("text") or message.get("caption")
    has_support_attachment = bool(support_attachment(message))
    if not text and not (has_support_attachment and get_user_state(user_id)):
        return

    reply_text, reply_markup = build_reply(token, message)
    send_message(token, chat_id, reply_text, reply_markup)
    order_id = extract_order_id(reply_text)
    if order_id:
        lang = get_user_lang(message.get("from", {}).get("id"))
        try:
            maybe_send_payment_qr(token, chat_id, order_id, lang)
        except Exception as exc:
            print(f"QR yuborish xatosi: {exc}")


def run_bot(token: str) -> None:
    offset = None
    last_reminder_check = 0.0
    print("Bot ishga tushdi. To'xtatish uchun Ctrl+C bosing.")

    while True:
        payload = {
            "timeout": 30,
            "allowed_updates": ["message", "edited_message", "callback_query"],
        }
        if offset is not None:
            payload["offset"] = offset

        try:
            now = time.time()
            if now - last_reminder_check > 3600:
                process_polis_reminders(token)
                last_reminder_check = now

            response = telegram_request(token, "getUpdates", payload)
            for update in response.get("result", []):
                offset = update["update_id"] + 1
                handle_update(token, update)
        except urllib.error.HTTPError as exc:
            print(f"Telegram HTTP xatosi: {exc.code} {exc.reason}")
            time.sleep(5)
        except urllib.error.URLError as exc:
            print(f"Tarmoq xatosi: {exc.reason}")
            time.sleep(5)
        except Exception as exc:
            print(f"Kutilmagan xato: {exc}")
            time.sleep(5)


def main() -> None:
    load_env_file(Path(__file__).with_name(".env"))
    token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not token:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN topilmadi. .env fayl yarating yoki environment variable sozlang."
        )

    run_bot(token)


if __name__ == "__main__":
    main()

