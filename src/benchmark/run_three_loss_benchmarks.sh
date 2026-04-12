#!/bin/bash
# =============================================================
# Wrapper Linux/macOS para el runner multiplataforma.
#
# Uso:
#   bash src/benchmark/run_three_loss_benchmarks.sh
# =============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

if command -v python >/dev/null 2>&1; then
	python src/benchmark/run_three_loss_benchmarks.py
elif command -v python3 >/dev/null 2>&1; then
	python3 src/benchmark/run_three_loss_benchmarks.py
else
	echo "Error: no se encontro python ni python3 en PATH." >&2
	exit 1
fi
