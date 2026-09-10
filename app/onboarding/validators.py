"""Deterministic Consent & Yes/No (DCYN) Business Validators.

All validation functions in this module enforce strict binary logic (YES / NO).
No ambiguous intermediate states (e.g. maybe, pending, unknown) are permitted.
"""

import re

from rest_framework.exceptions import ValidationError

ALLOWED_REGIONS = {"NA", "EMEA", "APAC", "LATAM", "MENA"}
ALLOWED_SUPPORT_TYPES = {"NONE", "ACADEMIC", "TECHNICAL", "COUNSELING", "SPECIAL_NEEDS"}
NAME_REGEX = re.compile(r"^[A-Za-z]+([ A-Za-z\-']+[A-Za-z]+)*$")
ACTIVE_SCHEMA_VERSION = "1.0.0"


def validate_parental_consent(consent: bool) -> None:
    """DCYN-001: Mandatory Parental Consent Check.

    Binary Gate:
      Question: Did parent/guardian grant consent (consent == True)?
      YES -> Proceed
      NO  -> Raise ValidationError (ERR_DCYN_CONSENT_REFUSED)
    """
    if consent is not True:
        raise ValidationError(
            "Parental or legal guardian consent is mandatory and must be explicitly True.",
            code="ERR_DCYN_CONSENT_REFUSED",
        )


def validate_support_coherence(support_required: bool, learning_support_type: str) -> None:
    """DCYN-002: Support Coherence Check.

    Binary Gate:
      Question: Is learning_support_type coherent with support_required flag?
      YES -> Proceed
      NO  -> Raise ValidationError (ERR_DCYN_SUPPORT_INCOHERENT)
    """
    if support_required is False and learning_support_type != "NONE":
        raise ValidationError(
            f"When support_required is False, learning_support_type must be 'NONE'. Received: '{learning_support_type}'.",
            code="ERR_DCYN_SUPPORT_INCOHERENT",
        )
    if support_required is True and learning_support_type == "NONE":
        raise ValidationError(
            "When support_required is True, learning_support_type cannot be 'NONE'. Please select a specific support category.",
            code="ERR_DCYN_SUPPORT_INCOHERENT",
        )


def validate_region_eligibility(region: str) -> None:
    """DCYN-003: Operational Region Membership Check.

    Binary Gate:
      Question: Is the region within active operational domains?
      YES -> Proceed
      NO  -> Raise ValidationError (ERR_DCYN_UNSUPPORTED_REGION)
    """
    if region not in ALLOWED_REGIONS:
        raise ValidationError(
            f"Region '{region}' is not in supported operational regions: {sorted(ALLOWED_REGIONS)}.",
            code="ERR_DCYN_UNSUPPORTED_REGION",
        )


def validate_name_syntax(name: str, field_label: str) -> None:
    """DCYN-FORMAT: Name Syntax and Character Boundary Check."""
    if not isinstance(name, str):
        raise ValidationError(f"{field_label} must be a string.", code="invalid_type")

    stripped = name.strip()
    if len(stripped) < 2:
        raise ValidationError(
            f"{field_label} must be at least 2 characters.",
            code="min_length",
        )
    if len(stripped) > 100:
        raise ValidationError(
            f"{field_label} must not exceed 100 characters.",
            code="max_length",
        )
    if not NAME_REGEX.match(stripped):
        raise ValidationError(
            f"{field_label} contains invalid characters. Only alphabetic characters, spaces, hyphens, and apostrophes are allowed.",
            code="invalid_characters",
        )


def validate_schema_version_match(schema_version: str) -> None:
    """DCYN-005: Schema Version Compatibility Check."""
    if schema_version != ACTIVE_SCHEMA_VERSION:
        raise ValidationError(
            f"Schema version mismatch: expected '{ACTIVE_SCHEMA_VERSION}', received '{schema_version}'.",
            code="ERR_DCYN_VERSION_MISMATCH",
        )
