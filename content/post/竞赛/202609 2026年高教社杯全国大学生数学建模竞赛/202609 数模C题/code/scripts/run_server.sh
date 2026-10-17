#!/usr/bin/env bash
set -Eeuo pipefail

# ============================================================
# C题 Linux服务器统一启动脚本
#
# 用法：
#   bash scripts/run_server.sh check
#   bash scripts/run_server.sh q1
#   bash scripts/run_server.sh q2
#   bash scripts/run_server.sh q3
#   bash scripts/run_server.sh q4-2
#   bash scripts/run_server.sh q4-3
#   bash scripts/run_server.sh all
#
# 可追加run.py参数：
#   bash scripts/run_server.sh all --reuse-cache
#   bash scripts/run_server.sh q2 --no-figures
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_DIR}"

STAGE="${1:-all}"
if [[ $# -gt 0 ]]; then
    shift
fi

PYTHON_BIN="${PYTHON_BIN:-python3}"

# 如果存在项目虚拟环境，则自动激活。
if [[ -f "${PROJECT_DIR}/.venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "${PROJECT_DIR}/.venv/bin/activate"
fi

export PYTHONPATH="${PROJECT_DIR}/src:${PYTHONPATH:-}"
export MPLBACKEND="Agg"
export PYTHONUNBUFFERED="1"
export LANG="${LANG:-C.UTF-8}"
export LC_ALL="${LC_ALL:-C.UTF-8}"

mkdir -p \
    "${PROJECT_DIR}/output/results" \
    "${PROJECT_DIR}/output/figures" \
    "${PROJECT_DIR}/output/tables" \
    "${PROJECT_DIR}/output/logs" \
    "${PROJECT_DIR}/models"

TIMESTAMP="$(date +'%Y%m%d_%H%M%S')"
LOG_FILE="${PROJECT_DIR}/output/logs/run_${STAGE}_${TIMESTAMP}.log"

exec > >(tee -a "${LOG_FILE}") 2>&1

echo "============================================================"
echo "C题 server runner"
echo "Project : ${PROJECT_DIR}"
echo "Stage   : ${STAGE}"
echo "Python  : ${PYTHON_BIN}"
echo "Log     : ${LOG_FILE}"
echo "Start   : $(date)"
echo "============================================================"

case "${STAGE}" in
    check|figures)
        "${PYTHON_BIN}" scripts/check_env.py
        ;;
    q1|q2|q3|q4-2|q4-3|all)
        "${PYTHON_BIN}" scripts/check_env.py --require-gurobi
        ;;
    *)
        echo "Unknown stage: ${STAGE}"
        echo "Allowed: check q1 q2 q3 q4-2 q4-3 figures all"
        exit 2
        ;;
esac

echo "[SERVER] Running unit tests..."
"${PYTHON_BIN}" -m pytest -q tests

echo "[SERVER] Starting pipeline..."
"${PYTHON_BIN}" run.py --stage "${STAGE}" "$@"

echo "============================================================"
echo "Finished: $(date)"
echo "Results : ${PROJECT_DIR}/output/results"
echo "Figures : ${PROJECT_DIR}/output/figures"
echo "Tables  : ${PROJECT_DIR}/output/tables"
echo "Log     : ${LOG_FILE}"
echo "============================================================"
