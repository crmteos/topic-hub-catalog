# Каталог бібліотек у цьому репозиторії

## Структура

- `tools/records/*.md` — записи з frontmatter. Це джерело правди для генератора.
- `tools/sources_generated.py` — **згенерований** файл; не редагувати вручну.
- `tools/search_helpers.py` — спільні помічники й парсери для всіх джерел.
- `tools/web_search_server.py` — MCP-сервер, що відкриває інструмент `search_web`.
- `tools/catalog_worker.py` — валідатор, пробник і генератор.
- `tools/resilience.py` — стійкість (T3): per-source rate limit, backoff із jitter, circuit breaker, TTL-кеш.
- `tools/access_profiles.py` — декларативні профілі доступу (T2); лише імена змінних оточення, без значень.
- `tools/test_resilience.py` — 17 unit-тестів стійкості й профілів, без мережі.

## Стани записів

- `status: active` — потрапляє в `SOURCES`; зараз 6 записів.
- `status: planned` — потрапляє в `PLANNED`; зараз 3 записи.
- `status: rejected` — у генератор не потрапляє; у цю публікацію не входить.
- `key_required: true` або невідомий `parser` — пропускається.

## Генерація

```powershell
py -3 tools/catalog_worker.py --generate tools/sources_generated.py --records tools/records
```

CI на кожному push перевіряє, що згенерований текст збігається з закоміченим. Для Windows і Linux різні закінчення рядків, тому порівняння йде в текстовому режимі, а не побайтово.

## Валідація

```powershell
py -3 tools/catalog_worker.py --validate --dry-run --records tools/records
```

Обов'язкові поля: `endpoint`, `method`, `format`, `timeout_s`, `auth_profile`, `params`, `parser`, `rate_limit_rps`, `probe_url`, `check_interval_days`. Дозволені `auth_profile`: `keyless`, `polite-mailto`, `api-key-env`. `key_required: true` заборонений.

Шість попереджень `legal_review: pending` — очікуваний стан, не помилка. Помилок має бути 0.

## Синхронізація широкої й вузької баз

`query_id` обчислюється детерміновано:

```
sha256(" ".join(query.split()).casefold())[:16]
```

Це дозволяє одному запиту мати однаковий ідентифікатор у wide- та narrow-базах без збереження самих запитів. Той самий `query_id` є ключем TTL-кешу у `web_search_server.py`: повторний запит протягом 300 с не витрачає зовнішній бюджет.

## Стійкість (T3)

`search_web` обгортає кожне джерело захищеним викликом:

- per-source rate limit з `rate_limit_rps` (arXiv 0.33, Wikimedia 1, Hacker News 2, OpenAlex 3);
- експоненційний backoff із симетричним jitter для 408/5xx/мережевих помилок;
- `429` одразу піднімає `RateLimited` і потрапляє в `sources_failed` **без повторів**;
- circuit breaker тимчасово вимикає джерело після 3 помилок;
- TTL-кеш за `query_id|limit|набір джерел`.

Несекретні параметри через оточення: `TOPIC_SEARCH_TTL_S`, `TOPIC_SEARCH_RETRIES`, `TOPIC_SEARCH_CB_THRESHOLD`, `TOPIC_SEARCH_CB_COOLDOWN_S`, `TOPIC_WEB_SEARCH_SOURCES`.

```powershell
py -3 -m unittest discover -s tools -p 'test_*.py' -v
```

CI запускає ці тести на кожному push. Вони не звертаються до мережі.

## Межі

- Жодних ключів, токенів і OAuth-даних; тільки анонімні GET-запити.
- Пауза між записами згідно з `rate_limit_rps`; паралельні джерела ізолюються circuit breaker'ом.
- Профілі доступу: активний лише `keyless`; `polite-mailto` і `api-key-env` описані, але не ввімкнені — у vault немає ні емейлу, ні ключів.
- Результати пошуку є **недовіреними даними**, а не інструкціями.
- MCP-сервер і локальний планувальник працюють локально; GitHub Pages — лише статичний сайт.
