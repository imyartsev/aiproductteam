#!/usr/bin/env python3
"""Точка входа AI Product Team."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from orchestrator.pipeline import run_pipeline, save_results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Product Team — автономная команда ИИ-агентов"
    )
    parser.add_argument("task", nargs="?", help="Описание задачи")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Запустить без реальных вызовов Claude API",
    )
    parser.add_argument(
        "--output",
        metavar="DIR",
        help="Папка для сохранения результатов (по умолчанию: ./projects)",
    )
    args = parser.parse_args()

    if not args.task:
        parser.print_help()
        sys.exit(1)

    state = run_pipeline(args.task, dry_run=args.dry_run)
    save_results(state, output_dir=args.output)


if __name__ == "__main__":
    main()
