from __future__ import annotations

import re
from pathlib import Path

_BLOCK_RE = re.compile(r"```[^\n]*\n# path: ([^\n]+)\n(.*?)```", re.DOTALL)


def extract_files(content: str, base_dir: Path) -> list[Path]:
    """Парсит code-блоки с маркером # path: и создаёт файлы на диске.

    Формат маркера (первая строка внутри блока):
        # path: src/main.py

    Возвращает список путей созданных файлов.
    """
    created: list[Path] = []
    for match in _BLOCK_RE.finditer(content):
        rel_path = match.group(1).strip()
        file_content = match.group(2)
        target = base_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(file_content, encoding="utf-8")
        created.append(target)
    return created
