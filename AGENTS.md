# AGENTS.md — інструкція для агента публікації

Ця директорія є **curated підмножиною vault**, підготовленою стати коренем публічного GitHub-репозиторію. У системному реєстрі vault вона описана як ресурс `repo-topic-hub-catalog` (категорія `resource`, статус `planned`); джерело правди лишається у vault.

## Мета

Створити публічний репозитарій `crmteos/topic-hub-catalog` і запушити **вміст цієї директорії** як корінь репо. Репо виконує дві ролі: публічний контакт у `User-Agent` та дзеркало каталогу бібліотек.

## Межа роботи — прочитати перед будь-якою дією

- Працюй **тільки** всередині цієї директорії.
- **Не** копіюй і не публікуй інші директорії vault: `Система/`, `База Знань/`, `Інтерфейс користувача Бази знань/`, `.obsidian/`, `Система/copilot/copilot-conversations/`, інвентар, реєстри, скрипти планувальника.
- **Не** додавай емейл у будь-який файл. Контакт — GitHub Issues.
- **Не** змінюй `legal_review`, `tos_verified_at` або інші юридичні поля у записах.
- **Не** записуй ключі, токени, паролі, OAuth-дані чи значення Keychain. Не проси користувача надати їх.
- **Не** використовуй `--dangerously-skip-permissions` і не обходи дозволи.
- Використовуй тільки безкоштовні опції: публічне репо, стандартні runners. Larger runners платні навіть для публічних репо.

## Передпушовий контроль (усі пункти обов'язкові)

1. Перевір, що присутні 9 записів: `tools/records/*.md` (6 active + 3 planned).
2. Перевір User-Agent у **двох** файлах — він має містити URL репо, а не опис:
   - `tools/search_helpers.py` → `topic-hub-web-search/1.0 (https://github.com/crmteos/topic-hub-catalog)`
   - `tools/catalog_worker.py` → `topic-hub-catalog-worker/1.0 (https://github.com/crmteos/topic-hub-catalog)`
3. Скануй на секрети (результат має бути порожнім):

   ```powershell
   Get-ChildItem -Recurse -File | Select-String -Pattern 'AIza[0-9A-Za-z_-]{20,}|ghp_[A-Za-z0-9]{20,}|Bearer\s+\S{16,}|(api[_-]?key|password|secret)\s*[:=]\s*\S+'
   ```

   Якщо доступний `rg`: `rg -n "AIza|ghp_|Bearer\s|api[_-]?key\s*[:=]|password\s*[:=]|secret\s*[:=]" .`
4. Перевір відсутність локальних абсолютних шляхів (результат має бути порожнім):

   ```powershell
   Get-ChildItem -Recurse -File -Exclude AGENTS.md,PROMPT.md,PUBLICATION.md | Select-String -Pattern 'C:\\Projects|C:\\Users'
   ```
5. Перевір локальну валідацію (0 помилок; 6 попереджень `legal_review: pending` — це очікувано):

   ```powershell
   py -3 tools/catalog_worker.py --validate --dry-run --records tools/records
   ```
6. Перевір, що згенерований файл збігається з поточним:

   ```powershell
   py -3 tools/catalog_worker.py --generate "$env:TEMP\sources_generated.py" --records tools/records
   ```
   Порівняй вміст із `tools/sources_generated.py` (для Windows і Linux різні закінчення рядків — порівнюй текст, а не байти).

## Кроки публікації

> Стан на 2026-11-22: локальний Git-репозитарій уже ініціалізовано, перший коміт зроблено. **Не повторюй `git init` і не створюй новий початковий коміт.** У середовищі підготовки `gh` відсутній, `git` доступний.

Спочатку створи порожнє **публічне** репо `crmteos/topic-hub-catalog` на GitHub **без** README, LICENSE і `.gitignore` — інакше перший push відхилиться через несумісні історії. Потім:

```powershell
$ErrorActionPreference = 'Stop'
Set-Location '<шлях до цієї директорії>'
git status --short          # має бути порожньо
git log -1 --oneline        # перший коміт уже є
git remote -v               # origin поки не налаштовано
git remote add origin https://github.com/crmteos/topic-hub-catalog.git
git push -u origin main
```

Автентифікацію виконує користувач через власні git-облікові дані — агент їх не зберігає й не запитує. Якщо `gh` доступний, після створення репо ним можна скористатися для перевірки: `gh auth status`, `gh repo view crmteos/topic-hub-catalog --json name,visibility,url`.

Увімкни GitHub Pages (Source: GitHub Actions). Якщо `gh` доступний:

```powershell
gh api -X PUT repos/crmteos/topic-hub-catalog/pages -f build_type=workflow
```

Інакше вручну: Settings → Pages → Build and deployment → Source: GitHub Actions. Окремий Obsidian-плагін для push не потрібен.

## Після пушу

- `gh api repos/crmteos/topic-hub-catalog --jq .html_url` — репо існує й публічне (або перевір у браузері, якщо `gh` відсутній).
- `gh run list --limit 5` — workflow `Catalog validation` завершився успішно (або вкладка Actions у браузері).
- Відкрий `https://crmteos.github.io/topic-hub-catalog/` — сайт відповідає.
- Повтори сканування на секрети вже в репо.

## Якщо назву репо змінено

Назва `topic-hub-catalog` фігурує в чотирьох код-файлах (два у vault, дві копії тут), у README, docs і site. Перед пушем заміни URL у всіх, інакше контакт у `User-Agent` вказуватиме на неіснуючу адресу.
