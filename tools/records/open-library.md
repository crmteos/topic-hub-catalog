---
record_type: web-source
name: open-library
status: planned
transport: https-get
provider: Internet Archive (Open Library)
endpoint: https://openlibrary.org/search.json
method: GET
format: JSON
auth: keyless
key_required: false
timeout_s: 12
rate_limit: "публічний API без ключа"
scope_path: "книги, автори, ISBN, роки видання"
used_by: none
verified_at: 2026-11-22
source: "HTTP 200, JSON; для Model Context Protocol — numFound 61; у SOURCES не додано"
connection_status: "checked-ok-not-connected"
auth_profile: keyless
params: "q=<запит>, limit=<limit>"
parser: open-library-search
rate_limit_rps: 1
probe_url: "https://openlibrary.org/search.json?q=test&limit=1"
license: ""
license_source: ""
tos_verified_at: ""
robots_allowed: unknown
attribution_required: false
attribution_text: ""
legal_review: pending
check_interval_days: 1
last_checked: 2026-11-22
last_error: ""
drift: "none"
expected_shape: "dict(docs,documentation_url,numFound,numFoundExact,num_found,offset,q,start)"
tags:
  - system/catalog
  - system/mcp
---

# open-library

Параметри виклику: `q=<запит>`, `limit=<limit>`.

Доступність перевірено, але до `web-search` не підключено. Для активації треба додати функцію з цією сигнатурою до кортежу `SOURCES`.
