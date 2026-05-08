#!/usr/bin/env python3
"""Верификатор сгенерированного проекта через Docker.

Использование:
    python verify.py projects/<slug>

Шаги:
    1. docker build -t <slug> <project_dir>
    2. docker run -d -p 8000:8000 --name <slug> <slug>  +  ожидание старта
    3. GET http://localhost:8000/health
    4. docker run --rm <slug> pytest

Выводит PASS или FAIL с деталями каждого шага.
"""

from __future__ import annotations

import sys
import time
import subprocess
from pathlib import Path

import requests


def run_cmd(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Запускает команду и возвращает результат."""
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def step_ok(label: str) -> None:
    print(f"[OK] {label}")


def step_fail(label: str, details: str = "") -> None:
    print(f"[FAIL] {label}")
    if details:
        print(f"       {details.strip()}")


def _docker_name(name: str) -> str:
    """Преобразует имя папки в валидное имя Docker-образа (ASCII, lowercase)."""
    import unicodedata
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    sanitized = "".join(c if c.isalnum() or c in "-_." else "-" for c in ascii_name)
    return sanitized.lower().strip("-_") or "project"


def verify(project_dir: Path) -> bool:
    slug = _docker_name(project_dir.name)
    container_name = slug

    # --- Шаг 1: docker build ---
    result = run_cmd(["docker", "build", "-t", slug, str(project_dir)])
    if result.returncode != 0:
        step_fail("docker build", result.stderr or result.stdout)
        return False
    step_ok(f"docker build -t {slug}")

    # --- Шаг 2: docker run + ожидание старта ---
    run_cmd(["docker", "rm", "-f", container_name])  # убрать старый если есть
    result = run_cmd([
        "docker", "run", "-d",
        "-p", "8000:8000",
        "--name", container_name,
        slug,
    ])
    if result.returncode != 0:
        step_fail("docker run", result.stderr or result.stdout)
        return False

    # Retry-loop: ждём до 15 секунд (3 попытки по 5 сек)
    started = False
    for attempt in range(1, 4):
        time.sleep(5)
        try:
            resp = requests.get("http://localhost:8000/health", timeout=3)
            if resp.status_code < 500:
                started = True
                break
        except requests.exceptions.ConnectionError:
            pass
        print(f"  (ожидание старта, попытка {attempt}/3...)")

    if not started:
        step_fail("docker run — сервер не запустился за 15 секунд")
        return False
    step_ok("docker run -d -p 8000:8000")

    # --- Шаг 3: GET /health ---
    try:
        resp = requests.get("http://localhost:8000/health", timeout=5)
        if resp.status_code == 200:
            step_ok(f"GET /health → {resp.status_code} {resp.text[:80]}")
        else:
            step_fail(f"GET /health → {resp.status_code}", resp.text[:200])
            return False
    except requests.exceptions.RequestException as exc:
        step_fail("GET /health", str(exc))
        return False

    # --- Шаг 4: pytest внутри Docker ---
    result = run_cmd(["docker", "run", "--rm", slug, "python", "-m", "pytest", "-v"])
    if result.returncode == 0:
        step_ok("docker run pytest")
        if result.stdout:
            lines = result.stdout.strip().splitlines()
            for line in lines[-5:]:
                print(f"  {line}")
    else:
        step_fail("docker run pytest", (result.stdout + result.stderr)[:500])
        return False

    return True


def cleanup(slug: str) -> None:
    """Остановить и удалить контейнер."""
    run_cmd(["docker", "stop", slug])
    run_cmd(["docker", "rm", slug])


def main() -> None:
    if len(sys.argv) != 2:
        print("Использование: python verify.py projects/<slug>")
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    if not project_dir.exists():
        print(f"[FAIL] Папка не найдена: {project_dir}")
        sys.exit(1)

    slug = project_dir.name
    print(f"\n=== Верификация проекта: {slug} ===\n")

    passed = False
    try:
        passed = verify(project_dir)
    finally:
        cleanup(slug)

    print()
    if passed:
        print("PASS")
        sys.exit(0)
    else:
        print("FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
