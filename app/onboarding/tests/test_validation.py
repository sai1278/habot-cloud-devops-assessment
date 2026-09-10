"""Unit tests for deterministic DCYN validation functions."""

import pytest
from rest_framework.exceptions import ValidationError

from onboarding.validators import (
    validate_name_syntax,
    validate_parental_consent,
    validate_region_eligibility,
    validate_schema_version_match,
    validate_support_coherence,
)


def test_parental_consent_pass():
    validate_parental_consent(True)


@pytest.mark.parametrize("invalid_consent", [False, None, 0, "True"])
def test_parental_consent_fail(invalid_consent):
    with pytest.raises(ValidationError) as exc:
        validate_parental_consent(invalid_consent)
    assert exc.value.get_codes() == ["ERR_DCYN_CONSENT_REFUSED"]


def test_support_coherence_valid_cases():
    validate_support_coherence(False, "NONE")
    validate_support_coherence(True, "ACADEMIC")
    validate_support_coherence(True, "TECHNICAL")
    validate_support_coherence(True, "COUNSELING")
    validate_support_coherence(True, "SPECIAL_NEEDS")


def test_support_coherence_invalid_cases():
    with pytest.raises(ValidationError) as exc1:
        validate_support_coherence(False, "TECHNICAL")
    assert exc1.value.get_codes() == ["ERR_DCYN_SUPPORT_INCOHERENT"]

    with pytest.raises(ValidationError) as exc2:
        validate_support_coherence(True, "NONE")
    assert exc2.value.get_codes() == ["ERR_DCYN_SUPPORT_INCOHERENT"]


def test_region_eligibility():
    for region in ["NA", "EMEA", "APAC", "LATAM", "MENA"]:
        validate_region_eligibility(region)

    with pytest.raises(ValidationError) as exc:
        validate_region_eligibility("MARS")
    assert exc.value.get_codes() == ["ERR_DCYN_UNSUPPORTED_REGION"]


def test_name_syntax():
    validate_name_syntax("Amina Al-Mansoor", "Student name")
    validate_name_syntax("John O'Connor", "Student name")
    validate_name_syntax("Mary-Jane Watson", "Student name")

    with pytest.raises(ValidationError):
        validate_name_syntax("A", "Student name")  # min_length

    with pytest.raises(ValidationError):
        validate_name_syntax("John123", "Student name")  # invalid chars


def test_schema_version():
    validate_schema_version_match("1.0.0")

    with pytest.raises(ValidationError) as exc:
        validate_schema_version_match("2.0.0")
    assert exc.value.get_codes() == ["ERR_DCYN_VERSION_MISMATCH"]
