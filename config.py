import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

USERS_FILE = BASE_DIR / "users.json"
DEFAULT_SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")


@dataclass(frozen=True)
class BotProfile:
    name: str
    telegram_id: int
    bot_token: str
    spreadsheet_id: str
    group_id: int | None
    service_account_file: str

    @property
    def service_account_path(self) -> Path:
        path = Path(self.service_account_file)
        return path if path.is_absolute() else BASE_DIR / path

    @property
    def has_owner_restriction(self) -> bool:
        return self.telegram_id != 0


def _validate_unique(values: list[str], field_name: str) -> None:
    duplicates = {value for value in values if values.count(value) > 1}
    if duplicates:
        duplicate_list = ", ".join(sorted(duplicates))
        raise ValueError(f"Найдены дубли по полю {field_name}: {duplicate_list}")


def _validate_unique_profile_routes(profiles: list["BotProfile"]) -> None:
    routes = [
        f"{profile.bot_token}:{profile.telegram_id}"
        for profile in profiles
        if profile.telegram_id != 0
    ]
    _validate_unique(routes, "bot_token + telegram_id")


def load_bot_profiles() -> list[BotProfile]:
    if not USERS_FILE.exists():
        raise FileNotFoundError(
            f"Файл конфигурации профилей не найден: {USERS_FILE}. "
            "Создай users.json рядом со скриптом."
        )

    raw_data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
    user_items = raw_data.get("users", [])

    if not isinstance(user_items, list):
        raise ValueError("Поле 'users' в users.json должно быть списком.")

    profiles: list[BotProfile] = []

    for index, item in enumerate(user_items, start=1):
        if not item.get("enabled", True):
            continue

        try:
            profile = BotProfile(
                name=item["name"],
                telegram_id=int(item.get("telegram_id", 0)),
                bot_token=item["bot_token"],
                spreadsheet_id=item["spreadsheet_id"],
                group_id=int(item["group_id"]) if item.get("group_id") is not None else None,
                service_account_file=item.get("service_account_file", DEFAULT_SERVICE_ACCOUNT_FILE),
            )
        except KeyError as exc:
            raise ValueError(f"Не хватает поля {exc} в users.json для записи #{index}") from exc
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Некорректные типы данных в users.json для записи #{index}") from exc

        profiles.append(profile)

    if not profiles:
        raise ValueError("В users.json нет ни одного активного профиля.")

    _validate_unique_profile_routes(profiles)

    return profiles


BOT_PROFILES = load_bot_profiles()

print(f"✅ Загружено профилей бота: {len(BOT_PROFILES)} из {USERS_FILE}")
