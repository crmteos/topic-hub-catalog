"""Перевірка портативного контракту проєктної пам'яті в публічному дзеркалі.

Не читає vault, не має шляхів до нього й не змінює файлів.
Перевіряє лише внутрішню узгодженість дзеркала з оголошеним контрактом.
Exit 0 — контракт узгоджений, exit 1 — розсинхрон.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTRACT = HERE / "project_memory_contract.json"
RECORDS = HERE / "records"
SKILLS = HERE.parent / "skills"


def main() -> int:
    if not CONTRACT.is_file():
        print("FAIL: project_memory_contract.json absent")
        return 1
    try:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: contract JSON invalid: {exc}")
        return 1

    problems: list[str] = []
    for field in ("contract_version", "memory_version", "memory_phase"):
        if not str(contract.get(field, "")).strip():
            problems.append(f"empty {field}")

    ids = contract.get("decision_ids", [])
    if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)):
        problems.append("decision_ids must be a non-empty list of unique ids")

    expected_codes = [f"S{n}" for n in range(1, 8)]
    if sorted(contract.get("expected_drift_codes", [])) != expected_codes:
        problems.append("expected_drift_codes must be exactly S1..S7")

    skills = sorted(p.name for p in SKILLS.glob("*/SKILL.md")
                    if p.is_file())
    if len(skills) != contract.get("skills_expected"):
        problems.append(f"skills: found {len(skills)}, contract {contract.get('skills_expected')}")

    records = sorted(p.stem for p in RECORDS.glob("*.md") if p.is_file())
    if len(records) != contract.get("records_expected"):
        problems.append(f"records: found {len(records)}, contract {contract.get('records_expected')}")

    if problems:
        for item in problems:
            print(f"FAIL: {item}")
        return 1

    print(f"PASS: contract {contract['contract_version']}, "
          f"memory {contract['memory_version']} / {contract['memory_phase']}, "
          f"{len(ids)} decisions, {len(skills)} skills, {len(records)} records, "
          f"{len(expected_codes)} drift codes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
