"""АВТОМАТИЧНО ЗГЕНЕРОВАНО catalog_worker.py --generate.

Джерело правди: Система/Каталог бібліотек/Записи/*.md.
Не редагувати вручну — змінюй запис каталогу й повтори генерацію.
"""

from search_helpers import make_source

SOURCES = (
    ("arxiv", make_source({"endpoint": "https://export.arxiv.org/api/query", "format": "Atom/XML", "name": "arxiv", "parser": "arxiv-atom", "timeout_s": 12})),
    ("ddg-instant", make_source({"endpoint": "https://api.duckduckgo.com/", "format": "JSON", "name": "ddg-instant", "parser": "ddg-instant", "timeout_s": 12})),
    ("hacker-news", make_source({"endpoint": "https://hn.algolia.com/api/v1/search", "format": "JSON", "name": "hacker-news", "parser": "algolia-search", "timeout_s": 12})),
    ("openalex", make_source({"endpoint": "https://api.openalex.org/works", "format": "JSON", "name": "openalex", "parser": "openalex-works", "timeout_s": 12})),
    ("wikipedia-en", make_source({"endpoint": "https://en.wikipedia.org/w/api.php", "format": "JSON", "link_base": "https://en.wikipedia.org/wiki/", "name": "wikipedia-en", "parser": "mediawiki-search", "timeout_s": 12})),
    ("wikipedia-uk", make_source({"endpoint": "https://uk.wikipedia.org/w/api.php", "format": "JSON", "link_base": "https://uk.wikipedia.org/wiki/", "name": "wikipedia-uk", "parser": "mediawiki-search", "timeout_s": 12})),
)

PLANNED = ('internet-archive', 'open-library', 'wikidata')
SKIPPED = ()
