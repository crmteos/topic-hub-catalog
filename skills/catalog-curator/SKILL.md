---
name: catalog-curator
description: Maintain the library catalog, its declarative source adapters, the local worker, and the public GitHub mirror; execute backlog T1–T7 in order without secrets or human sign-off assumptions.
metadata:
  copilot-enabled-agents: opencode
---

# Catalog Curator

Use this role for any work on the library catalog in `Система/Каталог бібліотек/`, the web-search MCP chain in `Система/Архітектура системи/MCP-клієнти/`, the local worker, or the public mirror in `Система/Каталог бібліотек/Публікація/`.

## System boundary

- The catalog is part of the **system contour**, not the Karpathy Wiki. Do not copy its records into `База Знань/wiki/`.
- Source of truth = `Система/Каталог бібліотек/Записи/*.md`. `sources_generated.py` is derived; never hand-edit it.
- `Система/Архітектура системи/` owns machine facts, model parameters, endpoints, and agent profiles. Link to it, do not duplicate it.
- Never write API keys, OAuth codes, passwords, Keychain values, or a personal email into the vault. The only contact in User-Agent is `https://github.com/crmteos/topic-hub-catalog`.
- Do not install a new Obsidian plugin for git or publishing. Copilot already has a terminal and `git`.

## Local limits

- Provider Ollama at `http://localhost:11434/v1`, model `ollama/qwen2.5:7b`, max_parallel 1. Run roles sequentially; do not start several models or agents in parallel.
- Prefer deterministic Python scripts over LLM calls. The worker must stay LLM-free.
- Keep bytecode out of the vault: `sys.dont_write_bytecode = True` or `PYTHONDONTWRITEBYTECODE=1`.

## Standard commands

```powershell
py -3 "Система/Архітектура системи/Скрипти/catalog_worker.py" --validate --dry-run
py -3 "Система/Архітектура системи/Скрипти/catalog_worker.py" --generate "Система/Архітектура системи/MCP-клієнти/sources_generated.py"
py -3 "Система/Архітектура системи/Скрипти/catalog_worker.py" --check --dry-run --only <source>
```

After changing canonical code, mirror the same files into `Система/Каталог бібліотек/Публікація/tools/`, re-run the pre-push checklist in that folder's `AGENTS.md`, then `git add`, `git commit`, `git push` from there. `gh` is not installed; use `git` and, if needed, the already configured git credentials without printing or storing tokens.

## Backlog playbook

Read [[Система/Каталог бібліотек/Обмеження каталогу як задачі]] first. Order: **T1 → T3 → T2 → T6 → T5 → T4 → T7**.

- **T1 (done):** records drive `SOURCES`. Keep it done: any new web source must work by adding a record and running `--generate`, not by editing Python.
- **T3:** implement per-source rate limiting, exponential backoff with jitter, a circuit breaker, and a TTL cache keyed by the hub's `query_id` (`sha256(" ".join(query.split()).casefold())[:16]`). A `429` must land in `sources_failed` without a retry cascade; one slow source must not block the others.
- **T2:** keep access profiles `keyless | polite-mailto | api-key-env` declarative. Store only the profile id and where the contact/key lives; never the value. `polite-mailto` is unavailable while no public contact email is allowed, so record that as a limitation, not a failure.
- **T6:** add a Base view that exposes overdue records using `last_checked` and `check_interval_days`. Revalidation must update `connection_status`, `verified_at`, `last_checked`, `last_error`, `drift` but never rewrite source content.
- **T5:** legal facts are research only. Do **not** set `legal_review: verified` or fill `tos_verified_at` without explicit human confirmation. Implement attribution in the wide note from `attribution_text` when `attribution_required: true`.
- **T4:** decide general keyless web search with evidence, or document a principled refusal. Keep `rejected` records with their reason.
- **T7:** use temporary settings files outside the vault for `agy`, delete them after the call, never keep a permanent allowlist, never use `--dangerously-skip-permissions`. Record quota checks as unresolved until a verified method exists.

## Reporting

- Close a backlog item only when its own criteria are met; otherwise mark the exact unmet criterion.
- For every factual change, preserve `source` and `verified_at` in the note.
- Separate confirmed facts from proposals and from items awaiting a human. Answer in Ukrainian, keeping original names in aliases.
- If a step needs a human decision (legal sign-off, repository license, quota method), stop that step and say precisely what is needed; continue with independent steps.
