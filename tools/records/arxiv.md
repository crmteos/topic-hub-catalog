---
record_type: web-source
name: arxiv
status: active
transport: https-get
provider: arXiv
endpoint: https://export.arxiv.org/api/query
method: GET
format: Atom/XML
auth: keyless
key_required: false
timeout_s: 12
rate_limit: "рекомендовано не частіше 1 запиту на 3 секунди; ключ не потрібен"
scope_path: "препринти; пошук за текстом, arXiv ID і повним посиланням"
used_by: web-search
verified_at: 2026-11-22
source: "HTTP 200 (HTTP і HTTPS); знайдено arXiv:0711.0770 за ID і URL; query_id d4f43dc978da82dd"
connection_status: "checked-ok"
auth_profile: keyless
params: "search_query=all:<запит> або id_list=<ID>, start=0, max_results=<limit>, sortBy=relevance"
parser: arxiv-atom
rate_limit_rps: 0.33
probe_url: "https://export.arxiv.org/api/query?search_query=all:test&start=0&max_results=1"
license: "описові метадані CC0 1.0; e-prints — copyright авторів/видавців"
license_source: "https://info.arxiv.org/help/api/tou.html"
tos_verified_at: 2026-11-22
robots_allowed: restricted
attribution_required: false
attribution_text: "рекомендоване підтвердження: Thank you to arXiv for use of its open access interoperability."
legal_review: verified
check_interval_days: 1
last_checked: 2026-11-22
last_error: ""
drift: "none"
expected_shape: "feed[id,link,title,updated]"
tags:
  - system/catalog
  - system/mcp
---

# arxiv

Параметри виклику: `start=0`, `max_results=<limit>` і **або** `search_query=all:<запит>` із `sortBy=relevance`, **або** `id_list=<arXiv ID>`.

Розпізнає `0711.0770` і `https://arxiv.org/abs/0711.0770` — в обох випадках підставляє `id_list`. Відповідь Atom/XML розбирається стандартним `xml.etree.ElementTree`: беруться `title`, `summary`, `published`, `id`.
