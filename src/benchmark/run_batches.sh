#!/bin/bash
# =============================================================
# Ejecuta el benchmark completo en batches separados.
# Cada batch corre como un proceso independiente → al terminar,
# el OS libera TODA la RAM de Julia/PySR.
#
# Uso:
#   cd src/benchmark
#   bash run_batches.sh
#
# Al final combina todos los resultados en un reporte unificado.
# =============================================================

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BASE_DIR="../benchmark_results/batches_${TIMESTAMP}"
mkdir -p "$BASE_DIR"

echo "============================================="
echo "  BENCHMARK POR BATCHES"
echo "  Resultados en: $BASE_DIR"
echo "============================================="

# ── Batch 1: Lineales (casos 0-9, 10 casos) ──
echo ""
echo ">>> BATCH 1/6: Lineales (casos 1-10)"
python run_benchmark.py --from-index 0 --to-index 10 \
    -o "${BASE_DIR}/batch_1_linear"

# ── Batch 2: Cuadráticas parte 1 (casos 10-16, 7 casos) ──
echo ""
echo ">>> BATCH 2/6: Cuadráticas 1-param (casos 11-17)"
python run_benchmark.py --from-index 10 --to-index 17 \
    -o "${BASE_DIR}/batch_2_quadratic_1"

# ── Batch 3: Cuadráticas parte 2 (casos 17-23, 7 casos) ──
echo ""
echo ">>> BATCH 3/6: Cuadráticas multi-param (casos 18-24)"
python run_benchmark.py --from-index 17 --to-index 24 \
    -o "${BASE_DIR}/batch_3_quadratic_2"

# ── Batch 4: Cúbicas (casos 24-29, 6 casos) ──
echo ""
echo ">>> BATCH 4/6: Cúbicas (casos 25-30)"
python run_benchmark.py --from-index 24 --to-index 30 \
    -o "${BASE_DIR}/batch_4_cubic"

# ── Batch 5: Cuárticas + quíntica (casos 30-34, 5 casos) ──
echo ""
echo ">>> BATCH 5/6: Cuárticas + quíntica (casos 31-35)"
python run_benchmark.py --from-index 30 --to-index 35 \
    -o "${BASE_DIR}/batch_5_quartic"

# ── Batch 6: Especiales (casos 35-42, 8 casos) ──
echo ""
echo ">>> BATCH 6/6: Especiales (casos 36-43)"
python run_benchmark.py --from-index 35 --to-index 43 \
    -o "${BASE_DIR}/batch_6_special"

# ── Combinar todos los resultados ──
echo ""
echo "============================================="
echo "  COMBINANDO RESULTADOS..."
echo "============================================="
python run_benchmark.py --merge "${BASE_DIR}"/batch_* \
    -o "${BASE_DIR}/COMBINED"

echo ""
echo "============================================="
echo "  ¡BENCHMARK COMPLETO!"
echo "  Reporte final: ${BASE_DIR}/COMBINED/report.txt"
echo "============================================="
