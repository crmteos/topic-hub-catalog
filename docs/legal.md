# Юридичне рев'ю джерел (research)

Дата збору: **2026-11-22**. Джерела — офіційні сторінки надавачів і їхні `robots.txt`.

**Межа статусу.** Це research, не юридичний висновок і не підтвердження людини. `legal_review: pending` і `tos_verified_at: ""` у всіх шести активних записах. Змінювати ці поля можна лише після явного прийняття людиною.

## Режими доступу

`robots.txt` і API ToU регулюють **різні режими**, тому їхня співнаявність не є суперечністю:

- **Crawler / spider** — обхід посилань і завантаження HTML; `robots.txt` (RFC 9309, конвенція, не закон).
- **API-клієнт** — цільові GET-запити до задокументованого endpoint із лімітами й ідентифікацією; API ToU / Robot Policy / API:Etiquette.

Наш `web-search` працює в режимі API-клієнта. Поле `robots_allowed` у записах фіксує буквальний стан `robots.txt` для crawler-ів, а не заборону на API-виклики.

## Зведена таблиця

| Джерело | Ліцензія | license_source | ToS URL | robots | attribution_required | attribution_text |
| --- | --- | --- | --- | --- | --- | --- |
| arxiv | описові метадані CC0 1.0; e-prints — copyright авторів/видавців | https://info.arxiv.org/help/api/tou.html | https://info.arxiv.org/help/api/tou.html | restricted — `export.arxiv.org/robots.txt` → `Disallow: /`; API регулюється окремим ToU | false | рекомендоване: «Thank you to arXiv for use of its open access interoperability.» |
| ddg-instant | DDG Terms of Service; окрему ліцензію даних Instant Answer API не опубліковано | https://duckduckgo.com/terms | https://duckduckgo.com/terms (оновлено 2025-01-07) | restricted — `api.duckduckgo.com/robots.txt` → `Disallow: /` | false (вимогу не підтверджено) | — |
| hacker-news | MIT на репозиторій HackerNews/API; дані HN/Algolia під окремою дата-ліцензією не опубліковані | https://github.com/HackerNews/API/blob/master/LICENSE | https://hn.algolia.com/api; https://www.ycombinator.com/legal/ | allowed — `hn.algolia.com/robots.txt` відсутній (404) | false | — |
| openalex | CC0 1.0 (дані OpenAlex); PDF-и — оригінальний copyright | https://openalex.org/about | https://openalex.org/OpenAlex_termsofservice.pdf (переглянуто 2026-10-02) | allowed — `api.openalex.org/robots.txt` → `Allow: /` | false | атрибуція бажана, не обов'язкова; Priem, Piwowar & Orr (2022), arXiv:2205.01833 |
| wikipedia-en | CC BY-SA 4.0 та GFDL (реюзе — будь-яка одна з ліцензій) | https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content | https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use (розд. 12 — API Terms) | restricted — `Disallow: /w/`, винятки для `action=mobileview` | true | гіперпосилання/URL, стабільна копія або список авторів |
| wikipedia-uk | CC BY-SA 4.0 та GFDL (реюзе — будь-яка одна з ліцензій) | https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content | https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use (розд. 12 — API Terms) | restricted — `Disallow: /w/`, винятки для `action=mobileview` | true | гіперпосилання/URL, стабільна копія або список авторів |

## Деталі й застереження

### arXiv

- [Terms of Use for arXiv APIs](https://info.arxiv.org/help/api/tou.html): метадані CC0 1.0; e-prints — copyright авторів/видавців.
- Ліміт legacy API: один запит на 3 секунди, одна конекція одночасно. У записі `rate_limit_rps: 0.33`.
- `export.arxiv.org/robots.txt` → `Disallow: /`; `arxiv.org/robots.txt` дозволяє `/abs`, `/pdf`, `/list` із `Crawl-delay: 15`, але забороняє `/api`, `/search`. Це crawler-контур; наш виклик іде на `export.arxiv.org/api/query` у режимі API-клієнта.

### DuckDuckGo Instant Answer API

- [Terms of Service](https://duckduckgo.com/terms), оновлено 2025-01-07.
- [API-сторінка](https://duckduckgo.com/api) майже порожня (JS-рендер): **вимогу атрибуції з офіційного джерела не підтверджено**. `attribution_required: false` означає «не знайдено вимоги», а не «атрибуція не потрібна».
- `api.duckduckgo.com/robots.txt` → `Disallow: /`.

### Hacker News / Algolia

- [HN Search API](https://hn.algolia.com/api) — публічний keyless endpoint; `robots.txt` відсутній (404).
- MIT у [HackerNews/API LICENSE](https://github.com/HackerNews/API/blob/master/LICENSE) покриває репозиторій (код), **не дані**. Окремої публічної data license не знайдено.
- `https://www.ycombinator.com/legal/terms` дав 404; [Y Combinator Legal](https://www.ycombinator.com/legal/) потребує повторної перевірки. **Незакрита прогалина.**

### OpenAlex

- [FAQ](https://docs.openalex.org/additional-help/faq): дані CC0; [About](https://openalex.org/about) підтверджує CC0 без «personal use only».
- [License.md](https://github.com/ourresearch/openalex-docs/blob/main/license.md): «We appreciate attribution where it's convenient, but it's not at all necessary.»
- [Terms of Service](https://openalex.org/OpenAlex_termsofservice.pdf), переглянуто 2026-10-02.
- `api.openalex.org/robots.txt` → `Allow: /`.

### Wikipedia (en/uk)

- [Terms of Use](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use), розд. 7: CC BY-SA 4.0 та GFDL; реюзе — одна з ліцензій.
- Атрибуція: гіперпосилання/URL до сторінки, стабільна копія або список авторів.
- Розд. 12 інкорпорує User-Agent Policy, Robot Policy та API:Etiquette; User-Agent має бути описовим із контактом.
- `Disallow: /w/` стосується crawler-ів; для API-клієнтів Robot Policy має окремий розділ «Action API rules» (concurrency 1, <5 req/s).

## Відкриті питання

1. User-Agent: контакт додано у вигляді URL публічного репозиторію з Issues — без емейлу.
2. DDG attribution requirements для Instant Answer API — не знайдено.
3. Дата-ліцензія HN/Algolia й повторна перевірка Y Combinator Legal — не закрито.
4. Human sign-off: після прийняття фактів заповнити `tos_verified_at` і перевести `legal_review: verified`.
