"""Deterministic Django REST Framework Serializer for Student Onboarding.

Enforces canonical schema constraints, rejects unrecognized fields (Poka-Yoke),
and delegates business rules to deterministic DCYN validators.
"""

from rest_framework import serializers

from onboarding.validators import (
    ALLOWED_REGIONS,
    ALLOWED_SUPPORT_TYPES,
    validate_name_syntax,
    validate_parental_consent,
    validate_schema_version_match,
    validate_support_coherence,
)


class StrictBooleanField(serializers.BooleanField):
    """Poka-Yoke: Enforces exact boolean literal (True/False) without string/integer coercion."""

    def to_internal_value(self, data):
        if not isinstance(data, bool):
            raise serializers.ValidationError(
                f"Must be a boolean literal (true or false), received {type(data).__name__}.",
                code="invalid_boolean",
            )
        return super().to_internal_value(data)


class StrictCharField(serializers.CharField):
    """Poka-Yoke: Enforces exact string literal without silent coercion of booleans, numbers, or objects."""

    def to_internal_value(self, data):
        if not isinstance(data, str):
            raise serializers.ValidationError(
                f"Must be a string literal, received {type(data).__name__}.",
                code="invalid_string",
            )
        return super().to_internal_value(data)


class StudentOnboardingSerializer(serializers.Serializer):
    """Canonical serializer validating student onboarding ingestion events."""

    schema_version = StrictCharField(
        max_length=10,
        required=True,
        allow_null=False,
    )
    student_name = StrictCharField(
        min_length=2,
        max_length=100,
        required=True,
        allow_null=False,
    )
    parent_name = StrictCharField(
        min_length=2,
        max_length=100,
        required=True,
        allow_null=False,
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        allow_null=False,
    )
    consent = StrictBooleanField(
        required=True,
        allow_null=False,
    )
    support_required = StrictBooleanField(
        required=True,
        allow_null=False,
    )
    region = serializers.ChoiceField(
        choices=sorted(ALLOWED_REGIONS),
        required=True,
        allow_null=False,
    )
    learning_support_type = serializers.ChoiceField(
        choices=sorted(ALLOWED_SUPPORT_TYPES),
        required=True,
        allow_null=False,
    )
    created_at = serializers.DateTimeField(
        required=True,
        allow_null=False,
    )

    def to_internal_value(self, data):
        """Poka-Yoke: Enforce strict schema contract by rejecting unknown fields."""
        if not isinstance(data, dict):
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid payload structure: expected a JSON object."]},
                code="invalid_payload",
            )

        declared_fields = set(self.fields.keys())
        provided_fields = set(data.keys())
        unknown_fields = provided_fields - declared_fields

        if unknown_fields:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        f"Unknown fields not permitted by canonical schema contract: {sorted(unknown_fields)}"
                    ]
                },
                code="unknown_fields_prohibited",
            )

        return super().to_internal_value(data)

    def validate_schema_version(self, value):
        validate_schema_version_match(value)
        return value

    def validate_student_name(self, value):
        validate_name_syntax(value, "Student name")
        return value.strip()

    def validate_parent_name(self, value):
        validate_name_syntax(value, "Parent name")
        return value.strip()

    def validate_consent(self, value):
        validate_parental_consent(value)
        return value

    def validate(self, attrs):
        """Cross-field DCYN binary decision gates."""
        validate_support_coherence(
            support_required=attrs["support_required"],
            learning_support_type=attrs["learning_support_type"],
        )
        return attrs
