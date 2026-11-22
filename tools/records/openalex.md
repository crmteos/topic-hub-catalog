---
record_type: web-source
name: openalex
status: active
transport: https-get
provider: OpenAlex
endpoint: https://api.openalex.org/works
method: GET
format: JSON
auth: keyless
key_required: false
timeout_s: 12
rate_limit: "анонімно — спільний денний бюджет ~$0.10 на IP; безкоштовний ключ дає $1/день (не використовуємо)"
scope_path: "наукові праці, DOI, рік публікації, цитування"
used_by: web-search
verified_at: 2026-11-22
source: "HTTP 200; у відповіді явне повідомлення про спільний анонімний бюджет"
connection_status: "checked-ok"
auth_profile: keyless
params: "search=<запит>, per-page=<limit>"
parser: openalex-works
rate_limit_rps: 3
probe_url: "https://api.openalex.org/works?search=test&per-page=1"
license: "CC0 1.0 (дані OpenAlex); PDF-и — оригінальний copyright"
license_source: "https://openalex.org/about"
tos_verified_at: ""
robots_allowed: allowed
attribution_required: false
attribution_text: "атрибуція бажана, але не обов'язкова; рекомендоване цитування: Priem, Piwowar & Orr (2022), arXiv:2205.01833"
legal_review: pending
check_interval_days: 1
last_checked: 2026-11-22
last_error: ""
drift: "none"
expected_shape: "dict(group_by,meta,results)"
tags:
  - system/catalog
  - system/mcp
---

# openalex

Параметри виклику: `search=<запит>`, `per-page=<limit>`.

Повертає `title`/`display_name`, `doi` або `id`, `publication_year`, `cited_by_count`. Через спільний бюджет може тимчасово відмовляти — інші п'ять джерел працюють незалежно.
