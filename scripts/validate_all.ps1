# ==============================================================================
# Habot Connect — Unified Local Validation Suite (PowerShell / Windows)
#
# Authoritative single entry point for local reproducibility and pre-commit checks.
# Executes all mandatory gates and halts immediately (fail-closed) on any error.
# ==============================================================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  HABOT CONNECT: UNIFIED QUALITY & SECURITY VALIDATION SUITE          " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# Determine Python and Terraform binaries
$PythonExe = if (Test-Path "$RepoRoot\.venv\Scripts\python.exe") { "$RepoRoot\.venv\Scripts\python.exe" } else { "python" }
$PytestExe = if (Test-Path "$RepoRoot\.venv\Scripts\pytest.exe") { "$RepoRoot\.venv\Scripts\pytest.exe" } else { "pytest" }
$RuffExe = if (Test-Path "$RepoRoot\.venv\Scripts\ruff.exe") { "$RepoRoot\.venv\Scripts\ruff.exe" } else { "ruff" }
$TerraformExe = if (Test-Path "$RepoRoot\tools\terraform.exe") { "$RepoRoot\tools\terraform.exe" } else { "terraform" }

function Run-Gate {
    param(
        [string]$GateName,
        [scriptblock]$Command
    )
    Write-Host "`n--> Executing: $GateName" -ForegroundColor Yellow
    try {
        & $Command
        if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
            throw "Command exited with non-zero exit code $LASTEXITCODE"
        }
        Write-Host "[PASSED] $GateName" -ForegroundColor Green
    }
    catch {
        Write-Host "[FAILED] ${GateName}: $_" -ForegroundColor Red
        Write-Host "`n[HALT] Fail-Closed policy triggered. Pipeline execution aborted." -ForegroundColor Red
        exit 1
    }
}

# Gate 1: Terraform Formatting Check
Run-Gate "Gate 1: Terraform Format Check (Canonical HCL)" {
    & $TerraformExe fmt -check -recursive "$RepoRoot\terraform"
}

# Gate 2: Terraform Validation
Run-Gate "Gate 2: Terraform Syntax & Type Validation" {
    & $TerraformExe -chdir="$RepoRoot\terraform" validate
}

# Gate 3: TFLint (Optional local tool, required in CI)
if (Get-Command tflint -ErrorAction SilentlyContinue) {
    Run-Gate "Gate 3: TFLint Deep Analysis" {
        tflint --chdir="$RepoRoot\terraform"
    }
} else {
    Write-Host "`n--> [NOTICE] TFLint not found on PATH; verified in GitHub Actions CI." -ForegroundColor DarkGray
}

# Gate 4: Secret Scanner Demonstration (Controlled Negative Test)
Run-Gate "Gate 4A: Poka-Yoke Secret Scanner Negative Test (Must Catch Mock Secret)" {
    $scanOutput = & $PythonExe "$RepoRoot\scripts\detect_secrets.py" --target "$RepoRoot\tests\fixtures\malicious_secret.py" 2>&1
    if ($LASTEXITCODE -eq 0) {
        throw "Secret scanner failed to catch mock credential fixture!"
    }
    Write-Host "  (Correctly caught synthetic secret with non-zero exit code: $LASTEXITCODE)" -ForegroundColor DarkGray
    $global:LASTEXITCODE = 0
}

# Gate 5: Secret Scanner (Clean Repository Check)
Run-Gate "Gate 4B: Poka-Yoke Secret Scanner Clean Repository Gate" {
    & $PythonExe "$RepoRoot\scripts\detect_secrets.py" --exclude "$RepoRoot\tests\fixtures\malicious_secret.py"
}

# Gate 6: Ruff Python Linting
Run-Gate "Gate 5: Ruff Python Linting" {
    & $RuffExe check "$RepoRoot"
}

# Gate 7: JSON Schema Canonical Contract Check
Run-Gate "Gate 6: Canonical JSON Schema Contract Validation" {
    & $PythonExe "$RepoRoot\scripts\validate_schema.py"
}

# Gate 8: Pytest Unit Test Suite (25 tests)
Run-Gate "Gate 7: DRF & DCYN Pytest Unit Test Suite" {
    & $PytestExe -v --tb=short "$RepoRoot\app\onboarding\tests"
}

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host "  ALL LOCAL REPRODUCIBILITY & SECURITY GATES PASSED (100% SUCCESS)    " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
exit 0
