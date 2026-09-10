from django.urls import include, path

urlpatterns = [
    path("api/v1/onboarding/", include("onboarding.urls")),
]
