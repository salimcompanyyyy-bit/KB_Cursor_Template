# Инструкция для агента — KB_Шаблон

**Это проект KB_Шаблон.** Рабочая папка: `C:\Users\Kawa\Desktop\Кб\KB_Шаблон`.  
Агент здесь ведёт себя **так же**, как в KB_MIB_PARSER: VERSION, auto-commit, context, Ask Question, русский язык.

## Сохранение (главное)

| | Путь |
|---|------|
| Полные правила | [`Шаблон_Сохранения.md`](Шаблон_Сохранения.md) |
| Указатель | [`context/КОНТЕКСТ_СОХРАНЕНИЕ.md`](context/КОНТЕКСТ_СОХРАНЕНИЕ.md) |
| Cursor rule | [`.cursor/rules/save-on-code-change.mdc`](.cursor/rules/save-on-code-change.mdc) |

После существенных правок: **`VERSION`** → контекст при смене поведения → **`git commit`** (формат в шаблоне). Не писать «готово» без коммита, если пользователь в чате не сказал «без коммита».

---

**Первое процедурное правило:** перед существенной работой прочитать все `.mdc` из [`.cursor/rules/`](.cursor/rules/), начиная с [`mandatory-rules-read-first.mdc`](.cursor/rules/mandatory-rules-read-first.mdc) и [`save-on-code-change.mdc`](.cursor/rules/save-on-code-change.mdc), затем корневой **[`Шаблон_Сохранения.md`](Шаблон_Сохранения.md)**. При расхождении по дисциплине агента, версиям и коммитам приоритет у **шаблона** (кроме явного указания пользователя в чате).

**Операционные правила** (уточнения, git, контекст) дублируются в [`.cursor/rules/project-context-template.mdc`](.cursor/rules/project-context-template.mdc).

**Источник правды по рабочему контексту репозитория:** файл [`context/КОНТЕКСТ_АГЕНТА.md`](context/КОНТЕКСТ_АГЕНТА.md).

**Цикл задачи (шаблон):** после `.mdc` и **`Шаблон_Сохранения.md`** — прочитать [`context/КОНТЕКСТ_АГЕНТА.md`](context/КОНТЕКСТ_АГЕНТА.md), [`context/КОНТЕКСТ_ПОЛЬЗОВАТЕЛЯ.md`](context/КОНТЕКСТ_ПОЛЬЗОВАТЕЛЯ.md), при работе с бэклогом — [`context/КОНТЕКСТ_ИДЕЙ.md`](context/КОНТЕКСТ_ИДЕЙ.md); по окончании порции — **+1 PATCH** в [`VERSION`](VERSION), обновить `context/*`, **обязательный `git commit`** (см. [`save-on-code-change.mdc`](.cursor/rules/save-on-code-change.mdc) — **не ждать** «закоммить»), в ответе — версия и хеш коммита.

Перед существенными изменениями кода откройте `КОНТЕКСТ_АГЕНТА.md` и следуйте разделам про ожидания и границы правок. **Новая видимая функциональность — сначала вопросы, без ответа код не писать**; варианты известны — **Ask Question** в Cursor **всегда** с **`allow_multiple: true`** у **каждого** вопроса (требование пользователя **2026-05-26**, hard-rule; **никаких** `false`, см. п. **2б–2в** в `КОНТЕКСТ_АГЕНТА.md`). См. **«Жёстко: вопросы до кода»** и п. **0, 2а–2в** в `КОНТЕКСТ_АГЕНТА.md` и п. **0** в [`.cursor/rules/project-domain.mdc`](.cursor/rules/project-domain.mdc).

Cursor подхватывает дополнительно правила из [`.cursor/rules/`](.cursor/rules/) (`alwaysApply`).

Версия: [`VERSION`](VERSION). После порции правок в репозитории — **поднять PATCH в `VERSION`**, обновить `context/*` при смене поведения и **один коммит** по формату из **`Шаблон_Сохранения.md`**. **Push** — только по явной просьбе. Идеи и бэклог — [`context/КОНТЕКСТ_ИДЕЙ.md`](context/КОНТЕКСТ_ИДЕЙ.md). Подробности — **`context/КОНТЕКСТ_АГЕНТА.md`**.

## Выгрузка коммитов в Excel

Любая просьба про «выгрузка коммитов» / «отчёт по коммитам» / «коммиты за день/период в Excel» → **только** через [`tools/export_commits_xlsx.py`](tools/export_commits_xlsx.py). Формат — [`.cursor/rules/commits-export-format.mdc`](.cursor/rules/commits-export-format.mdc).

| Запрос | Команда |
|--------|---------|
| «выгрузка коммитов» / «сегодня» | `py -3 tools/export_commits_xlsx.py` |
| «коммиты за 2026-06-02» | `py -3 tools/export_commits_xlsx.py --since 2026-06-02 --until 2026-06-02` |
| «коммиты с … по …» | `py -3 tools/export_commits_xlsx.py --since YYYY-MM-DD --until YYYY-MM-DD` |

Результат: `reports/Коммиты_YYYY_MM_DD.xlsx`. Перед первым запуском: `pip install -r requirements.txt`.

**Context:** только файлы в `context/` **этого** проекта. Не подтягивать историю из KB_MIB_PARSER.

## Bootstrap нового проекта (копия шаблона)

Если пользователь в **копии** шаблона просит создать новый проект / переименовать / bootstrap — следовать [`.cursor/rules/project-bootstrap.mdc`](.cursor/rules/project-bootstrap.mdc) и [`context/ИНСТРУКЦИЯ_НОВЫЙ_ПРОЕКТ.md`](context/ИНСТРУКЦИЯ_НОВЫЙ_ПРОЕКТ.md). **Не** bootstrap'ить материнский `KB_Шаблон`.
