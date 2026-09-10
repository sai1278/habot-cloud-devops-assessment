from django.db import models


class StudentOnboarding(models.Model):
    """Domain model representing a validated student onboarding submission.
    
    In the production cloud architecture, validated records are published
    directly to Google Cloud Pub/Sub and synced into BigQuery D1 staged storage.
    This model serves as a domain reference and local staging representation.
    """

    REGION_CHOICES = (
        ("NA", "North America"),
        ("EMEA", "Europe, Middle East, Africa"),
        ("APAC", "Asia-Pacific"),
        ("LATAM", "Latin America"),
        ("MENA", "Middle East & North Africa"),
    )

    SUPPORT_TYPE_CHOICES = (
        ("NONE", "No Additional Support"),
        ("ACADEMIC", "Academic Tutoring"),
        ("TECHNICAL", "Technical & Hardware Accommodation"),
        ("COUNSELING", "Student Counseling"),
        ("SPECIAL_NEEDS", "Accessibility / Special Educational Needs"),
    )

    schema_version = models.CharField(max_length=10, default="1.0.0")
    student_name = models.CharField(max_length=100)
    parent_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    consent = models.BooleanField(default=False)
    support_required = models.BooleanField(default=False)
    region = models.CharField(max_length=10, choices=REGION_CHOICES)
    learning_support_type = models.CharField(max_length=20, choices=SUPPORT_TYPE_CHOICES, default="NONE")
    created_at = models.DateTimeField()

    class Meta:
        managed = False  # Managed by canonical schema & BigQuery
        db_table = "student_onboarding"
        verbose_name = "Student Onboarding Submission"
        verbose_name_plural = "Student Onboarding Submissions"

    def __str__(self):
        return f"{self.student_name} ({self.region}) - {self.created_at}"
