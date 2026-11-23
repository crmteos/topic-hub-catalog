---
name: graph-control
description: Manage Obsidian graph views through the controlling Base — add graph-control records (contour + axis + selector), regenerate graph-presets, and publish an Excalidraw snapshot. Use when a task mentions graph slices, graph filters, color groups, or structuring the vault graph by contour/plugin/tag/property.
metadata:
  copilot-enabled-agents: opencode
---

# Graph Control

Use this skill to manage graphs as data, not as ad-hoc presets. The controlling Base [[Система/Графові зрізи/Керуюча база графів]] is the single source of truth; it is vault-wide, so it sees records in all three contours.

## Critical naming rule

`graph_axis` is a **filter axis** of the graph (contour, plugin, tag, property). It is NOT the scholarly notion of "виміри" (204/280 dimensions) studied in [[База Знань/wiki/Початок]]. Never use the word `dimension` for this field — that would collide with the knowledge-base concept. Keep the prefix `graph_`.

## Schema (stable columns)

| Field | Meaning | Example |
|---|---|---|
| `graph_contour` | 1st column: vault space | `Система`, `База Знань`, `Інтерфейс` |
| `graph_axis` | 2nd column: filter axis | `contour`, `plugin`, `tag`, `property` |
| `graph_selector` | 3rd column: value | `MCP-клієнти`, `web-page`, `type:concept` |
| `graph_color` | group color | `#4C8EDA` |
| `graph_enabled` | active flag | `true` |
| `graph_preset_id` | target preset | `contour-system` |
| `graph_kind` | record type | `filter`, `slice`, `annotation` |

A new parameter from the Knowledge Base becomes a **new record** with `graph_axis: <new axis>` — not a schema change. That is the Excel-like model: filter rows by columns and combine selectors.

## Agent role (proposed, not a host binding)

`graph-curator` is a **proposed role** in `.agents/agents/graph-curator/agent.md` (`status: proposed`, `evolves_from: graph-slice-publisher` — an evolution of the slice publisher, not a replacement). It edits graph-control records, checks the `graph_` prefix rule and calls the host-agnostic hub tool `regenerate_graph_presets`. The host is chosen at invocation — `agy`, Copilot, a worker or another runtime; the role is not tied to one CLI. The user never types `py -3 ...`. Runtimes that support project rules load `.agents/rules/graph-fields.md` automatically.

## Workflow

1. Add or edit a `type: graph-control` note in any contour's `Графові зрізи/Записи/`.
2. Regenerate presets through the host-agnostic hub tool `regenerate_graph_presets` (preferred). The direct command below is only a fallback for deterministic workers without the hub:

   ```powershell
   py -3 "Система/Архітектура системи/Скрипти/graph_presets_builder.py" --apply
   ```

3. The builder writes `.obsidian/plugins/graph-presets/data.json`. It never touches `.obsidian/graph.json` — Obsidian overwrites that file when the graph tab closes.
4. For a persistent artifact, render an Excalidraw snapshot with the `graph-slice-publisher` skill.

## Boundaries

- The builder reads vault-wide but skips `.obsidian/` and `copilot-conversations/`.
- Malformed frontmatter in unrelated notes is skipped, not fatal.
- Headless CLIs may gate MCP calls: use a temporary permission allowlist outside the vault; never `--dangerously-skip-permissions`.
- Answer in Ukrainian; keep original field names unchanged; separate confirmed facts from proposals.
