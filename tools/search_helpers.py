"""Спільні помічники для джерел, згенерованих із каталогу бібліотек.

Усі запити анонімні. Текст відповідей вважається недовіреними даними.
"""

from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

USER_AGENT = "topic-hub-web-search/1.0 (https://github.com/crmteos/topic-hub-catalog)"

_TAG = re.compile(r"<[^>]+>")
_SECURITY = (
    re.compile(r"\b(?:sk|pk)-[A-Za-z0-9_\-]{16,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_\-]{20,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{16,}\b", re.IGNORECASE),
    re.compile(r"\b(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*\S+", re.IGNORECASE),
)
_ATOM = {"a": "http://www.w3.org/2005/Atom"}
_ARXIV_ID = re.compile(r"(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?", re.I)


def _scrub(text: str) -> str:
    for pattern in _SECURITY:
        text = pattern.sub("[REDACTED]", text)
    return text


def _clean(value: object, limit: int = 320) -> str:
    text = _TAG.sub(" ", str(value or ""))
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return _scrub(text)[:limit]


def _fetch_json(url: str, timeout: int = 12) -> dict:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        raw = response.read(2_000_000)
    return json.loads(raw.decode("utf-8", errors="replace"))


def _fetch_text(url: str, timeout: int = 12, accept: str = "application/atom+xml") -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    with urlopen(request, timeout=timeout) as response:
        return response.read(2_000_000).decode("utf-8", errors="replace")


def _language(endpoint: str) -> str:
    return endpoint.split("//", 1)[-1].split(".", 1)[0]


def _build_params(parser: str, query: str, limit: int, endpoint: str) -> dict:
    if parser == "mediawiki-search":
        return {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": limit,
            "srprop": "snippet",
        }
    if parser == "algolia-search":
        return {"query": query, "hitsPerPage": limit}
    if parser == "openalex-works":
        return {"search": query, "per-page": limit}
    if parser == "ddg-instant":
        return {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
    if parser == "arxiv-atom":
        found = _ARXIV_ID.search(query)
        if found and len(query) < 80:
            return {"start": 0, "max_results": limit, "id_list": found.group(0)}
        return {
            "start": 0,
            "max_results": limit,
            "search_query": f"all:{query}",
            "sortBy": "relevance",
        }
    if parser == "open-library-search":
        return {"q": query, "limit": limit}
    if parser == "internet-archive-search":
        return {
            "q": query,
            "fl[]": ["identifier", "title"],
            "rows": limit,
            "page": 1,
            "output": "json",
        }
    if parser == "wikidata-search":
        return {
            "action": "wbsearchentities",
            "search": query,
            "language": "en",
            "format": "json",
            "limit": limit,
        }
    raise ValueError(f"Невідомий parser: {parser}")


def _item(source: str, title: object, url: object, snippet: object) -> dict[str, str]:
    return {
        "source": source,
        "title": _clean(title, 160),
        "url": str(url or ""),
        "snippet": _clean(snippet),
    }


def _parse_mediawiki(data: dict, spec: dict, query: str, limit: int) -> list[dict[str, str]]:
    source = spec["name"]
    lang = _language(spec["endpoint"])
    base = spec.get("link_base") or f"https://{lang}.wikipedia.org/wiki/"
    results = []
    for row in data.get("query", {}).get("search", []):
        title = str(row.get("title", ""))
        if title:
            results.append(_item(source, title, base + quote(title.replace(" ", "_")), row.get("snippet", "")))
    return results


def _parse_algolia(data: dict, spec: dict, query: str, limit: int) -> list[dict[str, str]]:
    source = spec["name"]
    results = []
    for hit in data.get("hits", []):
        title = hit.get("title") or hit.get("story_title") or ""
        if not title:
            continue
        object_id = hit.get("objectID", "")
        link = hit.get("url") or (f"https://news.ycombinator.com/item?id={object_id}" if object_id else "")
        detail = hit.get("story_text") or hit.get("comment_text") or ""
        if not detail:
            detail = f"Points: {hit.get('points', 0)}, comments: {hit.get('num_comments', 0)}"
        results.append(_item(source, title, link, detail))
    return results


def _parse_openalex(data: dict, spec: dict, query: str, limit: int) -> list[dict[str, str]]:
    source = spec["name"]
    results = []
    for work in data.get("results", []):
        title = work.get("title") or work.get("display_name") or ""
        if not title:
            continue
        snippet = f"{work.get('publication_year', '')} · цитувань: {work.get('cited_by_count', 0)}"
        results.append(_item(source, title, work.get("doi") or work.get("id") or "", snippet))
    return results


def _parse_ddg(data: dict, spec: dict, query: str, limit: int) -> list[dict[str, str]]:
    source = spec["name"]
    results = []
    abstract = data.get("AbstractText")
    if abstract:
        results.append(_item(source, data.get("Heading") or query, data.get("AbstractURL") or "", abstract))
    for topic in data.get("RelatedTopics", [])[:limit]:
        if not isinstance(topic, dict):
            continue
        text = topic.get("Text", "")
        if text:
            results.append(_item(source, str(text).split(" - ")[0], topic.get("FirstURL") or "", text))
    return results


def _parse_arxiv(body: str, spec: dict, query: str, limit: int) -> list[dict[str, str]]:
    source = spec["name"]
    root = ET.fromstring(body)
    results = []
    for entry in root.findall("a:entry", _ATOM):
        title = entry.findtext("a:title", default="", namespaces=_ATOM)
        if not title:
            continue
        summary = entry.findtext("a:summary", default="", namespaces=_ATOM)
        published = entry.findtext("a:published", default="", namespaces=_ATOM)
        link = entry.findtext("a:id", default="", namespaces=_ATOM)
        results.append(_item(source, title, str(link), f"{str(published)[:10]} · {summary}"))
    return results


def _parse_open_library(data: dict, spec: dict, query: str, limit: int) -> list[dict[str, str]]:
    source = spec["name"]
    results = []
    for doc in data.get("docs", []):
        title = doc.get("title") or ""
        if not title:
            continue
        key = str(doc.get("key") or "")
        url = f"https://openlibrary.org{key}" if key.startswith("/") else key
        authors = ", ".join(doc.get("author_name", [])[:3])
        results.append(_item(source, title, url, f"{authors} · {doc.get('first_publish_year', '')}"))
    return results


def _parse_internet_archive(data: dict, spec: dict, query: str, limit: int) -> list[dict[str, str]]:
    source = spec["name"]
    results = []
    for doc in data.get("response", {}).get("docs", []):
        identifier = str(doc.get("identifier") or "")
        if not identifier:
            continue
        results.append(_item(source, doc.get("title") or identifier, f"https://archive.org/details/{identifier}", identifier))
    return results


def _parse_wikidata(data: dict, spec: dict, query: str, limit: int) -> list[dict[str, str]]:
    source = spec["name"]
    results = []
    for row in data.get("search", []):
        title = row.get("label") or ""
        if not title:
            continue
        results.append(_item(source, title, row.get("concepturi") or "", row.get("description") or ""))
    return results


PARSERS = {
    "mediawiki-search": _parse_mediawiki,
    "algolia-search": _parse_algolia,
    "openalex-works": _parse_openalex,
    "ddg-instant": _parse_ddg,
    "open-library-search": _parse_open_library,
    "internet-archive-search": _parse_internet_archive,
    "wikidata-search": _parse_wikidata,
}


def make_source(spec: dict) -> object:
    """Повертає callable(query, limit) для одного запису каталогу."""

    def run(query: str, limit: int) -> list[dict[str, str]]:
        params = _build_params(str(spec.get("parser")), query, limit, str(spec.get("endpoint")))
        url = str(spec["endpoint"]) + "?" + urlencode(params)
        timeout = int(spec.get("timeout_s") or 12)
        if str(spec.get("parser")) == "arxiv-atom":
            body = _fetch_text(url, timeout)
            return _parse_arxiv(body, spec, query, limit)
        parser = PARSERS.get(str(spec.get("parser")))
        if parser is None:
            return []
        return parser(_fetch_json(url, timeout), spec, query, limit)

    return run
