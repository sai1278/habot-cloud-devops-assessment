#!/usr/bin/env bash
# ==============================================================================
# Habot Connect — Unified Local Validation Suite (POSIX Bash)
#
# Authoritative single entry point for Linux/macOS reproducibility.
# Executes all mandatory gates and halts immediately (fail-closed) on error.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "======================================================================"
echo "  HABOT CONNECT: UNIFIED QUALITY & SECURITY VALIDATION SUITE          "
echo "======================================================================"

PYTHON_BIN="python3"
if [ -f "${REPO_ROOT}/.venv/bin/python" ]; then
    PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
fi

PYTEST_BIN="pytest"
if [ -f "${REPO_ROOT}/.venv/bin/pytest" ]; then
    PYTEST_BIN="${REPO_ROOT}/.venv/bin/pytest"
fi

RUFF_BIN="ruff"
if [ -f "${REPO_ROOT}/.venv/bin/ruff" ]; then
    RUFF_BIN="${REPO_ROOT}/.venv/bin/ruff"
fi

echo -e "\n--> Gate 1: Checking Terraform Formatting..."
terraform -chdir="${REPO_ROOT}/terraform" fmt -check -recursive

echo -e "\n--> Gate 2: Validating Terraform Configuration..."
terraform -chdir="${REPO_ROOT}/terraform" validate

if command -v tflint &> /dev/null; then
    echo -e "\n--> Gate 3: Running TFLint..."
    tflint --chdir="${REPO_ROOT}/terraform"
else
    echo -e "\n--> [NOTICE] TFLint not installed on PATH; validated in GitHub Actions CI."
fi

echo -e "\n--> Gate 4A: Poka-Yoke Secret Scanner Negative Test..."
if "${PYTHON_BIN}" "${REPO_ROOT}/scripts/detect_secrets.py" --target "${REPO_ROOT}/tests/fixtures/malicious_secret.py" > /dev/null 2>&1; then
    echo "[ERROR] Secret scanner failed to catch mock credential fixture!"
    exit 1
else
    echo "[PASSED] Mock secret caught with non-zero exit code."
fi

echo -e "\n--> Gate 4B: Poka-Yoke Secret Scanner Clean Repository Gate..."
"${PYTHON_BIN}" "${REPO_ROOT}/scripts/detect_secrets.py" --exclude "${REPO_ROOT}/tests/fixtures/malicious_secret.py"

echo -e "\n--> Gate 5: Ruff Python Linting..."
"${RUFF_BIN}" check "${REPO_ROOT}"

echo -e "\n--> Gate 6: Canonical JSON Schema Contract Validation..."
"${PYTHON_BIN}" "${REPO_ROOT}/scripts/validate_schema.py"

echo -e "\n--> Gate 7: DRF & DCYN Pytest Suite..."
"${PYTEST_BIN}" -v --tb=short "${REPO_ROOT}/app/onboarding/tests"

echo -e "\n======================================================================"
echo "  ALL LOCAL REPRODUCIBILITY & SECURITY GATES PASSED (100% SUCCESS)    "
echo "======================================================================"
exit 0
