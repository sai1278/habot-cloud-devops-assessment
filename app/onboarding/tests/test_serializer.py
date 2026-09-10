"""Comprehensive test suite for StudentOnboardingSerializer.

Explicitly tests all 12 required failure and success modes:
1. Valid payload
2. Missing required field
3. Invalid type
4. Invalid boolean
5. Too-short value
6. Too-long value
7. Invalid email
8. Invalid enum/value
9. Null value
10. Unknown field
11. Invalid consent
12. Invalid DCYN decision
"""

import pytest

from onboarding.serializers import StudentOnboardingSerializer


@pytest.fixture
def valid_payload():
    return {
        "schema_version": "1.0.0",
        "student_name": "Amina Al-Mansoor",
        "parent_name": "Tariq Al-Mansoor",
        "email": "amina.almansoor@example.com",
        "consent": True,
        "support_required": True,
        "region": "MENA",
        "learning_support_type": "TECHNICAL",
        "created_at": "2026-09-10T12:00:00Z",
    }


def test_01_valid_payload(valid_payload):
    """Scenario 1: Valid conforming payload passes serializer validation."""
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert serializer.is_valid(), f"Expected valid, got errors: {serializer.errors}"
    assert serializer.validated_data["student_name"] == "Amina Al-Mansoor"
    assert serializer.validated_data["consent"] is True


def test_02_missing_required_field(valid_payload):
    """Scenario 2: Missing required field causes validation failure."""
    del valid_payload["student_name"]
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert not serializer.is_valid()
    assert "student_name" in serializer.errors
    assert serializer.errors["student_name"][0].code == "required"


def test_03_invalid_type(valid_payload):
    """Scenario 3: Non-string type for student_name causes validation failure."""
    valid_payload["student_name"] = 12345
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert not serializer.is_valid()
    assert "student_name" in serializer.errors


def test_04_invalid_boolean(valid_payload):
    """Scenario 4: Non-boolean value for support_required causes validation failure."""
    valid_payload["support_required"] = "not-a-boolean"
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert not serializer.is_valid()
    assert "support_required" in serializer.errors
    assert serializer.errors["support_required"][0].code in ("invalid", "invalid_boolean")


def test_05_too_short_value(valid_payload):
    """Scenario 5: Value below min_length causes validation failure."""
    valid_payload["student_name"] = "A"  # min_length is 2
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert not serializer.is_valid()
    assert "student_name" in serializer.errors
    assert serializer.errors["student_name"][0].code == "min_length"


def test_06_too_long_value(valid_payload):
    """Scenario 6: Value exceeding max_length causes validation failure."""
    valid_payload["student_name"] = "A" * 105  # max_length is 100
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert not serializer.is_valid()
    assert "student_name" in serializer.errors
    assert serializer.errors["student_name"][0].code == "max_length"


def test_07_invalid_email(valid_payload):
    """Scenario 7: Malformed email string causes validation failure."""
    valid_payload["email"] = "not-a-valid-email-address"
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert not serializer.is_valid()
    assert "email" in serializer.errors
    assert serializer.errors["email"][0].code == "invalid"


def test_08_invalid_enum_value(valid_payload):
    """Scenario 8: Region not in allowed enum list causes validation failure."""
    valid_payload["region"] = "ANTARCTICA"
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert not serializer.is_valid()
    assert "region" in serializer.errors
    assert serializer.errors["region"][0].code == "invalid_choice"


def test_09_null_value(valid_payload):
    """Scenario 9: Null value in non-nullable field causes validation failure."""
    valid_payload["email"] = None
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert not serializer.is_valid()
    assert "email" in serializer.errors
    assert serializer.errors["email"][0].code == "null"


def test_10_unknown_field_prohibited(valid_payload):
    """Scenario 10: Extra/unknown field in payload is strictly rejected (Poka-Yoke)."""
    valid_payload["unexpected_injected_column"] = "malicious_or_accidental_value"
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert not serializer.is_valid()
    assert "non_field_errors" in serializer.errors
    assert "Unknown fields not permitted" in str(serializer.errors["non_field_errors"])


def test_11_invalid_consent(valid_payload):
    """Scenario 11: Consent explicitly False causes DCYN rejection."""
    valid_payload["consent"] = False
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert not serializer.is_valid()
    assert "consent" in serializer.errors
    assert serializer.errors["consent"][0].code == "ERR_DCYN_CONSENT_REFUSED"


def test_12_invalid_dcyn_decision_incoherent_support(valid_payload):
    """Scenario 12: support_required=True but learning_support_type='NONE' rejected."""
    valid_payload["support_required"] = True
    valid_payload["learning_support_type"] = "NONE"
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert not serializer.is_valid()
    assert "non_field_errors" in serializer.errors
    assert serializer.errors["non_field_errors"][0].code == "ERR_DCYN_SUPPORT_INCOHERENT"


def test_13_boolean_string_coercion_prohibited(valid_payload):
    """Scenario 13: String 'true' must NOT be silently coerced to boolean True."""
    valid_payload["consent"] = "true"
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert not serializer.is_valid()
    assert "consent" in serializer.errors
    assert serializer.errors["consent"][0].code == "invalid_boolean"


def test_14_boolean_integer_coercion_prohibited(valid_payload):
    """Scenario 14: Integer 1 must NOT be silently coerced to boolean True."""
    valid_payload["support_required"] = 1
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert not serializer.is_valid()
    assert "support_required" in serializer.errors
    assert serializer.errors["support_required"][0].code == "invalid_boolean"


def test_15_string_boolean_coercion_prohibited(valid_payload):
    """Scenario 15: Boolean True must NOT be silently coerced to string 'True'."""
    valid_payload["student_name"] = True
    serializer = StudentOnboardingSerializer(data=valid_payload)
    assert not serializer.is_valid()
    assert "student_name" in serializer.errors
    assert serializer.errors["student_name"][0].code == "invalid_string"

