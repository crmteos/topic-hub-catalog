---
record_type: web-source
name: wikidata
status: planned
transport: https-get
provider: Wikimedia Foundation
endpoint: https://www.wikidata.org/w/api.php
method: GET
format: JSON
auth: keyless
key_required: false
timeout_s: 12
rate_limit: "жорсткого ліміту не задокументовано; бажаний описовий User-Agent"
scope_path: "структуровані факти й сутності (Q-ідентифікатори)"
used_by: none
verified_at: 2026-11-22
source: "HTTP 200, JSON; для Model Context Protocol — Q133436854; у SOURCES не додано"
connection_status: "checked-ok-not-connected"
auth_profile: keyless
params: "action=wbsearchentities, search=<запит>, language=en, format=json, limit=<limit>"
parser: wikidata-search
rate_limit_rps: 1
probe_url: "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=test&language=en&format=json&limit=1"
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
expected_shape: "dict(search,search-continue,searchinfo,success)"
tags:
  - system/catalog
  - system/mcp
---

# wikidata

Параметри виклику: `action=wbsearchentities`, `search=<запит>`, `language=en`, `format=json`, `limit=<limit>`.

Доступність перевірено, але в ланцюг не введено. Добре доповнює Wikipedia: дає `concepturi`, `url`, `display.label`.
