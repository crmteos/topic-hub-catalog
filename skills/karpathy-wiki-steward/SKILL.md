---
name: karpathy-wiki-steward
description: Ingest selected local sources, query the Karpathy LLM Wiki, and maintain provenance, aliases, tags, and graph links.
metadata:
  copilot-enabled-agents: opencode
---

# Karpathy Wiki Steward

Use this skill when the user asks to ingest, query, review, or maintain the subject-matter Wiki in `База Знань/wiki/`.

## System boundary

- Read [[База Знань/wiki/Початок]], [[База Знань/wiki/schema/config]], and the requested source before acting.
- The architecture registry in `Система/Архітектура системи/` owns machine facts, model parameters, endpoints, and agent instructions. The Wiki owns knowledge extracted from user-selected source notes.
- Do not copy the whole machine/model inventory into the subject Wiki. Link to an architecture note only when it is evidence for the requested topic.
- Never write API keys, OAuth codes, passwords, or Keychain values into the vault.

## Ingestion

1. Use only the source note or folder the user names. Never ingest the entire vault or silently add related notes.
2. Prefer one source per first run. Preserve the original source unchanged; the plugin writes provenance pages under `База Знань/wiki/sources/`.
3. Use the Karpathy plugin command for ingest when the current session exposes it. If it does not, tell the user which command to run and do not imitate a successful plugin ingest by hand.
4. Keep generated entity and concept tags inside the plugin's active vocabulary. Keep source quotations verbatim and cite their source page.
5. After ingest, inspect the operation history. Run Lint after a meaningful batch; review suggested repairs before applying them.

## Query and maintenance

- Answer in Ukrainian and ground factual statements in existing Wiki pages and their source links.
- Make gaps and contradictions explicit. Do not fill missing evidence with general knowledge.
- Use `Karpathy LLM Wiki: Query Wiki` when available; otherwise report that the plugin query panel must be opened in Obsidian.
- Do not edit the plugin-generated welcome note to fake configuration status. Use `Recreate Wiki Welcome Note` after the provider works.

## Local model limits

- Intended provider: Ollama at `http://localhost:11434/v1`, model `qwen2.5:7b`.
- Keep generation concurrency at 1 and use manual, incremental ingestion on this 16 GiB machine.
- Do not switch to a cloud provider or request a secret. If Test Connection fails, stop and report the exact failure without changing providers.
