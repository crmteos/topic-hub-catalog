---
record_type: web-source
name: wikipedia-en
status: active
transport: https-get
provider: Wikimedia Foundation
endpoint: https://en.wikipedia.org/w/api.php
method: GET
format: JSON
auth: keyless
key_required: false
timeout_s: 12
rate_limit: "жорсткого ліміту не задокументовано; бажаний описовий User-Agent"
scope_path: "англомовні енциклопедичні статті"
used_by: web-search
verified_at: 2026-11-22
source: "HTTP 200 у складі web-search; для Model Context Protocol — 4091 збіг"
connection_status: "checked-ok"
auth_profile: keyless
params: "action=query, list=search, srsearch=<запит>, format=json, srlimit=<limit>, srprop=snippet"
parser: mediawiki-search
rate_limit_rps: 1
probe_url: "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=test&format=json&srlimit=1&srprop=snippet"
license: "CC BY-SA 4.0 та GFDL (реюзе — будь-яка одна з ліцензій)"
license_source: "https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content"
tos_verified_at: ""
robots_allowed: restricted
attribution_required: true
attribution_text: "гіперпосилання/URL до сторінки, стабільна копія або список авторів"
legal_review: pending
check_interval_days: 1
last_checked: 2026-11-22
last_error: ""
drift: "none"
expected_shape: "dict(batchcomplete,continue,query)"
tags:
  - system/catalog
  - system/mcp
---

# wikipedia-en

Параметри виклику: ті самі, що у `wikipedia-uk`, з англомовним доменом. Використовується разом із українським як окреме джерело в `SOURCES`.
