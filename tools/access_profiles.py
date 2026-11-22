"""Декларативні профілі доступу для каталогу бібліотек (беклог T2).

У нотатці зберігається лише ідентифікатор профілю (`auth_profile`).
Контакт і ключ НІКОЛИ не зберігаються у vault: тут є тільки імена змінних
оточення, з яких значення читається під час запуску. Жодне значення не
пишеться в логи, відповіді MCP чи нотатки.

Важливо: `keyless` — єдиний активний профіль у безключовому контурі.
`polite-mailto` і `api-key-env` описані як доступні, але НЕ активовані:
- polite-mailto вимагає публічного емейлу, а контакт — лише URL репо в
  User-Agent (емейл заборонено публікувати й додавати в HTTP-заголовки);
- api-key-env вимагає ключа, а безкоштовний контур свідомо працює анонімно.
Це обмеження контуру, а не технічна неспроможність шару профілів.
"""

from __future__ import annotations

import os
from typing import Any

# Лише ІМЕНА змінних оточення. Значень тут немає й бути не може.
PROFILES: dict[str, dict[str, Any]] = {
    "keyless": {
        "active": True,
        "credential_env": "",
        "header": "",
        "where": "не потрібно — анонімний GET",
        "rotation": "не застосовується",
        "note": "Ідентифікація йде через описовий User-Agent з URL репо.",
    },
    "polite-mailto": {
        "active": False,
        "credential_env": "TOPIC_CONTACT_MAILTO",
        "header": "User-Agent",
        "where": "OS Keychain або оточення процесу; у vault — лише ім'я змінної",
        "rotation": "змінити значення змінної, перезапустити MCP-сервер",
        "note": "не активовано: публічний емейл заборонений, контакт — GitHub Issues.",
    },
    "api-key-env": {
        "active": False,
        "credential_env": "TOPIC_OPENALEX_API_KEY",
        "header": "Authorization",
        "where": "OS Keychain або оточення процесу; у vault — лише ім'я змінної",
        "rotation": "ротувати ключ у провайдера, оновити значення в Keychain",
        "note": "не активовано: безключовий контур; ключ дає приховані платні ліміти.",
    },
}


def resolve(profile_id: str) -> dict[str, str]:
    """Повертає заголовки для профілю. Ніколи не повертає значення в параметрах.

    Для неактивованих профілів повертає порожній словник, навіть якщо
    змінна оточення існує: увімкнення — окреме рішення людини.
    """
    profile = PROFILES.get(profile_id)
    if profile is None or not profile["active"]:
        return {}
    env_name = profile["credential_env"]
    if not env_name:
        return {}
    value = os.environ.get(env_name, "").strip()
    if not value:
        return {}
    return {str(profile["header"]): value}


def describe() -> list[dict[str, Any]]:
    """Безпечний опис профілів для документації — без значень."""
    return [
        {
            "id": key,
            "active": value["active"],
            "where": value["where"],
            "rotation": value["rotation"],
            "note": value["note"],
        }
        for key, value in PROFILES.items()
    ]
