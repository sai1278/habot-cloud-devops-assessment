# CI/CD Execution & Evidence Verification Guide

This directory contains real, machine-generated terminal execution outputs validating all security, data contract, Terraform, and Python gates.

Per the **Non-Fabrication & Zero-Guessing Engineering Rule**, screenshots of remote GitHub Actions runs are not artificially fabricated. Below are the verified execution logs and instructions for capturing remote GitHub UI screenshots.

---

## 1. Verified Local Evidence Files

| Evidence File | Verification Scope | Status | Result Summary |
|---|---|---|---|
| [`terraform-validation.txt`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/evidence/terraform-validation.txt) | `terraform fmt -check`, `terraform validate`, & format failure demo | **PASS / VERIFIED** | Valid HCL syntax; caught unformatted fixture |
| [`pytest-results.txt`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/evidence/pytest-results.txt) | 25 unit tests for DRF serializer & DCYN binary gates | **PASS / VERIFIED** | 25 passed in 0.24s |
| [`schema-validation.txt`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/evidence/schema-validation.txt) | Canonical Draft 2020-12 JSON Schema validation | **PASS / VERIFIED** | Examples pass; invalid fixture caught 5 violations |
| [`secret-scan-failure.txt`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/evidence/secret-scan-failure.txt) | Poka-Yoke Secret Scanner on `tests/fixtures/malicious_secret.py` | **FAIL / VERIFIED** | Gate triggered exit code 1; pipeline halted |
| [`secret-scan-success.txt`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/docs/evidence/secret-scan-success.txt) | Poka-Yoke Secret Scanner on clean repository | **PASS / VERIFIED** | 0 secret alerts; exit code 0 |

---

## 2. Remote GitHub Actions UI Screenshot Procedure

To capture `ci-failure.png` and `ci-success.png` from a live GitHub repository:

### Generating `ci-failure.png` (Fail-Closed Demonstration)
1. Commit `tests/fixtures/malicious_secret.py` to a branch:
   ```bash
   git checkout -b test/secret-failure-demo
   git add tests/fixtures/malicious_secret.py
   git commit -m "test: demonstrate secret scanner failure gate"
   git push origin test/secret-failure-demo
   ```
2. Open a Pull Request targeting `main`.
3. The `.github/workflows/security.yml` workflow will trigger.
4. **Expected Result**: The Gitleaks / Secret Detection step fails with red status `X`. The workflow halts with exit code 1, preventing merge.
5. Capture a screenshot of the GitHub Actions run and save as `docs/evidence/ci-failure.png`.

### Generating `ci-success.png` (Clean Verification)
1. Delete or remove the mock secret branch:
   ```bash
   git checkout main
   git push origin main
   ```
2. All 3 workflows (`pull-request.yml`, `security.yml`, `terraform.yml`) execute:
   - Ruff linting: Green checkmark
   - JSON Schema contract validation: Green checkmark
   - Pytest suite (22 tests): Green checkmark
   - Terraform fmt, init, validate: Green checkmark
   - Gitleaks secret scan: Green checkmark
   - Trivy IaC scan: Green checkmark
3. Capture a screenshot of the green GitHub Actions summary tab and save as `docs/evidence/ci-success.png`.
