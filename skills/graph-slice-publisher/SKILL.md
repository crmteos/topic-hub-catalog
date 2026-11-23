---
name: graph-slice-publisher
description: Build a separate evidence-based graph drawing from one saved graph-slice record and its selected Obsidian Base view.
metadata:
  copilot-enabled-agents: opencode
---

# Graph Slice Publisher

Use this skill when the user names a `slice_id` or asks for a separate graph perspective.

## Select one slice

1. Read [[Система/Графові зрізи/Каталог.base]] and the matching note under `Система/Графові зрізи/`.
2. Read only the record's `base_path`, `base_view`, and `scope_path`. Treat the selected view as the slice boundary, like a saved spreadsheet filter.
3. Follow the `agent_id`, `max_nodes`, `graph_mode`, and `drawing_path` fields. Do not merge two slices in one output unless the user asks.
4. If the selected knowledge view has no ingested entity/concept pages, leave it in `waiting-for-ingest` and report that there is no supported graph yet.

## Build an evidence graph

- Use only notes in the selected scope and existing `[[wiki-links]]` or explicitly documented relationships.
- Keep each node tied to an existing note. Do not infer an edge from simple co-occurrence.
- Prefer a readable overview: include the most connected, source-supported nodes first and respect `max_nodes`.
- One `slice_id` produces one separate drawing file. Keep other slice drawings untouched and update only the matching `drawing_path` and `last_rendered` fields.
- Include the slice name, source/Base view, generation date, and a short evidence/status note in the drawing or its companion note.

## Drawing format

- Use the Obsidian Excalidraw tool when it is available in the current session; never hand-write the Excalidraw serialization.
- In an OpenCode session without that tool, use the built-in `json-canvas` skill to create a separate `.canvas` snapshot. Update that slice's `drawing_path` to the file actually created.
- Embed the new drawing under the matching slice section in [[Система/Графові зрізи/Каталог графів]] so it is visible from the catalog.
- Do not overwrite a drawing for a different `slice_id`.
- If there are no supported relationships, produce a small note stating why the slice is empty instead of drawing speculative arrows.
