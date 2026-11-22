---
record_type: web-source
name: internet-archive
status: planned
transport: https-get
provider: Internet Archive
endpoint: https://archive.org/advancedsearch.php
method: GET
format: JSON
auth: keyless
key_required: false
timeout_s: 12
rate_limit: "публічний API без ключа; запит може бути повільним (перевірено ~603 мс)"
scope_path: "архів книг, текстів, медіа, метаданих"
used_by: none
verified_at: 2026-11-22
source: "HTTP 200, JSON; у SOURCES не додано"
connection_status: "checked-ok-not-connected"
auth_profile: keyless
params: "q=<запит>, fl[]=identifier, fl[]=title, rows=<limit>, page=1, output=json"
parser: internet-archive-search
rate_limit_rps: 1
probe_url: "https://archive.org/advancedsearch.php?q=test&fl[]=identifier&rows=1&page=1&output=json"
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
expected_shape: "dict(response,responseHeader)"
tags:
  - system/catalog
  - system/mcp
---

# internet-archive

Параметри виклику: `q=<запит>`, `fl[]=identifier`, `fl[]=title`, `rows=<limit>`, `page=1`, `output=json`.

Доступність перевірено, але в ланцюг не введено. Потребує окремої функції в `SOURCES`.
