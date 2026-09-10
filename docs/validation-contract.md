# Validation Contract & Type Enforcement Architecture

This document details the layered validation pipeline that processes student onboarding requests at Habot Connect, from raw JSON wire input to analytical data staging.

---

## 1. End-to-End Validation Flow

```text
                       Inbound JSON Request Body
                                  |
                                  v
+-------------------------------------------------------------------+
| Stage 1: JSON Wire Parser & Strict Structure Check               |
| - Verify valid RFC 8259 JSON structure                            |
| - Verify payload is a JSON Object (dict), not list/primitive     |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| Stage 2: Poka-Yoke Unknown Field Rejection (to_internal_value)    |
| - Calculate: set(data.keys()) - set(declared_fields.keys())       |
| - If unknown fields exist: FAIL HTTP 400 immediately              |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| Stage 3: Strict Field Typing & Anti-Coercion (DRF Field Level)    |
| - StrictCharField: No silent coercion of bool/int to string       |
| - StrictBooleanField: No silent coercion of "true"/1 to boolean  |
| - EmailField: RFC 5322 syntax validation                         |
| - ChoiceField: Enum membership verification                       |
| - DateTimeField: ISO-8601 UTC timestamp parsing                   |
| - allow_null = False: Reject any null values                      |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| Stage 4: Deterministic DCYN Business Rules (validators.py)        |
| - validate_parental_consent: consent must be explicitly True      |
| - validate_support_coherence: support_required vs support_type    |
| - validate_region_eligibility: region in operational catalog      |
| - validate_name_syntax: length bounds & regex                     |
| - validate_schema_version_match: exact match to '1.0.0'           |
+---------------------------------+---------------------------------+
                                  |
               +------------------+------------------+
               | Any Check Fails                     | All Checks Pass
               v                                     v
+-----------------------------+       +-----------------------------+
| HTTP 400 Bad Request        |       | HTTP 201 Created            |
| Status: REJECTED            |       | Status: ACCEPTED            |
| Error Code: Deterministic   |       | Event Published to Pub/Sub  |
+-----------------------------+       +-----------------------------+
```

---

## 2. Anti-Coercion Guarantee (Poka-Yoke)

In standard Django REST Framework, `BooleanField` automatically parses permissive truthy strings (`"true"`, `"True"`, `"1"`, `1`) into boolean `True`. However, in the canonical JSON Schema (`schemas/student_onboarding.schema.json`), `"type": "boolean"` strictly rejects string representations.

To prevent silent type coercion:
- `StrictBooleanField` in [`app/onboarding/serializers.py`](file:///c:/Users/kanchiDhyana%20sai/OneDrive/Desktop/Habot/app/onboarding/serializers.py) enforces:
  ```python
  if not isinstance(data, bool):
      raise serializers.ValidationError(..., code="invalid_boolean")
  ```
- `StrictCharField` enforces:
  ```python
  if not isinstance(data, str):
      raise serializers.ValidationError(..., code="invalid_string")
  ```

### Coercion Test Verification
| Submitted Payload | Standard DRF Behavior | Habot Poka-Yoke Behavior | Test Reference |
|---|---|---|---|
| `{"consent": "true"}` | Coerced to `True` (Silent Pass) | **REJECTED** (`invalid_boolean`) | `test_13_boolean_string_coercion_prohibited` |
| `{"support_required": 1}` | Coerced to `True` (Silent Pass) | **REJECTED** (`invalid_boolean`) | `test_14_boolean_integer_coercion_prohibited` |
| `{"student_name": True}` | Coerced to `"True"` (Silent Pass) | **REJECTED** (`invalid_string`) | `test_15_string_boolean_coercion_prohibited` |
| `{"student_name": 12345}` | Coerced to `"12345"` (Silent Pass) | **REJECTED** (`invalid_string`) | `test_03_invalid_type` |

---

## 3. Deterministic Error Code Registry

| Error Code | Triggering Condition | HTTP Status | Response Example |
|---|---|---|---|
| `unknown_fields_prohibited` | Extra field present in JSON payload | 400 | `{"non_field_errors": ["Unknown fields not permitted: ['injected_col']"]}` |
| `ERR_DCYN_CONSENT_REFUSED` | `consent` is `False`, `null`, or missing | 400 | `{"consent": ["Parental or legal guardian consent is mandatory..."]}` |
| `ERR_DCYN_SUPPORT_INCOHERENT`| `support_required=False` with support type, or `support_required=True` with `NONE` | 400 | `{"non_field_errors": ["When support_required is True, type cannot be NONE..."]}` |
| `ERR_DCYN_UNSUPPORTED_REGION`| `region` not in `["NA", "EMEA", "APAC", "LATAM", "MENA"]` | 400 | `{"region": ["\"MARS\" is not a valid choice."]}` |
| `ERR_DCYN_VERSION_MISMATCH` | `schema_version` not equal to `"1.0.0"` | 400 | `{"schema_version": ["Schema version mismatch: expected '1.0.0'..."]}` |
| `invalid_boolean` | Non-boolean primitive passed for boolean field | 400 | `{"consent": ["Must be a boolean literal (true or false)..."]}` |
| `invalid_string` | Non-string primitive passed for string field | 400 | `{"student_name": ["Must be a string literal..."]}` |
| `min_length` | String length below 2 characters | 400 | `{"student_name": ["Ensure this field has at least 2 characters."]}` |
| `max_length` | String length exceeds 100 characters | 400 | `{"student_name": ["Ensure this field has no more than 100 characters."]}` |
| `null` | Non-nullable field receives JSON `null` | 400 | `{"email": ["This field may not be null."]}` |
| `required` | Mandatory contract field omitted from payload | 400 | `{"parent_name": ["This field is required."]}` |
