# План публікації — рішення й межі

Статус: **опубліковано**. Дата: 2026-11-22. Репозитарій: https://github.com/crmteos/topic-hub-catalog · Сайт: https://crmteos.github.io/topic-hub-catalog/

## Рішення

| Параметр | Значення | Причина |
| --- | --- | --- |
| Репозитарій | `crmteos/topic-hub-catalog` | Стабільний публічний URL для `User-Agent` і Issues як канал зв'язку |
| Видимість | public | Публічний контакт; Actions на стандартних runners безкоштовні лише для публічних репо |
| Гілка | `main` | Стандарт для Pages |
| Корінь репо | вміст цієї директорії | Vault публікувати заборонено |
| Контакт | GitHub Issues | Замість емейлу: контакт є, адреса не потрапляє в логи й не збирається спам-ботами |
| Юридичний статус | research complete, **human confirmation pending** | `legal_review: pending`, `tos_verified_at: ""` — не змінювати |

## Що входить

- `tools/` — `search_helpers.py`, `sources_generated.py`, `web_search_server.py`, `catalog_worker.py`
- `tools/records/` — 9 записів: 6 active + 3 planned
- `docs/` — каталог, юридичне рев'ю, правила для агентів
- `site/` — статичний сайт для GitHub Pages
- `.github/workflows/` — валідація, перевірка джерел, деплой сайту
- `README.md`, `AGENTS.md`, `PROMPT.md`, `.gitignore`

## Що **не** входить

- Весь vault і будь-який з трьох контурів
- `.obsidian/`, copilot-conversations, інвентар, реєстри, Base-файли
- `antigravity-cli.md` — містить локальний абсолютний шлях
- `ddg-html-scraping.md`, `searxng-public.md` — status `rejected`, у генератор не потрапляють
- `mcpServers.json` — містить локальний шлях `C:\Projects\...`
- Будь-які ключі, токени, емейли, платіжні дані

## Відкриті питання (не блокують пуш)

1. Ліцензія самого репозиторію не обрана — без `LICENSE` GitHub вважає «all rights reserved». Рішення за користувачем.
2. DDG attribution requirements для Instant Answer API — не знайдено з офіційного джерела.
3. Дата-ліцензія HN/Algolia й повторна перевірка Y Combinator Legal — не закрито.
4. `legal_review: verified` і `tos_verified_at` — лише після явного підтвердження людиною.

## Чеклист стану

- [x] Створено структуру директорії
- [x] Скопійовано код і 9 записів
- [x] Виправлено User-Agent у 4 код-файлах
- [x] Написано `AGENTS.md`, `PROMPT.md`, README, docs, site, workflows
- [x] Фінальна перевірка: 0 проблем; живі GET із новим UA — 4× HTTP 200
- [x] Зареєстровано в системному реєстрі як `repo-topic-hub-catalog`, статус `planned`
- [x] Локальний Git-репозитарій ініціалізовано, перший коміт зроблено
- [x] Агент виконав передпушовий контроль
- [x] Репо створено й запушено (коміт `c43a31c`, 26 файлів)
- [x] GitHub Pages увімкнено (`build_type: workflow`)
- [x] CI завершився успішно (`Catalog validation`, `Deploy site`)
