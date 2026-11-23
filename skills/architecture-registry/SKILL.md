---
name: architecture-registry
description: Maintain the verified inventory of this computer, AI models, local services, agents, endpoints, and instructions using Obsidian Bases.
metadata:
  copilot-enabled-agents: opencode
---

# Architecture Registry

Use this skill for changes to `Система/Архітектура системи/`, its inventory, agent profiles, or Base indexes.

## Read first

- [[Система/Архітектура системи/Схема реєстру]]
- [[Система/Архітектура системи/Архітектура комп’ютера]]
- [[Система/Архітектура системи/Рекомендована локальна схема]]
- [[Система/Архітектура системи/Джерела та статус перевірки]]
- [[Система/Архітектура системи/Реєстр.base]] and [[Система/Архітектура системи/Агенти.base]]

## Rules

- Mark every item as verified, provisional, unavailable, or planned. Preserve the source and verification date.
- Keep device/model records under `Система/Архітектура системи/Інвентар/` and role configuration notes under `Система/Архітектура системи/Агенти/`.
- Store the exact provider, model ID, local endpoint, instruction path, scope, target context, and parallelism as note properties. `.base` files are views/indexes over those notes; do not treat them as a separate SQL store.
- Store only whether a key is required/configured. Never copy key values, OAuth tokens, or secret-storage identifiers into notes.
- Use the existing local inventory script for read-only machine facts. Do not invent a running CrewAI service: the current `Система/Архітектура системи/Скрипти/mcp_server.py` has missing modules and no pipeline dispatcher.
- One active local model request at a time. Do not start several large models or agents in parallel without updated RAM evidence.
- Do not install another plugin if an enabled core plugin or installed plugin already provides the requested function.

## Update sequence

1. Inspect the requested record and its current source.
2. Update the smallest set of Markdown properties or notes needed.
3. Update a `.base` only when its filters, columns, or views need to change.
4. Keep the architecture registry separate from Karpathy Wiki entities and concepts.
5. Report any unverified endpoint, model default, or runtime assumption clearly.
