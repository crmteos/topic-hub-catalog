---
record_type: web-source
name: hacker-news
status: active
transport: https-get
provider: Algolia (Hacker Search API)
endpoint: https://hn.algolia.com/api/v1/search
method: GET
format: JSON
auth: keyless
key_required: false
timeout_s: 12
rate_limit: "публічний API без ключа; перевірено стабільні на низькій частоті запитів"
scope_path: "технічні новини, обговорення, посилання спільноти Hacker News"
used_by: web-search
verified_at: 2026-11-22
source: "HTTP 200 у складі web-search; знайдено обговорення arXiv:0711.0770"
connection_status: "checked-ok"
auth_profile: keyless
params: "query=<запит>, hitsPerPage=<limit>"
parser: algolia-search
rate_limit_rps: 2
probe_url: "https://hn.algolia.com/api/v1/search?query=test&hitsPerPage=1"
license: "MIT (репозиторій HackerNews/API); дані HN/Algolia під окремою дата-ліцензією не опубліковані"
license_source: "https://github.com/HackerNews/API/blob/master/LICENSE"
tos_verified_at: 2026-11-22
robots_allowed: allowed
attribution_required: false
attribution_text: ""
legal_review: verified
check_interval_days: 1
last_checked: 2026-11-22
last_error: ""
drift: "none"
expected_shape: "dict(exhaustive,exhaustiveNbHits,exhaustiveTypo,hits,hitsPerPage,nbHits,nbPages,page,params,processingTimeMS)"
tags:
  - system/catalog
  - system/mcp
---

# hacker-news

Параметри виклику: `query=<запит>`, `hitsPerPage=<limit>`.

З кожного hit беремо `title` або `story_title`, `url` (або `https://news.ycombinator.com/item?id=<objectID>`) і `story_text`/`comment_text`; якщо тексту немає — `points` і `num_comments`.
