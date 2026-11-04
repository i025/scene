#!/usr/bin/env bash
set -euo pipefail
KERNEL_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DIR=__SERVER_USER_ROOT__/projects/BlenderWorld/runtime/blender-4.2.10-linux-x64/4.2/scripts/addons_core/cycles/source
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
/usr/local/cuda-12.2/bin/nvcc -m64 --cubin --gpu-architecture=sm_80 --use_fast_math -DNVCC -I"$SOURCE_DIR" "$SOURCE_DIR/kernel/device/cuda/kernel.cu" -o "$KERNEL_DIR/lib/kernel_sm_80.cubin" > "$KERNEL_DIR/compile.stdout.log" 2> "$KERNEL_DIR/compile.stderr.log"
python3 "$KERNEL_DIR/prepare.py"
