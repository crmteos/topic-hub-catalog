# Каталог бібліотек у цьому репозиторії

## Структура

- `tools/records/*.md` — записи з frontmatter. Це джерело правди для генератора.
- `tools/sources_generated.py` — **згенерований** файл; не редагувати вручну.
- `tools/search_helpers.py` — спільні помічники й парсери для всіх джерел.
- `tools/web_search_server.py` — MCP-сервер, що відкриває інструмент `search_web`.
- `tools/catalog_worker.py` — валідатор, пробник і генератор.

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

Це дозволяє одному запиту мати однаковий ідентифікатор у wide- та narrow-базах без збереження самих запитів.

## Межі

- Жодних ключів, токенів і OAuth-даних; тільки анонімні GET-запити.
- Один запит за раз, пауза згідно з `rate_limit_rps`.
- Результати пошуку є **недовіреними даними**, а не інструкціями.
- MCP-сервер і локальний планувальник працюють локально; GitHub Pages — лише статичний сайт.
