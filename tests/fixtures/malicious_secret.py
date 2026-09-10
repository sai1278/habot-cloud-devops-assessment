"""SAFE TEST FIXTURE: Controlled Mock Secret for Secret Scanner Verification.

CRITICAL NOTICE:
This file contains deliberate, NON-PRODUCTION, SYNTHETIC mock credentials.
It is explicitly designed to test the fail-closed behavior of CI/CD secret detection gates
(Gitleaks, detect-secrets, regex scanners).
NEVER commit genuine credentials or API keys.
"""

# Synthetic GCP Service Account Private Key Mock (SAFE MOCK PATTERN)
MOCK_GCP_PRIVATE_KEY_PATTERN = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC3fakefakefake\nfakefakefakefakefakefakefakefakefakefakefakefakefakefakefakefake\n-----END PRIVATE KEY-----"

# Synthetic High-Entropy Token (SAFE MOCK PATTERN)
MOCK_HARDCODED_API_TOKEN = "AIzaSyFakeGoogleApiKeyPatternTestingOnly1234567"
MOCK_AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
# Synthetic Generic Token (SAFE MOCK PATTERN - High-Entropy Assignment)
mock_auth_token = "synthetic_test_token_habot_security_check_9876543210"
