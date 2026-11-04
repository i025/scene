#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export CUDA_VISIBLE_DEVICES=''
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export PYTHONDONTWRITEBYTECODE=1
export MPLCONFIGDIR="$SCRIPT_DIR/../../work/matplotlib"
PYTHON_BIN=__SCENEEVOLVE_REPRO__/work/.venv/bin/python
case "${1:-resume}" in
  smoke) "$PYTHON_BIN" "$SCRIPT_DIR/runner.py" smoke ;;
  pilot) "$PYTHON_BIN" "$SCRIPT_DIR/pilot.py" ;;
  evaluate|report) "$PYTHON_BIN" "$SCRIPT_DIR/analyze.py"; "$PYTHON_BIN" "$SCRIPT_DIR/report.py" --root "$SCRIPT_DIR" ;;
  resume)
    "$PYTHON_BIN" "$SCRIPT_DIR/runner.py" smoke
    "$PYTHON_BIN" "$SCRIPT_DIR/pilot.py"
    "$PYTHON_BIN" "$SCRIPT_DIR/supplement.py"
    "$PYTHON_BIN" "$SCRIPT_DIR/extras.py"
    "$PYTHON_BIN" "$SCRIPT_DIR/replay.py"
    "$PYTHON_BIN" "$SCRIPT_DIR/external.py"
    "$PYTHON_BIN" "$SCRIPT_DIR/analyze.py"
    "$PYTHON_BIN" "$SCRIPT_DIR/report.py" --root "$SCRIPT_DIR"
    ;;
  *) echo 'Usage: bash run.sh smoke|pilot|evaluate|report|resume' >&2; exit 2 ;;
esac
