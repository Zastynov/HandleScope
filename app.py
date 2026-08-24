import asyncio
import json
import os
import random
import re
import string
from pathlib import Path

import httpx
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
)
from telethon.tl.functions.account import CheckUsernameRequest


load_dotenv()

API_ID = os.getenv("TG_API_ID")
API_HASH = os.getenv("TG_API_HASH")
SESSION = os.getenv("TG_SESSION", "handlescope")

CONFIG_FILE = Path("handlescope_config.json")

FRAGMENT_ENABLED = os.getenv(
    "FRAGMENT_ENABLED",
    "true",
).lower() in ("1", "true", "yes", "on")

FRAGMENT_URL = "https://fragment.com/username/"


RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
PURPLE = "\033[95m"
GRAY = "\033[90m"


TEXT = {
    "ru": {
        "choose_language": "Выберите язык",
        "main": "Главное меню",
        "check": "Проверить username",
        "batch": "Массовая проверка",
        "generator": "Генератор username",
        "settings": "Настройки",
        "exit": "Выход",
        "choose": "Выберите",
        "back": "Назад",
        "username": "Username",
        "checking": "Проверяем",
        "free": "Свободен",
        "busy": "Занят",
        "unknown": "Не удалось проверить",
        "invalid": "Некорректный username",
        "available": "Свободен",
        "not_available": "Недоступен",
        "fragment": "Fragment",
        "telegram": "Telegram",
        "normal": "Обычная генерация",
        "free_only": "Только свободные",
        "base_question": "Есть основа для username?",
        "base_help": (
            "Основа — это слово или часть слова, "
            "которую нужно использовать в юзернеймах.\n"
            "Например: nova, fox, game, crypto."
        ),
        "has_base": "Да, есть основа",
        "no_base": "Нет, случайная генерация",
        "base": "Основа",
        "topic": "Тема",
        "amount": "Количество",
        "style": "Стиль",
        "suffix": "Слово + суффикс",
        "numbers": "Слово + цифры",
        "random": "Случайный",
        "words": "Слова",
        "length": "Длина",
        "any": "Любая",
        "use_digits": "Использовать цифры?",
        "yes": "Да",
        "no": "Нет",
        "searching": "Поиск свободных",
        "found": "Найдено",
        "nothing": "Свободных вариантов не найдено.",
        "language": "Язык",
        "fragment_check": "Проверка Fragment",
        "on": "Включена",
        "off": "Выключена",
        "saved": "Сохранено",
        "file": "Файл",
        "error": "Ошибка",
        "press": "Нажмите Enter...",
        "connected": "Telegram подключён.",
        "connecting": "Подключение к Telegram...",
        "result": "Результат",
    },
    "en": {
        "choose_language": "Choose language",
        "main": "Main menu",
        "check": "Check username",
        "batch": "Batch check",
        "generator": "Username generator",
        "settings": "Settings",
        "exit": "Exit",
        "choose": "Choose",
        "back": "Back",
        "username": "Username",
        "checking": "Checking",
        "free": "Available",
        "busy": "Occupied",
        "unknown": "Could not check",
        "invalid": "Invalid username",
        "available": "Available",
        "not_available": "Unavailable",
        "fragment": "Fragment",
        "telegram": "Telegram",
        "normal": "Normal generation",
        "free_only": "Only available",
        "base_question": "Do you have a username base?",
        "base_help": (
            "A base is a word or part of a word "
            "that should be used in usernames.\n"
            "For example: nova, fox, game, crypto."
        ),
        "has_base": "Yes, I have a base",
        "no_base": "No, random generation",
        "base": "Base",
        "topic": "Topic",
        "amount": "Amount",
        "style": "Style",
        "suffix": "Word + suffix",
        "numbers": "Word + numbers",
        "random": "Random",
        "words": "Words",
        "length": "Length",
        "any": "Any",
        "use_digits": "Use digits?",
        "yes": "Yes",
        "no": "No",
        "searching": "Searching",
        "found": "Found",
        "nothing": "No available usernames found.",
        "language": "Language",
        "fragment_check": "Fragment check",
        "on": "Enabled",
        "off": "Disabled",
        "saved": "Saved",
        "file": "File",
        "error": "Error",
        "press": "Press Enter...",
        "connected": "Telegram connected.",
        "connecting": "Connecting to Telegram...",
        "result": "Result",
    },
}


class App:
    def __init__(self):
        self.lang = self.load_language()

    def load_language(self):
        try:
            data = json.loads(
                CONFIG_FILE.read_text(
                    encoding="utf-8"
                )
            )
            value = data.get("language")

            if value in TEXT:
                return value

        except Exception:
            pass

        return None

    def save_language(self):
        CONFIG_FILE.write_text(
            json.dumps(
                {"language": self.lang},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def t(self, key):
        return TEXT.get(
            self.lang or "ru",
            TEXT["ru"],
        ).get(key, key)

    def clear(self):
        os.system(
            "cls" if os.name == "nt" else "clear"
        )

    def header(self):
        print(
            f"{PURPLE}{BOLD}HandleScope{RESET}"
        )
        print(
            f"{GRAY}username finder{RESET}\n"
        )

    def pause(self):
        input(
            f"\n{GRAY}{self.t('press')}{RESET}"
        )


app = App()


def normalize_username(value):
    value = value.strip()

    value = re.sub(
        r"^https?://t\.me/",
        "",
        value,
        flags=re.I,
    )

    value = value.split("/", 1)[0]

    if value.startswith("@"):
        value = value[1:]

    return value


def clean_base(value):
    value = normalize_username(value)

    value = re.sub(
        r"[^A-Za-z0-9_]",
        "",
        value,
    )

    return value.lower()


def valid_username(value):
    return bool(
        re.fullmatch(
            r"[A-Za-z0-9_]{5,32}",
            value,
        )
    )


class TelegramChecker:
    def __init__(self):
        if not API_ID or not API_HASH:
            raise RuntimeError(
                "TG_API_ID и TG_API_HASH не указаны в .env"
            )

        self.client = TelegramClient(
            SESSION,
            int(API_ID),
            API_HASH,
        )

    async def start(self):
        print(
            f"{CYAN}[*]{RESET} "
            f"{app.t('connecting')}"
        )

        await self.client.start()

        print(
            f"{GREEN}[+]{RESET} "
            f"{app.t('connected')}"
        )

        await asyncio.sleep(0.5)

    async def check(self, username):
        try:
            result = await self.client(
                CheckUsernameRequest(
                    username=username
                )
            )

            if result is True:
                return "free"

            return "busy"

        except FloodWaitError:
            return "rate"

        except Exception as e:
            error_name = type(e).__name__

            if error_name == "UsernameOccupiedError":
                return "busy"

            if error_name == "UsernamePurchaseAvailableError":
                return "fragment"

            if error_name == "UsernameInvalidError":
                return "invalid"

            return "unknown"

    async def close(self):
        await self.client.disconnect()


async def check_fragment(username):
    if not FRAGMENT_ENABLED:
        return "disabled"

    url = FRAGMENT_URL + username

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        async with httpx.AsyncClient(
            timeout=12,
            follow_redirects=True,
            headers=headers,
        ) as client:
            response = await client.get(url)

        if response.status_code == 404:
            return "free"

        if response.status_code != 200:
            return "unknown"

        html = response.text.lower()

        occupied_markers = (
            "place a bid",
            "current bid",
            "make an offer",
            "username sold",
            "username is not for sale",
        )

        if any(
            marker in html
            for marker in occupied_markers
        ):
            return "busy"

        return "unknown"

    except Exception:
        return "unknown"


async def check_username(
    telegram,
    username,
):
    username = normalize_username(username)

    if not valid_username(username):
        return {
            "username": username,
            "telegram": "invalid",
            "fragment": "invalid",
        }

    telegram_status = await telegram.check(
        username
    )

    if telegram_status == "rate":
        return {
            "username": username,
            "telegram": "rate",
            "fragment": "unknown",
        }

    fragment_status = await check_fragment(
        username
    )

    return {
        "username": username,
        "telegram": telegram_status,
        "fragment": fragment_status,
    }


def status_text(status):
    if status == "free":
        return (
            f"{GREEN}🟢 "
            f"{app.t('free')}{RESET}"
        )

    if status == "busy":
        return (
            f"{RED}🔴 "
            f"{app.t('busy')}{RESET}"
        )

    if status == "invalid":
        return (
            f"{RED}❌ "
            f"{app.t('invalid')}{RESET}"
        )

    if status == "disabled":
        return f"{GRAY}—{RESET}"

    if status == "rate":
        return (
            f"{YELLOW}⚠️ "
            f"{app.t('unknown')}{RESET}"
        )

    return (
        f"{YELLOW}🟡 "
        f"{app.t('unknown')}{RESET}"
    )


def telegram_is_free(result):
    return result["telegram"] == "free"


def fully_free(result):
    return result["telegram"] == "free"


async def single_check(telegram):
    app.clear()
    app.header()

    username = input(
        f"{CYAN}{app.t('username')}: {RESET}"
    )

    username = normalize_username(username)

    if not username:
        return

    print()

    result = await check_username(
        telegram,
        username,
    )

    print(
        f"{BOLD}@{result['username']}{RESET}\n"
    )

    print(
        f"{app.t('telegram')}: "
        f"{status_text(result['telegram'])}"
    )

    print(
        f"{app.t('fragment')}: "
        f"{status_text(result['fragment'])}"
    )

    if fully_free(result):
        print(
            f"\n{GREEN}✅ "
            f"{app.t('available')}{RESET}"
        )

    elif telegram_is_free(result):
        print(
            f"\n{YELLOW}🟡 Telegram: "
            f"{app.t('free')}. "
            f"Fragment: "
            f"{app.t('unknown')}.{RESET}"
        )

    else:
        print(
            f"\n{RED}❌ "
            f"{app.t('not_available')}{RESET}"
        )

    app.pause()


def choose_length():
    app.clear()
    app.header()

    print(
        f"{BOLD}{app.t('length')}{RESET}\n"
    )

    print("[1] Any")
    print("[2] 5")
    print("[3] 6")
    print("[4] 7")
    print("[5] 8")
    print("[6] 9")
    print("[7] 10")

    choice = input(
        f"\n{CYAN}{app.t('choose')}: {RESET}"
    )

    return {
        "1": None,
        "2": 5,
        "3": 6,
        "4": 7,
        "5": 8,
        "6": 9,
        "7": 10,
    }.get(choice)


def choose_style():
    app.clear()
    app.header()

    print(
        f"{BOLD}{app.t('style')}{RESET}\n"
    )

    print(
        f"[1] {app.t('words')}"
    )
    print(
        f"[2] {app.t('suffix')}"
    )
    print(
        f"[3] {app.t('numbers')}"
    )
    print(
        f"[4] {app.t('random')}"
    )

    choice = input(
        f"\n{CYAN}{app.t('choose')}: {RESET}"
    )

    return {
        "1": "words",
        "2": "suffix",
        "3": "numbers",
        "4": "random",
    }.get(
        choice,
        "suffix",
    )


def choose_digits():
    print()
    print(
        app.t("use_digits")
    )
    print(
        f"[1] {app.t('yes')}"
    )
    print(
        f"[2] {app.t('no')}"
    )

    choice = input(
        f"\n{CYAN}{app.t('choose')}: {RESET}"
    )

    return choice == "1"


def generate_random_word(length):
    vowels = "aeiou"
    consonants = (
        "bcdfghjklmnpqrstvwxyz"
    )

    result = []

    for i in range(length):
        if i % 2 == 0:
            result.append(
                random.choice(consonants)
            )
        else:
            result.append(
                random.choice(vowels)
            )

    return "".join(result)


def generate_with_base(
    base,
    amount,
    style,
    use_digits,
    target_length,
):
    base = clean_base(base)

    if not base:
        return []

    result = []
    seen = set()

    suffixes = [
        "bot",
        "dev",
        "app",
        "hub",
        "lab",
        "pro",
        "io",
        "x",
        "go",
        "one",
        "plus",
        "zone",
        "core",
        "flow",
        "sync",
        "byte",
    ]

    prefixes = [
        "my",
        "get",
        "go",
        "the",
        "hey",
        "its",
        "real",
        "use",
    ]

    def add(value):
        value = value.lower()

        if value in seen:
            return

        if not valid_username(value):
            return

        if (
            target_length is not None
            and len(value) != target_length
        ):
            return

        seen.add(value)
        result.append(value)

    if style == "words":
        for prefix in prefixes:
            add(prefix + base)
            add(prefix + "_" + base)

            if len(result) >= amount:
                return result[:amount]

        for suffix in suffixes:
            add(base + suffix)
            add(base + "_" + suffix)

            if len(result) >= amount:
                return result[:amount]

    elif style == "suffix":
        for suffix in suffixes:
            add(base + suffix)
            add(base + "_" + suffix)

            if len(result) >= amount:
                return result[:amount]

        for prefix in prefixes:
            add(prefix + base)

            if len(result) >= amount:
                return result[:amount]

    elif style == "numbers":
        for number in range(1, 10000):
            add(f"{base}{number}")

            if use_digits:
                add(f"{base}_{number}")

            if len(result) >= amount:
                return result[:amount]

    else:
        chars = string.ascii_lowercase

        if use_digits:
            chars += string.digits

        for _ in range(
            max(amount * 100, 500)
        ):
            if target_length is None:
                length = random.randint(
                    max(5, len(base)),
                    min(20, len(base) + 7),
                )
            else:
                length = target_length

            if len(base) >= length:
                continue

            extra_length = (
                length - len(base)
            )

            extra = "".join(
                random.choice(chars)
                for _ in range(extra_length)
            )

            if random.choice(
                (True, False)
            ):
                candidate = base + extra
            else:
                candidate = extra + base

            add(candidate)

            if len(result) >= amount:
                return result[:amount]

    return result[:amount]


def generate_without_base(
    amount,
    style,
    use_digits,
    target_length,
):
    result = []
    seen = set()

    suffixes = [
        "bot",
        "dev",
        "app",
        "hub",
        "lab",
        "pro",
        "io",
        "x",
        "go",
        "one",
        "plus",
        "zone",
        "core",
        "flow",
        "sync",
        "byte",
    ]

    def add(value):
        value = value.lower()

        if value in seen:
            return

        if not valid_username(value):
            return

        if (
            target_length is not None
            and len(value) != target_length
        ):
            return

        seen.add(value)
        result.append(value)

    words = [
        "nova",
        "vexa",
        "luma",
        "nexo",
        "zora",
        "viro",
        "mira",
        "zuno",
        "kora",
        "xeno",
        "rivo",
        "nora",
        "vexa",
        "movo",
        "lyra",
        "zeta",
        "kivo",
        "sora",
        "voro",
        "niva",
        "qora",
        "vexa",
        "luno",
        "raya",
        "zivo",
        "mexo",
        "tora",
        "vani",
    ]

    if style == "words":
        for word in words:
            add(word)

            if len(result) >= amount:
                return result[:amount]

        while len(result) < amount:
            length = (
                target_length
                or random.randint(5, 9)
            )

            add(
                generate_random_word(
                    length
                )
            )

    elif style == "suffix":
        for word in words:
            suffix = random.choice(
                suffixes
            )

            add(
                word + suffix
            )

            if len(result) >= amount:
                return result[:amount]

        while len(result) < amount:
            word = random.choice(words)
            suffix = random.choice(suffixes)
            add(word + suffix)

    elif style == "numbers":
        for word in words:
            number = random.randint(
                1,
                9999,
            )

            if use_digits:
                add(
                    f"{word}{number}"
                )
            else:
                add(word)

            if len(result) >= amount:
                return result[:amount]

        while len(result) < amount:
            word = random.choice(words)
            number = random.randint(
                1,
                99999,
            )
            add(f"{word}{number}")

    else:
        chars = string.ascii_lowercase

        if use_digits:
            chars += string.digits

        while len(result) < amount:
            length = (
                target_length
                or random.randint(5, 12)
            )

            value = "".join(
                random.choice(chars)
                for _ in range(length)
            )

            add(value)

    return result[:amount]


def generate_candidates(
    base,
    amount,
    style,
    use_digits,
    target_length,
):
    if base:
        return generate_with_base(
            base,
            amount,
            style,
            use_digits,
            target_length,
        )

    return generate_without_base(
        amount,
        style,
        use_digits,
        target_length,
    )


async def ask_base():
    app.clear()
    app.header()

    print(
        f"{BOLD}"
        f"{app.t('base_question')}"
        f"{RESET}\n"
    )

    print(
        f"{GRAY}"
        f"{app.t('base_help')}"
        f"{RESET}\n"
    )

    print(
        f"[1] {app.t('has_base')}"
    )
    print(
        f"[2] {app.t('no_base')}"
    )

    choice = input(
        f"\n{CYAN}{app.t('choose')}: {RESET}"
    )

    if choice == "1":
        base = input(
            f"\n{CYAN}"
            f"{app.t('base')}: "
            f"{RESET}"
        )

        return clean_base(base)

    return ""


async def configure_generation():
    base = await ask_base()

    app.clear()
    app.header()

    style = choose_style()

    app.clear()
    app.header()

    use_digits = choose_digits()

    target_length = choose_length()

    return (
        base,
        style,
        use_digits,
        target_length,
    )


async def normal_generator():
    (
        base,
        style,
        use_digits,
        target_length,
    ) = await configure_generation()

    app.clear()
    app.header()

    raw = input(
        f"{CYAN}"
        f"{app.t('amount')} [10]: "
        f"{RESET}"
    )

    try:
        amount = int(raw or 10)
    except ValueError:
        amount = 10

    amount = max(
        1,
        min(amount, 100),
    )

    result = generate_candidates(
        base,
        amount,
        style,
        use_digits,
        target_length,
    )

    app.clear()
    app.header()

    if not result:
        print(
            f"{YELLOW}"
            f"{app.t('nothing')}"
            f"{RESET}"
        )
        app.pause()
        return

    for username in result:
        print(
            f"@{username}"
        )

    print(
        f"\n{GRAY}"
        f"{len(result)}"
        f"{RESET}"
    )

    app.pause()


async def free_generator(telegram):
    (
        base,
        style,
        use_digits,
        target_length,
    ) = await configure_generation()

    app.clear()
    app.header()

    raw = input(
        f"{CYAN}"
        f"{app.t('amount')} [10]: "
        f"{RESET}"
    )

    try:
        amount = int(raw or 10)
    except ValueError:
        amount = 10

    amount = max(
        1,
        min(amount, 50),
    )

    candidate_count = max(
        amount * 30,
        100,
    )

    candidates = generate_candidates(
        base,
        candidate_count,
        style,
        use_digits,
        target_length,
    )

    if not candidates:
        print(
            f"{YELLOW}"
            f"{app.t('nothing')}"
            f"{RESET}"
        )
        app.pause()
        return

    free = []
    checked = 0

    app.clear()
    app.header()

    for username in candidates:
        checked += 1

        print(
            f"\r{CYAN}🔎 "
            f"{app.t('checking')} "
            f"@{username} "
            f"({checked}/{len(candidates)})"
            f"{RESET}",
            end="",
            flush=True,
        )

        result = await check_username(
            telegram,
            username,
        )

        if fully_free(result):
            free.append(username)

            if len(free) >= amount:
                break

        await asyncio.sleep(0.25)

    print(
        "\r" + (" " * 100) + "\r",
        end="",
    )

    app.clear()
    app.header()

    print(
        f"{GREEN}{BOLD}"
        f"🟢 {app.t('free_only')}"
        f"{RESET}\n"
    )

    if not free:
        print(
            f"{YELLOW}"
            f"{app.t('nothing')}"
            f"{RESET}"
        )
    else:
        for username in free:
            print(
                f"{GREEN}@{username}{RESET}"
            )

        print(
            f"\n{GRAY}"
            f"{app.t('found')}: "
            f"{len(free)}"
            f"{RESET}"
        )

    app.pause()


async def generator_menu(telegram):
    while True:
        app.clear()
        app.header()

        print(
            f"{BOLD}"
            f"{app.t('generator')}"
            f"{RESET}\n"
        )

        print(
            f"[1] 🎲 "
            f"{app.t('normal')}"
        )

        print(
            f"[2] 🔥 "
            f"{app.t('free_only')}"
        )

        print(
            f"[0] ↩ "
            f"{app.t('back')}"
        )

        choice = input(
            f"\n{CYAN}"
            f"{app.t('choose')}: "
            f"{RESET}"
        )

        if choice == "1":
            await normal_generator()

        elif choice == "2":
            await free_generator(
                telegram
            )

        elif choice == "0":
            return


async def batch_check(telegram):
    app.clear()
    app.header()

    print(
        f"{BOLD}📋 {app.t('batch')}{RESET}\n"
    )

    print(
        f"{GRAY}"
        "Можно указать название .txt файла "
        "или полный путь к нему."
        f"{RESET}\n"
    )

    filename = input(
        f"{CYAN}"
        f"{app.t('file')}: "
        f"{RESET}"
    ).strip().strip('"')

    path = Path(filename).expanduser()

    if not path.is_absolute():
        path = Path.cwd() / path

    if not path.exists():
        print(
            f"\n{RED}"
            f"{app.t('error')}: "
            f"файл не найден."
            f"{RESET}"
        )
        app.pause()
        return

    if not path.is_file():
        print(
            f"\n{RED}"
            f"{app.t('error')}: "
            f"указанный путь не является файлом."
            f"{RESET}"
        )
        app.pause()
        return

    if path.suffix.lower() != ".txt":
        print(
            f"\n{RED}"
            f"{app.t('error')}: "
            f"нужен файл с расширением .txt."
            f"{RESET}"
        )
        app.pause()
        return

    try:
        names = [
            normalize_username(x)
            for x in path.read_text(
                encoding="utf-8"
            ).splitlines()
            if x.strip()
        ]
    except Exception as e:
        print(
            f"\n{RED}"
            f"{app.t('error')}: "
            f"{e}"
            f"{RESET}"
        )
        app.pause()
        return

    if not names:
        print(
            f"\n{YELLOW}"
            "Файл пуст."
            f"{RESET}"
        )
        app.pause()
        return

    results = []

    for index, username in enumerate(
        names,
        1,
    ):
        print(
            f"\r{CYAN}🔎 "
            f"{app.t('checking')} "
            f"@{username} "
            f"({index}/{len(names)})"
            f"{RESET}",
            end="",
            flush=True,
        )

        result = await check_username(
            telegram,
            username,
        )

        results.append(result)

        await asyncio.sleep(0.25)

    print(
        "\r" + (" " * 100) + "\r",
        end="",
    )

    output = Path("results.json")

    output.write_text(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"{GREEN}✓ "
        f"{app.t('saved')}: "
        f"{output}"
        f"{RESET}"
    )

    app.pause()


def choose_language():
    app.clear()
    app.header()

    print(
        f"{BOLD}"
        f"{app.t('choose_language')}"
        f"{RESET}\n"
    )

    print("[1] Русский")
    print("[2] English")

    choice = input(
        f"\n{CYAN}"
        f"{app.t('choose')}: "
        f"{RESET}"
    )

    if choice == "1":
        app.lang = "ru"
        app.save_language()

    elif choice == "2":
        app.lang = "en"
        app.save_language()


def settings():
    while True:
        app.clear()
        app.header()

        print(
            f"{BOLD}"
            f"{app.t('settings')}"
            f"{RESET}\n"
        )

        language = (
            "Русский"
            if app.lang == "ru"
            else "English"
        )

        print(
            f"[1] "
            f"{app.t('language')}: "
            f"{language}"
        )

        print(
            f"[0] "
            f"{app.t('back')}"
        )

        choice = input(
            f"\n{CYAN}"
            f"{app.t('choose')}: "
            f"{RESET}"
        )

        if choice == "1":
            choose_language()

        elif choice == "0":
            return


async def main():
    if app.lang is None:
        app.lang = "ru"
        choose_language()

    telegram = TelegramChecker()

    try:
        await telegram.start()

        while True:
            app.clear()
            app.header()

            print(
                f"{BOLD}"
                f"{app.t('main')}"
                f"{RESET}\n"
            )

            print(
                f"[1] 🔎 "
                f"{app.t('check')}"
            )

            print(
                f"[2] 📋 "
                f"{app.t('batch')}"
            )

            print(
                f"[3] ✨ "
                f"{app.t('generator')}"
            )

            print(
                f"[4] ⚙️ "
                f"{app.t('settings')}"
            )

            print(
                f"[0] 🚪 "
                f"{app.t('exit')}"
            )

            choice = input(
                f"\n{CYAN}"
                f"{app.t('choose')}: "
                f"{RESET}"
            )

            if choice == "1":
                await single_check(
                    telegram
                )

            elif choice == "2":
                await batch_check(
                    telegram
                )

            elif choice == "3":
                await generator_menu(
                    telegram
                )

            elif choice == "4":
                settings()

            elif choice == "0":
                break

    finally:
        await telegram.close()


if __name__ == "__main__":
    asyncio.run(main())
