#!/usr/bin/env bash
# ==============================================================================
# Habot Connect — Secret Detection Script (POSIX Shell / CI Wrapper)
#
# Runs python-based secret detection and/or gitleaks if installed.
# Fails closed (exit 1) if any credentials or private keys are discovered.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Running Secret Detection Gate ==="

if command -v gitleaks &> /dev/null; then
    echo "[INFO] Running Gitleaks detect..."
    gitleaks detect --source="${REPO_ROOT}" --verbose --redact
else
    echo "[INFO] Gitleaks binary not present in PATH; falling back to internal scanner..."
    python3 "${REPO_ROOT}/scripts/detect_secrets.py" --target "${REPO_ROOT}" --exclude "${REPO_ROOT}/tests/fixtures/malicious_secret.py"
fi

echo "[SUCCESS] Secret detection passed."
