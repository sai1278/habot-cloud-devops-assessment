# CI/CD Gate Enforcement & GitHub Repository Protection Audit

This document audits the mechanics of continuous integration, status check reporting, and the architectural boundary between **workflow job execution** and **repository merge enforcement**.

---

## 1. Critical Distinction: CI Failure vs. Merge Protection

> [!WARNING]
> **Staff Engineer Review Finding**:
> A GitHub Actions workflow returning a non-zero exit code (failure) does **NOT** automatically block a developer from merging a Pull Request or pushing directly to `main` unless **GitHub Branch Protection Rules** are explicitly configured in the remote repository settings.
> 
> **Status**: `NOT VERIFIED — REPOSITORY SETTINGS REQUIRE GITHUB WEB UI INSPECTION`.
> Local Git repositories do not store remote GitHub branch protection rules, required reviewer policies, or status check gating.

```text
Local / Remote Push
        |
        v
GitHub Actions Workflow Executes
        |
   FAIL / PASS
   /        \
  v          v
FAIL       PASS
  |          |
  v          v
GitHub Status Check Reported (e.g. "Pull Request Gates / python-validation" = failure)
        |
        |  MISSING BRANCH PROTECTION? ---> Direct push / force merge STILL POSSIBLE!
        |
        +-- WITH BRANCH PROTECTION RULE (Enforced):
                 |
                 +---> "Require status checks to pass before merging"
                 +---> "Require branches to be up to date before merging"
                 +---> "Do not allow bypassing the above settings"
                 |
                 v
           MERGE PHYSICALLY BLOCKED
```

---

## 2. Mandatory Pipeline Gate Inventory

The repository defines three GitHub Actions workflows in [`.github/workflows/`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/.github/workflows/):

| Gate ID | Pipeline Name | Tool / Command | Inspection Scope | Fail-Closed Exit Condition | Blocks Merge? (With Branch Protection) |
|---|---|---|---|---|---|
| **GATE-01** | `pull-request.yml` | `ruff check .` | Python code style, unused imports, PEP 8 compliance | Non-zero exit code on lint violation | **YES** |
| **GATE-02** | `pull-request.yml` | `python scripts/validate_schema.py` | Validates payloads against Draft 2020-12 contract | Non-zero exit code on schema mismatch | **YES** |
| **GATE-03** | `pull-request.yml` | `pytest -v --tb=short` | 25 unit tests (DRF serializer, DCYN, anti-coercion) | Non-zero exit code on test failure | **YES** |
| **GATE-04** | `pull-request.yml` | `terraform fmt -check -recursive` | Canonical HashiCorp HCL style | Non-zero exit code on unformatted HCL | **YES** |
| **GATE-05** | `pull-request.yml` | `terraform init -backend=false` | Provider schema & plugin resolution | Non-zero exit code on plugin failure | **YES** |
| **GATE-06** | `pull-request.yml` | `terraform validate` | Syntax, variable typing, and resource arguments | Non-zero exit code on syntax/type error | **YES** |
| **GATE-07** | `pull-request.yml` | `tflint` | Deep Terraform linting & deprecated argument checks | Non-zero exit code on linter issue | **YES** |
| **GATE-08** | `security.yml` | `gitleaks` / `detect_secrets.py` | High-entropy credentials, private keys, API tokens | Non-zero exit code on secret detection | **YES** |
| **GATE-09** | `security.yml` | `trivy` IaC scanner | Misconfigurations, open buckets, excessive IAM | Non-zero exit code on HIGH/CRITICAL | **YES** |
| **GATE-10** | `terraform.yml` | `terraform plan` (via WIF) | Cloud resource delta & state planning | Non-zero exit code on plan error | **YES** |

**Total Count of Automated Gates**: Exactly **10 distinct automated checks**.

---

## 3. Required GitHub Repository Settings Checklist

To ensure that the CI/CD pipeline physically prevents insecure or invalid code from entering `main`, repository administrators must configure the following settings in GitHub (`Settings > Branches > Branch protection rules` for `main`):

- [ ] **Require a pull request before merging**
  - Require approvals: minimum 1 peer review.
  - Dismiss stale pull request approvals when new commits are pushed.
- [ ] **Require status checks to pass before merging**
  - Check: `Python Linting, Tests & Schema Contract`
  - Check: `Terraform Formatting, Init & Validation`
  - Check: `Gate: Secret Detection (Gitleaks)`
  - Check: `Gate: IaC Security & Misconfiguration Scan (Trivy)`
- [ ] **Require branches to be up to date before merging**
- [ ] **Do not allow bypassing the above settings** (Enforce for administrators).
- [ ] **Block force pushes** and **Block branch deletion**.
