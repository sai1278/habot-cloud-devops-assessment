#!/usr/bin/env bash
# ==============================================================================
# Habot Connect — Terraform Validation Script (POSIX Shell / CI Wrapper)
#
# Validates formatting, syntax, and static configuration without requiring cloud credentials.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="$(cd "${SCRIPT_DIR}/../terraform" && pwd)"

echo "=== 1. Checking Terraform Formatting ==="
terraform -chdir="${TF_DIR}" fmt -check -recursive

echo "=== 2. Initializing Terraform (Backend-disabled) ==="
terraform -chdir="${TF_DIR}" init -backend=false

echo "=== 3. Validating Terraform Syntax and Types ==="
terraform -chdir="${TF_DIR}" validate

if command -v tflint &> /dev/null; then
    echo "=== 4. Running TFLint ==="
    tflint --chdir="${TF_DIR}"
fi

echo "[SUCCESS] All Terraform validation gates passed."
