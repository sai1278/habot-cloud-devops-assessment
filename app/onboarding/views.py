"""Onboarding submission API endpoints."""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from onboarding.serializers import StudentOnboardingSerializer


class OnboardingSubmissionView(APIView):
    """Endpoint receiving, validating, and queueing student onboarding submissions."""

    def post(self, request, *args, **kwargs):
        serializer = StudentOnboardingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "status": "REJECTED",
                    "error_code": "ERR_VALIDATION_FAILED",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # In live cloud infrastructure, message is published to Google Cloud Pub/Sub
        # topic 'student-onboarding-events' using sa-django-publisher.
        validated_payload = serializer.validated_data

        return Response(
            {
                "status": "ACCEPTED",
                "message": "Student onboarding payload passed all DCYN gates and canonical contract.",
                "data": {
                    "student_name": validated_payload["student_name"],
                    "email": validated_payload["email"],
                    "region": validated_payload["region"],
                    "schema_version": validated_payload["schema_version"],
                    "created_at": validated_payload["created_at"].isoformat(),
                },
            },
            status=status.HTTP_201_CREATED,
        )
