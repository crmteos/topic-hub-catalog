# Copilot instructions

Цей репозитарій — публічна curated підмножина каталогу бібліотек.

Повні інструкції для агентів лежать у [`AGENTS.md`](../AGENTS.md). Перед будь-якою зміною прочитай його, особливо розділи «Межа роботи» й «Жорсткі заборони».

Коротко:

- не публікуй vault, ключі, токени, паролі й емейли;
- контакт — GitHub Issues, не емейл;
- не змінюй `legal_review` і `tos_verified_at` у записах;
- `tools/sources_generated.py` генерується з `tools/records/*.md` — редагуй записи, потім повтори генерацію;
- шість active-записів мають `legal_review: verified` і `tos_verified_at: 2026-11-22` після sign-off; три planned лишаються `pending`, доки не активуються.
