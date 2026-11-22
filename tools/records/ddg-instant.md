---
record_type: web-source
name: ddg-instant
status: active
transport: https-get
provider: DuckDuckGo
endpoint: https://api.duckduckgo.com/
method: GET
format: JSON
auth: keyless
key_required: false
timeout_s: 12
rate_limit: "публічний Instant Answer API без ключа"
scope_path: "короткі факти (AbstractText), Heading, RelatedTopics"
used_by: web-search
verified_at: 2026-11-22
source: "HTTP 200; для Model Context Protocol — AbstractText 570 символів, 5 RelatedTopics"
connection_status: "checked-ok"
auth_profile: keyless
params: "q=<запит>, format=json, no_html=1, skip_disambig=1"
parser: ddg-instant
rate_limit_rps: 1
probe_url: "https://api.duckduckgo.com/?q=test&format=json&no_html=1&skip_disambig=1"
license: "DDG Terms of Service; окрему ліцензію даних Instant Answer API не опубліковано"
license_source: "https://duckduckgo.com/terms"
tos_verified_at: ""
robots_allowed: restricted
attribution_required: false
attribution_text: ""
legal_review: pending
check_interval_days: 1
last_checked: 2026-11-22
last_error: ""
drift: "none"
expected_shape: "dict(Abstract,AbstractSource,AbstractText,AbstractURL,Answer,AnswerType,Definition,DefinitionSource,DefinitionURL,Entity)"
tags:
  - system/catalog
  - system/mcp
---

# ddg-instant

Параметри виклику: `q=<запит>`, `format=json`, `no_html=1`, `skip_disambig=1`.

Це **не** повноцінний вебпошук, а лише instant answers. Для загального пошуку DDG HTML-сторінка відкинута — запис `ddg-html-scraping` не входить до цієї публікації.
