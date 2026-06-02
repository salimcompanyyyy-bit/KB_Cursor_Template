"""Bootstrap нового проекта из копии KB_Шаблон.

Использование:
    py -3 tools/bootstrap_project.py --name KB_MyApp
    py -3 tools/bootstrap_project.py --name KB_MyApp --path D:\\Projects\\KB_MyApp
    py -3 tools/bootstrap_project.py --name KB_MyApp --github-public
    py -3 tools/bootstrap_project.py --name KB_MyApp --dry-run

Безопасность: отказывает, если нет маркера шаблона (VERSION + KB_Шаблон в AGENTS.md)
или если cwd — материнская папка KB_Шаблон (override: BOOTSTRAP_OK=1).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

TEMPLATE_NAME = "KB_Шаблон"
TEXT_SUFFIXES = {".md", ".mdc"}
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules"}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        print(f"  [dry-run] write {path}")
        return
    path.write_text(content, encoding="utf-8", newline="\n")


def _detect_old_path(root: Path) -> str:
    agents = root / "AGENTS.md"
    if agents.is_file():
        for line in _read_text(agents).splitlines():
            if "Рабочая папка:" in line or "**Путь:**" in line or "**Проект:**" in line:
                match = re.search(r"`([^`]+)`", line)
                if match:
                    return match.group(1)
    return str(root.resolve())


def _is_template_marker(root: Path) -> bool:
    version = root / "VERSION"
    agents = root / "AGENTS.md"
    if not version.is_file() or not agents.is_file():
        return False
    return TEMPLATE_NAME in _read_text(agents)


def _is_master_template(root: Path, name: str) -> bool:
    if os.environ.get("BOOTSTRAP_OK") == "1":
        return False
    if name == TEMPLATE_NAME:
        return True
    return root.name == TEMPLATE_NAME


def _iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
    return sorted(files)


def _agent_context_template(name: str, path: str) -> str:
    return f"""# Контекст агента — {name}

**VERSION:** 1.0.0. **Путь:** `{path}`

## Назначение

Проект с **полной дисциплиной Cursor-агента** (rules, VERSION, auto-commit, Ask Question, context).
Свой код и домен — добавляй сюда.

---

## Ключи настроек (чеклист)

| Ключ | Файл | Статус |
|------|------|--------|
| Порядок чтения правил | `.cursor/rules/mandatory-rules-read-first.mdc` | ✅ |
| Auto-commit + VERSION | `.cursor/rules/save-on-code-change.mdc` | ✅ |
| Уточнения, типы коммитов, context | `.cursor/rules/project-context-template.mdc` | ✅ |
| Домен **этого** проекта | `.cursor/rules/project-domain.mdc` | ✅ |
| Выгрузка коммитов Excel | `.cursor/rules/commits-export-format.mdc` + `tools/export_commits_xlsx.py` | ✅ |
| Главный шаблон | `Шаблон_Сохранения.md` | ✅ |
| Точка входа агента | `AGENTS.md` | ✅ |
| Prefs пользователя | `context/КОНТЕКСТ_ПОЛЬЗОВАТЕЛЯ.md` | ✅ |
| Bootstrap нового проекта | `.cursor/rules/project-bootstrap.mdc` + `tools/bootstrap_project.py` | — (только в KB_Шаблон) |

---

## Ожидания к работе агента (задано пользователем)

0. **Всегда спрашивать**, если что-то **непонятно** — не писать код, пока не ясно, что нужно.
0а. **Нет конкретного исправления** — сначала вопросы; не «чинить вслепую».
1. **Сначала уточнения — потом выполнение.**
2. Уточняющих вопросов может быть **несколько**.
2а. **Новая фича** — сначала уточнить; варианты известны — **Ask Question** с **`allow_multiple: true`** у **каждого** вопроса.
2б. **Hard-rule 2026-05-26:** Ask Question — **всегда** `allow_multiple: true`; `false` **запрещён**.
2в. **Radio запрещён** — два последовательных вопроса, если нужен «ровно один» ответ.

### Жёстко: вопросы до кода

- **Нельзя** писать код **новой видимой функциональности** без **Ask Question** и ответа.
- Подробности — `context/КОНТЕКСТ_ПОЛЬЗОВАТЕЛЯ.md`, `.cursor/rules/project-domain.mdc`.

3. **Язык:** русский; английские термины — с кратким пояснением.
4. **Не нравится:** действия без уточнения при неочевидном намерении.
5. **После правок:** обновлять `context/*` автоматически при смене поведения.
6. **Минимальный дифф.**
7. **Git и VERSION:** после существенных правок — **VERSION + commit** (без push, если не просили).

---

## Сделано

- **v1.0.0** — инициализация из KB_Шаблон
"""


def _ideas_context_template(name: str) -> str:
    return f"""# Контекст идей — {name}

Только **нереализованное**. Сделанное → `КОНТЕКСТ_АГЕНТА.md`.

| § | Статус | Тема |
|---|--------|------|
| — | — | Пока пусто — добавляй по мере задач |
"""


def _reset_user_context(content: str, name: str) -> str:
    lines = content.splitlines()
    if lines:
        lines[0] = f"# Предпочтения пользователя — {name}"
    return "\n".join(lines) + "\n"


def _replace_in_files(
    root: Path,
    old_name: str,
    new_name: str,
    old_path: str,
    new_path: str,
    dry_run: bool,
) -> int:
    count = 0
    for path in _iter_text_files(root):
        if path.name == "ИНСТРУКЦИЯ_НОВЫЙ_ПРОЕКТ.md":
            continue
        original = _read_text(path)
        updated = original.replace(old_name, new_name)
        updated = updated.replace(old_path, new_path)
        updated = updated.replace(old_path.replace("\\", "/"), new_path.replace("\\", "/"))
        if updated != original:
            _write_text(path, updated, dry_run)
            count += 1
            print(f"  replace: {path.relative_to(root)}")
    return count


def _reset_context_files(root: Path, name: str, new_path: str, dry_run: bool) -> None:
    ctx = root / "context"
    agent = ctx / "КОНТЕКСТ_АГЕНТА.md"
    ideas = ctx / "КОНТЕКСТ_ИДЕЙ.md"
    user = ctx / "КОНТЕКСТ_ПОЛЬЗОВАТЕЛЯ.md"

    _write_text(agent, _agent_context_template(name, new_path), dry_run)
    _write_text(ideas, _ideas_context_template(name), dry_run)

    if user.is_file():
        _write_text(user, _reset_user_context(_read_text(user), name), dry_run)
    print("  reset: context/КОНТЕКСТ_*.md")


def _run_git(args: list[str], root: Path, dry_run: bool) -> subprocess.CompletedProcess[str]:
    if dry_run:
        print(f"  [dry-run] git {' '.join(args)}")
        return subprocess.CompletedProcess(args, 0, "", "")
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _git_bootstrap(root: Path, name: str, dry_run: bool) -> None:
    origin = _run_git(["remote", "get-url", "origin"], root, dry_run)
    if origin.returncode == 0 and origin.stdout.strip():
        print(f"  remove origin: {origin.stdout.strip()}")
        _run_git(["remote", "remove", "origin"], root, dry_run)

    _run_git(["add", "-A"], root, dry_run)

    msg_path = root / ".git_commit_msg.txt"
    commit_body = f"v1.0.0: база - инициализация {name}\n\n1. Проект из KB_Шаблон\n2. VERSION 1.0.0\n3. Context сброшен\n"
    if dry_run:
        print(f"  [dry-run] commit message:\n{commit_body}")
    else:
        msg_path.write_text(commit_body, encoding="utf-8")
        result = _run_git(["commit", "-F", ".git_commit_msg.txt"], root, dry_run)
        if result.returncode != 0:
            print(result.stderr or result.stdout, file=sys.stderr)
            raise SystemExit(f"git commit failed (code {result.returncode})")


def _gh_create_repo(root: Path, name: str, public: bool, dry_run: bool) -> None:
    flag = "--public" if public else "--private"
    cmd = [
        "gh",
        "repo",
        "create",
        name,
        flag,
        "--source=.",
        "--remote=origin",
        "--push",
    ]
    if dry_run:
        print(f"  [dry-run] {' '.join(cmd)}")
        return
    result = subprocess.run(cmd, cwd=root, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        raise SystemExit(f"gh repo create failed (code {result.returncode})")
    print(result.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap нового проекта из KB_Шаблон")
    parser.add_argument("--name", required=True, help="Имя нового проекта (например KB_MyApp)")
    parser.add_argument("--path", help="Новый абсолютный путь (по умолчанию — cwd)")
    parser.add_argument("--github-public", action="store_true", help="Создать public repo на GitHub")
    parser.add_argument("--github-private", action="store_true", help="Создать private repo на GitHub")
    parser.add_argument("--dry-run", action="store_true", help="Только показать действия, без записи")
    args = parser.parse_args()

    root = Path.cwd().resolve()
    new_name = args.name.strip()
    new_path = str(Path(args.path).resolve()) if args.path else str(root)

    if not re.match(r"^[A-Za-z0-9_-]+$", new_name):
        print(
            "Ошибка: имя проекта должно содержать только латиницу, цифры, _ и - "
            "(GitHub remote).",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if not _is_template_marker(root) and os.environ.get("BOOTSTRAP_OK") != "1":
        print(
            "Ошибка: нет маркера шаблона (VERSION + KB_Шаблон в AGENTS.md). "
            "Bootstrap только для копий шаблона.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if _is_master_template(root, new_name):
        print(
            "Ошибка: отказ — это материнский KB_Шаблон. Bootstrap только для копий. "
            "(override: BOOTSTRAP_OK=1)",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if args.github_public and args.github_private:
        print("Ошибка: укажите только один из --github-public / --github-private", file=sys.stderr)
        raise SystemExit(1)

    old_path = _detect_old_path(root)
    print(f"Bootstrap: {TEMPLATE_NAME} -> {new_name}")
    print(f"  cwd:      {root}")
    print(f"  old path: {old_path}")
    print(f"  new path: {new_path}")
    if args.dry_run:
        print("  mode:     DRY-RUN")

    _write_text(root / "VERSION", "1.0.0\n", args.dry_run)
    print("  VERSION -> 1.0.0")

    replaced = _replace_in_files(root, TEMPLATE_NAME, new_name, old_path, new_path, args.dry_run)
    print(f"  replaced in {replaced} file(s)")

    _reset_context_files(root, new_name, new_path, args.dry_run)

    if (root / ".git").is_dir():
        _git_bootstrap(root, new_name, args.dry_run)
    else:
        print("  warn: .git не найден — пропуск git commit")

    if args.github_public or args.github_private:
        _gh_create_repo(root, new_name, args.github_public, args.dry_run)

    print("\nГотово.")
    if root.name == TEMPLATE_NAME or str(root) != new_path:
        print(
            f"\n[!] Переименуй папку на диске в '{new_name}' и открой ее в Cursor "
            f"(текущий cwd: {root})."
        )


if __name__ == "__main__":
    main()
