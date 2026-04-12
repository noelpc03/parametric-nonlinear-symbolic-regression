#!/usr/bin/env python3
"""
Runner multiplataforma para benchmark completo en 3 pérdidas:
  - MSE
  - Match Count
  - Sigmoid

Salidas:
  - src/benchmark_results/test_mse
  - src/benchmark_results/test_match_count
  - src/benchmark_results/test_sigmoid

Preserva src/config.py restaurándolo al finalizar.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def _replace_once(text: str, pattern: str, replacement: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1)
    if count == 0:
        raise RuntimeError(f"No se pudo aplicar patrón: {pattern}")
    return updated


def update_config(config_path: Path, use_sigmoid: bool, use_match_count: bool) -> None:
    content = config_path.read_text(encoding="utf-8")

    content = _replace_once(
        content,
        r"USE_SIGMOID_LOSS\s*=\s*(True|False)",
        f"USE_SIGMOID_LOSS = {str(use_sigmoid)}",
    )
    content = _replace_once(
        content,
        r"USE_MATCH_COUNT_LOSS\s*=\s*(True|False)",
        f"USE_MATCH_COUNT_LOSS = {str(use_match_count)}",
    )
    content = _replace_once(
        content,
        r"SR_INPUT_MODE\s*=\s*['\"][^'\"]+['\"]",
        "SR_INPUT_MODE = 'combined'",
    )

    config_path.write_text(content, encoding="utf-8")


def run_mode(repo_root: Path, config_path: Path, mode: str, use_sigmoid: bool, use_match_count: bool) -> None:
    output_dir = f"src/benchmark_results/test_{mode}"

    print("\n" + "=" * 61)
    print(f"Ejecutando modo: {mode}")
    print(f"Salida: {output_dir}")
    print("=" * 61)

    update_config(config_path, use_sigmoid=use_sigmoid, use_match_count=use_match_count)

    cmd = [
        sys.executable,
        "src/benchmark/run_benchmark.py",
        "--output",
        output_dir,
    ]
    subprocess.run(cmd, cwd=repo_root, check=True)


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    config_path = repo_root / "src" / "config.py"
    backup_path = repo_root / "src" / "config.py.bak_3loss_tests"

    if not config_path.exists():
        print(f"Error: no se encontró {config_path}", file=sys.stderr)
        return 1

    if backup_path.exists():
        print(f"Error: ya existe {backup_path}. Revísalo antes de continuar.", file=sys.stderr)
        return 1

    backup_path.write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Backup creado: {backup_path.relative_to(repo_root)}")

    try:
        run_mode(repo_root, config_path, mode="mse", use_sigmoid=False, use_match_count=False)
        run_mode(repo_root, config_path, mode="match_count", use_sigmoid=False, use_match_count=True)
        run_mode(repo_root, config_path, mode="sigmoid", use_sigmoid=True, use_match_count=False)
    finally:
        if backup_path.exists():
            config_path.write_text(backup_path.read_text(encoding="utf-8"), encoding="utf-8")
            backup_path.unlink()
            print(f"Config restaurada: {config_path.relative_to(repo_root)}")

    print("\n" + "=" * 61)
    print("Benchmark 3 pérdidas finalizado")
    print("Resultados generados en src/benchmark_results/test_*")
    print("=" * 61)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
