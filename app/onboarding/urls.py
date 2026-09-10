from django.urls import path

from onboarding.views import OnboardingSubmissionView

urlpatterns = [
    path("", OnboardingSubmissionView.as_view(), name="onboarding-submission"),
]
