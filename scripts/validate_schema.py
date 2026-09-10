#!/usr/bin/env python3
"""Canonical JSON Schema validation utility for Habot Connect.

Validates payload files against schemas/student_onboarding.schema.json.
Provides fail-closed exit codes for CI/CD integration.
"""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


def load_json(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_file(schema: dict, file_path: Path, expect_valid: bool = True) -> bool:
    validator = Draft202012Validator(schema)
    instance = load_json(file_path)

    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    if errors:
        if expect_valid:
            print(f"[FAIL] Contract violation in {file_path.name}:")
            for err in errors:
                path = ".".join([str(p) for p in err.path]) or "root"
                print(f"  - Field '{path}': {err.message}")
            return False
        else:
            print(f"[PASS] Expected rejection confirmed for {file_path.name}:")
            for err in errors:
                path = ".".join([str(p) for p in err.path]) or "root"
                print(f"  - Correctly caught: '{path}': {err.message}")
            return True
    else:
        if not expect_valid:
            print(f"[FAIL] Expected {file_path.name} to fail validation, but it passed!")
            return False
        print(f"[PASS] {file_path.name} fully conforms to canonical contract.")
        return True


def main():
    root = Path(__file__).resolve().parent.parent
    schema_path = root / "schemas" / "student_onboarding.schema.json"

    if not schema_path.exists():
        print(f"[ERROR] Schema file not found: {schema_path}")
        sys.exit(1)

    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    print(f"[INFO] Successfully validated schema definition: {schema_path.name}")

    all_passed = True

    # 1. Validate example file (Must PASS)
    example_path = root / "schemas" / "student_onboarding.example.json"
    if not validate_file(schema, example_path, expect_valid=True):
        all_passed = False

    # 2. Validate valid fixture (Must PASS)
    valid_fixture = root / "tests" / "fixtures" / "valid_student.json"
    if not validate_file(schema, valid_fixture, expect_valid=True):
        all_passed = False

    # 3. Validate invalid fixture (Must REJECT / PASS expectation)
    invalid_fixture = root / "tests" / "fixtures" / "invalid_student.json"
    if not validate_file(schema, invalid_fixture, expect_valid=False):
        all_passed = False

    if not all_passed:
        print("\n[RESULT] Schema verification FAILED.")
        sys.exit(1)

    print("\n[RESULT] All schema contract checks PASSED successfully.")
    sys.exit(0)


if __name__ == "__main__":
    main()
