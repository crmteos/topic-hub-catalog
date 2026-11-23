---
name: airtable-resources
description: Use the topic-hub MCP tools for Airtable bases, tables and records when a task needs structured vault resources, cached inventory, or read/write record operations. Covers search_topic discovery, list_tables, list_records, search_records and create_records.
metadata:
  copilot-enabled-agents: opencode
---

# Airtable Resources through topic-hub

Use this skill when a task mentions Airtable, the base **Obsidian Vault Resources**, structured resources of this vault, or when structured read/write of inventory data would help. The Airtable MCP is reached through the local `topic-hub` MCP server, not through Copilot Connectors (those are a paid Supporters preview and are not available).

## When to use which tool

| Goal | Tool | Notes |
|---|---|---|
| Find the base by name | `search_topic(query="Obsidian Vault Resources")` | upstream `airtable`, fallback `list_bases`; returns `query_id` |
| Discover table and field IDs | `list_tables(base_id)` | required before writing records — writes need `fld...` IDs |
| Read records | `list_records(base_id, table, page_size, field_ids)` | `table` accepts an ID or a name |
| Search records by keyword | `search_records(base_id, table, query, fields, limit)` | `fields` = `ALL_SEARCHABLE_FIELDS` or a comma-separated list |
| Create records | `create_records(base_id, table_id, records)` | `records` is a JSON string; fields must use `fld...` IDs |

Canonical IDs (verify with `list_tables` if an ID changes):

- Workspace `My First Workspace` = `wsp3TYEi9gQxTRPps`
- Base `Obsidian Vault Resources` = `appW4Aw1zZhUECz6z`
- Tables: `Sources` = `tblKrVPmmsGL84Ltz`, `MCP Servers` = `tblIepp4jodGbLEH6`, `Model Catalog` = `tblD59VMmbh4SamUb`

## Boundaries

- Vault registry notes remain the **source of truth**; Airtable is a structured mirror. Do not treat Airtable records as authoritative over [[Система/Архітектура системи/Архітектура комп’ютера]] or [[Система/Архітектура системи/Реєстр.base]].
- The PAT lives only in the user environment variable `AIRTABLE_PAT`. Never print it, never write it into a note, config, prompt, or log. In config files there is only `${AIRTABLE_PAT}`.
- Never use `--dangerously-skip-permissions` with `agy`. In headless mode pass a temporary `--settings` allowlist for `mcp(topic-hub/*)` and delete the file afterwards.
- `create_records` changes remote data: confirm intent and scope first, then verify with `list_records`. Remove test records with `delete_records_for_table` when done.
- The record tools write directly to Airtable and do **not** create wide/narrow vault notes. `save_wide`/`save_narrow`/`save_pair` remain a separate flow keyed by `query_id`.
- New workspaces cannot be created via MCP (requires Enterprise admin). Create bases only in the existing workspace.

## Automatic mirroring (goal A)

For routine, deterministic syncing do **not** call an LLM or open `agy`. Use [[Система/Архітектура системи/Інвентар/script-airtable-sync-worker|Airtable Sync Worker]] — it reads vault frontmatter and calls hub tools by itself:

```powershell
py -3 "Система/Архітектура системи/Скрипти/airtable_sync_worker.py" --check
py -3 "Система/Архітектура системи/Скрипти/airtable_sync_worker.py" --apply
```

It only adds missing records; it never edits or deletes existing ones. The Windows task `TopicHub-AirtableSync` runs it daily at 09:10. Use this skill (goal B) only for interactive, judgment-based work.

## Verify after changes

1. `list_upstreams()` → `airtable ... credential: ready`.
2. `list_tables(base_id)` → expected tables.
3. For writes: `list_records(...)` → expected count; remove test records.
4. Keep bytecode out of the vault (`PYTHONDONTWRITEBYTECODE=1`).

Answer in Ukrainian; keep original product/model names unchanged; separate confirmed facts from proposals.
