#!/usr/bin/env python3
"""Локальний worker каталогу бібліотек (P0+P1).

Режими:
  --validate         перевіряє схему записів без звернення до мережі;
  --check            робить по одному безключовому probe на джерело й оновлює
                     connection_status, verified_at, last_checked, last_error, drift;
  --dry-run          нічого не записує у vault, друкує звіт у консоль.

Запуск:
  py -3 catalog_worker.py --validate --check --dry-run
  py -3 catalog_worker.py --validate --check

Обмеження:
  - жодних ключів, токенів і OAuth-даних; тільки анонімні GET-запити;
  - один запит за раз, пауза згідно з rate_limit_rps;
  - генератор адаптерів (T1/P2) тут ще не реалізований;
  - LLM не викликається.
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Потрібен PyYAML: py -3 -m pip install pyyaml")
    raise SystemExit(2)

try:
    VAULT = Path(__file__).resolve().parents[3]
except IndexError:  # staging поза vault: шлях записів задається через --records
    VAULT = Path(__file__).resolve().parent
CATALOG = VAULT / "Система" / "Каталог бібліотек"
RECORDS = CATALOG / "Записи"
REPORT = CATALOG / "Звіт перевірок.md"

USER_AGENT = "topic-hub-catalog-worker/1.0 (https://github.com/crmteos/topic-hub-catalog)"
REQUIRED = (
    "endpoint",
    "method",
    "format",
    "timeout_s",
    "auth_profile",
    "params",
    "parser",
    "rate_limit_rps",
    "probe_url",
    "check_interval_days",
)
LEGAL = ("license", "license_source", "tos_verified_at", "robots_allowed")
AUTH_PROFILES = {"keyless", "polite-mailto", "api-key-env"}
PARSERS = {
    "mediawiki-search",
    "algolia-search",
    "openalex-works",
    "ddg-instant",
    "arxiv-atom",
    "open-library-search",
    "internet-archive-search",
    "wikidata-search",
}


def fmt(value):
    """Один рядок frontmatter: рядки завжди в лапках, дати лишаємо датами."""
    if value is None or value == "":
        return '""'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(value)):
        return str(value)
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    return f'"{escaped}"'


def load_records(only="", directory=None):
    names = {n.strip() for n in only.split(",") if n.strip()}
    base = Path(directory) if directory else RECORDS
    result = []
    for path in sorted(base.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        end = text.find("\n---\n", 4)
        if end < 0:
            continue
        data = yaml.safe_load(text[4:end])
        if not isinstance(data, dict):
            continue
        if names and data.get("name") not in names:
            continue
        result.append((path, data))
    return result


def write_fields(path, updates):
    """Змінює тільки перераховані поля, решту frontmatter лишає недоторканою."""
    text = path.read_text(encoding="utf-8")
    end = text.find("\n---\n", 4)
    if end < 0:
        return
    lines = text[4:end].split("\n")
    tail = text[end + 5 :]
    for key, value in updates.items():
        pattern = re.compile(r"^" + re.escape(key) + r"\s*:")
        new_line = f"{key}: {fmt(value)}"
        for index, line in enumerate(lines):
            if pattern.match(line):
                lines[index] = new_line
                break
        else:
            lines.append(new_line)
    new_text = "---\n" + "\n".join(lines) + "\n---\n" + tail
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")


def validate(records):
    errors, warnings = [], []
    for path, data in records:
        if data.get("record_type") != "web-source" or data.get("status") == "rejected":
            continue
        name = str(data.get("name") or path.stem)
        for field in REQUIRED:
            if data.get(field) in (None, "", []):
                errors.append(f"{name}: відсутнє поле {field}")
        profile = data.get("auth_profile")
        if profile not in AUTH_PROFILES:
            errors.append(f"{name}: невідомий auth_profile {profile!r}")
        if data.get("key_required") is True:
            errors.append(f"{name}: key_required: true заборонено у безключовому контурі")
        if data.get("status") == "active":
            if data.get("legal_review") != "verified":
                warnings.append(
                    f"{name}: legal_review={data.get('legal_review')!r} — юридичну перевірку не підтверджено"
                )
            else:
                for field in LEGAL:
                    if data.get(field) in (None, ""):
                        errors.append(f"{name}: legal_review=verified, але порожнє поле {field}")
    return errors, warnings


def parse_shape(body, response_format):
    if "XML" in str(response_format).upper():
        root = ET.fromstring(body)
        tag = root.tag.split("}")[-1]
        children = sorted({item.tag.split("}")[-1] for item in list(root)[:4]})
        return f"{tag}[{','.join(children)}]" if children else tag
    obj = json.loads(body)
    if isinstance(obj, dict):
        return "dict(" + ",".join(sorted(obj.keys())[:10]) + ")"
    if isinstance(obj, list):
        return f"list[{len(obj)}]"
    return type(obj).__name__


def probe(data):
    url = str(data.get("probe_url") or "")
    timeout = int(data.get("timeout_s") or 12)
    rps = float(data.get("rate_limit_rps") or 1)
    accept = "application/atom+xml" if "XML" in str(data.get("format")).upper() else "application/json"
    if rps > 0:
        time.sleep(1.0 / rps)
    started = time.monotonic()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(response.status)
            raw = response.read(2_000_000)
        body = raw.decode("utf-8", errors="replace")
        if not body.strip():
            return {"ok": False, "status": status, "error": "порожня відповідь", "latency": 0, "shape": ""}
        shape = parse_shape(body, data.get("format"))
        return {"ok": 200 <= status < 300, "status": status, "error": "", "latency": round((time.monotonic() - started) * 1000), "shape": shape}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": int(exc.code), "error": f"HTTP {exc.code}", "latency": round((time.monotonic() - started) * 1000), "shape": ""}
    except Exception as exc:  # timeout, DNS, JSON/XML parse
        message = str(exc).replace("|", "/").strip()[:180] or type(exc).__name__
        return {"ok": False, "status": 0, "error": message, "latency": round((time.monotonic() - started) * 1000), "shape": ""}


def check(records, dry_run):
    today = date.today().isoformat()
    rows = []
    for path, data in records:
        if data.get("record_type") != "web-source" or data.get("status") == "rejected":
            continue
        name = str(data.get("name") or path.stem)
        result = probe(data)
        updates = {"last_checked": today}
        if result["ok"]:
            expected = str(data.get("expected_shape") or "")
            drift = "none" if (not expected or expected == result["shape"]) else "shape-changed"
            checked_status = "checked-ok" if data.get("status") == "active" else "checked-ok-not-connected"
            updates.update(
                {
                    "connection_status": checked_status,
                    "verified_at": today,
                    "last_error": "",
                    "drift": drift,
                    "expected_shape": expected or result["shape"],
                }
            )
            note = "перевірено" if drift == "none" else "форма відповіді змінилася"
        else:
            updates.update({"connection_status": "check-failed", "last_error": result["error"]})
            note = result["error"]
        if not dry_run:
            write_fields(path, updates)
        rows.append(
            {
                "name": name,
                "status": data.get("status"),
                "ok": result["ok"],
                "http": result["status"],
                "latency": result["latency"],
                "shape": result["shape"],
                "note": note,
            }
        )
    return rows


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_report(rows, errors, warnings, dry_run, today):
    ok_count = sum(1 for row in rows if row["ok"])
    lines = [
        "---",
        "report_type: catalog-check",
        f"generated: {today}",
        f"mode: {'dry-run' if dry_run else 'applied'}",
        "---",
        "",
        "# Звіт перевірок каталогу",
        "",
        f"Перевірено джерел: **{len(rows)}**, успішно: **{ok_count}**. ",
        "Пауза між записами обчислюється з `rate_limit_rps`; всі запити анонімні.",
        "",
        "| Джерело | Стан | HTTP | Час, мс | Форма | Нотатка |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {cell(row['name'])} | {cell('ok' if row['ok'] else 'FAIL')} | {cell(row['http'])} "
            f"| {cell(row['latency'])} | {cell(row['shape'])} | {cell(row['note'])} |"
        )
    lines += [
        "",
        "## Валідація схеми",
        "",
        f"- Помилок: **{len(errors)}**",
        f"- Попереджень (юридичну перевірку не підтверджено): **{len(warnings)}**",
        "",
    ]
    for item in errors:
        lines.append(f"- ПОМИЛКА: {item}")
    for item in warnings:
        lines.append(f"- УВАГА: {item}")
    lines += [
        "",
        "> [!note] Межа перевірки",
        "> Worker перевіряє доступність і форму відповіді, а не зміст. "
        "Юридичні поля лишаються `pending`, доки їх не перегляне людина або `agy` під рев'ю.",
        "",
    ]
    return "\n".join(lines)


def generate_sources(out_path, records):
    """Збирає sources_generated.py з активних записів каталогу."""
    known = set(PARSERS)
    active, planned, skipped = [], [], []
    for path, data in records:
        if data.get("record_type") != "web-source" or data.get("status") == "rejected":
            continue
        name = str(data.get("name") or path.stem)
        status = data.get("status")
        parser_name = str(data.get("parser") or "")
        if status != "active":
            planned.append(name)
            continue
        if parser_name not in known or data.get("key_required") is True:
            skipped.append(name)
            continue
        spec = {
            "name": name,
            "endpoint": str(data.get("endpoint") or ""),
            "parser": parser_name,
            "format": str(data.get("format") or "JSON"),
            "timeout_s": int(data.get("timeout_s") or 12),
        }
        if parser_name == "mediawiki-search":
            spec["link_base"] = str(data.get("endpoint") or "").replace("/w/api.php", "/wiki/")
        active.append((name, json.dumps(spec, ensure_ascii=True, sort_keys=True)))

    lines = [
        '"""АВТОМАТИЧНО ЗГЕНЕРОВАНО catalog_worker.py --generate.',
        "",
        "Джерело правди: Система/Каталог бібліотек/Записи/*.md.",
        "Не редагувати вручну — змінюй запис каталогу й повтори генерацію.",
        '"""',
        "",
        "from search_helpers import make_source",
        "",
        "SOURCES = (",
    ]
    for name, spec in active:
        lines.append(f'    ("{name}", make_source({spec})),')
    lines += [
        ")",
        "",
        f"PLANNED = ({', '.join(repr(name) for name in planned)})" if planned else "PLANNED = ()",
        f"SKIPPED = ({', '.join(repr(name) for name in skipped)})" if skipped else "SKIPPED = ()",
        "",
    ]
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"Згенеровано {len(active)} активних джерел: {Path(out_path)}")
    if planned:
        print(f"У PLANNED (не в SOURCES): {', '.join(planned)}")
    if skipped:
        print(f"Пропущено (невідомий parser або key_required): {', '.join(skipped)}")


def main():
    parser = argparse.ArgumentParser(description="Локальний worker каталогу бібліотек")
    parser.add_argument("--validate", action="store_true", help="перевірити схему записів")
    parser.add_argument("--check", action="store_true", help="перевірити доступність джерел")
    parser.add_argument("--generate", metavar="OUT", help="шлях до згенерованого sources_generated.py")
    parser.add_argument("--records", metavar="DIR", help="альтернативна директорія записів (наприклад, staging)")
    parser.add_argument("--dry-run", action="store_true", help="не записувати у vault")
    parser.add_argument("--only", default="", help="тільки вказані імена через кому")
    args = parser.parse_args()
    if not (args.validate or args.check or args.generate):
        parser.error("вкажіть --validate, --check або --generate OUT")

    records = load_records(args.only, args.records)
    if not records:
        print("Записів не знайдено")
        return 1

    if args.generate:
        generate_sources(args.generate, records)
        return 0

    errors, warnings = validate(records) if args.validate else ([], [])
    rows = check(records, args.dry_run) if args.check else []
    today = date.today().isoformat()
    report = build_report(rows, errors, warnings, args.dry_run, today)

    if args.dry_run:
        print(report)
    else:
        REPORT.write_text(report, encoding="utf-8")
        print(f"Звіт записано: {REPORT.relative_to(VAULT)}")
    print(f"Підсумок: {len(rows)} перевірено, {len(errors)} помилок, {len(warnings)} попереджень")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
