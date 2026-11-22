# topic-hub-catalog

A public, curated subset of a personal Obsidian library catalog. It is **not** the vault itself. The repository contains:

- `tools/` — a keyless web-search MCP server, its generated source adapters, and a deterministic catalog worker;
- `tools/records/` — nine source records (six active, three planned);
- `docs/` — catalog structure, dated legal research, and rules for agents;
- `site/` — a static site published with GitHub Pages.

## Contact

**Use GitHub Issues to contact the operator.** No email address is published anywhere in this repository, and none is placed in HTTP headers.

The two User-Agent strings intentionally point here:

```
topic-hub-web-search/1.0 (https://github.com/crmteos/topic-hub-catalog)
topic-hub-catalog-worker/1.0 (https://github.com/crmteos/topic-hub-catalog)
```

This follows the [Wikimedia Foundation User-Agent Policy](https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy): a descriptive client name, a version, and a reachable contact.

## Access mode

`robots.txt` and API Terms of Use govern **different modes** and are not contradictory:

- **Crawler / spider** — link following and HTML download; governed by `robots.txt` (RFC 9309 convention).
- **API client** — targeted structured GET requests to a documented endpoint with rate limits and identification; governed by the API ToU / Robot Policy / API:Etiquette.

This project operates exclusively as an **API client**: low-frequency GET requests to documented endpoints, descriptive User-Agent, `Accept: application/json`. It does not crawl pages. The `robots_allowed` field in the records describes the literal crawler-mode state of `robots.txt`, not a prohibition on API calls.

## Active sources

| Source | Endpoint | License |
| --- | --- | --- |
| arxiv | `https://export.arxiv.org/api/query` | metadata CC0 1.0; e-prints remain author/publisher copyright |
| ddg-instant | `https://api.duckduckgo.com/` | DDG Terms; no separate Instant Answer data license published |
| hacker-news | `https://hn.algolia.com/api/v1/search` | MIT covers the HackerNews/API repository, not the data |
| openalex | `https://api.openalex.org/works` | CC0 1.0 (data) |
| wikipedia-en | `https://en.wikipedia.org/w/api.php` | CC BY-SA 4.0 and GFDL |
| wikipedia-uk | `https://uk.wikipedia.org/w/api.php` | CC BY-SA 4.0 and GFDL |

Planned but not active: `internet-archive`, `open-library`, `wikidata`.

## Run locally

```powershell
py -3 -m pip install pyyaml mcp

# Validate records without network access
py -3 tools/catalog_worker.py --validate --dry-run --records tools/records

# Probe the six active endpoints politely (one request at a time)
py -3 tools/catalog_worker.py --check --dry-run --only arxiv,ddg-instant,hacker-news,openalex,wikipedia-en,wikipedia-uk --records tools/records

# Regenerate adapters from records
py -3 tools/catalog_worker.py --generate tools/sources_generated.py --records tools/records

# Run the MCP server over stdio
py -3 tools/web_search_server.py
```

No API keys, OAuth tokens, passwords or paid services are used. `TOPIC_WEB_SEARCH_SOURCES` can narrow the active source list; it is not a secret.

## Legal status

Research was completed on **2026-11-22** from official provider pages and **accepted by the operator on 2026-11-22** after review of the three documented gaps: the repository URL in the User-Agent is treated as the reachable contact, no official DDG attribution requirement was found, and the HN/Algolia data license remains unpublished. The six active records now carry `legal_review: verified` and `tos_verified_at: 2026-11-22`; the three planned records stay `pending` until activated. This is an operator decision, not a legal opinion. See [`docs/legal.md`](docs/legal.md) for the facts and the mode clarification.

## License

The repository code, docs and site are licensed under the [MIT License](LICENSE). Third-party data keeps its own licenses (see the table above); required attribution is emitted into wide notes from the records. This repository license does not relicense Wikipedia, arXiv, OpenAlex, DDG or HN data.

## Attribution

- **arXiv** — recommended acknowledgement: “Thank you to arXiv for use of its open access interoperability.”
- **OpenAlex** — attribution appreciated but not required; suggested citation: Priem, Piwowar & Orr (2022), arXiv:2205.01833.
- **Wikipedia / Wikimedia** — hyperlink or URL to the source page, a stable copy, or a list of authors.

## CI

- `Catalog validation` — schema validation plus a check that `sources_generated.py` matches the records.
- `Source health` — weekly polite probe of the six active endpoints (rate limits respected).
- `Deploy site` — publishes `site/` with GitHub Pages.

## Ukrainian summary

Це публічна підмножина каталогу бібліотек, не сам vault. Контакт — Issues, без емейлу. Шість active-записів мають `legal_review: verified` і `tos_verified_at: 2026-11-22` після sign-off оператора; три planned лишаються `pending` до активації.

