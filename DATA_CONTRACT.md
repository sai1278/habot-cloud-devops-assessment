# Canonical Data Contract Specification

This document defines the authoritative data contract governing student onboarding data across Habot Connect systems.

---

## 1. Authoritative Schema Specification

The canonical contract is maintained as a machine-readable JSON Schema (Draft 2020-12) located at:
[`schemas/student_onboarding.schema.json`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/schemas/student_onboarding.schema.json).

### Field Definitions & Type Constraints

| Field Name | Type | Constraints | Required | Description |
|---|---|---|---|---|
| `schema_version` | string | Enum: `["1.0.0"]` | **YES** | Immutable semantic contract version identifier. |
| `student_name` | string | Min: 2, Max: 100, Regex: `^[A-Za-z]+([ A-Za-z\-']+[A-Za-z]+)*$` | **YES** | Full legal name of the registering student. |
| `parent_name` | string | Min: 2, Max: 100, Regex: `^[A-Za-z]+([ A-Za-z\-']+[A-Za-z]+)*$` | **YES** | Full legal name of the parent or appointed legal guardian. |
| `email` | string | Max: 254, Format: `email` (RFC 5322) | **YES** | Official contact email address for communications. |
| `consent` | boolean | Constant: `true` | **YES** | Mandatory parental consent flag. Must strictly be `true`. |
| `support_required` | boolean | Boolean (`true` or `false`) | **YES** | Indicates if educational accommodations are requested. |
| `region` | string | Enum: `["NA", "EMEA", "APAC", "LATAM", "MENA"]` | **YES** | Primary operational region code for student residency. |
| `learning_support_type` | string | Enum: `["NONE", "ACADEMIC", "TECHNICAL", "COUNSELING", "SPECIAL_NEEDS"]` | **YES** | Specific category of accommodation requested. |
| `created_at` | string | Format: `date-time` (ISO-8601 UTC) | **YES** | Moment record passed validation and entered ingestion. |

**Strict Rule**: `additionalProperties: false`. Any field not declared in this contract is considered a violation and rejected immediately.

---

## 2. End-to-End Field Mapping

| Canonical Field Name | DRF Serializer Field | Pub/Sub Message Attribute | BigQuery Column | BigQuery Data Type | BigQuery Mode |
|---|---|---|---|---|---|
| `schema_version` | `CharField(max_length=10)` | `schema_version` | `schema_version` | `STRING` | `REQUIRED` |
| `student_name` | `CharField(min_length=2, max_length=100)` | `student_name` | `student_name` | `STRING` | `REQUIRED` |
| `parent_name` | `CharField(min_length=2, max_length=100)` | `parent_name` | `parent_name` | `STRING` | `REQUIRED` |
| `email` | `EmailField(max_length=254)` | `email` | `email` | `STRING` | `REQUIRED` |
| `consent` | `BooleanField()` | `consent` | `consent` | `BOOLEAN` | `REQUIRED` |
| `support_required` | `BooleanField()` | `support_required` | `support_required` | `BOOLEAN` | `REQUIRED` |
| `region` | `ChoiceField(...)` | `region` | `region` | `STRING` | `REQUIRED` |
| `learning_support_type` | `ChoiceField(...)` | `learning_support_type` | `learning_support_type` | `STRING` | `REQUIRED` |
| `created_at` | `DateTimeField()` | `created_at` | `created_at` | `TIMESTAMP` | `REQUIRED` |

---

## 3. Schema Evolution & Versioning Rules
1. **Patch Updates (`1.0.x`)**: Clarifications, non-structural documentation updates.
2. **Minor Updates (`1.x.0`)**: Adding optional fields. Backward-compatible changes require a planned BigQuery table migration and schema update before deploying new producer versions.
3. **Major Updates (`2.0.0`)**: Breaking changes (removing fields, altering types, narrowing regex). Requires new Pub/Sub topics and versioned BigQuery tables (e.g. `student_onboarding_v2`).
