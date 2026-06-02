# KB_Шаблон

**Проект:** `C:\Users\Kawa\Desktop\Кб\KB_Шаблон`  
**Статус:** настроен и работает (агент как в KB_MIB_PARSER).

## Как пользоваться

1. **Cursor → Open Folder** → эта папка (`KB_Шаблон`).
2. Новый чат — агент читает `AGENTS.md`, `Шаблон_Сохранения.md`, `.cursor/rules/`, `context/*`.
3. Пишешь задачу — агент делает код/правки, **VERSION + commit** после порции, **Ask Question** до новой функциональности.

## Что настроено

| Компонент | Где |
|-----------|-----|
| Правила Cursor | `.cursor/rules/` — **5 файлов**, `alwaysApply: true`: `mandatory-rules-read-first.mdc`, `save-on-code-change.mdc`, `project-context-template.mdc`, `project-domain.mdc`, `commits-export-format.mdc` |
| Дисциплина агента | `Шаблон_Сохранения.md` |
| Память / идеи | `context/КОНТЕКСТ_*.md` |
| Версия | `VERSION` |
| Выгрузка коммитов | `tools/export_commits_xlsx.py` → `reports/` |

## Выгрузка коммитов в Excel

Перед первым запуском:

```powershell
pip install -r requirements.txt
```

**Сегодня:**

```powershell
py -3 tools/export_commits_xlsx.py
```

**За конкретный день:**

```powershell
py -3 tools/export_commits_xlsx.py --since 2026-06-02 --until 2026-06-02
```

**За период:**

```powershell
py -3 tools/export_commits_xlsx.py --since 2026-06-01 --until 2026-06-02
```

Результат: `reports/Коммиты_YYYY_MM_DD.xlsx` (8 колонок, подсветка типа — см. `commits-export-format.mdc`). Если Excel открыт — закрыть файл и повторить.

## Глобальное правило Cursor (User Rules)

В **Cursor → Settings → Rules** глобально может быть правило «коммить только по просьбе». В этом проекте его **перебивают** проектные правила: после порции кода — **VERSION + git commit** без ожидания слова «закоммить» (исключение: «без коммита» в текущем чате).

Рекомендуемая строка в User Rules (если копируете MIB-дискiplину):

```text
В проектах с файлом Шаблон_Сохранения.md и .cursor/rules/save-on-code-change.mdc
приоритет у проектных правил: после порции кода — VERSION + git commit без ожидания слова «закоммить».
```

## Проверка

**Шаблон проверен** — 2 июня 2026.  
**VERSION:** см. файл `VERSION`.

## Позже — другой проект

Скопируй папку под новым именем, если понадобится второй репозиторий. Планы переноса лежат в **KB_MIB_PARSER** (`context/ПЛАН_ПЕРЕНОС_…`), не здесь.
